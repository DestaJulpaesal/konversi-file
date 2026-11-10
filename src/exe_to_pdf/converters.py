from __future__ import annotations

from collections import deque
from io import BytesIO
from pathlib import Path

from exe_to_pdf.core import ExtractionError, extract_pdf


class ConversionError(ValueError):
    """Raised when a conversion cannot be completed."""


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _extension(name: str) -> str:
    return Path(name).suffix.lower()


def _image_to_image(source: bytes, output_format: str) -> tuple[bytes, str, str]:
    try:
        from PIL import Image
    except ImportError as error:
        raise ConversionError("Pillow belum terpasang.") from error
    try:
        image = Image.open(BytesIO(source))
        if output_format in {"JPEG", "PDF"} and image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        output = BytesIO()
        image.save(output, format=output_format)
    except Exception as error:
        raise ConversionError("File gambar tidak valid atau rusak.") from error
    extension = output_format.lower().replace("jpeg", "jpg")
    return output.getvalue(), extension, f"image/{extension}"


def _load_image(source: bytes):
    try:
        from PIL import Image
    except ImportError as error:
        raise ConversionError("Pillow belum terpasang.") from error
    try:
        return Image.open(BytesIO(source)).convert("RGBA")
    except Exception as error:
        raise ConversionError("File gambar tidak valid atau rusak.") from error


def _remove_background(image, tolerance: int = 48):
    width, height = image.size
    pixels = image.load()
    samples = [
        pixels[0, 0],
        pixels[width - 1, 0],
        pixels[0, height - 1],
        pixels[width - 1, height - 1],
    ]
    threshold = tolerance * tolerance
    queue = deque()
    visited = bytearray(width * height)
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(1, height - 1):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if visited[index]:
            continue
        visited[index] = 1
        pixel = pixels[x, y]
        distance = min(
            sum((pixel[channel] - sample[channel]) ** 2 for channel in range(3))
            for sample in samples
        )
        if distance > threshold:
            continue
        pixels[x, y] = (*pixel[:3], 0)
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))
    return image


