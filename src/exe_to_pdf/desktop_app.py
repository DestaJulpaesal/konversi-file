from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from .core import ExtractionError, extract_pdf


def main() -> None:
    root = tk.Tk()
    root.title("EXE → PDF")
    root.geometry("480x220")
    root.resizable(False, False)

    status = tk.StringVar(value="Pilih EXE wrapper yang berisi PDF.")

    def select_file() -> None:
        source_path = filedialog.askopenfilename(
            title="Pilih file EXE",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")],
        )
        if not source_path:
            return
        try:
            result = extract_pdf(Path(source_path).read_bytes(), source_path)
        except (OSError, ExtractionError) as error:
            messagebox.showerror("Gagal", str(error))
            return

        destination = filedialog.asksaveasfilename(
            title="Simpan PDF",
            initialfile=f"{Path(source_path).stem}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not destination:
            return
        try:
            Path(destination).write_bytes(result.pdf)
        except OSError as error:
            messagebox.showerror("Gagal menyimpan", str(error))
            return
        status.set(f"Berhasil: {Path(destination).name}")
        messagebox.showinfo("Selesai", f"PDF berhasil disimpan ke:\n{destination}")

    tk.Label(
        root,
        text="EXE → PDF",
        font=("Segoe UI", 22, "bold"),
    ).pack(pady=(28, 8))
    tk.Label(
        root,
        text="Ekstrak PDF tertanam tanpa menjalankan file EXE.",
    ).pack()
    tk.Button(root, text="Pilih EXE dan ekstrak PDF", command=select_file).pack(pady=24)
    tk.Label(root, textvariable=status, fg="#555").pack()
    root.mainloop()


if __name__ == "__main__":
    main()

