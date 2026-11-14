# Edit dasar: alur standar, apply_operations, menentukan elemen

## Alur operasi standar

### Langkah 1: Pastikan koneksi
- Panggil `corel_status` untuk memastikan CDR online; jika CDR belum terbuka (dan Anda sudah jelas ingin memakainya) akan dijalankan otomatis; jika tidak ditemukan, buka CorelDRAW secara manual dulu.

### Langkah 2: Ikat dokumen
- Panggil `attach_active_document` untuk mendapat `session_id`; jika pengguna menyebut nama dokumen, pakai `attach_open_document` dengan `name_or_path`.

### Langkah 3: Lihat kondisi saat ini (wajib)
- Panggil `inspect_document` (dengan session_id) untuk mendapat `shape_id`, tipe, posisi, ukuran, dan isi teks semua bentuk. Tidak boleh menebak shape_id.

### Langkah 4: Jalankan perubahan
- Panggil `apply_operations` dengan `session_id`, `expected_revision` (revision yang dikembalikan di langkah 3), `label` (keterangan perubahan ini), dan `operations` (array operasi, lihat di bawah).

### Langkah 5: Pratinjau (opsional)
- Panggil `render_preview` untuk merender PNG agar dikonfirmasi pengguna.

### Langkah 6: Simpan
- Panggil `save_current_document` hanya jika pengguna jelas memintanya.

## Sistem koordinat

- Titik asal: kiri atas halaman; X bertambah ke kanan; Y bertambah ke bawah; satuan: milimeter.

## Operasi yang didukung apply_operations

Setiap elemen adalah objek operasi, dengan field `op` menentukan tipenya:

| Nama op | Fungsi | Parameter kunci |
|---|---|---|
| `text.set_content` | Ubah isi teks | `shape_id`, `value` |
| `text.set_style` | Ubah gaya font | `shape_id`, `font_family`, `font_size_pt`, `bold` |
| `text.create_frame` | Buat frame teks baru | `x_mm`, `y_mm`, `width_mm`, `height_mm`, `value`, `font_family`, `font_size_pt`, `bold` |
| `shape.create_rectangle` | Gambar persegi | `x_mm`, `y_mm`, `width_mm`, `height_mm`, `corner_radius` |
| `shape.create_ellipse` | Gambar elips/lingkaran (lingkaran sempurna: lebar=tinggi) | `x_mm`, `y_mm`, `width_mm`, `height_mm`, `fill_rgb`, `outline_rgb`, `outline_width_pt`, `no_outline` |
| `shape.move` | Pindahkan | `shape_id`, `x_mm`, `y_mm` |
| `shape.resize` | Ubah ukuran | `shape_id`, `width_mm`, `height_mm` |
| `shape.rotate` | Putar | `shape_id`, `angle_deg` |
| `shape.delete` | Hapus (⚠️ hanya jika disebut jelas oleh pengguna) | `shape_id` |
| `fill.set_cmyk` | Isi warna CMYK | `shape_id`, `c`, `m`, `y`, `k` (0-100) |
| `fill.set_rgb` | Isi warna RGB | `shape_id`, `r`, `g`, `b` (0-255) |

### Contoh operasi pembuatan

Membuat frame teks baru:
```json
{
  "op": "text.create_frame",
  "x_mm": 40, "y_mm": 80, "width_mm": 120, "height_mm": 30,
  "value": "CYBER MONDAY",
  "font_family": "Arial", "font_size_pt": 24, "bold": true
}
```

Membuat persegi baru:
```json
{
  "op": "shape.create_rectangle",
  "x_mm": 50, "y_mm": 100, "width_mm": 160, "height_mm": 90,
  "corner_radius": 8
}
```

Jika teks bisa dibuat langsung, jangan minta pengguna menambahkannya manual; jika perlu miring, panggil `shape.rotate`.

## Menentukan elemen (cara menemukan target dengan tepat sebelum mengubah)

Berdasarkan prioritas:

1. **🔴 Pengguna sudah memilih di CDR → `get_selection` (tercepat dan paling akurat)**
   - Membaca bentuk yang sedang dipilih (multi-pilih, pilih kotak, grup), mengembalikan `shape_id`, tipe, posisi, ukuran, teks tiap bentuk.
   - Jika pengguna berkata "ubah yang ini" / "ubah yang saya pilih", atau ada elemen berulang/sulit dideskripsikan, panggil ini dulu untuk mendapat ID, baru ubah.
   - Jika count=0, minta pengguna memilih/memblok dulu, jangan menebak.
2. **Pengguna langsung mendeskripsikan isi/posisi → `inspect_document`**
   - Memindai seluruh kanvas, mencocokkan shape_id berdasarkan isi/posisi.
3. Tangkapan layar hanya sebagai referensi tambahan, tidak bisa langsung memberi shape_id.
