# Menggambar kurva bebas dan isi gradien

## Kurva bebas (bendera, gelombang, pita, bentuk tak beraturan)

Untuk menggambar kontur non-persegi (bendera berkibar, gelombang, pita, alas bentuk khusus), pakai `create_curve_shape`, jangan dipaksakan dengan persegi.

**Parameter:**
- `subpaths`: array path, tiap path berisi:
  - `points`: daftar titik, satuan mm, titik asal di kiri atas halaman, y ke bawah
    - Titik pertama adalah titik awal: `{"x": 50, "y": 50}`
    - Tiap titik berikutnya adalah satu segmen:
      - Segmen garis lurus `{"type": "line", "x": 100, "y": 100}`
      - Segmen kurva Bezier `{"type": "curve", "x": 100, "y": 40,
        "cp1x": 60, "cp1y": 50,   # handle kontrol 1, dekat titik sebelumnya
        "cp2x": 90, "cp2y": 40}`  # handle kontrol 2, dekat titik saat ini
  - `closed`: apakah tertutup (untuk diisi warna harus true)
- `fill_rgb`: warna isi `[r,g,b]`; atau `fill_cmyk`: `[c,m,y,k]`
- Default tanpa outline

**Ide menggambar bendera berkibar:**
1. Pakai `create_curve_shape` menggambar kontur luar bendera bergelombang (2-3 segmen Bezier di bagian atas untuk gelombang), isi merah
2. Lalu gambar beberapa kurva merah tua/gelap yang ditumpuk untuk memberi kesan lipatan dan bayangan
3. Tiang bendera dengan persegi atau garis (bisa memakai shape.create_rectangle dari apply_operations)

**Perhatian:** titik kontrol Bezier memakai koordinat absolut, tool otomatis mengonversinya; cukup beri sesuai posisi visual.

## Isi gradien

Untuk membuat gradien pada bentuk (linear/radial/conical/persegi), pakai `apply_gradient_fill`.

**Parameter:**
- `shape_id`: bentuk target
- `start_rgb` / `end_rgb`: warna awal dan akhir `[r,g,b]` (atau `start_cmyk`/`end_cmyk`)
- `gradient_type`: `"linear"` (linear, default) / `"radial"` (radial) / `"conical"` (conical) / `"square"` (persegi)
- `angle`: sudut, untuk linear: 0 dari kiri ke kanan, 90 dari bawah ke atas
- `midpoint`: titik tengah 0-100 (default 50)
- `edge_pad`: ruang kosong tepi 0-49
- `center_offset_x/y`: pergeseran pusat radial/conical
- `color_stops`: titik warna tengah untuk gradien multiwarna, `[{"position":33,"rgb":[r,g,b]}]`; jika tidak diberikan maka dua warna

**Skenario penggunaan:** latar poster, alas gradien, kesan tiga dimensi bendera, tekstur logam, dll.
