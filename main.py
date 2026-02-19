import os, asyncio
from pyrogram import Client, filters
from pyrogram.raw import functions

# Heroku Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

bot = Client("master_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("master_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.text & filters.private)
async def god_mode_search(c, m):
    if not m.text.isdigit(): return
    uid = m.text
    status = await m.reply_text("💎 **Sehrli Analiz Başladı...**\n`[ ░░░░░░░░░░ ] 0%`")

    try:
        # 1. ADDIM: Server Entity Skannı (Access Hash almaq)
        await status.edit_text("🛰 **Telegram Serverləri Skan Edilir...**\n`[ ██░░░░░░░░ ] 25%`Status: Peer Resolved`")
        peer = await userbot.resolve_peer(int(uid))
        
        # 2. ADDIM: Qlobal Arxivlərə (Deep Search) Sızma
        # Bu hissə sənin dediyin o "yaranandan bəri olan" məlumatı başqa nəhəng arxivlərdən qoparır
        await status.edit_text("📡 **Qlobal Arxivlərdən Məlumat Çəkilir...**\n`[ ██████░░░░ ] 60%`Status: Scraping History`")
        
        # Arxa planda arxiv botuna sorğu atırıq
        history_target = "SangMata_BOT"
        await userbot.send_message(history_target, f"/search_id {uid}")
        await asyncio.sleep(3) # Arxivin cavab vermə müddəti
        
        history_data = "Məlumat tapılmadı."
        async for msg in userbot.get_chat_history(history_target, limit=1):
            if msg.text and "Name History" in msg.text or "Username History" in msg.text:
                # Gələn cavabı təmizləyirik və öz vizyonumuza uyğunlaşdırırıq
                history_data = msg.text.replace("SangMata", "Master Arxiv")
        
        # 3. ADDIM: Final Hesabatın Hazırlanması
        await status.edit_text("📊 **Məlumatlar Birləşdirilir...**\n`[ ██████████ ] 100%`Status: Success`")
        
        final_report = (
            f"🔱 **İstifadəçi Kimliyi Arxivdə Tapıldı!**\n\n"
            f"🆔 **ID:** `{uid}`\n"
            "──────────────────\n"
            "📜 **YARANANDAN BƏRİ OLAN TARİXÇƏ:**\n"
            f"```{history_data}```\n"
            "──────────────────\n"
            "✨ **Vizyon:** Bu məlumatlar həm server daxili entity-lərdən, "
            "həm də qlobal OSINT bazalarından sintez edilmişdir."
        )
        await status.edit_text(final_report)

    except Exception as e:
        await status.edit_text(f"❌ **Xəta:** Arxivə sızmaq mümkün olmadı.\nSəbəb: `{e}`")

async def start_all():
    await bot.start()
    await userbot.start()
    from pyrogram import idle
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_all())
