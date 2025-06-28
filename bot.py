import os
import telebot
from telebot import types
import yt_dlp
import subprocess

BOT_TOKEN = "8186207517:AAEvSLdgHEnn7IQYjwolkjsOD5CmSWrDmfU"
bot = telebot.TeleBot(BOT_TOKEN)

def telecharger_video(url: str, sortie: str = "video.mp4") -> str:
    ydl_opts = {
        'outtmpl': sortie,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return sortie

def compresser_video(input_path: str, output_path: str):
    cmd = [
        "ffmpeg", "-i", input_path,
        "-vcodec", "libx264", "-crf", "28",
        "-preset", "fast", output_path
    ]
    subprocess.run(cmd, check=True)

@bot.message_handler(commands=['start'])
def handle_start(msg):
    bot.reply_to(msg, "🎬 Envoie-moi un lien contenant une vidéo à télécharger.")

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith("http"))
def handle_url(msg):
    url = msg.text.strip()
    bot.reply_to(msg, f"🔍 Téléchargement depuis : {url}")
    
    try:
        chemin = "video.mp4"
        telecharger_video(url, chemin)
        
        # Vérifie la taille
        taille = os.path.getsize(chemin)
        if taille > 50 * 1024 * 1024:
            # Compression
            chemin_compressé = "video_compressed.mp4"
            compresser_video(chemin, chemin_compressé)
            os.remove(chemin)
            chemin = chemin_compressé
            bot.send_document(msg.chat.id, open(chemin, 'rb'), caption="📂 Vidéo compressée")
        else:
            # Envoie direct
            with open(chemin, 'rb') as f:
                video = types.InputFile(f, file_name="video.mp4")
                bot.send_video(msg.chat.id, video, timeout=120, caption="📽️ Voici ta vidéo")

        os.remove(chemin)

    except Exception as e:
        bot.reply_to(msg, f"❌ Erreur : {e}")

bot.infinity_polling()
