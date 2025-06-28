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

# 🔁 Format taille lisible
def format_bytes(bytes_size):
    return f"{bytes_size / (1024 * 1024):.1f}MB"

# 📶 Affichage de la progression de téléchargement
def hook_progress(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        percent = downloaded / total * 100 if total else 0
        eta = d.get('eta', 0)
        print(f"⬇️ {format_bytes(downloaded)} / {format_bytes(total)} "
              f"({percent:.1f}%) | ⏳ {eta}s restant")

# 📥 Téléchargement vidéo via yt-dlp
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

# 📦 Compression automatique jusqu'à <90MB
def compresser_jusqua_90mb(input_path: str, output_path: str, max_size_mb: int = 90):
    crf = 28
    scale = "scale=-2:480"  # max 480p

    while crf <= 35:
        print(f"🔧 Compression tentative avec CRF={crf}...")

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", scale,
            "-vcodec", "libx264", "-crf", str(crf),
            "-preset", "ultrafast",
            "-acodec", "aac", "-b:a", "64k",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if not os.path.exists(output_path):
            print("⚠️ Compression échouée.")
            break

        taille_finale = os.path.getsize(output_path) / (1024 * 1024)
        print(f"📦 Taille finale : {taille_finale:.2f}MB")

        if taille_finale < max_size_mb:
            print("✅ Compression réussie sous 90MB.")
            return True

        crf += 2

    print("❌ Impossible de compresser sous 90MB.")
    return False

# ▶️ Commande /start
@bot.message_handler(commands=['start'])
def handle_start(msg):
    bot.reply_to(msg, "🎬 Envoie-moi un lien contenant une vidéo à télécharger.")

# 🌐 Traitement du lien
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
            # Compression jusqu'à <90MB
            success = compresser_jusqua_90mb(chemin, chemin_compressé)
            os.remove(chemin)
            chemin = chemin_compressé

            if success:
                bot.send_document(msg.chat.id, open(chemin, 'rb'), caption="📂 Vidéo compressée (<90MB)")
            else:
                bot.reply_to(msg, "🚫 Impossible de compresser cette vidéo sous 90MB.")
                return
        else:
            # Envoi direct si petit fichier
            sending_msg = bot.reply_to(msg, "📤 Envoi de la vidéo...")
            with open(chemin, 'rb') as f:
                video = types.InputFile(f, file_name="video.mp4")
                bot.send_video(msg.chat.id, video, timeout=180, caption="📽️ Voici ta vidéo")
            bot.edit_message_text("✅ Vidéo envoyée avec succès !", msg.chat.id, sending_msg.message_id)

    except Exception as e:
        bot.reply_to(msg, f"❌ Erreur : {e}")

    finally:
        for f in [chemin, chemin_compressé]:
            if os.path.exists(f):
                os.remove(f)

bot.infinity_polling()