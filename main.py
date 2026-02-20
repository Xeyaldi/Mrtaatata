import os
import yt_dlp
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ayarlar (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "gemini_key")

# --- GEMINI AYARLARI (Heç nə silinmədi, sadəcə gücləndirildi) ---
try:
    genai.configure(api_key=GEMINI_KEY)
    
    # AI-nın hər şeyi cavablandırması üçün filtrləri "BLOCK_NONE" edirik
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    ai_model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )
except Exception as e:
    print(f"Gemini başlatma xətası: {e}")

app = Client("ht_ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MEDIA YÜKLƏYİCİ (TikTok, Insta, Pinterest - QALIR) ---
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

# --- START MESAJI VƏ BUTONLAR (QALIR) ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    caption = (
        "🤖 **HT AI Xidmətinizdədir!**\n\n"
        "📥 **Media:** TikTok, Instagram, Pinterest linki atın.\n"
        "🧠 **AI:** İstənilən sualı yazın, Gemini cavablasın."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [
            InlineKeyboardButton("🐐 Sahib", url="https://t.me/kullaniciadidi"),
            InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots")
        ]
    ])
    await message.reply_text(caption, reply_markup=buttons)

# --- ƏSAS MƏNTİQ (HEÇ NƏ SİLİNMƏYİB) ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    text = message.text
    
    # 1. Media Linki Yoxlanışı
    if any(x in text.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com"]):
        status = await message.reply("📥 **HT AI videonu hazırlayır...**")
        try:
            path = download_media(text)
            await message.reply_video(path, caption="🚀 **HT AI Downloader**")
            await status.delete()
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            await status.edit(f"❌ Video yüklənmədi: {str(e)}")
    
    # 2. AI Söhbət Hissəsi
    else:
        try:
            response = ai_model.generate_content(text)
            if response.text:
                await message.reply_text(response.text)
            else:
                await message.reply_text("🤔 Cavab boşdur. Başqa cür soruşun.")
        except Exception as e:
            # Əgər xəta olarsa, səbəbini Telegram-da yazacaq (Region bloku və s.)
            await message.reply_text(f"❌ **AI Xətası:**\n`{str(e)}`")

app.run()
