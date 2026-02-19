import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Heroku-da Config Vars hissəsindən oxuyacaq
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("history_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    text = (
        "**👋 Salam, mən Arxiv Detektiviyəm!**\n\n"
        "Mənə istənilən istifadəçinin **ID-sini** göndər, mən isə sənə onun "
        "keçmişdə işlətdiyi bütün adları tapıb gətirim.\n\n"
        "🔍 **Gözləyirəm...**"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🇦🇿 Kanalımız", url="https://t.me/ht_bots")]
    ]))

@app.on_message(filters.text & ~filters.command("start"))
async def search_history(client, message):
    user_input = message.text
    status = await message.reply_text("🔎 **Arxivlər alt-üst edilir...**")
    
    # Vizual Nəticə Şablonu (Bura real API qoşula bilər)
    result = (
        f"👤 **İstifadəçi:** `{user_input}`\n"
        "──────────────────\n"
        "📜 **Keçmiş Adları:**\n"
        "  ├ `Rofat_01` (2022)\n"
        "  ├ `Baku_Boy` (2023)\n"
        "  └ `Shadow` (İndi)\n\n"
        "🆔 **Username Tarixi:**\n"
        "  ├ `@old_user` \n"
        "  └ `@new_account` \n"
        "──────────────────\n"
        "✅ **Axtarış tamamlandı.**"
    )
    await status.edit_text(result)

print("Bot Heroku-da uğurla işə düşdü!")
app.run()
