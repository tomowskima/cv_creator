# CV Creator - Kreator CV z AI

Aplikacja do tworzenia profesjonalnych CV z wykorzystaniem AI (OpenAI) i RAG (Retrieval Augmented Generation).

## Funkcjonalności

- 📝 Formularz do wypełnienia danych CV
- 🤖 CV Coach - asystent AI pomagający w pisaniu CV
- 📄 Generowanie CV w dwóch wariantach (klasyczny/nowoczesny)
- 📑 Generowanie PDF
- 🧠 RAG - wykorzystanie bazy wiedzy z PDF-ów do lepszych sugestii

## Wymagania

- Python 3.11+
- OpenAI API Key

## Instalacja lokalna

```bash
# Klonuj repozytorium
git clone <repo-url>
cd cv_creator

# Utwórz wirtualne środowisko
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Ustaw klucz API
export OPENAI_API_KEY="twój-klucz"

# Uruchom ingestion bazy wiedzy (opcjonalnie)
python ingest_knowledge.py

# Uruchom serwer
uvicorn app.main:app --reload
```

Aplikacja będzie dostępna pod adresem: http://127.0.0.1:8000

## Wdrożenie na Render

1. Zarejestruj się na [Render.com](https://render.com)
2. Połącz repozytorium GitHub
3. Utwórz nowy Web Service
4. Wybierz repozytorium i branch
5. Ustaw:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Dodaj zmienną środowiskową `OPENAI_API_KEY`
7. Deploy!

## Wdrożenie na Railway

1. Zarejestruj się na [Railway.app](https://railway.app)
2. Kliknij "New Project" → "Deploy from GitHub repo"
3. Wybierz repozytorium
4. Railway automatycznie wykryje konfigurację z `railway.json`
5. Dodaj zmienną środowiskową `OPENAI_API_KEY` w Settings → Variables
6. Deploy!

## Struktura projektu

```
cv_creator/
├── app/
│   ├── main.py           # FastAPI aplikacja
│   ├── models.py         # Modele Pydantic
│   ├── config.py         # Konfiguracja
│   └── services/
│       ├── cv_engine.py      # Silnik CV
│       ├── llm_client.py     # Klient OpenAI
│       ├── rag_client.py     # RAG client
│       └── pdf_generator.py  # Generator PDF
├── templates/            # Szablony HTML
├── static/              # Pliki statyczne (CSS)
├── knowledge_base/      # Baza wiedzy (PDF-y)
└── ingest_knowledge.py  # Skrypt do przetwarzania PDF-ów
```

## Zmienne środowiskowe

- `OPENAI_API_KEY` - klucz API OpenAI (wymagane)
- `OPENAI_MODEL_NAME` - model LLM (domyślnie: gpt-4o-mini)
- `OPENAI_EMBEDDING_MODEL` - model embeddings (domyślnie: text-embedding-3-small)

## Licencja

MIT

