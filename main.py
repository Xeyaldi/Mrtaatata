import os, asyncio, sqlite3
from pyrogram import Client, filters, idle
from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid

# Config (Heroku-da mütləq olmalıdır)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# Database: Botun öz "yaddaşı" üçün
db = sqlite3.connect("master_archive.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS history (uid INTEGER, names TEXT)")
db.commit()

bot = Client("bot_service", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("user_service", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.command("start") & filters.private)
async def start(c, m):
    await m.reply_text(
        "**🔱 Pro-Arxiv Mega Detektor Aktivdir!**\n\n"
        "Mən 4 fərqli üsulla (Server, Global Arxiv, Metadata, Local DB) "
        "istifadəçinin bütün keçmişini analiz edirəm.\n\n"
        "🔍 **Analiz üçün ID göndərin:**"
    )

@bot.on_message(filters.text & filters.private & ~filters.command("start"))
async def mega_search(c, m):
    if not m.text.replace("-", "").isdigit(): return
    uid = int(m.text)
    
    status = await m.reply_text("📡 **Sistemlər birləşdirilir, dərin skan başladı...**\n`[ ░░░░░░░░░░ ] 0%`")

    try:
        # --- ÜSUL 1: Server & Metadata Analizi ---
        await status.edit_text("🛰 **Üsul 1: Server Metadata analizi...**\n`[ ██░░░░░░░░ ] 20%`")
        peer = await userbot.resolve_peer(uid)
        u = await userbot.get_users(uid)
        full = await userbot.invoke(functions.users.GetFullUser(id=peer))
        
        curr_name = f"{u.first_name} {u.last_name or ''}".strip()
        bio = full.full_user.about or "Bio tapılmadı"
        photo_count = await userbot.get_chat_photos_count(uid)

        # --- ÜSUL 2: Qlobal Arxiv Sızması (Zaman Maşını) ---
        await status.edit_text("🌐 **Üsul 2: Qlobal Arxivlərdən (SangMata) məlumat qoparılır...**\n`[ █████░░░░░ ] 50%`")
        archive_bot = "SangMata_BOT"
        await userbot.send_message(archive_bot, f"/search_id {uid}")
        await asyncio.sleep(3.5) # Arxivin cavab verməsi üçün vaxt
        
        global_history = "❌ Qlobal arxivdə keçmiş tapılmadı."
        async for msg in userbot.get_chat_history(archive_bot, limit=1):
            if msg.text and ("Name" in msg.text or "Username" in msg.text):
                global_history = msg.text.replace("SangMata", "Pro-Arxeoloq")

        # --- ÜSUL 3: Şəxsi Verilənlər Bazası ---
        await status.edit_text("📂 **Üsul 3: Botun daxili yaddaşı yoxlanılır...**\n`[ ███████░░░ ] 75%`")
        cursor.execute("SELECT names FROM history WHERE uid=?", (uid,))
        db_res = cursor.fetchone()
        
        if not db_res:
            cursor.execute("INSERT INTO history (uid, names) VALUES (?, ?)", (uid, curr_name))
            local_history = "Bu ID bot tərəfindən ilk dəfə skan edilir."
        else:
            local_history = db_res[0]
            if curr_name not in local_history:
                new_history = f"{local_history} -> {curr_name}"
                cursor.execute("UPDATE history SET names=? WHERE uid=?", (new_history, uid))
        db.commit()

        # --- FİNAL HESABAT ---
        await status.edit_text("📊 **Analiz tamamlandı. Hesabat hazırlanır...**\n`[ ██████████ ] 100%`")
        
        report = (
            f"👤 **AD:** `{curr_name}`\n"
            f"🆔 **ID:** `{uid}`\n"
            f"📝 **BİO:** `{bio}`\n"
            f"🖼 **PROFİL ŞƏKİLLƏRİ:** `{photo_count}` ədəd\n"
            "──────────────────────\n"
            "📜 **QLOBAL TARİXÇƏ (Bütün dövrlər):**\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            "📂 **BOTUN ŞƏXSİ ARXİVİ:**\n"
            f"_{local_history}_\n"
            "──────────────────────\n"
            "✨ _Skan 4 fərqli OSINT metodu ilə icra olundu._"
        )
        await status.edit_text(report)

    except PeerIdInvalid:
        await status.edit_text("❌ **Xəta:** Bot bu ID-ni tanımır. İstifadəçinin bir mesajını bota yönləndirin.")
    except Exception as e:
        await status.edit_text(f"⚠️ **Sistem Xətası:** {e}")

async def run_services():
    await bot.start()
    await userbot.start()
    print("🚀 Mega Detektor uçuşa hazırdır!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_services())
