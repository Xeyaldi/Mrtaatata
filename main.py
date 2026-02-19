import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Config məlumatları
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Client-lər
userbot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
bot = Client("history_bot_api", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- START MESAJI ---
@bot.on_message(filters.command("start"))
async def start(client, message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Salam, {user_name}!**\n\n"
        "🔍 Bu bot vasitəsilə istifadəçilərin Telegram arxivlərindəki **keçmiş adlarını və usernamelərini** tapa bilərsiniz.\n\n"
        "⚙️ **Necə istifadə etməli?**\n"
        "Sadəcə axtarmaq istədiyiniz şəxsin **User ID**-sini bura göndərin."
    )
    
    # Düymələr
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Sahib", url="https://t.me/kullaniciadidi")], # Öz username-ni yaz
        [InlineKeyboardButton("❓ ID Necə Tapılır?", callback_data="help_id")]
    ])
    
    await message.reply_text(welcome_text, reply_markup=buttons)

# --- ID TAPILMASI ÜÇÜN KÖMƏK (Callback) ---
@bot.on_callback_query(filters.regex("help_id"))
async def help_callback(client, callback_query):
    help_text = (
        "ℹ️ **User ID-ni necə tapmaq olar?**\n\n"
        "1. @userinfobot-a şəxsin mesajını yönləndirərək.\n"
        "2. Bəzi Telegram müştərilərində (məsələn: Plus, 67Gram) birbaşa profil bölməsində ID görünür."
    )
    await callback_query.answer(help_text, show_alert=True)

# --- ARAŞDIRMA MƏNTİQİ ---
@bot.on_message(filters.text & filters.private)
async def get_history(client, message):
    if not message.text.isdigit():
        await message.reply_text("⚠️ Zəhmət olmasa yalnız **rəqəmlərdən ibarət User ID** göndərin.")
        return

    target_id = int(message.text)
    wait_msg = await message.reply_text("🕵️‍♂️ **Arxivlər alt-üst edilir...**\nBu proses 10-30 saniyə çəkə bilər.")

    found_names = set()

    try:
        # Userbot ilə qlobal axtarış
        async with userbot:
            async for msg in userbot.search_global(filter="empty"):
                if msg.from_user and msg.from_user.id == target_id:
                    name = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    uname = f"(@{msg.from_user.username})" if msg.from_user.username else ""
                    found_names.add(f"📝 {name} {uname}")
                
                if len(found_names) >= 15: break # Max 15 nəticə
    except Exception as e:
        await wait_msg.edit(f"❌ Xəta baş verdi: {e}")
        return

    if found_names:
        result_text = "\n".join(found_names)
        await wait_msg.edit(f"✅ **ID: `{target_id}` üçün tapılan nəticələr:**\n\n{result_text}")
    else:
        await wait_msg.edit(f"😔 Təəssüf ki, `{target_id}` ID-si üçün arxivdə heç bir köhnə ad tapılmadı.")

# Sistemi başlat
async def main():
    await userbot.start()
    await bot.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
