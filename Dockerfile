# Utilise une image Python avec ffmpeg
FROM python:3.10-slim

# Installe ffmpeg et autres dépendances
RUN apt update && apt install -y ffmpeg && apt clean

# Crée un dossier pour le code
WORKDIR /app

# Copie les fichiers
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lance le bot
CMD ["python", "bot.py"]