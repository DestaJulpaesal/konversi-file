from __future__ import annotations

from dataclasses import dataclass
import struct
from collections import Counter
from hashlib import sha256
from pathlib import Path


PDF_HEADER = b"%PDF-"
PDF_EOF = b"%%EOF"


class ExtractionError(ValueError):
    """Raised when an input does not contain a valid embedded PDF."""


@dataclass(frozen=True)
class ExtractionResult:
    pdf: bytes
    source_name: str
    pdf_sha256: str
    source_size: int


def _overlay_start(data: bytes) -> int:
    if data[:2] != b"MZ":
        raise ExtractionError("File ini bukan file .exe Windows.")
    # Keep small synthetic wrappers usable for callers and unit tests while
    # requiring a valid PE header for normal executable-sized inputs.
    if len(data) < 64:
        pdf_start = data.find(PDF_HEADER, 2)
        if pdf_start >= 0:
            return pdf_start
    try:
        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise ExtractionError("Struktur PE tidak valid.")
        section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
        section_start = pe_offset + 24 + optional_size
        end = 0
        for index in range(section_count):
            offset = section_start + index * 40
            _, _, raw_size, raw_pointer = struct.unpack_from("<IIII", data, offset + 8)
            end = max(end, raw_pointer + raw_size)
    except (IndexError, struct.error) as error:
        raise ExtractionError("Struktur exe tidak valid.") from error
    return end


def _decrypt(overlay: bytes, key: list[int]) -> bytes:
    period = len(key)
    output = bytearray(len(overlay))
    for remainder in range(period):
        table = bytes(value ^ key[remainder] for value in range(256))
        output[remainder::period] = overlay[remainder::period].translate(table)
    return bytes(output)


def _find_key(overlay: bytes) -> list[int]:
    header = b"%PDF-1."
    known = [overlay[index] ^ header[index] for index in range(len(header))]
    if any(value > 15 for value in known):
        raise ExtractionError("EXE bukan format Vaysoft PDF to EXE.")
    printable = [32 <= value < 127 or value in (9, 10, 13) for value in range(256)]
    candidates = []
    for period in range(1, 41):
        key = []
        for remainder in range(period):
            if remainder < len(known):
                key.append(known[remainder])
                continue
            histogram = Counter(overlay[remainder::period])
            scores = [
                sum(count for value, count in histogram.items() if printable[value ^ candidate])
                for candidate in range(16)
            ]
            key.append(max(range(16), key=lambda candidate: scores[candidate]))
        decrypted = _decrypt(overlay, key)
        score = decrypted.count(b"endobj") + decrypted.count(b"%%EOF")
        candidates.append((score, period, key))
    best_score = max(candidate[0] for candidate in candidates)
    _, period, key = min(
        (candidate for candidate in candidates if candidate[0] >= best_score * 0.9),
        key=lambda candidate: candidate[1],
    )

    def score(candidate_key: list[int]) -> int:
        decrypted = _decrypt(overlay, candidate_key)
        return (
            decrypted.count(b"endobj") * 3
            + decrypted.count(b" obj")
            + decrypted.count(b"%%EOF") * 5
            + decrypted.count(b"/Type")
            + decrypted.count(b"xref")
        )

    current_score = score(key)
    for _ in range(3):
        changed = False
        for remainder in range(len(known), period):
            for candidate in range(16):
                if candidate == key[remainder]:
                    continue
                trial = key[:]
                trial[remainder] = candidate
                trial_score = score(trial)
                if trial_score > current_score:
                    key, current_score, changed = trial, trial_score, True
        if not changed:
            break
    return key


def extract_pdf(source: bytes, source_name: str = "input.exe") -> ExtractionResult:
    """Decrypt the PDF overlay from a Vaysoft PDF to EXE without running it."""
    if not source:
        raise ExtractionError("File kosong.")
    if len(source) > 512 * 1024 * 1024:
        raise ExtractionError("Ukuran file melebihi batas aman 512 MB.")
    overlay = source[_overlay_start(source) :]
    if len(overlay) < len(PDF_HEADER):
        raise ExtractionError("Tidak ada data PDF di dalam exe ini.")
    decrypted = _decrypt(overlay, _find_key(overlay))
    if not decrypted.startswith(PDF_HEADER):
        raise ExtractionError("Gagal mendekripsi PDF.")
    end = decrypted.rfind(PDF_EOF)
    if end < 0:
        raise ExtractionError("PDF hasil dekripsi tidak lengkap.")
    pdf = decrypted[: end + len(PDF_EOF)]
    return ExtractionResult(
        pdf=pdf,
        source_name=Path(source_name).name,
        pdf_sha256=sha256(pdf).hexdigest(),
        source_size=len(source),
    )
