import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Ayarlar
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")

app = Client("ht_media_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- YÜKLƏMƏ FUNKSİYASI ---
def download_media(url, mode="video"):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if mode == "video" else 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }
    if mode == "music":
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info), info.get('title', 'Media')

# --- START MESAJI (Vizual Effektli) ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    text = (
        "✨ **HT ULTIMATE DOWNLOADER** ✨\n\n"
        "🚀 **Dəstəklənən Platformalar:**\n"
        " ├ 📹 `YouTube`, `TikTok`, `Instagram`\n"
        " ├ 🖼 `Pinterest`, `Facebook`\n"
        " └ 🎵 `SoundCloud` və daha çox...\n\n"
        "📥 *Sadəcə linki göndərin, gerisini mənə buraxın!*"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots")],
        [InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadi")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# --- ƏSAS MƏNTİQ ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    url = message.text
    
    # YouTube Linki Yoxlanışı
    if "youtube.com" in url or "youtu.be" in url:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎬 Video", callback_data=f"vid|{url}"),
                InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")
            ]
        ])
        await message.reply_text("🎞 **YouTube aşkarlandı!**\nHansı formatda endirmək istəyirsiniz?", reply_markup=buttons)
    
    # Digər Sosial Şəbəkələr
    elif any(x in url.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com", "facebook.com"]):
        status = await message.reply("⚡ **Analiz edilir...** 📥")
        try:
            path, title = download_media(url, mode="video")
            await status.edit("📤 **Serverə yüklənir... 🚀**")
            await message.reply_video(path, caption=f"✅ **Hazırdır:** `{title}`\n\n🚀 @ht_bots")
            await status.delete()
            if os.path.exists(path): os.remove(path)
        except Exception as e:
            await status.edit(f"❌ **Xəta:** {str(e)}")

# --- CALLBACK (YouTube Seçimi Üçün) ---
@app.on_callback_query(filters.regex(r"^(vid|mus)\|"))
async def youtube_callback(client, callback_query: CallbackQuery):
    mode_raw, url = callback_query.data.split("|")
    mode = "video" if mode_raw == "vid" else "music"
    
    await callback_query.message.edit(f"⏳ **Hazırlanır...** ({mode.upper()})")
    
    try:
        path, title = download_media(url, mode=mode)
        if mode == "video":
            await callback_query.message.reply_video(path, caption=f"🎬 `{title}`\n\n🚀 @ht_bots")
        else:
            # MP3 uzantısını düzəltmək üçün (FFmpeg sonrası)
            final_path = path.rsplit('.', 1)[0] + ".mp3"
            await callback_query.message.reply_audio(final_path, caption=f"🎵 `{title}`\n\n🚀 @ht_bots")
        
        await callback_query.message.delete()
        if os.path.exists(path): os.remove(path)
    except Exception as e:
        await callback_query.message.edit(f"❌ **Xəta:** {str(e)}")

app.run()
