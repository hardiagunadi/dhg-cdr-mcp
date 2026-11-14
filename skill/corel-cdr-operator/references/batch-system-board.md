# Papan data / papan aturan massal (sekali parse + tata letak massal)

Menggandakan satu templat papan yang sudah jadi menjadi banyak papan sesuai data, tiap papan diganti judul dan isinya, dan disusun otomatis dalam grid. Dua tool bekerja bersama: `parse_board_records` (parse data) → `batch_system_board` (gandakan dan atur tata letak).

## Alur lengkap

**Langkah 1: Minta pengguna menyiapkan templat dan memilih seluruh papan**
- Templat = bentuk papan dasar + teks judul + teks paragraf isi (satu papan lengkap).
- Minta pengguna di CDR **memblok seluruh papan templat (termasuk judul dan isi) dan tetap memilihnya**.
- Judul dan isi dikenali otomatis: judul = teks dengan ukuran font terbesar, isi = teks paragraf (jika tidak ada teks paragraf, ambil yang karakternya paling banyak); jika pengenalan kurang tepat, minta pengguna menentukannya.

**Langkah 2: Ambil data (tiga sumber)**
1. **Word (.doc/.docx)**: dibaca langsung dengan python-docx (tanpa menjalankan Word, sangat cepat), dipecah menurut tingkat judul (gaya Heading 1-9, atau baris pendek tebal dikenali otomatis), satu rekaman per judul, teks di bawah judul menjadi body.
   - **Tabel Word tidak diekstrak tetapi diberi peringatan**: isi tabel tidak diambil, hasil parse akan memberi petunjuk "terdeteksi N tabel, isi tabel tidak diekstrak".
2. **Excel (.xls/.xlsx)**: satu baris satu rekaman, kolom A = judul, kolom B dan seterusnya = isi (jika ada header "judul/isi" akan dilewati otomatis).
3. **Teks biasa (dikirim langsung di percakapan)**: judul ditandai dengan tanda kurung lebar penuh （） atau biasa () pada baris tersendiri, teks di bawahnya hingga judul berikutnya adalah isi. Format:
   ```
   （Aturan Satu）
   Pasal 1 ……
   Pasal 2 ……
   （Aturan Dua）
   Pasal 3 ……
   ```

**Langkah 3: Panggil `parse_board_records` untuk parse**
- Parameter:
  - File: `source_type` ("word"/"excel", kosongkan untuk mengikuti ekstensi), `file_path`
  - Teks percakapan: `text` (judul ditandai dengan （）)
  - Word dapat ditambah `heading_level` (1-9, 0 otomatis)
- Mengembalikan `records` (tiap rekaman berisi index/title/body).
- **Setelah parse berhasil langsung lanjut ke tata letak, tidak perlu mendaftar rekaman satu per satu untuk diperiksa pengguna** (pengguna memeriksa akhirnya di CDR); hanya jika parse gagal/error baru berhenti dan tangani.

**Langkah 4: Tentukan jumlah kolom (berapa per baris)**
- **Default 4 per baris, tidak perlu bertanya**.
- Hanya jika **jumlah rekaman lebih dari 12**, tampilkan dialog (pilihan angka) agar pengguna menentukan berapa per baris.
- Jarak default 10mm (pakai ini jika pengguna tidak meminta lain).

**Langkah 5: Panggil `batch_system_board` sekali jalan**
- Parameter: `records`, `columns` (default 4), `gap` (default 10).
- Secara internal tool: membaca templat terpilih → menggandakan dalam grid (templat asli dipertahankan, mulai dari sisi kanan templat) → mengganti judul/isi (mempertahankan font/ukuran/spasi huruf/perataan/spasi baris) → **jika isi terlalu panjang, ukuran font salinan itu dikecilkan otomatis hingga muat (salinan lain tidak berubah, shrink_pt tercantum di hasil)** → tiap salinan dijadikan grup.

**Langkah 6: Setelah selesai jangan render pratinjau, langsung ingatkan untuk cek di CDR**
- Beri tahu "sudah dibuat N papan, silakan cek di CDR", pengguna memeriksa sendiri di CDR. Tidak menyimpan otomatis.

## Perhatian

- Templat asli dipertahankan, tidak ditimpa.
- Jika isi suatu papan terlalu panjang, hanya papan itu yang dikecilkan, tidak memengaruhi papan lain.
- Jika parse error (file tidak ada, tidak ada rekaman terparse, judul kosong), berhenti dan beri tahu pengguna, jangan memaksakan tata letak.
