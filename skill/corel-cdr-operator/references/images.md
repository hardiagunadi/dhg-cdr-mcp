# Impor gambar: bitmap, SVG, penggantian

## Tool

- **`import_bitmap`**: mengimpor gambar lokal ke kanvas (tempel lewat clipboard, stabil per gambar). Parameter: `image_path`, opsional `x_mm`/`y_mm` (kiri atas), `width_mm` (menentukan lebar dengan skala proporsional); mengembalikan `shape_id`.
- **`import_svg`**: mengimpor **file vektor SVG** lokal ke kanvas, tetap berupa vektor yang bisa diedit (biasanya satu grup, bisa juga beberapa objek terpisah). Parameter: `svg_path`, opsional `x_mm`/`y_mm` (kiri atas, jika tidak diberikan dicarikan ruang kosong otomatis); mengembalikan `shape_id`, `shape_count`, `shape_ids`, ukuran.
  - **Buka kunci otomatis**: setelah impor otomatis mendeteksi dan membuka kunci objek terkunci hasil impor ini (setara klik kanan → Unlock, rekursif ke dalam grup, grup tidak dibongkar; hanya membuka kunci yang diimpor kali ini, tidak menyentuh objek terkunci lain, `unlocked_object_count` tercantum di hasil). Jika layer saat ini terkunci juga dibuka otomatis (`layer_was_unlocked`).
- **`replace_bitmap`**: mengganti bitmap yang ada (mendukung di dalam kontainer PowerClip).
- **Dilarang meminta pengguna mengimpor manual dengan Ctrl+I**: jika gambar ada di lokal, langsung impor otomatis dengan tool.

## Penanganan otomatis gambar sangat besar (tidak crash)

- `import_bitmap`/`trace_bitmap` lebih dulu men-downsample gambar secara proporsional hingga sisi terpanjang 2000px, mengimpor pada 300 DPI, **setelah impor sisi terpanjang tetap ≤169mm** (berapa pun ukuran asli; bitmap besar yang sudah ada di kanvas otomatis diperkecil hingga dalam 400mm sebelum di-trace).
- Sudah diverifikasi: gambar sangat besar seperti 8000×6000, 12000×800 semuanya diimpor menjadi 169mm, trace selesai dalam beberapa detik, tidak lagi timeout karena ukuran terlalu besar hingga terputus (Transport closed).

## Penempatan otomatis (tengah di halaman kosong; jika ada konten cari ruang kosong; baru di sekitar jika penuh)

- Jika posisi tidak ditentukan:
  - **Halaman sama sekali kosong → langsung ditempatkan di tengah halaman (tengah horizontal + vertikal)**
  - Ada konten → cari ruang kosong tanpa tumpang tindih di dalam halaman (dahulu kiri atas, lalu lanjut ke kanan/bawah elemen yang ada, tetap dalam halaman)
  - Benar-benar tidak muat di halaman → baru ditempatkan di area pasteboard di kanan atau bawah halaman
- Jangan menempatkan di luar halaman atau di kiri atas saat halaman kosong. `on_page` di hasil menunjukkan apakah berada di dalam halaman.
