# 🤖 AI-Assisted News Scraper API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-2EAD33.svg?style=flat&logo=microsoft&logoColor=white)](https://playwright.dev)
# 🤖 AI-Assisted News Scraper API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-2EAD33.svg?style=flat&logo=microsoft&logoColor=white)](https://playwright.dev)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-FF6B6B.svg?style=flat)](https://openai.com)

> **Platform scraping berbasis AI yang menggunakan OpenAI API untuk generate template CSS selector secara otomatis**

## 🎯 Tujuan

Membangun platform **Scraping Portal Berita Online** yang:

* ✅ Mempermudah user membuat **template scraping** menggunakan **contoh halaman + JSON schema**
* ✅ Menggunakan **OpenAI API** untuk generate **selector mapping** secara otomatis
* ✅ Mendukung konten **teks + gambar inline** (HTML/Markdown/PlainText)
* ✅ Bisa dipakai ulang untuk scraping artikel lain di **domain yang sama**
* ✅ Tersedia sebagai **REST API (FastAPI)** sehingga mudah diintegrasikan

---

## 🏗️ Arsitektur Sistem

```mermaid
flowchart TD
    A[User Input: URL + JSON Schema] --> B[Scraper ambil DOM]
    B --> C[OpenAI API Generator]
    C --> D[Template Mapping CSS/XPath]
    D --> E[SQLite Template Store]

    F[Scraper Runner] -->|Gunakan Template| G[Parse Artikel Lain]
    G --> H[Output JSON text + images inline]
    H --> I[API Response / Export]
```

---

## 📂 Struktur Proyek

```
scrapers-kemenbud/
│── app/
│   ├── main.py              # 🚀 Entry point FastAPI
│   ├── routers/
│   │   ├── training.py      # 📚 Endpoint training template
│   │   └── scraping.py      # 🔍 Endpoint scraping artikel
│   ├── services/
│   │   ├── scraper.py       # 🕷️ Engine scraping (Playwright/BS4)
│   │   ├── llm_agent.py     # 🤖 Integrasi OpenAI API
│   │   └── template.py      # 📋 Logic template generator
│   ├── models/
│   │   └── schema.py        # 📊 Pydantic schemas
│   ├── db.py                # 🗄️ SQLite database
│   └── utils.py             # 🛠️ Helper functions
│── tests/
│   ├── test_scraper.py      # 🧪 Test scraper engine
│   └── test_api.py          # 🧪 Test API endpoints
│── data/                    # 📁 SQLite database files
│── requirements.txt         # 📦 Dependencies
│── Dockerfile              # 🐳 Container image
│── docker-compose.yml      # 🐳 Service setup
│── .env.template           # ⚙️ Environment config
└── README.md               # 📖 Documentation
```

---

## 🚀 Quick Start

### 1️⃣ Setup dengan Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd scrapers-kemenbud

# Setup environment
cp .env.template .env
# Edit .env dan masukkan OpenAI API key

# Jalankan service
docker-compose up -d

# Check status
curl http://localhost:8000/health
```

### 2️⃣ Setup Manual

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Setup environment
cp .env.template .env
# Edit dan masukkan OPENAI_API_KEY

# Run API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Akses API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 Penggunaan API

### 🎓 Training Template

**Endpoint**: `POST /train`

```bash
curl -X POST "http://localhost:8000/train" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://example.com/article/123",
  "expected_schema": {
    "title": "string",
    "date": "string", 
    "author": "string",
    "content": "string"
  }
}'
```

**Response**:
```json
{
  "domain": "example.com",
  "template": {
    "selectors": {
      "title": "h1.article-title",
      "date": "time.publish-date",
      "author": ".author-name", 
      "content": "div.article-body p, div.article-body img"
    },
    "confidence_score": 0.85,
    "created_at": "2025-09-22T10:00:00Z"
  },
  "success": true,
  "message": "Template created successfully"
}
```

### 🔍 Scraping Artikel

**Endpoint**: `POST /scrape`

```bash
curl -X POST "http://localhost:8000/scrape" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://example.com/article/456",
  "output_format": "html"
}'
```

**Response**:
```json
{
  "url": "https://example.com/article/456",
  "domain": "example.com", 
  "template_used": "template_abc123",
  "scraped_at": "2025-09-22T10:00:00Z",
  "data": {
    "title": "New Cultural Event in Jakarta...",
    "date": "2025-09-20T10:00:00Z",
    "author": "Reporter Name",
    "content": "<p>Jakarta held a cultural event...</p><p><img src='https://example.com/img1.jpg'></p><p>It was attended by...</p>"
  },
  "success": true
}
```

### 📦 Batch Scraping

**Endpoint**: `POST /scrape/batch`

```bash
curl -X POST "http://localhost:8000/scrape/batch" \
-H "Content-Type: application/json" \
-d '{
  "urls": [
    "https://example.com/article/1",
    "https://example.com/article/2", 
    "https://example.com/article/3"
  ],
  "output_format": "markdown",
  "max_concurrent": 3
}'
```

### 🔍 Preview Scraping

**Endpoint**: `GET /scrape/preview`

```bash
curl "http://localhost:8000/scrape/preview?url=https://example.com/article&show_selectors=true"
```

---

## ⚙️ Konfigurasi

### Environment Variables

```bash
# Database
DATABASE_PATH=./data/scraper.db

