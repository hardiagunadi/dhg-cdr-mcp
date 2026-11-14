# Trace bitmap (mengubah bitmap menjadi kontur vektor)

Jika perlu meniru gambar asli (logo, teks, grafik; mengubah bitmap menjadi vektor yang bisa diedit menurut kontur), pakai `trace_bitmap`, yang memanggil Corel PowerTRACE untuk membuat kurva vektor otomatis menurut kontur, seperti alat pen yang menelusuri kontur.

## 🔴 Langkah 0: Jika prompt mungkin melewatkan elemen, tampilkan dialog agar pengguna memilih (dipicu bersyarat, tidak bertele-tele)

Pengguna sering berkata "trace teks / trace gambar ini", tetapi di gambar bisa ada beberapa jenis elemen sekaligus: **huruf Mandarin, huruf Latin, logo, grafik**, dll. **Dilarang memutuskan sendiri hanya men-trace satu jenis** (mis. hanya Mandarin, melewatkan huruf Latin dan logo).

Caranya:
1. Pertama tentukan: apakah prompt pengguna sudah jelas mencakup elemen yang akan di-trace?
   - Jika pengguna berkata "semua/seluruh/seluruh gambar/Mandarin dan Latin keduanya", atau gambar hanya berisi jenis yang disebut pengguna → **langsung ke langkah 1, tanpa menyela, tanpa menyebut satu per satu**.
2. **Hanya jika pengguna berbicara umum, sementara gambar berisi beberapa jenis elemen yang mungkin terlewat**, baru panggil dialog `interaction.ask`, dan di `display_message` **hanya sebut bagian yang mungkin terlewat** (tidak mendaftar panjang satu per satu):
   - question_id: `trace_scope`; header: `Cakupan trace`
   - Contoh display_message: `Selain huruf Mandarin, di gambar ada huruf Latin dan logo yang mungkin terlewat. Kali ini mau men-trace yang mana?`
   - Pilihan:
     1. option_id `all`, label `Trace semuanya (tanpa terlewat)`, description: `Huruf Mandarin, huruf Latin, logo, grafik semuanya menjadi vektor, tanpa terlewat (rekomendasi default).`
     2. option_id `named_only`, label `Hanya yang saya sebut`, description: `Hanya men-trace bagian yang baru saja saya sebut (mis. hanya huruf Mandarin).`
     3. option_id `custom`, label `Saya tentukan sendiri`, description: `Saya jelaskan secara rinci mana yang diinginkan dan mana yang tidak.`
   - Setelah pengguna memilih, baru ke langkah 1.
3. Jika tidak yakin dengan maksud pengguna, perlakukan sebagai "tanpa terlewat", atau langsung tampilkan dialog.

## 🔴 Langkah 1: Minta pengguna memilih cara konversi ke vektor (wajib)

**Pertama panggil `interaction.ask` agar pengguna memilih mode**, jelaskan dua cara dan berikan rekomendasi kepada pengguna, lalu jalankan sesuai pilihan; jangan memutuskan sendiri.

- question_id: `trace_mode`; header: `Cara konversi vektor`
- display_message: `Pilih cara konversi ke vektor (saya juga sertakan rekomendasi):`
- Pilihan:
  1. option_id `direct`, label `Langsung ke vektor`, description: `Cocok untuk gambar yang memang sudah bersih, latar warna solid/datar (mis. ikon, gambar teks dengan latar solid). Langsung trace, cepat, tanpa konfirmasi.`
  2. option_id `cleanup`, label `Pisahkan latar dulu, konfirmasi baru konversi (direkomendasikan)`, description: `Cocok untuk foto, tangkapan layar, dan gambar dengan latar/bayangan/kesan 3D. Pertama diekstrak menjadi gambar datar yang bersih untuk Anda konfirmasi, setelah puas baru dikonversi ke vektor, hasil terbaik.`

**Memberi rekomendasi:** kecuali gambar asli jelas bersih dan berwarna solid/datar, rekomendasikan `cleanup`, karena foto/gambar kompleks yang langsung dikonversi hasilnya buruk.

Setelah pengguna memilih, lanjut ke alur yang sesuai.

## Alur satu: pisahkan latar dan murnikan dulu, baru trace (cleanup, hasil terbaik)

