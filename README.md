# CorelDRAW Live MCP

---

## 1. Masalah yang diselesaikan proyek ini

Desainer setiap hari mengerjakan banyak operasi CorelDRAW yang repetitif dan mekanis: mengganti teks, mengatur warna, membuat papan nomor/papan aturan secara massal, mencari gambar di web lalu menempelkannya satu per satu, mengekspor ke berbagai format... Pekerjaan ini memakan waktu dan mudah salah.

Proyek ini membungkus antarmuka COM CorelDRAW menjadi **layanan tool MCP**, sehingga klien AI seperti Claude Desktop, Claude Code, Cursor, dan VS Code bisa mengendalikan CorelDRAW lokal lewat bahasa alami:

- **Tanpa pindah aplikasi**: AI langsung mengoperasikan file desain yang sedang Anda buka
- **Edit realtime yang aman**: semua perubahan melalui "sesi + validasi versi"; jika salah, cukup satu kali Undo
- **Otomasi massal**: pencarian gambar, penempatan, tata letak, dan ekspor selesai dengan satu perintah

> **Batasan platform**: hanya mendukung Windows (COM API CorelDRAW bergantung pada Windows). MCP Server harus berjalan di komputer Windows yang sama dengan CorelDRAW.

---

## 2. Fitur utama

Secara default produksi memakai **tool set ringkas compact (28 tool)** yang mencakup sekitar 90% kebutuhan harian:

| Modul | Tool utama | Keterangan |
|---|---|---|
| Pemeriksaan salah ketik | `extract_selected_text`, `mark_text_errors`, `fix_text_errors`, `restore_marked_colors` | Ekstrak teks terpilih → AI memeriksa salah ketik/tata bahasa → tandai dengan warna → perbaiki sekali klik → kembalikan warna asli, tanpa token tambahan |
| Edit realtime aman | `corel_status`, `attach_active_document`, `inspect_document`, `apply_operations`, `render_preview`, `save_current_document`, `undo_last_edit` | Attach ke dokumen yang terbuka → periksa → ubah batch secara atomik (satu Undo) → pratinjau → simpan, seluruhnya dengan sesi + validasi versi |
| Cari & tempatkan gambar massal | `batch_search_images`, `batch_search_and_place`, `batch_place_images` | Cari gambar otomatis berdasarkan kata kunci (sisi terpanjang ≥1000px, filter watermark/animasi, unduh paralel), tempatkan ke frame terpilih via PowerClip dalam satu panggilan |
| Papan data/papan aturan massal | `parse_board_records`, `batch_system_board` | Parse data Word/Excel/teks → gandakan templat papan secara massal, susun dalam grid dan ganti judul serta isi |
| Bagan organisasi | `create_org_chart` | Masukkan teks/JSON, otomatis membuat bagan organisasi vertikal/horizontal |
| Grafik & bitmap | `import_bitmap`, `import_svg`, `trace_bitmap`, `apply_gradient_fill`, `create_curve_shape`, `duplicate_shapes`, `get_selection` | Impor bitmap/SVG, trace bitmap menjadi kurva, isi gradien, baca elemen terpilih menurut urutan baca |
| Manajemen file | `create_new_document`, `save_document_as`, `export_document` | Dokumen baru, simpan sebagai, ekspor PDF/SVG/PNG, dll. |
| Bangun dari spesifikasi | `build_from_spec` | Membangun desain dari spesifikasi deklaratif (JSON) |

Setel variabel lingkungan `COREL_TOOL_PROFILE=legacy` untuk beralih ke **tool set legacy lengkap (70+ tool tingkat rendah)**, termasuk:

- **Produksi templat**: papan nomor/papan nama (`composite`), faktur/banner/kartu nama/poster cerdas (`smart_layout`), gambar teknik (`engineering`)
- **Menggambar dasar**: persegi/elips/garis, operasi boolean, group/ungroup, perataan dan distribusi, rotasi dan skala, PowerClip (`shapes`)
- **Teks**: ganti isi, atur gaya, teks ke kurva, deteksi overflow (`text`)
- **Warna**: isi CMYK/RGB/Pantone, outline, gradien, transparansi, latar halaman (`colors`)
- **Layer**: buat/query/tetapkan/tampil-sembunyi/kunci (`layers`)
- **Preflight**: cek ukuran, overflow teks, font hilang, laporan warna (`preflight`)
- **Penggabungan data**: baca Excel, gabung massal, buat barcode/QR code (`data_merge`)

> Tool set legacy yang terlalu besar dapat menurunkan akurasi AI dalam memilih tool; untuk pemakaian harian disarankan tetap memakai compact.

---

## 3. Instalasi

### Persyaratan

- Windows 10/11
- CorelDRAW X6 atau lebih baru (harus sudah terpasang; verifikasi versi Anda sebelum dipakai sungguhan)
- Python 64-bit 3.11–3.13 (bitness Python harus sama dengan CorelDRAW)