# OpenAI Configuration  
OPENAI_API_KEY=your_openai_api_key_here

# Application
ENVIRONMENT=development
DEBUG=true
PLAYWRIGHT_ENABLED=true
MAX_CONCURRENT_SCRAPES=10
```

### Supported Output Formats

- **html**: Output dengan HTML tags (default)
- **markdown**: Konversi ke Markdown format
- **plaintext**: Plain text tanpa formatting

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run unit tests
pytest tests/ -v

# Run dengan coverage
pytest tests/ --cov=app --cov-report=html

# Run integration tests (requires OpenAI API key)
pytest tests/ -m integration
```

---

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t scraper-api .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_api_key \
  -v $(pwd)/data:/app/data \
  scraper-api
```

### Docker Compose

```bash
# Development
docker-compose up -d

# View logs
docker-compose logs -f scraper-api

# Scale API instances
docker-compose up -d --scale scraper-api=3
```

---

## 📊 Monitoring & Health

### Health Endpoints

- **Main Health**: `GET /health`
- **Training Service**: `GET /train/health` 
- **Scraping Service**: `GET /scrape/health`
- **API Status**: `GET /status`

### Metrics

```bash
# Check template statistics
curl http://localhost:8000/scrape/domain/example.com

# View API info
curl http://localhost:8000/info

# List templates (coming soon)
curl http://localhost:8000/templates
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Clone & setup
git clone <repo>
cd scrapers-kemenbud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Pre-commit hooks
pip install pre-commit
pre-commit install

# Run in development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code  
flake8 app/ tests/
mypy app/

# Security check
bandit -r app/
```

---

## 🛠️ Teknologi Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **API Framework** | FastAPI | 0.104.1 |
| **Web Scraping** | Playwright + BeautifulSoup4 | 1.40.0 + 4.12.2 |
| **AI Service** | OpenAI API | Latest |
| **Database** | SQLite + aiosqlite | Latest |
| **HTTP Client** | aiohttp | 3.9.1 |
| **Containerization** | Docker + Docker Compose | Latest |
| **Testing** | pytest + httpx | 7.4.3 + 0.25.2 |

---

## 🚀 Roadmap

### ✅ Completed Features

- [x] AI-powered CSS selector generation with OpenAI
- [x] Multi-format output (HTML/Markdown/PlainText)
- [x] SQLite-based template storage & reuse
- [x] Batch scraping capability
- [x] Docker containerization
- [x] Comprehensive API documentation

### 🔄 In Progress

- [ ] Advanced template optimization
- [ ] Performance monitoring dashboard
- [ ] Rate limiting & authentication

### 📋 Planned Features

- [ ] **Export**: CSV/JSON/Excel export functionality
- [ ] **Scheduler**: Automated scraping (hourly/daily)
- [ ] **Web UI**: Management dashboard
- [ ] **Analytics**: Success rate tracking & reporting
- [ ] **VectorDB**: Integration with Qdrant/Chroma for search
- [ ] **Sentiment Analysis**: Content analysis features
- [ ] **Multi-language**: Support for various languages

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Pastikan direktori data exists
mkdir -p data
chmod 755 data
```

**OpenAI API Error:**
```bash
# Pastikan API key valid di .env
export OPENAI_API_KEY=your_key_here
```

**Playwright Browser Error:**
```bash
# Install ulang browsers
playwright install chromium --with-deps
```

### Debug Mode

```bash
# Run dengan debug logging
DEBUG=true uvicorn app.main:app --reload --log-level debug
```

