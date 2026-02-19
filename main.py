import os
import asyncio
from pyrogram import Client, filters

# Heroku Config Vars-dan məlumatları götürürük
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# 1. Userbot (Arxivləri skan etmək üçün)
userbot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# 2. Adi Bot (İstifadəçilərlə danışmaq üçün)
bot = Client("history_bot_api", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Salam! Keçmiş adları tapmaq üçün istifadəçi ID-sini göndərin.")

@bot.on_message(filters.text & filters.private)
async def get_history(client, message):
    if not message.text.isdigit():
        await message.reply_text("Zəhmət olmasa düzgün bir ID göndərin.")
        return

    target_id = int(message.text)
    wait_msg = await message.reply_text("🔍 Arxivlər skan olunur, bu bir az vaxt ala bilər...")

    found_names = set()

    try:
        # Userbot vasitəsilə qlobal axtarış edirik
        async with userbot:
            async for msg in userbot.search_global(filter="empty"):
                if msg.from_user and msg.from_user.id == target_id:
                    name = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                    username = f"@{msg.from_user.username}" if msg.from_user.username else ""
                    found_names.add(f"👤 {name} {username}")
                
                if len(found_names) >= 10: # Limit
                    break
    except Exception as e:
        await wait_msg.edit(f"Xəta baş verdi: {e}")
        return

    if found_names:
        result = "\n".join(found_names)
        await wait_msg.edit(f"✅ **Tapılan keçmiş adlar:**\n\n{result}")
    else:
        await wait_msg.edit("❌ Bu ID-yə aid keçmiş iz tapılmadı.")

# Hər iki sistemi eyni anda başladırıq
async def main():
    await userbot.start()
    await bot.start()
    print("Sistem işləyir!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
