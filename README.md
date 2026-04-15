## 🌪️ PROXY STORM V1
**High-Performance Proxy Scraper & Asynchronous Validator**

PROXY_STORM adalah alat baris perintah (CLI) profesional yang dirancang untuk mengumpulkan dan memvalidasi ribuan proxy publik dalam hitungan detik. Menggunakan engine **Asynchronous I/O** untuk kecepatan maksimal.

## 🚀 Fitur Unggulan
- **Extreme Speed:** Validasi hingga 250+ proxy secara simultan.
- **Auto-Cleaning:** Menghapus duplikat dan format yang rusak secara otomatis.
- **Latency Ranking:** Hasil disimpan berdasarkan urutan proxy tercepat.
- **Beautiful Interface:** Tampilan terminal modern dengan tabel dan progress bar.
- **Cross-Platform:** Berjalan lancar di Termux, Linux, Windows (CMD/Powershell), dan MacOS.

## 🛠️ Instalasi

### 1. Termux (Android)
```bash
pkg update && pkg upgrade
pkg install python
pip install aiohttp rich
