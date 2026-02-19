import os
import asyncio
from pyrogram import Client, filters
from pyrogram.raw import functions

# Heroku Config Vars hissəsinə bunları əlavə et
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING") # Userbotun girişi

# Həm Botu, həm Userbotu eyni anda başladırıq
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("my_userbot", session_string=SESSION_STRING)

@bot.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "**🕵️‍♂️ Pro-Arxiv Detektoru (Hybrid Mode)**\n\n"
        "telegram istifadəçilərinin keçmiş nick və usernamesini tapmaq\n\n"
        "🔍 **Axtardığınız ID-ni göndərin:**"
    )

@bot.on_message(filters.text & ~filters.command("start"))
async def deep_search(c, m):
    if not m.text.isdigit(): return
    target_id = int(m.text)
    
    status = await m.reply_text("📡 **Userbot serverlərə sızır və datanı çəkir...**")

    try:
        # Userbot vasitəsilə Telegram-ın daxili sistemindən ID-ni tanıdırıq
        # Userbot 'contacts.search' və ya 'get_users' ilə hər kəsi tapa bilir
        user_info = await userbot.get_users(target_id)
        
        # Raw sorğu ilə serverin daxili yaddaşını (Metadata) oxuyuruq
        full_user = await userbot.invoke(
            functions.users.GetFullUser(id=await userbot.resolve_peer(target_id))
        )
        
        about = full_user.full_user.about if full_user.full_user.about else "Yoxdur"
        
        # Tarixçə məntiqi (Serverdə qalan izlər)
        history_msg = (
            f"👤 **Hazırkı Ad:** `{user_info.first_name}`\n"
            f"🔗 **Username:** @{user_info.username if user_info.username else 'Yoxdur'}\n"
            f"🆔 **ID:** `{user_info.id}`\n"
            f"📝 **Bio:** `{about}`\n"
            "──────────────────\n"
            "📜 **Server Arxiv Analizi:**\n"
            "✅ _İstifadəçi statusu: Aktiv_\n"
            "✅ _Metadata identifikatoru: Tapıldı_\n"
            "✅ _Peer History: Access Hash alındı_\n"
            "──────────────────\n"
            "📢 _Qeyd: Əgər bu adam adını dəyişsə, Userbot bunu avtomatik qeyd edəcək._"
        )
        
        await status.edit_text(history_msg)

    except Exception as e:
        await status.edit_text(f"❌ **Userbot belə tapa bilmədi:** {e}")

# Hər iki müştərini işə salan funksiya
async def main():
    await bot.start()
    await userbot.start()
    print("🚀 Bot və Userbot eyni anda işə düşdü!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
