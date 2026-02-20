import os
import yt_dlp
import google.generativeai as genai
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ayarlar (Heroku Config Vars bölməsinə əlavə et)
API_ID = int(os.environ.get("API_ID", "12345"))
API_HASH = os.environ.get("API_HASH", "hash_kodun")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "gemini_key")

# Gemini AI Konfiqurasiyası
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

app = Client("ht_ai_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Video yükləmə mexanizmi
def download_media(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True, 'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# --- START MESAJI VƏ REAKSİYA ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    # 🎃 Reaksiyası
    await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji="🎃")
    
    caption = (
        "🤖 **HT AI sizə kömək etməyə hazırdır!**\n\n"
        "✨ **Funksiyalar:**\n"
        "├ 🧠 `/startai` — Süni İntellekti işə salır\n"
        "├ 📥 **Media:** Insta, TikTok, Pinterest yükləyici\n"
        "└ 💬 **Söhbət:** Bota reply ataraq danışın\n\n"
        "💡 _Məni qruplarda idarəçi etməyi unutmayın!_"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Məni Qrupa Əlavə Et", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [
            InlineKeyboardButton("🐐 Sahib", url="https://t.me/kullaniciadidi"),
            InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots")
        ],
        [InlineKeyboardButton("💬 Kömək Qrupu", url="https://t.me/_ht_bots_chat")]
    ])
    
    await message.reply_text(caption, reply_markup=buttons)

# --- AI MƏNTİQİ: /startai VƏ YA REPLY ---
@app.on_message(filters.group & (filters.command("startai") | filters.reply))
async def group_ai_handler(client, message):
    # Əgər reply-dırsa, yalnız BOTA atılan reply-ları cavabla
    if message.reply_to_message:
        if message.reply_to_message.from_user.id != client.me.id:
            return 
    elif not message.text.startswith("/startai"):
        return

    # Sualı təmizləyirik
    user_query = message.text.replace("/startai", "").strip()
    
    if not user_query and message.reply_to_message:
        user_query = message.text

    if not user_query:
        return await message.reply_text("🤔 **HT AI:** Eşidirəm, sualınızı verin!")

    processing_msg = await message.reply("⚡️ `HT AI emal edir...`")
    try:
        response = ai_model.generate_content(user_query)
        await processing_msg.edit(f"🤖 **HT AI:**\n\n{response.text}")
    except:
        await processing_msg.edit("❌ Üzr istəyirəm, beyin hüceyrələrimdə qısaqapanma oldu.")

# --- MÜSTƏQİL VİDEO YÜKLƏYİCİ (PM) ---
@app.on_message(filters.private & ~filters.command("start"))
async def pm_logic(client, message):
    text = message.text
    if any(x in text.lower() for x in ["tiktok.com", "instagram.com", "pin.it", "pinterest.com"]):
        status = await message.reply("📥 **HT AI videonu gətirir...**")
        try:
            path = download_media(text)
            await message.reply_video(path, caption="🚀 **HT AI Media Downloader**")
            await status.delete()
            os.remove(path)
        except:
            await status.edit("❌ Video tapılmadı və ya xəta baş verdi.")
    else:
        # Şəxsi mesajda birbaşa söhbət
        res = ai_model.generate_content(text)
        await message.reply_text(res.text)

app.run()
