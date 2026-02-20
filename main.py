import os
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# Mistral rəsmi kitabxanası
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Ayarlar (Heroku Config Vars)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")
MISTRAL_KEY = os.environ.get("MISTRAL_KEY", "mistral_api_key")

# Mistral Başlatma
mistral_client = MistralClient(api_key=MISTRAL_KEY)
AI_MODEL = "mistral-tiny" # Pulsuz və stabil model

app = Client("ht_ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MEDIA YÜKLƏYİCİ (Dəyişilmədi) ---
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

# --- START MESAJI VƏ BUTONLAR (Dəyişilmədi) ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    caption = (
        "🤖 **HT AI Xidmətinizdədir! (Mistral AI)**\n\n"
        "📥 **Media:** TikTok, Instagram linki atın.\n"
        "🧠 **AI:** Sualınızı yazın və ya `/ai` ilə soruşun."
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [
            InlineKeyboardButton("🐐 Sahib", url="https://t.me/kullaniciadidi"),
            InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots")
        ]
    ])
    await message.reply_text(caption, reply_markup=buttons)

# --- /ai KOMANDASI ---
@app.on_message(filters.command("ai") & filters.private)
async def ai_cmd_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❗ Sualınızı yazın. Məsələn: `/ai Salam` ")
        return
    query = " ".join(message.command[1:])
    status = await message.reply("🤔 **Mistral düşünür...**")
    try:
        chat_response = mistral_client.chat(
            model=AI_MODEL,
            messages=[ChatMessage(role="user", content=query)]
        )
        await status.edit(chat_response.choices[0].message.content)
    except Exception as e:
        await status.edit(f"❌ Mistral Xətası: {str(e)}")

# --- ƏSAS MƏNTİQ (Media + Birbaşa AI) ---
@app.on_message(filters.text & filters.private)
async def main_logic(client, message):
    text = message.text
    if text.startswith("/"): return

    if any(x in text.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com"]):
        status = await message.reply("📥 **Yüklənir...**")
        try:
            path = download_media(text)
            await message.reply_video(path, caption="🚀 @HT_AI")
            await status.delete()
            if os.path.exists(path): os.remove(path)
        except Exception as e:
            await status.edit(f"❌ Xəta: {str(e)}")
    else:
        status = await message.reply("🤔 **Düşünürəm...**")
        try:
            chat_response = mistral_client.chat(
                model=AI_MODEL,
                messages=[ChatMessage(role="user", content=text)]
            )
            await status.edit(chat_response.choices[0].message.content)
        except Exception as e:
            await status.edit(f"❌ AI Xətası: {str(e)}")

app.run()
