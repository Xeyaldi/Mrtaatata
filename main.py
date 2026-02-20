import os
import yt_dlp
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ayarlar (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "gemini_api_keyin")

app = Client("ht_ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MEDIA YÜKLƏYİCİ (Bütün linklər bərpa olundu) ---
def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# --- GEMINI AI (Requests ilə daha stabildir) ---
async def get_ai_response(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        if 'candidates' in res_json:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "🤔 Gemini hazırda cavab verə bilmir (Region bloku ola bilər)."
    except Exception as e:
        return f"❌ Xəta baş verdi: {str(e)}"

# --- START MESAJI VƏ BUTONLAR (Bərpa olundu) ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    caption = (
        "🤖 **HT AI Xidmətinizdədir!**\n\n"
        "📥 **Media:** TikTok, Instagram, Pinterest linki atın.\n"
        "🧠 **AI:** İstənilən sualı yazın və ya `/ai` komandasını işlədin."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [
            InlineKeyboardButton("🐐 Sahib", url="https://t.me/kullaniciadidi"),
            InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots")
        ]
    ])
    await message.reply_text(caption, reply_markup=buttons)

# --- /ai KOMANDASI (Bərpa olundu) ---
@app.on_message(filters.command("ai") & filters.private)
async def ai_cmd_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❗ Sualınızı yazın. Məsələn: `/ai Salam` ")
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply("🤔 **Düşünürəm...**")
    response = await get_ai_response(query)
    await status.edit(response)

# --- ƏSAS MƏNTİQ (Yükləmə + AI) ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    text = message.text
    if text.startswith("/"): return

    # Media Linkləri Yoxlanışı (TikTok, Instagram, Pinterest)
    if any(x in text.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com"]):
        status = await message.reply("📥 **Hazırlanır...**")
        try:
            path = download_media(text)
            await message.reply_video(path, caption="🚀 **HT AI Downloader**")
            await status.delete()
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            await status.edit(f"❌ Yüklənmədi: {str(e)}")
    
    # Əgər link deyilsə, AI-ya göndər
    else:
        status = await message.reply("🤔 **Düşünürəm...**")
        response = await get_ai_response(text)
        await status.edit(response)

app.run()
