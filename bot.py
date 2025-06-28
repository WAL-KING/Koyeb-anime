import os
import telebot
from telebot import types
import yt_dlp
import subprocess
import time
import math
import shutil

BOT_TOKEN = "8186207517:AAEvSLdgHEnn7IQYjwolkjsOD5CmSWrDmfU"
bot = telebot.TeleBot(BOT_TOKEN)

# 🔁 Formatage taille
def format_bytes(bytes_size):
    return f"{bytes_size / (1024 * 1024):.1f}MB"

# 📶 Progression yt-dlp
def hook_progress(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        percent = downloaded / total * 100 if total else 0
        eta = d.get('eta', 0)

        print(f"⬇️ Téléchargement: {format_bytes(downloaded)} / {format_bytes(total)} "
              f"({percent:.1f}%) | ⏳ {eta}s restant")

# 📥 Téléchargement vidéo
def telecharger_video(url: str, sortie: str = "video.mp4") -> str:
    ydl_opts = {
        'outtmpl': sortie,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
        'progress_hooks': [hook_progress],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return sortie

# 🎞️ Compression si trop lourd
def compresser_video(input_path: str, output_path: str):
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vcodec", "libx264", "-crf", "28",
        "-preset", "fast", output_path
    ]
    subprocess.run(cmd, check=True)

# ▶️ Start
@bot.message_handler(commands=['start'])
def handle_start(msg):
    bot.reply_to(msg, "🎬 Envoie-moi un lien contenant une vidéo à télécharger.")

# 🌐 Réception de lien
@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("http"))
def handle_url(msg):
    url = msg.text.strip()
    bot.reply_to(msg, f"🔍 Téléchargement depuis : {url}")

    chemin = "video.mp4"
    chemin_compressé = "video_compressed.mp4"

    try:
        # Téléchargement
        telecharger_video(url, chemin)

        taille = os.path.getsize(chemin)
        if taille > 50 * 1024 * 1024:
            # Compression si > 50MB
            compresser_video(chemin, chemin_compressé)
            os.remove(chemin)
            chemin = chemin_compressé

            bot.send_document(msg.chat.id, open(chemin, 'rb'), caption="📂 Vidéo compressée")
        else:
            # Envoi avec message temporaire
            sending_msg = bot.reply_to(msg, "📤 Envoi de la vidéo...")
            with open(chemin, 'rb') as f:
                video = types.InputFile(f, file_name="video.mp4")
                bot.send_video(msg.chat.id, video, timeout=180, caption="📽️ Voici ta vidéo")
            bot.edit_message_text("✅ Vidéo envoyée avec succès !", msg.chat.id, sending_msg.message_id)

    except Exception as e:
        bot.reply_to(msg, f"❌ Erreur : {e}")

    finally:
        # Nettoyage
        for f in [chemin, chemin_compressé]:
            if os.path.exists(f):
                os.remove(f)

bot.infinity_polling() 
