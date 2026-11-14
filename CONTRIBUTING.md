# Berkontribusi pada CorelDRAW Signage MCP

## Batasan platform

Fitur inti proyek ini bergantung pada **Windows + COM API CorelDRAW**; persyaratan lingkungan pengembangan:

- Windows 10/11
- CorelDRAW X6 atau lebih baru (harus sudah terpasang dan diaktifkan)
- Python 3.11+, **harus 64-bit** (bitness sama dengan CorelDRAW)

Di lingkungan non-Windows hanya bisa dilakukan pemeriksaan sintaks (`ruff check`), uji end-to-end tidak dapat dijalankan.

---

## Memulai dengan cepat

```bash
git clone https://github.com/<fork-anda>/coreldraw-signage-mcp
cd coreldraw-signage-mcp

python -m venv .venv
.venv\Scripts\activate

pip install -e ".[dev]"

cp .env.example .env
# Isi setidaknya satu LLM API Key
```

---

## Aturan commit

Gunakan [Conventional Commits](https://www.conventionalcommits.org/id/):

| Prefiks | Kegunaan |
|------|------|
| `feat:` | Tool atau fitur baru |
| `fix:` | Perbaikan bug |
| `docs:` | Perubahan dokumentasi |
| `refactor:` | Refactor kode yang tidak memengaruhi fitur |
| `chore:` | Perubahan build/toolchain |

## Aturan kode

Jalankan lint sebelum commit:

```bash
ruff check server/
```

Konfigurasi ada di `pyproject.toml`: `line-length=120`, `target-version=py311`, `select=E,F,I,N,W`.

---

## Menambah tool MCP

Tool baru wajib menyelesaikan ketiga hal berikut sekaligus, tidak boleh kurang satu pun:

1. **Implementasi fungsi**: letakkan di modul yang sesuai di `server/tools/`, mengembalikan `ToolResult`, lihat pola terpadu di [CLAUDE.md](CLAUDE.md)
2. **Daftarkan tool**: panggil `mcp.add_tool()` di `register_tools()` pada `server/server.py`
3. **Tulis docstring**: docstring fungsi langsung diperlihatkan kepada Agent, jelaskan arti parameter dengan jelas

Konstanta COM memakai bilangan bulat yang ditulis langsung (`cdrPNG=776`, dll.), tidak diimpor dari `win32com.client.constants`.

---

## Alur Pull Request

1. Fork → buat branch baru (`feat/fitur-anda` atau `fix/bug-anda`)
2. Implementasi + `ruff check` lolos
3. Di deskripsi PR jelaskan: tool mana yang diubah, diuji di CorelDRAW versi berapa
4. Jika tidak bisa diuji lokal (non-Windows), catat di PR

---

## Umpan balik masalah

- Laporan bug: gunakan GitHub Issues, sertakan versi CorelDRAW, versi Python, dan log error
- Usulan fitur: buka Issue untuk diskusi terlebih dahulu, hindari pekerjaan ganda
