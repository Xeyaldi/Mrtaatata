import os
import yt_dlp
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Ayarlar
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")

app = Client("ht_media_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- COOKIE YÜKLƏMƏ FUNKSİYASI ---
def get_cookies():
    cookie_url = "https://batbin.me/deuteride"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        response = requests.get(cookie_url, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text.strip()
            header = "# Netscape HTTP Cookie File"
            if not content.startswith(header):
                content = header + "\n" + content
            
            with open("cookies.txt", "w", encoding="utf-8") as f:
                f.write(content)
            return "cookies.txt"
    except:
        return None
    return None

# --- YÜKLƏMƏ FUNKSİYASI ---
def download_media(url, mode="video"):
    cookie_file = get_cookies()
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[m4a]/best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'cookiefile': cookie_file,
        # PO-TOKEN və bot qorumasını keçmək üçün əsas tənzimləmələr
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
        'params': {'allow_unplayable_formats': True},
    }
    
    if mode == "music":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if not info:
            raise Exception("Media tapılmadı.")
        
        filename = ydl.prepare_filename(info)
        
        if mode == "music":
            base, ext = os.path.splitext(filename)
            if os.path.exists(base + ".mp3"):
                filename = base + ".mp3"

        is_video = True
        if info.get('ext') in ['jpg', 'png', 'webp', 'jpeg'] or info.get('vcodec') == 'none' or mode == "music":
            is_video = False

        return filename, info.get('title', 'Media'), is_video

# --- START MESAJI ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    text = (
        "✨ **HT ULTIMATE DOWNLOADER** ✨\n\n"
        "🚀 Salam! Mən sosial şəbəkələrdən video, musiqi və şəkil yükləmək üçün nəzərdə tutulmuşam.\n\n"
        "📥 **İstifadə:** Sadəcə linki göndərin"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Dəstəklənən Platformalar", callback_data="help_list")],
        [InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots"),
         InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadidi")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# --- YOUTUBE AXTARIŞ KOMANDASI ---
@app.on_message(filters.command("youtube") & filters.private)
async def youtube_search(client, message):
    query = message.text.split(None, 1)
    if len(query) < 2:
        return await message.reply_text("❌ **Zəhmət olmasa axtarış sözünü yazın!**\nNümunə: `/youtube mahnı adı`")
    
    status = await message.reply("🔍 **YouTube-da axtarılır...**")
    search_query = query[1]
    
    ydl_opts = {'quiet': True, 'no_warnings': True, 'cookiefile': get_cookies()}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch5:{search_query}", download=False)['entries']
            if not results:
                return await status.edit("❌ **Heç bir nəticə tapılmadı!**")
            
            buttons = []
            for video in results:
                title = (video.get('title')[:35] + "..") if len(video.get('title')) > 35 else video.get('title')
                v_url = video.get('webpage_url')
                buttons.append([InlineKeyboardButton(f"🎬 {title}", callback_data=f"yt_choice|{v_url}")])
            
            await status.edit(f"🔎 **'{search_query}' üçün nəticələr:**", reply_markup=InlineKeyboardMarkup(buttons))
        except Exception as e:
            await status.edit(f"❌ **Axtarış xətası:** {str(e)}")

# --- ƏSAS MƏNTİQ ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    url = message.text
    if url.startswith("/"): return

    if "youtube.com" in url or "youtu.be" in url:
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video", callback_data=f"vid|{url}"),
             InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")]
        ])
        await message.reply_text("🎞 **YouTube aşkarlandı! Seçim edin:**", reply_markup=buttons)
    
    else:
        status = await message.reply("⚡ **Analiz edilir...** 📥")
        try:
            path, title, is_video = download_media(url, mode="video")
            await status.edit("📤 **Serverə yüklənir... 🚀**")
            
            if is_video:
                await message.reply_video(path, caption=f"✅ **Video:** `{title}`\n🚀 @ht_bots")
            else:
                await message.reply_photo(path, caption=f"✅ **Şəkil:** `{title}`\n🚀 @ht_bots")
            
            await status.delete()
            if os.path.exists(path): os.remove(path)
        except Exception as e:
            await status.edit(f"❌ **Xəta:** {str(e)}")

# --- CALLBACK EMALÇISI ---
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data

    if data.startswith("yt_choice|"):
        url = data.split("|")[1]
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎬 Video", callback_data=f"vid|{url}"),
             InlineKeyboardButton("🎵 Musiqi (MP3)", callback_data=f"mus|{url}")]
        ])
        await callback_query.message.edit("⏬ **Formatı seçin:**", reply_markup=buttons)

    elif data == "help_list":
        help_text = (
            "🚀 **Dəstəklənən Platformalar və İmkanlar:**\n\n"
            "📹 **Sosial Media:**\n"
            "• `TikTok` - Loqosuz videolar\n"
            "• `Instagram` - Reels, Post, Hekayə\n"
            "• `Pinterest` - Video və Yüksək keyfiyyətli Şəkillər\n"
            "• `Facebook` - Bütün kütləvi videolar\n"
            "• `Snapchat` - Spotlight videoları\n\n"
            "🐦 **Xəbər & Forum:**\n"
            "• `Twitter (X)` - Video və GIF\n"
            "• `Reddit` - Səsli videolar\n"
            "• `Threads` - Video yükləmə\n\n"
            "🎵 **Musiqi:**\n"
            "• `SoundCloud`, `Spotify`, `Bandcamp` (MP3 formatda)\n\n"
            "🎬 **Və 1000-dən çox sayt:**\n"
            "• `Vimeo`, `Twitch`, `Dailymotion`, `Steam` ve s."
        )
        await callback_query.message.edit(help_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Geri", callback_data="back_start")]
        ]))

    elif data == "back_start":
        text = (
            "✨ **HT ULTIMATE DOWNLOADER** ✨\n\n"
            "🚀 Salam! Mən sosial şəbəkələrdən video, musiqi və şəkil yükləmək üçün nəzərdə tutulmuşam.\n\n"
            "📥 **İstifadə:** Sadəcə yükləmək istədiyiniz medianın linkini bura göndərin."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 Dəstəklənən Platformalar", callback_data="help_list")],
            [InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots"),
             InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadidi")]
        ])
        await callback_query.message.edit(text, reply_markup=buttons)

    elif "|" in data:
        mode_raw, url = data.split("|")
        mode = "video" if mode_raw == "vid" else "music"
        await callback_query.message.edit(f"⏳ **Hazırlanır...** ({mode.upper()})")
        
        try:
            path, title, is_video = download_media(url, mode=mode)
            if mode == "video":
                await callback_query.message.reply_video(path, caption=f"🎬 `{title}`\n🚀 @ht_bots")
            else:
                final_path = path.rsplit('.', 1)[0] + ".mp3"
                if not os.path.exists(final_path): final_path = path
                await callback_query.message.reply_audio(final_path, caption=f"🎵 `{title}`\n🚀 @ht_bots")
                if os.path.exists(final_path) and final_path != path: os.remove(final_path)
            
            await callback_query.message.delete()
            if os.path.exists(path): os.remove(path)
        except Exception as e:
            await callback_query.message.edit(f"❌ **Xəta:** {str(e)}")

app.run()
