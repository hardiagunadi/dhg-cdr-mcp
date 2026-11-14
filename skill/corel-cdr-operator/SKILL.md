---
name: corel-cdr-operator
description: Mengoperasikan file desain CorelDRAW 2026 lokal. Aktif otomatis ketika pengguna menyebut CDR, CorelDRAW, ganti teks, ganti warna, gambar bentuk, ekspor desain, ubah file desain secara massal, impor gambar ke CDR, menggambar di CDR, papan nomor, papan nama, papan aturan, atau desain poster. Semua operasi WAJIB lewat konektor MCP yang sudah dikonfigurasi ("心哥cdr效率AI操作插件"); dilarang keras menulis sendiri PowerShell / Python / win32com untuk memanggil COM CDR.
version: 2.0
---

# Aturan Inti Operasi CorelDRAW

Anda sudah terhubung ke konektor MCP CorelDRAW ("心哥cdr效率AI操作插件"). **File ini hanya berisi aturan wajib yang dibaca setiap kali dan daftar tool; parameter/alur terperinci tiap fitur dibaca sesuai kebutuhan dari file terkait di `references/`, jangan baca semuanya di awal.**

## 🔴 Aturan wajib (selalu ditaati)

1. **Dilarang menulis kode sendiri untuk menyambung ke CDR**: semua operasi hanya lewat tool MCP; GetActiveObject/Dispatch bermasalah pada CDR 2026 dan kode buatan sendiri akan membuatnya hang. Jika tool belum ada, katakan langsung kepada pengguna "belum dibuat di MCP", jangan menempuh jalan pintas dengan skrip.
2. **🔴 Dilarang keras menghapus elemen yang tidak disebut jelas oleh pengguna**: menggambar/mengubah selalu ditumpuk di atas gambar yang ada, dilarang "kosongkan dulu baru gambar"; hapus hanya jika pengguna jelas berkata "hapus/buang/kosongkan". Jika ragu, pertahankan.
3. **🔴 Dilarang keras menyimpan otomatis**: setelah trace/impor/ubah, jangan menyimpan atas inisiatif sendiri dan jangan bilang "saya simpan ke drive sekian"; simpan hanya jika pengguna jelas berkata "simpan/simpan sebagai/simpan ke drive sekian", dan jangan digabung dengan operasi lain dalam satu giliran.
4. **Hubungkan sesuai kebutuhan**: sambungkan/jalankan CDR hanya ketika benar-benar perlu mengoperasikannya; jika tidak perlu, tidak dibuka otomatis.
5. **Setelah operasi CDR berhasil, jangan render pratinjau** (kecuali perbandingan berdampingan saat trace), cukup beri tahu "silakan cek di CDR".
6. **Satu hal per giliran**: jangan menjejalkan beberapa perubahan tak terkait dalam satu panggilan, karena sulit di-rollback jika salah.

## Daftar tool (32 buah, per kategori)

| Kategori | Tool | Kegunaan |
|---|---|---|
| Koneksi/dokumen | corel_status | Cek status online (koneksi sesuai kebutuhan) |
| | list_open_documents | Daftar dokumen yang terbuka |
| | attach_active_document | Ikat dokumen aktif, dapatkan session_id |
| | attach_open_document | Ikat dokumen tertentu berdasarkan nama/path |
| | create_new_document | Buat dokumen baru |
| | inspect_document | Lihat semua bentuk (ID/tipe/posisi/ukuran/teks) |
| | apply_operations | Jalankan operasi batch: ganti teks/warna/gambar bentuk, dll. |
| | render_preview | Render pratinjau PNG |
| | undo_last_edit / redo_last_edit | Urungkan / ulangi |
| | save_current_document / save_document_as | Simpan / simpan sebagai (hanya jika diminta pengguna) |
| | export_document | Ekspor pdf/svg/png/jpg/dxf |
| | detach_document | Lepas dokumen |
| Menggambar | create_curve_shape | Kurva bebas/kontur tak beraturan (bendera, gelombang) |
| | apply_gradient_fill | Isi gradien (linear/radial/conical/persegi) |
| Gambar | import_bitmap | Impor bitmap (downsample otomatis, tengah di halaman kosong) |
| | import_svg | Impor vektor SVG (otomatis dibuka kuncinya, dapat diedit) |
| | replace_bitmap | Ganti bitmap yang ada (mendukung di dalam PowerClip) |
| | trace_bitmap | Trace bitmap menjadi vektor |
| Batch | duplicate_shapes | Gandakan grup secara massal, susun grid, ubah teks satu per satu |
| | get_selection | Baca elemen terpilih saat ini (cara tercepat menentukan target) |
| | batch_place_images | Tempatkan gambar lokal secara massal dengan PowerClip |
| | batch_search_images | Hanya cari dan unduh gambar (tidak ditempatkan) |
| | batch_search_and_place | Cari gambar + tempatkan PowerClip dalam sekali jalan |
| | create_org_chart | Gambar bagan organisasi otomatis di dalam area |
| Pemeriksaan salah ketik | extract_selected_text | Ekstrak seluruh teks terpilih (untuk diperiksa, mengembalikan teks akurat untuk penentuan posisi) |
| | mark_text_errors | Tandai kesalahan dengan warna berdasarkan rentang karakter (merah=salah ketik/biru=kalimat tidak jelas/oranye=masalah logika, warna asli dicatat otomatis) |
| | fix_text_errors | Ganti kesalahan berdasarkan rentang karakter (warna tanda dipertahankan, bisa dipulihkan sekali klik) |
| | restore_marked_colors | Kembalikan semua tanda ke warna aslinya sekali klik |
| Papan data massal | parse_board_records | Parse Word/Excel/teks menjadi rekaman (judul + isi) |
| | batch_system_board | Gandakan templat secara massal, ganti judul dan isi |

