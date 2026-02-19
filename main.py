import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Config - Heroku Config Vars-dan oxunur
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
        # Userbot-un axtarış etməsi üçün mütləq asinxron mühitdə (start vəziyyətində) olmalıdır
        async for msg in userbot.search_global(filter="empty"):
            if msg.from_user and msg.from_user.id == target_id:
                name = f"{msg.from_user.first_name} {msg.from_user.last_name or ''}".strip()
                if msg.from_user.username:
                    name += f" (@{msg.from_user.username})"
                found_names.add(f"• {name}")
            
            if len(found_names) >= 15: 
                break
            
        if found_names:
            await m.edit(f"✅ **ID `{target_id}` üçün tapılanlar:**\n\n" + "\n".join(found_names))
        else:
            await m.edit("❌ Arxivdə heç nə tapılmadı.")
    except Exception as e:
        await m.edit(f"Xəta: {e}")

# --- ƏSAS HİSSƏ (XƏTANI DÜZƏLDƏN YER) ---
async def main():
    print("🚀 Botlar başladılır...")
    await userbot.start()
    await bot.start()
    print("✅ Bot və Userbot uğurla işə düşdü!")
    # Botun sönməməsi üçün sonsuz döngüdə saxlayırıq
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Bu metod həm Heroku-da, həm də yeni Python versiyalarında loop xətasını 100% həll edir
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except Exception as e:
        print(f"Kritik xəta: {e}")
        # Alternativ başlama metodu
        asyncio.run(main())
