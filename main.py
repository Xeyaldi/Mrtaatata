import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# Gemini əvəzinə tam stabil və pulsuz DuckDuckGo AI
from duckduckgo_search import DDGS

# Ayarlar (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")

app = Client("ht_ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MEDIA YÜKLƏYİCİ (Toxunulmadı, eynilə qalır) ---
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

# --- AI CAVAB FUNKSİYASI (Bloklanmayan GPT-4o-mini) ---
async def get_ai_response(text):
    try:
        with DDGS() as ddgs:
            response = ""
            # Burada 'gpt-4o-mini' modeli işləyir, çox sürətlidir
            for r in ddgs.chat(text, model='gpt-4o-mini'):
                response += r
            return response if response else "🤔 Cavab ala bilmədim."
    except Exception as e:
        return f"❌ AI Xətası: {str(e)}"

# --- START MESAJI VƏ BUTONLAR (Toxunulmadı, eynilə qalır) ---
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

# --- /ai KOMANDASI (Əlavə olundu) ---
@app.on_message(filters.command("ai") & filters.private)
async def ai_cmd_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❗ Sualınızı yazın. Məsələn: `/ai Salam necəsən?` ")
        return
    
    query = " ".join(message.command[1:])
    status = await message.reply("🤔 **Düşünürəm...**")
    response = await get_ai_response(query)
    await status.edit(response)

# --- ƏSAS MƏNTİQ (Media + Birbaşa AI) ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    text = message.text
    
    # Komandadırsa keç
    if text.startswith("/"):
        return

    # 1. Media Linki Yoxlanışı (TikTok, Insta, Pinterest)
    if any(x in text.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com"]):
        status = await message.reply("📥 **HT AI yükləyir...**")
        try:
            path = download_media(text)
            await message.reply_video(path, caption="🚀 **HT AI Downloader**")
            await status.delete()
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            await status.edit(f"❌ Video yüklənmədi: {str(e)}")
    
    # 2. Birbaşa AI sualı (Link deyilsə)
    else:
        status = await message.reply("🤔 **Düşünürəm...**")
        response = await get_ai_response(text)
        await status.edit(response)

app.run()