### Langkah instalasi

```powershell
# 1. Buat virtual environment
py -3.12 -m venv .venv

# 2. Aktifkan virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Pasang dependensi
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Dependensi opsional (pasang sesuai kebutuhan)

```powershell
pip install ".[agent]"       # Streamlit + LLM Agent bawaan (opsional)
pip install ".[datamerge]"   # Data Excel, barcode, QR code, bantuan gambar
pip install ".[https]"       # Pembungkus HTTPS lokal (opsional)
pip install ".[all]"         # Pasang semuanya
```

---

## 4. Cara penggunaan

### 4.1 Menjalankan MCP Server

Jalankan CorelDRAW dan buka dokumen yang akan dioperasikan, lalu jalankan layanan:

```powershell
$env:COREL_ATTACH_POLICY = "existing_only"
python server\server.py --transport stdio
```

> Saat layanan dimulai, CorelDRAW **tidak dibuka otomatis**; koneksi baru dibuat (lazy) ketika tool pertama dipanggil, agar tidak mengganggu pekerjaan Anda.

### 4.2 Konfigurasi klien MCP

Contoh untuk Claude Desktop, tambahkan ke file konfigurasi MCP-nya (ganti kedua path dengan path asli di komputer Anda):

```json
{
  "mcpServers": {
    "coreldraw-live": {
      "command": "C:\\path\\to\\corel-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\path\\to\\corel-mcp\\server\\server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1",
        "COREL_ATTACH_POLICY": "existing_only",
        "COREL_TOOL_PROFILE": "compact"
      }
    }
  }
}
```

File acuan: `claude_desktop_config.example.json` dan `mcp_config_guide.md` di root repositori.

### 4.3 Alur kerja standar (edit realtime aman)

Setiap perubahan sebaiknya memanggil tool dengan urutan berikut:

1. `corel_status` — pastikan koneksi dan dokumen yang terbuka
2. `list_open_documents` — daftar dokumen yang tersedia
3. `attach_active_document` (atau `attach_open_document`) — attach ke dokumen
4. `inspect_document` — lihat struktur dokumen, dapatkan shape_id
5. `apply_operations` — ubah batch secara atomik dengan `revision` yang dikembalikan
6. `render_preview` — render pratinjau PNG bila perlu untuk pengecekan
7. `save_current_document` — simpan hanya jika pengguna meminta dengan jelas
8. `detach_document` — akhiri sesi

> `attach_active_document` tidak pernah membuat atau membuka dokumen baru; `save_current_document` tidak pernah menyimpan dengan nama file baru tanpa diminta.

### 4.4 Variabel lingkungan

| Variabel | Default | Keterangan |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Mode transport: `stdio` / `streamable-http` / `sse` |
| `MCP_HOST` | `127.0.0.1` | Alamat listen mode HTTP/SSE |
| `MCP_PORT` | `8765` | Port listen mode HTTP/SSE |
| `COREL_ATTACH_POLICY` | `existing_only` | Hanya attach ke instans CorelDRAW yang sudah ada |
| `COREL_TOOL_PROFILE` | `compact` | Tool set: `compact` (ringkas) / `legacy` (lengkap) |
| `COREL_OUTPUT_ROOT` | tidak ada | Batasi path ekspor/simpan hanya di dalam direktori tertentu |

### 4.5 Konvensi koordinat

Semua data geometri publik memakai **titik asal di kiri atas halaman, sumbu Y ke bawah, satuan milimeter**:

```json
{
  "coordinate_space": "page_top_left",
  "unit": "mm",
  "bounds": {"x": 10, "y": 20, "width": 80, "height": 30}
}
```

Koordinat hanya dikonversi satu kali oleh lapisan driver, sehingga tidak ada konversi ganda antara AI dan CorelDRAW.

---

## 5. Contoh masukan dan keluaran

### Contoh 1: Cari gambar massal dan tempatkan (seluruh alur dengan satu perintah)

Di CDR pilih N frame, lalu katakan kepada AI "carikan gambar untuk 4 frame ini: bakso, soto, ayam goreng, gado-gado". AI akan memanggil:

**Masukan** (`batch_search_and_place`):

```json
{
  "keywords": ["bakso", "soto", "ayam goreng", "gado-gado"],
  "container_ids": null,
  "fit_mode": "fill",
  "min_long_edge": 1000
}
```

**Keluaran**: tiap kata kunci dicari gambarnya (otomatis disaring sisi terpanjang ≥1000px, tanpa watermark, bukan animasi) lalu ditempatkan lewat PowerClip ke kontainer yang sesuai, dengan hasil penempatan per kontainer:

```json
{
  "ok": true,
  "placed": [
    {"keyword": "bakso", "container_id": "136", "image": "D:/temp/bakso_01.jpg", "w_px": 1200, "h_px": 800},
    {"keyword": "soto", "container_id": "137", "image": "D:/temp/soto_02.jpg", "w_px": 1000, "h_px": 1000}
  ]
}
```

### Contoh 2: Edit realtime aman (perubahan batch atomik)

**Masukan** (`apply_operations`, mengganti judul dengan teks promosi dan memindahkannya):

```json
{
  "session_id": "sess_example",
  "expected_revision": 4,
  "label": "Perbarui judul promo",
  "operations": [
    {
      "op": "text.set_content",
      "shape_id": "128",
      "value": "SUMMER SALE"
    },
    {
      "op": "text.set_style",
      "shape_id": "128",
      "font_family": "Montserrat",
      "font_size_pt": 30,
      "bold": true
    },
    {
      "op": "shape.move",
      "shape_id": "128",
      "x": 20,
      "y": 15
    }
  ]
}
```

**Keluaran**: seluruh batch dijalankan sebagai satu transaksi atomik dan mengembalikan revision baru; jika terjadi error, seluruh batch di-rollback sehingga tidak ada keadaan setengah berubah.

Operasi atomik yang didukung tool set compact:

- `text.set_content` / `text.set_style` / `text.create_frame`
- `shape.set_bounds` / `shape.move` / `shape.resize` / `shape.create_rectangle` / `shape.rotate` / `shape.rename` / `shape.delete`
- `fill.set_cmyk` / `fill.set_rgb`

### Contoh 3: Papan data/papan aturan massal

**Langkah 1 — parse data** (`parse_board_records`, ekstrak rekaman dari Excel/Word/teks):

**Masukan**:

```json
{
  "source_type": "excel",
  "file_path": "D:/data/papan_aturan.xlsx"
}
```

**Keluaran** (tiap rekaman berisi judul + isi, untuk diperiksa AI):

```json
{
  "ok": true,
  "records": [
    {"title": "Aturan Keselamatan Kerja", "body": "1. Wajib memakai helm keselamatan saat masuk bengkel..."},
    {"title": "Aturan Pemadam Kebakaran", "body": "1. Alat pemadam diperiksa sebulan sekali..."}
  ],
  "table_count": 0
}
```

**Langkah 2 — tata letak massal** (`batch_system_board`, pilih satu templat papan yang sudah jadi di CDR):

**Masukan**:

```json
{
  "records": [
    {"title": "Aturan Keselamatan Kerja", "body": "1. Wajib memakai helm keselamatan saat masuk bengkel..."},
    {"title": "Aturan Pemadam Kebakaran", "body": "1. Alat pemadam diperiksa sebulan sekali..."}
  ],
  "columns": 4,
  "gap": 10.0
}
```

**Keluaran**: templat asli dipertahankan, salinan disusun dalam grid mulai dari sisi kanan templat (4 per baris, jarak 10mm), judul dan isi diganti satu per satu.

---

## Pengujian

Uji unit lintas platform:

```powershell
python -m unittest discover -s tests -v
python -m compileall -q server tests
```

Uji end-to-end Windows/CorelDRAW (CorelDRAW lokal harus sudah berjalan):

```powershell
python server\test_e2e.py
```

> Sebelum rilis, gerbang rilis akhir harus dijalankan di Windows + setiap versi CorelDRAW yang didukung; perilaku COM tidak dapat diverifikasi di Linux.

---

## Keamanan

- Jangan commit `.env`, API Key, log, file desain pelanggan, atau crash dump ke repositori
- Layanan lokal hanya memakai stdio atau jaringan loopback saja
- Jangan membuka otomasi COM CorelDRAW langsung ke internet publik
- Konfirmasi secara eksplisit sebelum menimpa file, melakukan edit destruktif, atau eksekusi jarak jauh
- Setel `COREL_OUTPUT_ROOT` untuk membatasi ekspor/simpan ke direktori tertentu
- Pratinjau/ekspor default `overwrite=false`; jika file tujuan sudah ada, penimpaan ditolak

---

## Sinkronisasi otomatis ke GitHub

Skrip `scripts/auto-sync.ps1` mengommit semua perubahan lokal lalu mendorongnya ke `origin`. Jalankan manual, atau daftarkan sebagai tugas terjadwal Windows (mis. tiap 10 menit):

```powershell
schtasks /Create /TN "dhg-cdr-mcp-auto-sync" /SC MINUTE /MO 10 /TR "pwsh -NoProfile -WindowStyle Hidden -File C:\Users\<user>\tools\dhg-cdr-mcp\scripts\auto-sync.ps1"
```

---

## Lisensi

Apache License 2.0. Lihat `LICENSE` dan `NOTICE` (memuat atribusi pemegang hak cipta asli Xuanshang Zhineng dan atribusi tambahan proyek ini, dhxg).
