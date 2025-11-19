#!/bin/bash
# Skrypt do inicjalizacji git i wrzucenia projektu na GitHub
# Użycie: ./SETUP_GIT.sh

echo "🚀 Inicjalizacja repozytorium Git..."

# Inicjalizuj git
git init

# Dodaj wszystkie pliki
echo "📦 Dodawanie plików..."
git add .

# Pierwszy commit
echo "💾 Tworzenie pierwszego commita..."
git commit -m "Initial commit: CV Creator z AI i RAG"

echo ""
echo "✅ Git zainicjalizowany!"
echo ""
echo "📝 Teraz musisz:"
echo "1. Utworzyć repozytorium na GitHub (https://github.com/new)"
echo "2. Skopiować URL repozytorium (np. https://github.com/twoja-nazwa/cv_creator.git)"
echo "3. Wykonać komendy:"
echo ""
echo "   git remote add origin <URL-TWOJEGO-REPO>"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

