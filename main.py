import os, asyncio, sqlite3, datetime
from pyrogram import Client, filters, idle
from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ Məni Qrupunuza Əlavə Edin", url=f"https://t.me/{(await c.get_me()).username}?startgroup=true")
    ]])
    await m.reply_text(
        "**🔱 Pro-Arxeoloq Sistemi Aktivdir!**\n\n"
        "Skan etmək üçün:\n"
        "1️⃣ İstifadəçi ID-si yazın\n"
        "2️⃣ @username yazın\n"
        "3️⃣ Başqasından bota mesaj yönləndirin\n\n"
        "📢 **Məni qrupunuza əlavə etsəniz, ordakı dəyişiklikləri də arxivləyərəm!**",
        reply_markup=btn
    )

# --- COMBOT METODU: QRUPLARI İZLƏMƏK ---
@bot.on_message(filters.group & ~filters.service)
async def group_monitor(c, m):
    if m.from_user:
        uid = m.from_user.id
        name = f"{m.from_user.first_name} {m.from_user.last_user or ''}".strip()
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

# --- ƏSAS SKANER (ID, Username, Forward) ---
@bot.on_message((filters.text | filters.forwarded) & filters.private & ~filters.command("start"))
async def master_scan(c, m):
    # ID-ni müəyyən etmək
    if m.forward_from:
        target_id = str(m.forward_from.id)
    elif m.text.startswith("@"):
        try:
            tmp = await userbot.get_users(m.text)
            target_id = str(tmp.id)
        except:
            return await m.reply_text("❌ Username tapılmadı.")
    elif m.text.replace("-", "").isdigit():
        target_id = m.text
    else:
        return

    status = await m.reply_text("📡 **Sinxronizasiya edilir...**\n`[ ░░░░░░░░░░ ] 0%`")

    try:
        # --- ÜSUL 1: SERVER ENTITY ---
        peer = await userbot.resolve_peer(int(target_id))
        u_info = await userbot.get_users(int(target_id))
        full_u = await userbot.invoke(functions.users.GetFullUser(id=peer))
        
        c_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()
        bio = full_u.full_user.about or "Bio tapılmadı"

        # --- ÜSUL 2: SANGMATA (PRYAMOY SORĞU) ---
        arc_bot = "SangMata_BOT"
        await userbot.send_message(arc_bot, target_id) # Heç bir command yoxdur, birbaşa ID
        await asyncio.sleep(6) 
        
        global_history = "❌ Qlobal arxivdə iz tapılmadı."
        async for msg in userbot.get_chat_history(arc_bot, limit=3):
            if msg.text and (target_id in msg.text or "Name" in msg.text):
                global_history = msg.text.replace("SangMata", "Master-System")
                break

        # --- ÜSUL 3: LOCAL DB ---
        cursor.execute("SELECT history FROM users WHERE uid=?", (int(target_id),))
        db_data = cursor.fetchone()
        local_display = db_data[0] if db_data else "Bot bu adamı ilk dəfə görür."

        # --- FİNAL HESABAT ---
        final_text = (
            f"👤 **AD:** `{c_name}`\n"
            f"🆔 **ID:** `{target_id}`\n"
            f"📝 **BİO:** `{bio}`\n"
            "──────────────────────\n"
            "📜 **HESAB YARANANDAN BƏRİ (Global):**\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            "📂 **BOTUN QRUPLARDAN YIĞDIĞI (Local):**\n"
            f"_{local_display}_\n"
            "──────────────────────\n"
            "✨ _Skan: Server + Forward + Group Tracker + OSINT_"
        )
        await status.edit_text(final_text)

    except Exception as e:
        await status.edit_text(f"⚠️ **Sistem Xətası:** {e}")

async def main():
    await bot.start()
    await userbot.start()
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
