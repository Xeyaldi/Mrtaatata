import os
from pytdbot import Client, types
# Digər fayldan funksiyanı çağırırıq
try:
    from yt_dlp import youtube_cmd
except ImportError:
    pass

# Ayarlar
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot_tokenin")

# Pytdbot Client-i
app = Client(
    api_token=BOT_TOKEN,
    lib_path=None # Heroku-da avtomatik tdfind istifadə edir
)

# --- START MESAJI ---
@app.on_message(filters="text")
async def handle_messages(c: Client, message: types.Message):
    # Əgər mesaj /start komandasıdırsa
    if message.text == "/start":
        text = (
            "✨ **HT ULTIMATE DOWNLOADER** ✨\n\n"
            "🚀 Salam! Mən sosial şəbəkələrdən video, musiqi və şəkil yükləmək üçün nəzərdə tutulmuşam.\n\n"
            "📥 **İstifadə:** Sadəcə linki bura göndərin və ya /youtube yazıb axtarış edin."
        )
        buttons = types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("📚 Dəstəklənən Platformalar", callback_data="help_list")],
            [types.InlineKeyboardButton("📢 Bot Kanalı", url="https://t.me/ht_bots"),
             types.InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadidi")]
        ])
        await message.reply_text(text, reply_markup=buttons)
        return

    # Əgər yardım siyahısı üçün callback lazımdırsa (Pytdbot callback fərqlidir)
    # Amma sən link göndərəndə youtube_cmd-yə getməsini istəyirsən:
    if "youtube.com" in message.text or "youtu.be" in message.text:
        # Sənin göndərdiyin youtube_cmd funksiyasını çağırırıq
        # Əvvəlcə mesajı youtube_cmd-nin tanıması üçün formatlayırıq
        if not message.text.startswith("/youtube"):
            message.text = f"/youtube {message.text}"
        await youtube_cmd(c, message)

# --- CALLBACK HANDLER ---
@app.on_callback_query()
async def on_callback(c: Client, cb: types.CallbackQuery):
    if cb.data == "help_list":
        help_text = (
            "🚀 **Dəstəklənən Platformalar və İmkanlar:**\n\n"
            "📹 **Sosial Media:**\n"
            "• `YouTube` - Video, Shorts, MP3\n"
            "• `TikTok` - Loqosuz\n"
            "• `Instagram`, `Pinterest`, `Facebook` və s."
        )
        await cb.edit_text(help_text, reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("⬅️ Geri", callback_data="back_start")]
        ]))
    
    elif cb.data == "back_start":
        # Start mesajına qayıdış
        await cb.edit_text("✨ **HT ULTIMATE DOWNLOADER** ✨\n\nYenidən xoş gəldin!", reply_markup=types.InlineKeyboardMarkup([
            [types.InlineKeyboardButton("📚 Dəstəklənən Platformalar", callback_data="help_list")]
        ]))

app.run()
