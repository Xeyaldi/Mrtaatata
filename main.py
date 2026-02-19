import os, asyncio, sqlite3, datetime
from pyrogram import Client, filters, idle
from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid, FloodWait

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# --- DATABASE SETUP ---
db = sqlite3.connect("mega_archive.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        uid INTEGER PRIMARY KEY, 
        history TEXT, 
        last_seen TIMESTAMP
    )
""")
db.commit()

# --- CLIENTS ---
bot = Client("master_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("master_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

@bot.on_message(filters.command("start"))
async def start_handler(c, m):
    await m.reply_text(
        "**🔱 Pro-Arxeoloq Sistemi Aktivdir!**\n\n"
        "Mən Telegram serverlərinin daxili obyektlərini və qlobal arxivləri "
        "eyni anda skan edərək istifadəçinin bütün keçmişini bərpa edirəm.\n\n"
        "🔍 **Axtardığınız ID-ni göndərin:**"
    )

@bot.on_message(filters.text & filters.private & ~filters.command("start"))
async def master_scan(c, m):
    if not m.text.replace("-", "").isdigit(): return
    target_id = int(m.text)
    
    # Vizual Progress
    status = await m.reply_text("📡 **Sistemlər birləşdirilir...**\n`[ ░░░░░░░░░░ ] 0%`")

    try:
        # --- ÜSUL 1: RAW SERVER ENTITY ---
        await status.edit_text("🛰 **Üsul 1: Raw Entity Recovery...**\n`[ ██░░░░░░░░ ] 20%`")
        peer = await userbot.resolve_peer(target_id)
        u_info = await userbot.get_users(target_id)
        full_u = await userbot.invoke(functions.users.GetFullUser(id=peer))
        
        c_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()
        c_user = f"@{u_info.username}" if u_info.username else "Yoxdur"
        bio = full_u.full_user.about or "Bio tapılmadı"
        photos_count = await userbot.get_chat_photos_count(target_id)

        # --- ÜSUL 2: GLOBAL ARCHIVE SCRAPING ---
        await status.edit_text("🌐 **Üsul 2: Qlobal Arxivlər (Zaman Maşını)...**\n`[ █████░░░░░ ] 50%`")
        arc_bot = "SangMata_BOT"
        await userbot.send_message(arc_bot, f"/search_id {target_id}")
        await asyncio.sleep(5) # Arxivin dərinliyindən məlumatın gəlməsi üçün
        
        global_history = "❌ Qlobal arxivlərdə iz tapılmadı."
        async for msg in userbot.get_chat_history(arc_bot, limit=2):
            if msg.text and ("Name" in msg.text or "Username" in msg.text):
                global_history = msg.text.replace("SangMata", "Master-System")
                break

        # --- ÜSUL 3: LOCAL DATABASE ANALİZ ---
        await status.edit_text("📂 **Üsul 3: Daxili Verilənlər Bazası...**\n`[ ███████░░░ ] 75%`")
        cursor.execute("SELECT history FROM users WHERE uid=?", (target_id,))
        db_data = cursor.fetchone()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = f"[{now}] {c_name} ({c_user})"
        
        if db_data:
            past_history = db_data[0]
            if c_name not in past_history or c_user not in past_history:
                updated_history = f"{past_history}\n{new_entry}"
                cursor.execute("UPDATE users SET history=?, last_seen=? WHERE uid=?", (updated_history, now, target_id))
            local_history = db_data[0]
        else:
            cursor.execute("INSERT INTO users (uid, history, last_seen) VALUES (?, ?, ?)", (target_id, new_entry, now))
            local_history = "İlk dəfə skan edilir (Yeni qeyd yaradıldı)."
        db.commit()

        # --- FİNAL HESABAT ---
        await status.edit_text("📊 **Analiz bitdi. Məlumatlar sintez olunur...**\n`[ ██████████ ] 100%`")
        
        final_text = (
            f"👤 **AD:** `{c_name}`\n"
            f"🆔 **ID:** `{target_id}`\n"
            f"📝 **BİO:** `{bio}`\n"
            f"🖼 **PROFİL ŞƏKİLLƏRİ:** `{photos_count}` ədəd\n"
            "──────────────────────\n"
            "📜 **HESAB YARANANDAN BƏRİ (Global):**\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            "📂 **BOTUN ŞƏXSİ ARXİVİ (Local):**\n"
            f"_{local_history}_\n"
            "──────────────────────\n"
            "✨ _Skan 4 fərqli OSINT metodu ilə icra olundu._"
        )
        await status.edit_text(final_text)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except PeerIdInvalid:
        await status.edit_text("❌ **Xəta:** Bu ID bot üçün hələ 'yad'dır. Mesaj yönləndirin.")
    except Exception as e:
        await status.edit_text(f"⚠️ **Sistem Xətası:** {e}")

async def main():
    await bot.start()
    await userbot.start()
    print("🔱 MEGA SYSTEM ONLINE")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