### Performance Tuning

* Gunakan Playwright untuk JavaScript-heavy sites
* Gunakan BeautifulSoup untuk static sites (lebih cepat)
* Set timeout yang reasonable di scraper config
* Monitor database size dan optimize queries

---

## 💬 Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Playwright Documentation](https://playwright.dev)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Built with ❤️ for efficient web scraping**

## 🎯 Tujuan

Membangun platform **Scraping Portal Berita Online** yang:

* ✅ Mempermudah user membuat **template scraping** menggunakan **contoh halaman + JSON schema**
* ✅ Menggunakan **Local LLM (Ollama)** untuk generate **selector mapping** secara otomatis
* ✅ Mendukung konten **teks + gambar inline** (HTML/Markdown/PlainText)
* ✅ Bisa dipakai ulang untuk scraping artikel lain di **domain yang sama**
* ✅ Tersedia sebagai **REST API (FastAPI)** sehingga mudah diintegrasikan

---

## 🏗️ Arsitektur Sistem

```mermaid
flowchart TD
    A[User Input: URL + JSON Schema] --> B[Scraper ambil DOM]
    B --> C[LLM Generator]
    C --> D[Template Mapping CSS/XPath]
    D --> E[Template Store DB]

    F[Scraper Runner] -->|Gunakan Template| G[Parse Artikel Lain]
    G --> H[Output JSON text + images inline]
    H --> I[API Response / Export]
```

---

## 📂 Struktur Proyek

```
scrapers-kemenbud/
│── app/
│   ├── main.py              # 🚀 Entry point FastAPI
│   ├── routers/
│   │   ├── training.py      # 📚 Endpoint training template
│   │   └── scraping.py      # 🔍 Endpoint scraping artikel
│   ├── services/
│   │   ├── scraper.py       # 🕷️ Engine scraping (Playwright/BS4)
│   │   ├── llm_agent.py     # 🤖 Integrasi local LLM (Ollama)
│   │   └── template.py      # 📋 Logic template generator
│   ├── models/
│   │   └── schema.py        # 📊 Pydantic schemas
│   ├── db.py                # 🗄️ Koneksi DB (Postgres/Mongo)
│   └── utils.py             # 🛠️ Helper functions
│── tests/
│   ├── test_scraper.py      # 🧪 Test scraper engine
│   └── test_api.py          # 🧪 Test API endpoints
│── requirements.txt         # 📦 Dependencies
│── Dockerfile              # 🐳 Container image
│── docker-compose.yml      # 🐳 Multi-service setup
│── .env.template           # ⚙️ Environment config
└── README.md               # 📖 Documentation
```

---

## 🚀 Quick Start

### 1️⃣ Setup dengan Docker (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd scrapers-kemenbud

# Setup environment
cp .env.template .env
# Edit .env sesuai kebutuhan

# Jalankan semua services
docker-compose up -d

# Check status
curl http://localhost:8000/health
```

### 2️⃣ Setup Manual

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Setup Ollama (Local LLM)
# Install Ollama dari https://ollama.ai
ollama serve
ollama pull llama3.2

# Setup Database (PostgreSQL)
createdb scraper_db

# Setup environment
cp .env.template .env
# Edit database dan LLM configuration

# Run API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3️⃣ Akses API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📖 Penggunaan API

### 🎓 Training Template

**Endpoint**: `POST /train`

```bash
curl -X POST "http://localhost:8000/train" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://example.com/article/123",
  "expected_schema": {
    "title": "string",
    "date": "string", 
    "author": "string",
    "content": "string"
  }
}'
```

**Response**:
```json
{
  "domain": "example.com",
  "template": {
    "selectors": {
      "title": "h1.article-title",
      "date": "time.publish-date",
      "author": ".author-name", 
      "content": "div.article-body p, div.article-body img"
    },
    "confidence_score": 0.85,
    "created_at": "2025-09-22T10:00:00Z"
  },
  "success": true,
  "message": "Template created successfully"
}
```

### 🔍 Scraping Artikel

**Endpoint**: `POST /scrape`

```bash
curl -X POST "http://localhost:8000/scrape" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://example.com/article/456",
  "output_format": "html"
}'
```

**Response**:
```json
{
  "url": "https://example.com/article/456",
  "domain": "example.com", 
  "template_used": "template_abc123",
  "scraped_at": "2025-09-22T10:00:00Z",
  "data": {
    "title": "New Cultural Event in Jakarta...",
    "date": "2025-09-20T10:00:00Z",
    "author": "Reporter Name",
    "content": "<p>Jakarta held a cultural event...</p><p><img src='https://example.com/img1.jpg'></p><p>It was attended by...</p>"
  },
  "success": true
}
```

### 📦 Batch Scraping

**Endpoint**: `POST /scrape/batch`

```bash
curl -X POST "http://localhost:8000/scrape/batch" \
-H "Content-Type: application/json" \
-d '{
  "urls": [
    "https://example.com/article/1",
    "https://example.com/article/2", 
    "https://example.com/article/3"
  ],
  "output_format": "markdown",
  "max_concurrent": 3
}'
```

### 🔍 Preview Scraping

**Endpoint**: `GET /scrape/preview`

```bash
curl "http://localhost:8000/scrape/preview?url=https://example.com/article&show_selectors=true"
```

---

## ⚙️ Konfigurasi

### Environment Variables

```bash
# Database
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:password@localhost:5432/scraper_db

