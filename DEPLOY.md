# Instrukcja wdrożenia CV Creator

## Krok 1: Utwórz konto na GitHub

1. Wejdź na https://github.com
2. Kliknij "Sign up"
3. Wypełnij formularz i potwierdź email

## Krok 2: Utwórz nowe repozytorium na GitHub

1. Po zalogowaniu, kliknij "+" w prawym górnym rogu
2. Wybierz "New repository"
3. Wypełnij:
   - **Repository name**: `cv_creator` (lub inna nazwa)
   - **Description**: "Kreator CV z AI i RAG"
   - **Public** (dla darmowego hostingu na Render)
   - **NIE zaznaczaj** "Add a README file" (mamy już pliki)
   - **NIE zaznaczaj** "Add .gitignore" (mamy już)
4. Kliknij "Create repository"

## Krok 3: Wrzuć projekt na GitHub

W terminalu w katalogu projektu wykonaj:

```bash
# Inicjalizuj git (jeśli jeszcze nie)
git init

# Dodaj wszystkie pliki
git add .

# Zrób pierwszy commit
git commit -m "Initial commit: CV Creator z AI i RAG"

# Dodaj remote (ZASTĄP <twoja-nazwa> swoją nazwą użytkownika GitHub)
git remote add origin https://github.com/<twoja-nazwa>/cv_creator.git

# Wrzuć na GitHub
git branch -M main
git push -u origin main
```

**Uwaga**: GitHub może poprosić o autoryzację. Możesz użyć:
- Personal Access Token (Settings → Developer settings → Personal access tokens)
- Lub GitHub CLI (`gh auth login`)

## Krok 4: Wdróż na Render

1. Wejdź na https://render.com
2. Zarejestruj się (można przez GitHub)
3. Dashboard → "New" → "Web Service"
4. "Connect account" → wybierz GitHub
5. Wybierz repozytorium `cv_creator`
6. Wypełnij:
   - **Name**: `cv-creator` (lub inna nazwa)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
7. W sekcji "Environment Variables" dodaj:
   - `OPENAI_API_KEY` = twój klucz API
   - `OPENAI_MODEL_NAME` = `gpt-4o-mini` (opcjonalnie)
8. Kliknij "Create Web Service"
9. Render automatycznie zbuduje i wdroży aplikację (5-10 minut)

## Krok 5: Wdróż na Railway (alternatywa)

1. Wejdź na https://railway.app
2. Zarejestruj się (można przez GitHub)
3. "New Project" → "Deploy from GitHub repo"
4. Wybierz repozytorium `cv_creator`
5. Railway automatycznie wykryje konfigurację
6. W Settings → Variables dodaj:
   - `OPENAI_API_KEY` = twój klucz API
7. Railway automatycznie wdroży aplikację

## Po wdrożeniu

Aplikacja będzie dostępna pod adresem typu:
- Render: `https://cv-creator-xxx.onrender.com`
- Railway: `https://cv-creator.up.railway.app`

**Uwaga**: Na Render darmowy tier aplikacja może "zasypiać" po 15 min nieaktywności. Pierwsze żądanie po uśpieniu może trwać 30-60 sekund (budzenie).

## Troubleshooting

### Problem: "Module not found" podczas build
**Rozwiązanie**: Sprawdź czy `requirements.txt` zawiera wszystkie zależności

### Problem: Aplikacja nie startuje
**Rozwiązanie**: 
- Sprawdź logi w Render/Railway dashboard
- Upewnij się, że `OPENAI_API_KEY` jest ustawione
- Sprawdź czy port jest ustawiony na `$PORT`

### Problem: Błąd przy montowaniu static files
**Rozwiązanie**: Sprawdź czy katalogi `static/` i `templates/` są w repo

