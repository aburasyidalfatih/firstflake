# First Flake — landing page, PayPal checkout, protected download, admin dashboard

Satu container Node 24 (Alpine, ±60 MB), tanpa framework frontend. Database SQLite bawaan Node (tidak ada native module), Hono untuk HTTP, Nodemailer untuk SMTP Mailketing.

```
public/      index.html · checkout.html · download.html · style.css   (halaman pembeli, total < 15 KB)
private/     admin.html · first-flake-workbook.pdf                      (tidak bisa diakses langsung lewat URL)
src/         server.js · db.js · crypto.js · paypal.js · mail.js        (±350 baris total)
data/        app.db  (dibuat otomatis, simpan di volume)
Dockerfile · docker-compose.yml · .env.example
```

## Alur pembelian
1. `checkout.html` mengambil Client ID, harga, dan mata uang dari `/api/config` (jadi ganti kredensial di dashboard langsung berlaku, tanpa deploy ulang).
2. Setelah pembeli approve di PayPal, browser kirim `orderID` ke `/api/capture`.
3. Server capture order lewat PayPal API, cek status COMPLETED dan nominal sesuai harga, simpan ke tabel `orders`, kirim email berisi link download via SMTP Mailketing, dan kembalikan token download (berlaku 7 hari).
4. `/api/download?t=TOKEN` memverifikasi tanda tangan HMAC, memastikan order masih berstatus `paid` (order yang di-refund otomatis ditolak), lalu mengalirkan PDF.

## Admin: `https://firstflake.com/admin`
- **Orders:** omset hari ini / bulan ini / total, grafik 30 hari, tabel order dengan pencarian, kirim ulang email, salin link download baru, tandai refunded/paid.
- **Settings:** nama produk, harga, mata uang, site URL, email support, kredensial PayPal (sandbox/live), kredensial SMTP Mailketing, tombol tes koneksi PayPal dan SMTP.
- Secret PayPal dan password SMTP dienkripsi AES-256-GCM di database dengan kunci dari `APP_SECRET`.
- Login dibatasi 5 percobaan per 15 menit per IP. Session cookie HttpOnly 12 jam.

## Deploy di Dokploy
1. Push folder ini ke repo Git (GitHub/GitLab), atau upload sebagai zip.
2. Dokploy → Create Application → pilih **Docker Compose** (atau Application dengan Dockerfile, keduanya ada di repo).
3. Tab **Environment**, isi:
   ```
   APP_SECRET=<hasil openssl rand -hex 32>
   ADMIN_PASSWORD=<password admin yang kuat>
   ```
4. Tab **Domains**: tambahkan domain, port 3000, aktifkan HTTPS (Let's Encrypt). Dokploy/Traefik akan meneruskan header `x-forwarded-for` yang dipakai untuk rate limit login.
5. Deploy. Volume `firstflake-data` otomatis dibuat agar database tidak hilang saat redeploy.
6. Buka `/admin`, isi Settings:
   - **PayPal:** developer.paypal.com → Apps & Credentials → Live → Client ID + Secret. Mulai dengan Sandbox dulu untuk tes, lalu ganti ke Live.
   - **Mailketing SMTP:** host, port, username, password dari dashboard Mailketing, dan alamat pengirim yang sudah diverifikasi di Mailketing.
   - **Site URL:** `https://firstflake.com` (sudah default).
   - Klik "Test PayPal connection" dan "Test SMTP connection" untuk memastikan.

## Jalankan lokal
```bash
npm install
APP_SECRET=isi-acak-min-16-karakter ADMIN_PASSWORD=admin123 node --experimental-sqlite src/server.js
```
Node 24 tidak butuh flag `--experimental-sqlite`; Node 22 butuh.

## Mengganti produk
Timpa `private/first-flake-workbook.pdf` dengan file baru lalu redeploy, atau mount file ke path lain dan set env `PDF_PATH`. Nama produk dan harga diubah dari dashboard.

## Backup
Cukup salin `data/app.db` (atau volume `firstflake-data`). Secret di dalamnya hanya bisa dibaca dengan `APP_SECRET` yang sama, jadi simpan nilai itu juga.

## Bonus PDF
Sumber bonus ada di folder `bonus/` (HTML + CSS). PDF hasilnya disimpan di `private/` dan ikut ke Docker image.
- Bonus 1 dibuat dari `bonus/research-west.md` dan `bonus/research-east.md` lewat `python bonus/make_bonus1.py`.
- Render ulang semua PDF dengan `bash bonus/build.sh` (butuh Google Chrome terpasang).
- Halaman download memakai parameter `f` (workbook, bonus1 sampai bonus4). Daftar file ada di `FILES` dalam `src/server.js`.