# LLM Configuration  
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_TIMEOUT=60

# Application
ENVIRONMENT=development
DEBUG=true
PLAYWRIGHT_ENABLED=true
MAX_CONCURRENT_SCRAPES=10
```

### Supported Output Formats

- **html**: Output dengan HTML tags (default)
- **markdown**: Konversi ke Markdown format
- **plaintext**: Plain text tanpa formatting

### Supported LLM Models

- `llama3.2` (recommended)
- `llama3`
- `mistral`
- `phi3-mini`
- `codellama`

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run unit tests
pytest tests/ -v

# Run dengan coverage
pytest tests/ --cov=app --cov-report=html

# Run integration tests (requires services)
pytest tests/ -m integration
```

---

## 🐳 Docker Deployment

### Single Container

```bash
# Build image
docker build -t scraper-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e OLLAMA_HOST=http://ollama-host:11434 \
  scraper-api
```

### Multi-Service dengan Docker Compose

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f scraper-api

# Scale API instances
docker-compose up -d --scale scraper-api=3
```

---

## 📊 Monitoring & Health

### Health Endpoints

- **Main Health**: `GET /health`
- **Training Service**: `GET /train/health` 
- **Scraping Service**: `GET /scrape/health`
- **API Status**: `GET /status`

### Metrics

```bash
# Check template statistics
curl http://localhost:8000/scrape/domain/example.com

# View API info
curl http://localhost:8000/info

# List templates (coming soon)
curl http://localhost:8000/templates
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Clone & setup
git clone <repo>
cd scrapers-kemenbud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Pre-commit hooks
pip install pre-commit
pre-commit install

# Run in development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality

```bash
# Format code
black app/ tests/
isort app/ tests/

# Lint code  
flake8 app/ tests/
mypy app/

# Security check
bandit -r app/
```

---

## 🛠️ Teknologi Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **API Framework** | FastAPI | 0.104.1 |
| **Web Scraping** | Playwright + BeautifulSoup4 | 1.40.0 + 4.12.2 |
| **Local LLM** | Ollama | Latest |
| **Database** | PostgreSQL / MongoDB | 15 / 7 |
| **HTTP Client** | aiohttp | 3.9.1 |
| **Containerization** | Docker + Docker Compose | Latest |
| **Testing** | pytest + httpx | 7.4.3 + 0.25.2 |

---

## 🚀 Roadmap

### ✅ Completed Features

- [x] AI-powered CSS selector generation
- [x] Multi-format output (HTML/Markdown/PlainText)
- [x] Template storage & reuse
- [x] Batch scraping capability
- [x] Docker containerization
- [x] Comprehensive API documentation

### 🔄 In Progress

- [ ] Advanced template optimization
- [ ] Performance monitoring dashboard
- [ ] Rate limiting & authentication

### 📋 Planned Features

- [ ] **Export**: CSV/JSON/Excel export functionality
- [ ] **Scheduler**: Automated scraping (hourly/daily)
- [ ] **Web UI**: Management dashboard
- [ ] **Analytics**: Success rate tracking & reporting
- [ ] **VectorDB**: Integration with Qdrant/Chroma for search
- [ ] **Sentiment Analysis**: Content analysis features
- [ ] **Multi-language**: Support for various languages

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Documentation**: `/docs` endpoint
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Playwright Documentation](https://playwright.dev)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

---

**Built with ❤️ for efficient web scraping**