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
        last_name TEXT,
        last_seen TIMESTAMP
    )
""")
db.commit()

bot = Client("master_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("master_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- START MESAJI ---
@bot.on_message(filters.command("start"))
async def start_handler(c, m):
    text = (
        "**🔱 Pro-Arxeoloq Sistemi Aktivdir!**\n\n"
        "Bütün üsullarla axtarış:\n"
        "🔹 **Şəxsi:** ID, @username və ya forward.\n"
        "🔹 **Qrupda:** `/axdar ID` və ya `/axdar @username` yazın.\n\n"
        "🔍 _Sistem hər yerdə axtarır..._"
    )
    await m.reply_text(text)

# --- QRUPLARI İZLƏMƏK (BÜTÜN QRUPLARDA ANLIQ QEYD) ---
@bot.on_message(filters.group & ~filters.service & ~filters.command(["axdar", "start"]))
async def group_monitor(c, m):
    if m.from_user:
        uid = m.from_user.id
        name = f"{m.from_user.first_name} {m.from_user.last_name or ''}".strip()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute("SELECT last_name FROM users WHERE uid=?", (uid,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (uid, history, last_name, last_seen) VALUES (?, ?, ?, ?)", 
                         (uid, f"📍 İlk dəfə qrupda görüldü: {name}", name, now))
        elif row[0] != name:
            cursor.execute("UPDATE users SET history=history || ?, last_name=?, last_seen=? WHERE uid=?", 
                         (f"\n└ [{now}] Ad dəyişdi: {name}", name, now, uid))
        db.commit()

# --- ƏSAS MAKSİMUM SKANER ---
@bot.on_message((filters.command("axdar") | (filters.private & (filters.text | filters.forwarded))) & ~filters.command("start"))
async def master_scan(c, m):
    target_id = None
    if m.forward_from:
        target_id = str(m.forward_from.id)
    else:
        args = m.command if m.command else m.text.split()
        if len(args) > 1 and m.command: query = args[1]
        elif not m.command: query = args[0]
        else: return

        if query.replace("-", "").isdigit(): target_id = query
        elif query.startswith("@"):
            try:
                tmp = await userbot.get_users(query)
                target_id = str(tmp.id)
            except: return await m.reply_text("❌ Bu username tapılmadı.")
        else: return

    # 🔥 HAVALI VİZUAL SKAN PROSESİ
    status = await m.reply_text("📡 **Bütün şəbəkələr sinxronizasiya edilir...**\n`[ ░░░░░░░░░░ ] 0%`")
    await asyncio.sleep(0.5)

    try:
        # 🛰 ÜSUL 1: RAW SERVER ENTITY
        await status.edit_text("🛰 **Üsul 1: Server qalıqları qazılır...**\n`[ ██░░░░░░░░ ] 20%`")
        u_info = await userbot.get_users(int(target_id))
        c_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()
        
        # 🌐 ÜSUL 2: GLOBAL ARCHIVE SCRAPE (SANGMATA BYPASS)
        await status.edit_text("🌐 **Üsul 2: Qlobal arxivlərə sızılır...**\n`[ █████░░░░░ ] 50%`")
        arc_bot = "SangMata_BOT"
        await userbot.send_message(arc_bot, target_id)
        await asyncio.sleep(7) 
        
        global_history = "❌ Qlobal arxivdə heç bir iz tapılmadı."
        async for msg in userbot.get_chat_history(arc_bot, limit=5):
            if msg.from_user and msg.from_user.username == arc_bot:
                if msg.text or msg.caption:
                    global_history = (msg.text or msg.caption).replace("SangMata", "Pro-System")
                    break

        # 📂 ÜSUL 3: LOKAL BAZA (BOTUN ÖZ QRUPLARI)
        await status.edit_text("📂 **Üsul 3: Lokal baza təhlil edilir...**\n`[ ███████░░░ ] 75%`")
        cursor.execute("SELECT history FROM users WHERE uid=?", (int(target_id),))
        db_data = cursor.fetchone()
        local_display = db_data[0] if db_data else "Bu ID hələ botun olduğu heç bir qrupda görünməyib."

        # ✅ FİNAL VİZUAL
        await status.edit_text("📊 **Analiz bitdi. Məlumatlar paketlənir...**\n`[ ██████████ ] 100%`")
        await asyncio.sleep(0.5)

        final_text = (
            f"👤 **AD:** `{c_name}`\n"
            f"🆔 **ID:** `{target_id}`\n"
            "──────────────────────\n"
            "📜 **ARXİV TARİXÇƏSİ (Global):**\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            "📂 **BOTUN ÖZ ARXİVİ (Local):**\n"
            f"_{local_display}_\n"
            "──────────────────────\n"
            "✨ _Deep OSINT Metodu Tamamlandı._"
        )
        await status.edit_text(final_text)

    except Exception:
        await status.edit_text("⚠️ **Xəta: Məlumat çəkilə bilmədi.**")

async def main():
    await bot.start(); await userbot.start(); print("🚀 SİSTEM ONLAYN!"); await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
