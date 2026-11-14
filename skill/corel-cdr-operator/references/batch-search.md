# Cari gambar massal → tempatkan ke frame terpilih dengan PowerClip (sering dipakai toko iklan)

`batch_search_and_place`: **satu panggilan tool menyelesaikan semuanya** — otomatis membaca frame yang dipilih, mengurutkan menurut urutan baca (atas ke bawah, dalam baris kiri ke kanan), mencari gambar di situs materi, mengunduh, dan PowerClip ke dalam frame; **default mengisi proporsional (fill), gambar tetap utuh dan bisa diatur manual dari dalam kontainer**.

🔴 **Wajib memakai satu panggilan `batch_search_and_place`, dilarang mencari gambar manual lewat browser, dilarang memecah manual menjadi get_selection + batch_search_images + batch_place_images** (pemecahan manual membuat gambar salah tempat karena urutan hasil paralel berbeda).

## Alur

**Langkah 1: Minta pengguna memilih dulu frame/bentuk tujuan gambar di CDR** (boleh multi-pilih atau pilih kotak).
- Tidak perlu memanggil get_selection sendiri: jika `batch_search_and_place` dipanggil tanpa container_ids, ia otomatis membaca frame terpilih dan mengurutkannya menurut urutan baca.
- Jika pengguna belum memilih, tool mengembalikan petunjuk agar pengguna memilih lalu mencoba lagi.

**Langkah 2: Tentukan kata kunci (dua cara pemberian)**
- **Diberikan berurutan**: pengguna mengirim "apel" "pisang" "jeruk"..., jumlahnya harus sama dengan jumlah frame; **jika tidak cocok wajib minta dilengkapi atau disesuaikan**, jangan dipaksakan.
- **Membaca label di samping frame**: jika ada label teks di dekat frame, baca teksnya dengan `inspect_document`, cocokkan menurut **jarak terdekat** antara teks dan tiap frame.
- Jika beberapa frame memakai kata kunci yang sama, cukup beri 1 (tool otomatis menerapkannya ke semua frame).

**Langkah 3: Langsung panggil `batch_search_and_place` sekali jalan**
- Parameter: `keywords` (berurutan sesuai urutan baca); `fit_mode` default `"fill"`, pilihan:
  - `fill`: isi frame secara proporsional tanpa distorsi, bagian lebih dipotong, **gambar utuh dan bisa diedit di PowerClip** (default)
  - `fit`: tampilkan seluruh gambar secara proporsional, mungkin ada ruang kosong
  - `stretch`: regangkan hingga penuh, mungkin terdistorsi
  - `center`: ukuran asli di tengah
- Tool otomatis melakukan secara internal: meminta kandidat dari antarmuka materi → 🔴 penyaringan kualitas (kecualikan gambar kecil sisi terpanjang <1000px, situs penuh watermark, animasi, gambar buram/terdistorsi/tidak relevan) → host cepat diprioritaskan, unduh paralel, pembatalan dini → downsample otomatis (sisi terpanjang 2000px) → impor, PowerClip, skala dan tengahkan, tanpa crash.
- Pemilihan sumber dan jenis gambar ditentukan otomatis oleh tool, **tidak menampilkan dialog ke pengguna, tidak menampilkan URL**.

**Langkah 4: Setelah berhasil ditempatkan, jangan render pratinjau, langsung ingatkan untuk cek di CDR**
- Jangan panggil `render_preview`, cukup beri tahu "sudah ditempatkan, silakan cek di CDR".
- Jika ada kata kunci yang tidak menemukan gambar memenuhi syarat, tool mengembalikan kata kunci yang gagal; minta pengguna mengganti kata atau menurunkan ketajaman lalu coba lagi (gambar yang sudah berhasil dipertahankan).
- Jika pengguna berkata "ganti yang ke-X", panggil `batch_search_and_place` hanya untuk frame itu (dengan container_id frame tersebut + kata kunci baru), sisanya tidak diubah.

**Perhatian:** jangan memotong gambar sendiri dengan PIL sebelum ditempatkan (hilang permanen, pengguna tak bisa menyesuaikan); pada mode fill gambarnya utuh, hanya tampilannya dipotong oleh PowerClip.

**Tool terkait**: `batch_search_images` (hanya cari dan unduh, tidak ditempatkan, untuk jika pengguna hanya butuh materi gambar); `batch_search_and_place` (cari + tempatkan, default untuk skenario ini).