## 🔴 Aturan wajib pemeriksaan salah ketik (jika pengguna berkata "periksa salah ketik", wajib ikuti alur ini)

1. **Dilarang keras** memakai tool umum pengubah warna `apply_operations` / `fill.set_rgb` untuk menandai kesalahan — itu akan mewarnai seluruh paragraf, tidak bisa hanya menandai karakter yang salah
2. **Alur standar**:
   ① `extract_selected_text` untuk mendapat seluruh teks terpilih
   ② Baca teliti: periksa salah ketik huruf demi huruf, periksa tata bahasa dan logika kalimat demi kalimat
   ③ `mark_text_errors` langsung menandai (setelah pemeriksaan tidak perlu bertanya, langsung tandai; merah=salah ketik/biru=kalimat tidak jelas/oranye=masalah logika)
   ④ Tampilkan dialog dengan dua pilihan kepada pengguna: saya yang perbaiki / Anda perbaiki sendiri
   ⑤ Pilih "saya yang perbaiki" → `fix_text_errors` mengganti kesalahan → lalu tanyakan lewat dialog apakah warna asli dikembalikan
   ⑥ Pilih "Anda perbaiki sendiri" → setelah pengguna selesai mengubah → `restore_marked_colors` mengembalikan ke hitam
3. **Menentukan posisi kesalahan**: cari posisi kesalahan langsung di string text yang dikembalikan `extract_selected_text`, jangan menulis ulang teks secara manual (perbedaan karakter baris baru dan spasi akan menggeser indeks sehingga salah posisi)

## Referensi sesuai kebutuhan (skenario mana baca file mana)

| Skenario | File yang dibaca |
|---|---|
| Ganti teks/warna, alur operasi standar, tabel operasi apply_operations, menentukan elemen | `references/basic-editing.md` |
| Menggambar kurva bebas/kontur tak beraturan, isi gradien | `references/draw-shapes.md` |
| Impor bitmap/SVG, ganti gambar, gambar sangat besar/tengah di halaman kosong | `references/images.md` |
| Gandakan papan nomor/grup secara massal, susun grid | `references/duplicate.md` |
| Cari gambar massal dan tempatkan ke frame | `references/batch-search.md` |
| Menggambar bagan organisasi | `references/org-chart.md` |
| Papan data/papan aturan massal (parse + tata letak) | `references/batch-system-board.md` |
| Trace / bitmap ke vektor | `references/trace-bitmap.md` |

## 🔴 Mengembangkan fitur baru: wajib lewat branch fitur (saat mengubah kode konektor)

Saat mengembangkan/memperluas MCP (bukan memakai CDR sehari-hari, melainkan mengubah kode), dilarang langsung mengubah main (cabang utama yang stabil dan siap pakai):

1. Di root repositori jalankan `.\scripts\new-feature.ps1 start <nama-fitur>`, otomatis membuat `feature/nama-fitur` (branch fitur, cabang pengembangan sementara) dari main dan berpindah ke sana.
2. Kembangkan di branch tersebut, uji nyata di CDR (MCP membaca file di disk saat ini).
3. Setelah berjalan dan dikonfirmasi pengguna, jalankan `.\scripts\new-feature.ps1 finish -Tag <nomor-versi>`, otomatis merge (menggabungkan perubahan branch ke main), memberi tag (label versi), dan menghapus branch.
4. Jika dibatalkan, gunakan `.\scripts\new-feature.ps1 discard`; untuk cek status gunakan `.\scripts\new-feature.ps1 status`.

Pengguna sering memverifikasi fitur di percakapan baru, lalu kembali ke percakapan utama untuk menggabungkan sekaligus; di percakapan mana pun, pengembangan fitur baru selalu `start` branch terlebih dahulu.