PowerTRACE paling baik pada gambar yang **bersih, datar, dengan kontur tajam**; foto asli dengan latar kompleks, bayangan, ketebalan 3D, gradien sangat buruk jika langsung di-trace.

**Langkah pertama: gunakan desain kreatif (image_edit gambar ke gambar) untuk memurnikan target menjadi gambar bersih**
- Pertahankan utuh bentuk huruf/bentuk, warna, dan posisi relatif elemen target
- Hapus latar sepenuhnya, ganti dengan **latar putih polos #FFFFFF** (tanpa tekstur, gradien, noise)
- Hilangkan bayangan, ketebalan 3D, bayangan bawah, tepi gelap, jadikan grafik datar warna solid
- Buat tepi kontur bersih dan tajam, tanpa duri
- Jika perlu beberapa putaran (jika pengguna berkata "hilangkan bayangan/kontur lebih jelas lagi", image_edit lagi)

**Langkah kedua: 🔴 wajib berhenti menunggu konfirmasi pengguna, dilarang melanjutkan trace otomatis**
- Setelah pemisahan latar, tampilkan dulu gambar yang sudah dimurnikan kepada pengguna
- Tanyakan dengan jelas: "Apakah hasil ini sudah memuaskan? Setelah dikonfirmasi saya konversi ke vektor; jika belum puas saya perbaiki lagi."
- **Hanya jika pengguna jelas berkata "boleh/konfirmasi/lanjut/silakan trace", baru ke langkah ketiga**; sebelum pengguna mengonfirmasi tidak boleh memanggil trace_bitmap otomatis
- Jika pengguna tidak puas, lanjutkan image_edit sesuai masukan, setelah selesai kembali ke langkah ini untuk konfirmasi

**Langkah ketiga: setelah pengguna mengonfirmasi, jalankan gambar bersih ini dengan `trace_bitmap` (berikan image_path)**
- Vektor hasil trace gambar bersih rapi, node teratur, hasilnya sangat baik

## Alur dua: trace langsung (direct)

Jika pengguna memilih `direct`, atau gambar asli sudah bersih dan berwarna solid/datar (mis. logo latar solid, ikon), langsung pakai `trace_bitmap`, boleh menambah `remove_background=true`, tidak perlu konfirmasi di tengah.

## Parameter

- `image_path`: path gambar lokal, jika diberikan otomatis diimpor ke kanvas lalu di-trace (paling sering dipakai)
- `shape_id`: trace bitmap yang sudah ada di kanvas; jika kosong memakai satu-satunya bitmap di halaman saat ini
- `crop`: **hanya men-trace sebagian gambar** (bukan seluruh gambar). Format `[left, top, right, bottom]`, rasio terhadap lebar/tinggi gambar 0-1 (0,0=kiri atas, 1,1=kanan bawah). Lihat gambar dulu untuk menentukan rasio area target, baru potong dan trace.
- `trace_type`: jenis trace 1-8 (1 gambar garis/blok warna, makin besar makin condong ke gambar), default 1
- `smoothing`: kehalusan 0-100, default 30 (makin besar node makin sedikit)
- `detail_level`: detail 0-100, default 100
- `color_mode`: mode warna, default 2 (mengikuti gambar asli, mempertahankan warna)
- `color_count`: jumlah warna, default 16
- `delete_original`: apakah bitmap dihapus setelah trace, default False
- `remove_background`: apakah latar dihapus otomatis, default False
- `place`: posisi hasil, **default `"beside"` (diletakkan di sisi kanan gambar asli berdampingan, mudah dibandingkan langsung, dan gambar asli tidak dihapus)**; `"over"` ditumpuk di atas gambar asli (akan bertumpuk).

## Ucapan umum

- "Ambil huruf papan nama dari foto ini, latar putih, hilangkan bayangan" → image_edit dulu untuk dimurnikan
- Setelah pengguna mengonfirmasi gambar bersih: "trace gambar ini menjadi vektor" → baru trace_bitmap
- Jika hanya men-trace sebagian gambar, pada tahap pemurnian suruh image_edit hanya mempertahankan targetnya (lebih bersih daripada crop)
- **Setelah trace, hasil default diletakkan di sisi kanan gambar asli berdampingan**, kiri gambar asli, kanan vektor, tidak perlu menghapus gambar asli, dan tidak akan bertumpuk atau bergeser
