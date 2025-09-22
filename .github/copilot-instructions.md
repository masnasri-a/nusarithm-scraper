**dokumen Markdown** berisi instruksi pembuatan **platform scraping berbasis API (FastAPI)** dengan konsep **AI template-driven scraper** yang maintainable.

---

# 📰 AI-Assisted News Scraper API (FastAPI)

## 🎯 Tujuan

Membangun platform **Scraping Portal Berita Online** yang:

* Mempermudah user membuat **template scraping** menggunakan **contoh halaman + JSON schema**.
* Menggunakan **Local LLM** untuk generate **selector mapping**.
* Mendukung konten **teks + gambar inline** (HTML/Markdown).
* Bisa dipakai ulang untuk scraping artikel lain di **domain yang sama**.
* Tersedia sebagai **API (FastAPI)** sehingga mudah diintegrasikan.

---

## 🏗️ Arsitektur Sistem

```mermaid
flowchart TD
    A[User Input: URL + JSON Schema] --> B[Scraper ambil DOM]
    B --> C[LLM Generator]
    C --> D[Template Mapping (CSS/XPath)]
    D --> E[Template Store DB]

    F[Scraper Runner] -->|Gunakan Template| G[Parse Artikel Lain]
    G --> H[Output JSON (text + images inline)]
    H --> I[API Response / Export]
```

---

## 📂 Struktur Proyek

```
scraper-api/
│── app/
│   ├── main.py            # Entry point FastAPI
│   ├── routers/
│   │   ├── training.py    # Endpoint training template
│   │   ├── scraping.py    # Endpoint scraping artikel
│   ├── services/
│   │   ├── scraper.py     # Engine scraping (Playwright/BS4)
│   │   ├── llm_agent.py   # Integrasi local LLM (Ollama/LM Studio)
│   │   ├── template.py    # Logic template generator
│   ├── models/
│   │   ├── schema.py      # Pydantic schemas
│   ├── db.py              # Koneksi DB (Postgres/Mongo)
│   └── utils.py           # Helper functions
│── tests/
│   ├── test_scraper.py
│   ├── test_api.py
│── requirements.txt
│── README.md
```

---

## ⚙️ Endpoints (FastAPI)

### 1. Training Template

```http
POST /train
Content-Type: application/json

{
  "url": "https://example.com/article/123",
  "expected_schema": {
    "title": "string",
    "date": "string",
    "author": "string",
    "content": "string"
  }
}
```

**Response:**

```json
{
  "domain": "example.com",
  "template": {
    "title": "h1.article-title",
    "date": "span.pub-date",
    "author": ".author-name",
    "content": "div.article-body p, div.article-body img"
  }
}
```

---

### 2. Scrape Artikel dengan Template

```http
POST /scrape
Content-Type: application/json

{
  "url": "https://example.com/article/456"
}
```

**Response:**

```json
{
  "title": "New Cultural Event in Jakarta...",
  "date": "2025-09-20T10:00:00Z",
  "author": "Reporter",
  "content": "<p>Jakarta held a cultural event...</p><p><img src='https://example.com/img1.jpg'></p><p>It was attended by...</p>"
}
```

---

## 🔌 Teknologi Utama

* **FastAPI** → API framework.
* **Playwright / Requests + BeautifulSoup** → Scraper engine.
* **Ollama / Local LLM (Mistral, Llama3, Phi3-mini)** → Template generator.
* **Postgres/Mongo** → Template store.
* **Docker** → Containerized & portable.

---

## ✅ Prinsip Maintainability

* **Modular** → pisahkan `routers`, `services`, `models`.
* **Configurable** → gunakan `.env` untuk DB, LLM host, dsb.
* **Scalable** → support multi-domain dengan template per domain.
* **Testable** → unit test untuk scraper & API.
* **Extensible** → bisa tambah fitur sentiment analysis, keyword extraction, dsb.

---

## 🚀 Roadmap Fitur Tambahan

* [ ] Export hasil ke CSV/JSON/Excel.
* [ ] Scheduler (scraping otomatis setiap jam/hari).
* [ ] Dashboard web UI (filter berita, analitik).
* [ ] Multi-output mode (HTML/Markdown/Plaintext).
* [ ] Integrasi ke VectorDB (Qdrant/Chroma) untuk search/QA.

