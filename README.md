# Convertly

Convertly adalah aplikasi konversi file lokal dengan tampilan seperti contoh.
File diproses di komputer sendiri dan tidak dikirim ke server.

## Menjalankan web app Windows

```powershell
cd "C:\Users\Desta Julp\Downloads\matplotlib"
py -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\streamlit run src\exe_to_pdf\web_app.py
```

Buka `http://localhost:8501`.

## Konversi yang tersedia

- PNG, JPG, JPEG, dan WEBP ke PNG/JPG/WEBP/PDF
- PDF ke PNG atau JPG (satu halaman per file)
- PDF ke DOCX (ekstrak teks)
- PDF ke Excel XLSX (teks per baris)
- TXT/CSV ke PDF
- Banyak file sekaligus
- Hapus background foto secara lokal dengan hasil PNG transparan
- Ganti background foto dengan warna pilihan atau gambar lain

EXE buatan Vaysoft PDF to EXE akan didekripsi dari overlay-nya menjadi PDF
asli tanpa menjalankan program. EXE biasa atau EXE dari tool lain tidak
didukung karena format penyimpanan PDF-nya berbeda.
