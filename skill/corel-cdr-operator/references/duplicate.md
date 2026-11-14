# Gandakan massal / gandakan papan nomor (sering dipakai toko iklan)

`duplicate_shapes`: menggandakan satu **grup (gambar dasar + templat teks)** sebanyak N, disusun rapi dalam grid, dan bisa mengubah teks berbeda satu per satu. Memakai `Shape.Duplicate` CorelDRAW, gambar dasar, gaya, dan struktur sepenuhnya sama, **tidak mengimpor ulang gambar dasar**.

## Parameter

- `shape_id`: ID bentuk/grup templat (dapatkan dulu dengan `inspect_document`, atau yang dipilih pengguna).
- `count`: jumlah total akhir (termasuk yang asli). Mis. 10 = total 10, otomatis membuat 9 salinan.
- `per_row`: berapa per baris, otomatis pindah baris jika penuh; default 0 semua dalam satu baris.
- `gap`: jarak antar salinan dalam mm, default 10.
- `texts`: opsional, daftar teks (panjang = count), mengubah teks utama tiap target satu per satu (nama kelas/nomor/nama orang).
- `target_text`: teks asli di templat yang akan diganti (untuk penentuan posisi); jika tidak diisi dicari otomatis (satu-satunya teks dalam grup, atau judul utama dengan font terbesar).

## Cara pakai

- Contoh umum: "gandakan templat ini 10, 5 per baris, teks dari Kelas 1A sampai Kelas 1J", selesai dalam satu panggilan.
- Mendukung pencarian teks secara rekursif dalam grup bersarang; tidak mengubah gambar dasar, tidak menghapus elemen lain, tidak menyimpan otomatis.
