## SISTEM IKON KUSTOM (WAJIB, GANTIKAN SEMUA ATURAN IKON LAIN)

DILARANG memakai library ikon (Lucide, Feather, FontAwesome, Heroicons, Material), dilarang emoji sebagai ikon. Semua ikon digambar sendiri sebagai inline SVG dengan gaya "doodle stiker" berikut.

### Gaya dasar (sama untuk semua ikon)
- viewBox 48x48, stroke #1B1B1F lebar 2.5, stroke-linecap & stroke-linejoin "round", bentuk sedikit gemuk dan membulat (chunky), hindari sudut tajam.
- Efek "salah cetak stiker": setiap ikon punya bentuk isi warna pastel yang digeser 2.5px ke kanan-bawah dari garis tinta, tanpa stroke. Ini ciri khas utama, harus konsisten di semua ikon.
- Warna isi diambil dari palet (ungu, pink, kuning, mint, biru, oranye). Tanpa gradient, tanpa glow, tanpa 3D.
- Dibuat sebagai SVG <symbol> di satu sprite, dipanggil lewat <use>, supaya mudah diganti.

### Aturan "lucu tapi nggak lebay"
- Maksimal SATU detail lucu per ikon (mata titik, pipi pink, atau kaki mungil). Jangan semuanya sekaligus.
- Wajah (dua titik mata + senyum kecil) HANYA di 6 ikon utama: upload, file, download, sukses, level, dan tempat sampah. Ikon lain polos tapi tetap bergaya stiker.
- Tidak ada kilauan, bintang, atau sparkle tambahan di sekitar ikon.
- Ukuran dan ketebalan garis harus seragam, jangan campur gaya.

### Daftar ikon dan konsepnya
- Upload (dropzone): awan gemuk dengan dua mata titik dan mulut kecil menganga, panah kecil di atasnya seperti mau ditelan.
- File/badge format: lembar kertas dengan sudut terlipat dan wajah mungil, label format (JPG/PNG/PDF) ditulis di bawah wajah. Warna isi berbeda per format.
- Convert (panah tukar): dua panah melengkung yang saling mengejar ekor membentuk lingkaran gemuk.
- Download: panah turun yang jatuh ke mangkuk kecil, mangkuknya punya dua mata titik.
- Hapus: tong sampah gemuk dengan tutup sedikit terbuka dan satu mata mengintip.
- History ("Perut Nyam"): perut bulat dengan jam di tengahnya, jarum jamnya lucu dan tebal.
- Sukses: centang yang melengkung membentuk senyum.
- Gagal: silang dengan dua mata "x" dan mulut miring kecil.
- Streak: api kecil gemuk dengan satu mata saja, bukan api realistis.
- Level: mahkota mungil miring yang makin besar sesuai level Nyam.
- Dark mode: matahari tersenyum dan bulan sedang tidur (mata terpejam), dan keduanya bertukar dengan animasi putar singkat.
- Tools: tiap alat punya ikon sendiri (JPG→PDF: kertas bertemu buku, PNG→JPG: dua kotak bertukar warna, Gabung PDF: tumpukan kertas dijepit penjepit lucu, WEBP: bola kecil dengan sayap mungil, AI Magic: tongkat sihir pendek dengan satu bintang kecil saja).
- Menu ⋮: tiga titik berbentuk bulat gemuk, titik tengahnya sedikit lebih besar.

### Animasi ikon (halus, bukan lebay)
- Hover: ikon bergoyang kecil (rotate -6deg ke 6deg, 300ms) atau squash & stretch ringan.
- Ikon berwajah berkedip sesekali (animasi scaleY mata, interval acak 4–7 detik).
- Klik: pop kecil (scale 0.9 lalu 1.1 lalu 1).
- Hormati prefers-reduced-motion: matikan semua animasi ikon.

### Contoh gaya (ikuti pola ini untuk semua ikon lainnya)
<symbol id="i-file" viewBox="0 0 48 48" fill="none" stroke="#1B1B1F" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 8h17l8 8v24H12z" fill="currentColor" stroke="none" transform="translate(2.5 2.5)"/>
  <path d="M12 8h17l8 8v24H12z" fill="#FFF6E5"/>
  <path d="M29 8v8h8"/>
  <circle cx="20" cy="26" r="1.6" fill="#1B1B1F" stroke="none"/>
  <circle cx="29" cy="26" r="1.6" fill="#1B1B1F" stroke="none"/>
  <path d="M22 30q2.5 2.5 5 0"/>
</symbol>
(isi bayangan memakai currentColor supaya warnanya bisa diganti per format lewat CSS)