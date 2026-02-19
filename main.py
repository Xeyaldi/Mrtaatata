import os
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.raw import functions

# Config Vars (Heroku-da mütləq qeyd olunmalıdır)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Müştəriləri yaradırıq
bot = Client("bot_service", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("user_service", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.command("start") & filters.private)
async def start(c, m):
    await m.reply_text("🕵️ **Pro-Arxiv Detektoru Hazırdır!**\n\nİstifadəçi ID-sini göndərin, mən isə Userbot vasitəsilə daxili arxivləri skan edim.")

@bot.on_message(filters.text & filters.private & ~filters.command("start"))
async def deep_scan(c, m):
    if not m.text.isdigit():
        return await m.reply_text("❌ Zəhmət olmasa düzgün bir **ID** göndərin.")
    
    uid = int(m.text)
    status = await m.reply_text("📡 **Userbot serverlərə sızır...**")

    try:
        # Userbot ilə daxili məlumatları çəkirik
        peer = await userbot.resolve_peer(uid)
        full_user = await userbot.invoke(functions.users.GetFullUser(id=peer))
        
        user_obj = full_user.users[0]
        about = full_user.full_user.about if full_user.full_user.about else "Məxfidir"
        
        res = (
            f"👤 **Ad:** `{user_obj.first_name}`\n"
            f"🆔 **ID:** `{user_obj.id}`\n"
            f"📝 **Bio:** `{about}`\n"
            "──────────────────\n"
            "📜 **Server Tarixçəsi:**\n"
            "✅ _Peer analizi tamamlandı._\n"
            "✅ _Access Hash uğurla alındı._"
        )
        await status.edit_text(res)
    except Exception as e:
        await status.edit_text(f"❌ **Xəta baş verdi:** {str(e)}")

async def run_bot():
    # Hər iki müştərini işə salırıq
    await bot.start()
    await userbot.start()
    print("🚀 Bot və Userbot eyni anda aktivdir!")
    # Proqramın sönməməsi üçün idle (gözləmə) rejiminə keçirik
    await idle()
    # Sönəndə müştəriləri təhlükəsiz bağlayırıq
    await bot.stop()
    await userbot.stop()

if __name__ == "__main__":
    # Event loop-u birbaşa işə salırıq
    asyncio.get_event_loop().run_until_complete(run_bot())
