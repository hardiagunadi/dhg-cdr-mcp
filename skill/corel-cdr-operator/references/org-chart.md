# Bagan organisasi (digambar otomatis dalam area, kotak + teks + garis siku sekaligus)

`create_org_chart`: di dalam area yang ditentukan pengguna, menggambar pohon organisasi sebagai bagan standar — kotak sudut bulat, teks di tengah kotak, garis siku penghubung induk-anak, **diskalakan proporsional tepat sesuai ukuran area, diletakkan di tengah, tidak meluap**, setelah selesai tiap elemen bisa diedit.

## Alur

**Langkah 1: Minta pengguna menentukan area gambar dulu (🔴 utamakan tool membaca kotak terpilih otomatis)**
- Minta pengguna **memilih persegi tempat bagan di CDR dan tetap memilihnya**, lalu **langsung panggil `create_org_chart` tanpa region** — tool otomatis membaca kotak terpilih sebagai area dan menggambar bagan (termasuk judul) di dalam kotak. Ini cara paling andal, menghindari status pilihan hilang atau pemetaan koordinat salah di tengah jalan.
- Bisa juga menentukan satu kotak dengan `region_shape_id`; atau `get_selection` dulu untuk mengambil `left_x_mm/top_y_mm/width_mm/height_mm` kotak terpilih dan menyusun region (x=left_x_mm, y=top_y_mm, width=width_mm, height=height_mm); pengguna juga boleh langsung memberi ukuran area.
- Tool otomatis menyisakan margin aman 3mm di sekeliling area, konten tidak menempel tepi dan tidak meluap.
- Jika muncul pesan "area gambar tidak ditemukan", minta pengguna memilih kotak dulu lalu panggil lagi. Area wajib ditentukan dulu.

**Langkah 2: Ambil data organisasi (tiga cara pemberian semuanya didukung)**
1. **Bahasa sehari-hari**: "Di bawah direktur utama ada 3 wakil direktur, wakil direktur pertama membawahi departemen keselamatan, umum, pemasaran……" → Anda susun menjadi pohon.
2. **Teks berindentasi**: satu jabatan per baris, tingkat ditunjukkan dengan spasi/Tab (diberikan ke `text`).
3. **Excel/data terstruktur**: disusun menjadi pohon bersarang (diberikan ke `data`).
4. (Khusus) pengguna sudah menata kotak di CDR dan hanya perlu merapikan garis penghubung — tool ini belum mendukung, beri tahu pengguna.

**Langkah 3: Berikan hubungan hierarki yang sudah disusun kepada pengguna untuk diperiksa** (pastikan tidak ada yang terlewat, tidak salah susun, satu akar), gambar setelah pengguna mengonfirmasi.

**Langkah 4: Tentukan arah (🔴 wajib dengan dialog pilihan angka, dilarang kotak input yang meminta pengguna mengetik)**
- Pakai dialog `interaction.ask` **dengan display_option (tombol yang bisa diklik)**, display_message juga bernomor 1/2:
  - question_id: `org_direction`; header: `Horizontal/Vertikal`
  - display_message: `Pilih arah bagan (saya sertakan saran):`
  - Pilihan:
    1. option_id `vertical`, label `Vertikal (atas ke bawah)`, description: `Cocok untuk struktur lebar dan dangkal, banyak orang tiap tingkat (tingkat bawah satu baris berisi banyak departemen).`
    2. option_id `horizontal`, label `Horizontal (kiri ke kanan)`, description: `Cocok untuk struktur sempit dan dalam, banyak tingkat (turun tingkat demi tingkat).`
- Berikan rekomendasi di display_message (lebar-dangkal pilih vertikal, dalam-sempit pilih horizontal); **dilarang kotak input bebas untuk mengetik arah**.

**Langkah 5: Pilih gaya (🔴 wajib dialog pilihan angka, dilarang kotak input)**
- Pakai dialog `interaction.ask` dengan display_option, display_message bernomor 1-7:
  - question_id: `org_style`; header: `Gaya bagan`
  - display_message: `Pilih gaya bagan:`
  - Pilihan:
    1. option_id `orange`, label `Bisnis oranye-emas`, description: `Latar krem muda + outline oranye, paling umum (rekomendasi default).`
    2. option_id `blue`, label `Biru bisnis klasik`, description: `Latar biru muda + outline biru, formal dan mantap.`
    3. option_id `gray`, label `Sederhana tepi abu-abu`, description: `Latar putih + outline abu-abu, ringkas dan bersih.`
    4. option_id `solid`, label `Isi warna solid`, description: `Latar gelap + teks putih, kontras kuat.`
    5. option_id `green`, label `Hijau segar`, description: `Latar hijau muda + outline hijau.`
    6. option_id `blackgold`, label `Hitam-emas premium`, description: `Latar hitam + outline emas, kesan premium.`
    7. option_id `custom`, label `Kustom`, description: `Anda menjelaskan warna, saya wujudkan dengan custom_style.`
- **Dilarang kotak input bebas untuk mengetik gaya**.

**Langkah 6: Konfirmasi judul besar (jika pengguna lupa tetap ingatkan secara proaktif, pakai "input teks", bukan pilihan angka)**
- Pengguna sudah memberi judul di prompt → langsung pakai, lanjut ke langkah 7.
- Pengguna belum memberi → ingatkan secara proaktif, pakai **pertanyaan input bebas** `interaction.ask` (tanpa display_option, tanpa nomor 1/2/3), agar pengguna mengetik langsung:
  - question_id: `org_title`; header: `Judul besar`
  - display_message: `Perlu judul besar di bagian atas bagan? Jika perlu, kirim langsung teks judulnya (mis. "Bagan Organisasi PT XX"); jika tidak perlu, balas "tidak perlu".`
- Pengguna mengetik judul → pakai; membalas "tidak perlu/tidak usah" → tidak ditambahkan.
- Judul default besar, tebal, warna gelap (`title_style="dark"`); jika ingin warna tema atau kustom, pengguna menyebutkannya saat input.

**Langkah 7: Panggil `create_org_chart` sekali untuk menggambar**
- Parameter kunci: `data` (pohon bersarang) atau `text` (teks berindentasi, pilih salah satu), `direction`, `region`, `style`;
- Opsional: `font_family` (default Microsoft YaHei), `base_font_pt` (default 12, diskalakan sesuai area), `h_gap`/`v_gap` (jarak setingkat/antar tingkat), `corner_radius`, `custom_style`.
- **Judul besar**: judul dari langkah 6 diberikan ke `title`; judul digambar di tengah atas dalam area dan ditebalkan, bagan otomatis mengecil dan turun, keseluruhan tetap dalam area; gaya judul dengan `title_style` (`dark` default / `theme` warna utama / `custom` bersama `title_color`); judul yang terlalu panjang otomatis diperkecil agar tidak berganti baris.
- Tool otomatis menskalakan proporsional dan menengahkan; jika area terlalu kecil sehingga font di bawah 7pt akan **langsung error** dan menyarankan ganti arah/perbesar area, tidak meninggalkan hasil setengah jadi.

**Langkah 8: Setelah berhasil jangan render pratinjau, langsung ingatkan untuk cek di CDR**; jangan panggil `render_preview`, cukup beri tahu "sudah digambar, silakan cek di CDR". Tidak menyimpan otomatis; jika pengguna berkata ubah teks/ganti gaya/ubah judul, edit per kotak.
