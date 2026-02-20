import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# Öz yaratdığın yt_dlp.py faylını burada tanıdıq:
from yt_dlp import download_media, search_youtube

# Ayarlar
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")

app = Client("ht_media_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- START MESAJI (BÜTÖV VƏ TOXUNULMAZ) ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    text = (
        "✨ **HT ULTIMATE DOWNLOADER** ✨\n\n"
        "🚀 Salam! Mən sosial şəbəkələrdən video, musiqi və şəkil yükləmək üçün nəzərdə tutulmuşam.\n\n"
        "📥 **İstifadə:** Sadəcə linki bura göndərin və ya /youtube yazıb axtarış edin."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Dəstəklənən Platformalar", callback_data="help_list")],
        [InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots"),
         InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadidi")]
    ])
    await message.reply_text(text, reply_markup=buttons)

# --- YOUTUBE AXTARIŞ KOMANDASI (BÜTÖV VƏ TOXUNULMAZ) ---
@app.on_message(filters.command("youtube") & filters.private)
async def youtube_search_cmd(client, message):
    query = message.text.split(None, 1)
    if len(query) < 2:
        return await message.reply_text("❌ **Zəhmət olmasa axtarış sözünü yazın!**\nNümunə: `/youtube mahnı adı`")
    
    status = await message.reply("🔍 **YouTube-da axtarılır...**")
    try:
        results = search_youtube(query[1])
        if not results:
            return await status.edit("❌ **Heç bir nəticə tapılmadı!**")
        
        buttons = []
        for video in results:
            title = (video.get('title')[:35] + "..") if len(video.get('title')) > 35 else video.get('title')
            v_url = video.get('webpage_url')
            buttons.append([InlineKeyboardButton(f"🎬 {title}", callback_data=f"yt_choice|{v_url}")])
        
        await status.edit(f"🔎 **'{query[1]}' üçün nəticələr:**", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        await status.edit(f"❌ **Axtarış xətası:** {str(e)}")

# --- ƏSAS MƏNTİQ (BÜTÖV VƏ TOXUNULMAZ) ---
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

# --- CALLBACK EMALÇISI (TAM SİYAHI VƏ DÜYMƏLƏR) ---
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
            "• `YouTube` - Video (4K), Shorts, MP3\n"
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
