# Notatki z konfiguracji projektu - cv_creator

## Data: 2025-01-XX

## Opis projektu

CV Creator - aplikacja do tworzenia profesjonalnych CV z wykorzystaniem AI (OpenAI) i RAG (Retrieval Augmented Generation).

## Funkcjonalności

- 📝 Formularz do wypełnienia danych CV
- 🤖 CV Coach - asystent AI pomagający w pisaniu CV
- 📄 Generowanie CV w dwóch wariantach (klasyczny/nowoczesny)
- 📑 Generowanie PDF
- 🧠 RAG - wykorzystanie bazy wiedzy z PDF-ów do lepszych sugestii

## Konfiguracja klucza OpenAI API

**Lokalizacja:** https://platform.openai.com/api-keys

**Sposób konfiguracji:**
Projekt używa zmiennych środowiskowych systemowych lub można ustawić w `app/config.py` (fallback).

**Zmienne środowiskowe:**
```bash
export OPENAI_API_KEY="sk-proj-..."
export OPENAI_MODEL_NAME="gpt-4o-mini"  # opcjonalnie
export OPENAI_EMBEDDING_MODEL="text-embedding-3-small"  # opcjonalnie
```

**Lub w pliku `.env` (jeśli używasz python-dotenv):**
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

## Instalacja lokalna

```bash
# Przejdź do katalogu projektu
cd /Users/tomowski/PycharmProjects/PythonProject/cv_creator

# Utwórz wirtualne środowisko (jeśli nie istnieje)
python -m venv .venv

# Aktywuj środowisko
source .venv/bin/activate  # Mac/Linux
# lub
.venv\Scripts\activate  # Windows

# Zainstaluj zależności
pip install -r requirements.txt

# Ustaw klucz API
export OPENAI_API_KEY="twój-klucz"

# Uruchom ingestion bazy wiedzy (opcjonalnie - przetwarza PDF-y)
python ingest_knowledge.py

# Uruchom serwer
uvicorn app.main:app --reload
```

Aplikacja będzie dostępna pod: http://127.0.0.1:8000

## Struktura projektu

```
cv_creator/
├── app/
│   ├── main.py           # FastAPI aplikacja
│   ├── models.py         # Modele Pydantic
│   ├── config.py         # Konfiguracja (klucz API)
│   └── services/
│       ├── cv_engine.py      # Silnik CV
│       ├── llm_client.py     # Klient OpenAI
│       ├── rag_client.py     # RAG client
│       └── pdf_generator.py  # Generator PDF
├── templates/            # Szablony HTML (CV)
├── static/              # Pliki statyczne (CSS)
├── knowledge_base/      # Baza wiedzy (PDF-y)
└── ingest_knowledge.py  # Skrypt do przetwarzania PDF-ów
```

## Wersje pakietów

Z pliku `requirements.txt`:
- `fastapi>=0.121.0`
- `uvicorn[standard]>=0.38.0`
- `openai>=2.8.0`
- `xhtml2pdf>=0.2.17`
- `pydantic[email]>=2.12.0`
- `python-multipart>=0.0.20`
- `jinja2>=3.1.0`
- `pypdf>=6.2.0`

## Konfiguracja klucza API w kodzie

Projekt używa `app/config.py` z fallbackiem:
```python
FALLBACK_API_KEY = "WSTAW_TUTAJ_ALBO_UZYJ_ENV"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", FALLBACK_API_KEY)
```

**Uwaga:** W produkcji zawsze używaj zmiennych środowiskowych, nie hardcoduj klucza w kodzie!

## Git - konfiguracja i push

**Repozytorium:** https://github.com/tomowskima/cv_creator

```bash
# Sprawdź status
git status

# Dodaj zmiany
git add .

# Commit
git commit -m "Opis zmian"

# Push
git push origin main
```

## Wdrożenie na Render

1. Połącz repozytorium GitHub z Render
2. Utwórz Web Service
3. Ustaw:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Dodaj zmienne środowiskowe:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL_NAME` (opcjonalnie)
   - `OPENAI_EMBEDDING_MODEL` (opcjonalnie)

## Wdrożenie na Railway

1. Połącz repozytorium GitHub z Railway
2. Railway automatycznie wykryje konfigurację z `railway.json`
3. Dodaj zmienne środowiskowe w Settings → Variables

## Różnice w stosunku do hhg_baza_wiedzy

1. **Konfiguracja klucza API:**
   - `cv_creator` używa zmiennych środowiskowych systemowych lub fallback w `config.py`
   - `hhg_baza_wiedzy` używa pliku `.env` z python-dotenv

2. **Struktura:**
   - `cv_creator` ma bardziej złożoną strukturę z serwisami
   - `hhg_baza_wiedzy` jest prostszy, wszystko w `main.py`

3. **RAG:**
   - `cv_creator` używa prostszego podejścia do RAG (ingest_knowledge.py)
   - `hhg_baza_wiedzy` używa LangChain z ChromaDB

## Troubleshooting

### Problem: Klucz API nie działa
**Rozwiązanie:**
- Sprawdź czy zmienna środowiskowa jest ustawiona: `echo $OPENAI_API_KEY`
- Sprawdź czy klucz nie jest placeholderem w `config.py`
- Upewnij się, że klucz jest poprawny na https://platform.openai.com/api-keys

### Problem: Błąd przy generowaniu PDF
**Rozwiązanie:**
- Sprawdź czy `xhtml2pdf` jest zainstalowany
- Sprawdź logi aplikacji

### Problem: RAG nie działa
**Rozwiązanie:**
- Uruchom `python ingest_knowledge.py` aby przetworzyć PDF-y
- Sprawdź czy plik `knowledge_base/ingested_chunks.json` istnieje

## Uwagi

- Plik `.env` (jeśli istnieje) NIE powinien być w repozytorium
- Dokumenty PDF w `knowledge_base/` mogą być w repo (są częścią projektu)
- Na produkcji zawsze używaj zmiennych środowiskowych dla kluczy API

## Status

✅ Projekt działa na Windows
✅ Gotowy do wdrożenia na Render/Railway
✅ Repozytorium na GitHubie