def _fit_background(background, size: tuple[int, int]):
    from PIL import Image

    target_width, target_height = size
    scale = max(target_width / background.width, target_height / background.height)
    resized = background.resize(
        (round(background.width * scale), round(background.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_width) // 2
    top = (resized.height - target_height) // 2
    return resized.crop((left, top, left + target_width, top + target_height))


def edit_image(source: bytes, operation: str, background: bytes | None = None,
               background_color: str = "#E8F1FF") -> tuple[bytes, str, str]:
    """Apply local background editing to an image and return a transparent PNG."""
    try:
        from PIL import Image, ImageColor
    except ImportError as error:
        raise ConversionError("Pillow belum terpasang.") from error
    image = _remove_background(_load_image(source), tolerance=64)
    if operation == "REMOVE_BG":
        result = image
    elif operation == "REPLACE_BG_COLOR":
        try:
            color = ImageColor.getrgb(background_color)
        except (ImportError, ValueError) as error:
            raise ConversionError("Warna background tidak valid.") from error
        canvas = Image.new("RGBA", image.size, (*color, 255))
        result = Image.alpha_composite(canvas, image)
    elif operation == "REPLACE_BG_IMAGE":
        if background is None:
            raise ConversionError("Tambahkan gambar background kedua.")
        backdrop = _fit_background(_load_image(background), image.size)
        result = Image.alpha_composite(backdrop, image)
    else:
        raise ConversionError("Operasi background tidak dikenal.")
    output = BytesIO()
    result.save(output, format="PNG")
    return output.getvalue(), "png", "image/png"


def _pdf_to_images(source: bytes, output_format: str) -> tuple[bytes, str, str]:
    try:
        import fitz
    except ImportError as error:
        raise ConversionError("PyMuPDF belum terpasang.") from error
    document = fitz.open(stream=source, filetype="pdf")
    if not document.page_count:
        raise ConversionError("PDF tidak memiliki halaman.")
    if document.page_count > 1:
        raise ConversionError(
            "PDF memiliki beberapa halaman. Konversi satu halaman per file "
            "agar hasil download tidak membingungkan."
        )
    page = document[0]
    pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    extension = "jpg" if output_format == "JPEG" else "png"
    return pixmap.tobytes(extension), extension, f"image/{extension}"


def _pdf_to_docx(source: bytes) -> tuple[bytes, str, str]:
    try:
        import fitz
        from docx import Document
    except ImportError as error:
        raise ConversionError("PyMuPDF dan python-docx belum terpasang.") from error
    document = Document()
    pdf = fitz.open(stream=source, filetype="pdf")
    for index, page in enumerate(pdf):
        if index:
            document.add_page_break()
        text = page.get_text("text").strip()
        document.add_paragraph(text or "[Halaman tidak memiliki teks yang dapat diekstrak]")
    output = BytesIO()
    document.save(output)
    return output.getvalue(), "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _pdf_to_xlsx(source: bytes) -> tuple[bytes, str, str]:
    try:
        import fitz
        from openpyxl import Workbook
    except ImportError as error:
        raise ConversionError("PyMuPDF dan openpyxl belum terpasang.") from error
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "PDF text"
    sheet.append(["Halaman", "Baris teks"])
    pdf = fitz.open(stream=source, filetype="pdf")
    for page_number, page in enumerate(pdf, 1):
        for line in page.get_text("text").splitlines():
            if line.strip():
                sheet.append([page_number, line])
    output = BytesIO()
    workbook.save(output)
    return output.getvalue(), "xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _text_to_pdf(source: bytes) -> tuple[bytes, str, str]:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen.canvas import Canvas
    except ImportError as error:
        raise ConversionError("ReportLab belum terpasang.") from error
    output = BytesIO()
    canvas = Canvas(output, pagesize=A4)
    _, height = A4
    y = height - 48
    for line in source.decode("utf-8", errors="replace").splitlines():
        canvas.drawString(48, y, line[:120])
        y -= 14
        if y < 48:
            canvas.showPage()
            y = height - 48
    canvas.save()
    return output.getvalue(), "pdf", "application/pdf"


def _exe_to_pdf(source: bytes, source_name: str) -> tuple[bytes, str, str]:
    try:
        extracted = extract_pdf(source, source_name)
    except ExtractionError as error:
        raise ConversionError(str(error)) from error
    return extracted.pdf, "pdf", "application/pdf"


def convert(source: bytes, source_name: str, target: str) -> tuple[bytes, str, str]:
    """Convert one uploaded file to the selected target format."""
    extension = _extension(source_name)
    pair_targets = {
        "JPG_TO_PNG": (".png", "PNG"),
        "JPG_TO_WEBP": (".webp", "WEBP"),
        "JPG_TO_PDF": (".pdf", "PDF"),
        "PNG_TO_JPG": (".jpg", "JPEG"),
        "PNG_TO_WEBP": (".webp", "WEBP"),
        "PNG_TO_PDF": (".pdf", "PDF"),
        "WEBP_TO_JPG": (".jpg", "JPEG"),
        "WEBP_TO_PNG": (".png", "PNG"),
        "WEBP_TO_PDF": (".pdf", "PDF"),
    }
    if target in pair_targets:
        _, output_format = pair_targets[target]
        source_extensions = {
            "JPG_TO_PNG": {".jpg", ".jpeg"},
            "JPG_TO_WEBP": {".jpg", ".jpeg"},
            "JPG_TO_PDF": {".jpg", ".jpeg"},
            "PNG_TO_JPG": {".png"},
            "PNG_TO_WEBP": {".png"},
            "PNG_TO_PDF": {".png"},
            "WEBP_TO_JPG": {".webp"},
            "WEBP_TO_PNG": {".webp"},
            "WEBP_TO_PDF": {".webp"},
        }
        if extension not in source_extensions[target]:
            source_name_by_target = {
                "JPG_TO_PNG": "JPG",
                "JPG_TO_WEBP": "JPG",
                "JPG_TO_PDF": "JPG",
                "PNG_TO_JPG": "PNG",
                "PNG_TO_WEBP": "PNG",
                "PNG_TO_PDF": "PNG",
                "WEBP_TO_JPG": "WEBP",
                "WEBP_TO_PNG": "WEBP",
                "WEBP_TO_PDF": "WEBP",
            }
            raise ConversionError(
                f"Format ini membutuhkan file {source_name_by_target[target]}, "
                f"bukan {extension or 'file tanpa ekstensi'}."
            )
        return _image_to_image(source, output_format)
    pair_pdf_targets = {
        "PDF_TO_JPG": ("JPEG", ".jpg"),
        "PDF_TO_PNG": ("PNG", ".png"),
        "PDF_TO_DOCX": (None, ".docx"),
        "PDF_TO_XLSX": (None, ".xlsx"),
    }
    if target in pair_pdf_targets:
        if extension != ".pdf":
            raise ConversionError("Konversi ini membutuhkan file PDF.")
        output_format, _ = pair_pdf_targets[target]
        if target == "PDF_TO_JPG":
            return _pdf_to_images(source, "JPEG")
        if target == "PDF_TO_PNG":
            return _pdf_to_images(source, "PNG")
        if target == "PDF_TO_DOCX":
            return _pdf_to_docx(source)
        return _pdf_to_xlsx(source)
    if target in {"TXT_TO_PDF", "CSV_TO_PDF"}:
        expected = ".txt" if target == "TXT_TO_PDF" else ".csv"
        if extension != expected:
            raise ConversionError(f"Konversi ini membutuhkan file {expected[1:].upper()}.")
        return _text_to_pdf(source)
    if target == "EXE_TO_PDF":
        if extension != ".exe":
            raise ConversionError("Konversi ini membutuhkan file EXE Vaysoft.")
        return _exe_to_pdf(source, source_name)
    if extension == ".exe" and target == "EXE":
        target = "PDF"
    if target == "JPG" and extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return _image_to_image(source, "JPEG")
    if target == "PNG" and extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return _image_to_image(source, "PNG")
    if target == "WEBP" and extension in {".png", ".jpg", ".jpeg"}:
        return _image_to_image(source, "WEBP")
    if target == "PDF" and extension in {".png", ".jpg", ".jpeg", ".webp"}:
        return _image_to_image(source, "PDF")
    if target == "PNG" and extension == ".pdf":
        return _pdf_to_images(source, "PNG")
    if target == "JPG" and extension == ".pdf":
        return _pdf_to_images(source, "JPEG")
    if target == "DOCX" and extension == ".pdf":
        return _pdf_to_docx(source)
    if target == "XLSX" and extension == ".pdf":
        return _pdf_to_xlsx(source)
    if target == "PDF" and extension in {".txt", ".csv"}:
        return _text_to_pdf(source)
    if extension == ".exe":
        if target == "PDF":
            return _exe_to_pdf(source, source_name)
        raise ConversionError("EXE hanya dapat diproses sebagai PDF.")
    raise ConversionError(f"Konversi {extension or 'file'} ke {target} belum tersedia.")


def output_name(source_name: str, extension: str) -> str:
    return f"{Path(source_name).stem}.{extension}"
