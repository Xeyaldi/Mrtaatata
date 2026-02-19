import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Clientlər
userbot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
bot = Client("history_bot_api", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        f"👋 **Salam {message.from_user.first_name}!**\n\nID göndər, arxivləri yoxlayım.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🐐 Sahib", url="t.me/kullaniciadidi")]])
    )

@bot.on_message(filters.text & filters.private)
async def get_history(client, message):
    if not message.text.isdigit():
        return await message.reply("Zəhmət olmasa düzgün ID yazın.")
    
    target_id = int(message.text)
    m = await message.reply("🔎 Arxivlər skan edilir...")
    
    found_names = set()
    try:
        # search_global istifadə edirik
        async for msg in userbot.search_global(filter="empty"):
            if msg.from_user and msg.from_user.id == target_id:
                name = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                found_names.add(f"• {name}")
            if len(found_names) >= 15: break
            
        if found_names:
            await m.edit(f"✅ **ID `{target_id}` üçün tapılanlar:**\n\n" + "\n".join(found_names))
        else:
            await m.edit("❌ Arxivdə heç nə tapılmadı.")
    except Exception as e:
        await m.edit(f"Xəta: {e}")

# BU HİSSƏDƏ DƏYİŞİKLİK ETDİK (RuntimeError-un qarşısını almaq üçün)
async def start_services():
    await userbot.start()
    await bot.start()
    print("Bot və Userbot uğurla işə düşdü!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_services())
    except (KeyboardInterrupt, SystemExit):
        pass
