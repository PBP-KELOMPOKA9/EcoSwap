pypp# EcoSwap

## Deskripsi Aplikasi

EcoSwap adalah platform yang menghubungkan orang-orang di sekitar area kampus dan kos untuk **mendonasikan** atau **menjual murah** barang-barang bekas yang masih layak pakai, seperti buku, rak, baju, dan peralatan sehari-hari. Aplikasi ini lahir dari masalah sederhana yang sering terjadi, barang bekas kos sering berakhir jadi sampah begitu saja saat pemiliknya pindahan atau lulus, padahal masih bisa dipakai orang lain.

Lewat EcoSwap, siapa pun (tidak terbatas mahasiswa) bisa memposting barang yang sudah tidak terpakai untuk didonasikan atau dijual dengan harga terjangkau, dan pengguna lain bisa mengajukan minat untuk mengambilnya. Pengambilan barang bisa dilakukan lewat titik ketemuan langsung di sekitar kampus, atau dikirim lewat jasa kurir seperti JNE bagi yang membutuhkan. Dengan begitu, barang yang masih layak pakai tetap bermanfaat, mengurangi sampah, dan membantu orang lain mendapatkan barang dengan harga lebih ringan.

## Anggota Kelompok
1. Juan Imanuel Limpong - 2506619455
2. Nayla Putri Novita - 2506657182
3. Najwa Salsabil - 2506588701
4. Mirza Al Fathi - 2506618572
5. Cheryl Mahira Indarto - 2506606093

## Daftar Modul dan Pembagian Kerja

### 1. Manajemen Barang & Wishlist/Favorit — [Najwa Salsabil]
CRUD untuk postingan barang: tambah, lihat, edit, dan hapus barang yang akan didonasikan atau dijual murah, lengkap dengan filter kategori, tipe transaksi, dan pencarian barang. Termasuk CRUD wishlist/favorit, tempat pengguna menyimpan dan menghapus barang yang ingin dipantau.

### 2. Profil, Transaksi & History — [Nayla Putri Novita]
CRUD untuk profil pengguna (registrasi, login, data kontak, domisili, foto profil) dan CRUD untuk pengajuan minat/transaksi (ajukan minat, terima/tolak pengajuan, lihat status, batalkan pengajuan). Halaman history menampilkan transaksi yang sudah berstatus selesai.

### 3. Lokasi & Metode Pengambilan — [Mirza Al Fathi]
CRUD untuk opsi pengambilan barang: memilih ketemuan langsung dengan titik lokasi tertentu di peta, atau opsi dikirim lewat kurir (JNE/JNT). Titik lokasi ditampilkan lewat integrasi peta interaktif.

### 4. Ulasan & Rating — [Cheryl Mahira Indarto]
CRUD untuk ulasan setelah transaksi selesai: memberi ulasan dan rating, melihat ulasan pada profil pengguna, mengedit, dan menghapus ulasan.

### 5. Chat & Notifikasi — [Juan Imanuel Limpong]
CRUD untuk chat antara dua pengguna terkait suatu barang/transaksi: mengirim, melihat, dan menghapus pesan. Notifikasi muncul otomatis saat ada perubahan status transaksi atau pesan baru masuk.

## Public API

**Google Maps Platform** (Maps JavaScript API untuk menampilkan peta, dan Geocoding API untuk mengubah alamat menjadi koordinat).
Dokumentasi: https://developers.google.com/maps/documentation

## Peran Pengguna

- **Pemberi/penjual barang**: memposting barang untuk didonasikan atau dijual murah, mengatur opsi pengambilan, menerima atau menolak pengajuan minat
- **Pencari barang**: menelusuri barang yang tersedia, menyimpan barang ke wishlist, mengajukan minat, mengatur pertemuan atau pengiriman, memberi ulasan setelah transaksi


Tautan deployment PWS: https://cheryl-mahira-ecoswap.pws.cs.ui.ac.id/

Tautan desain Figma (wajib): https://www.figma.com/design/InO9fkN6OAPY8TbBGRyeWs/HTML?node-id=196-367&t=0FM2EbXJlOhqdGl1-1