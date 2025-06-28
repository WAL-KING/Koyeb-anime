# ✅ Image de base légère avec Python
FROM python:3.10-slim

# 📦 Installer ffmpeg et ses dépendances
RUN apt update && \
    apt install -y ffmpeg && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# 📁 Créer un dossier de travail
WORKDIR /app

# 📂 Copier les fichiers de ton projet dans le conteneur
COPY . .

# 🔧 Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 🚀 Lancer le bot
CMD ["python", "bot.py"]