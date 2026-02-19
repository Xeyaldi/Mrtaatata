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

# --- START MESAJI (Qrup və Şəxsi) ---
@bot.on_message(filters.command("start"))
async def start_handler(c, m):
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ Məni Qrupunuza Əlavə Edin", url=f"https://t.me/{(await c.get_me()).username}?startgroup=true")
    ]])
    text = (
        "**🔱 Pro-Arxeoloq Sistemi Aktivdir!**\n\n"
        "Skan etmək üçün:\n"
        "🔹 **Şəxsi çatda:** Birbaşa ID, @username və ya mesaj yönləndirin.\n"
        "🔹 **Qruplarda:** `/axdar ID` və ya `@username` yazın.\n\n"
        "📢 **Məni qrupunuza əlavə edib admin etsəniz, ordakı hər kəsin ad dəyişikliyini anlıq qeyd edərəm!**"
    )
    await m.reply_text(text, reply_markup=btn)

# --- COMBOT METODU: QRUPLARI İZLƏMƏK (AVTOMATİK) ---
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
            db.commit()
        elif row[0] != name:
            cursor.execute("UPDATE users SET history=history || ?, last_name=?, last_seen=? WHERE uid=?", 
                         (f"\n└ [{now}] Ad dəyişdi: {name}", name, now, uid))
            db.commit()

# --- ƏSAS SKANER (ID, Username, Forward və /axdar komandası) ---
@bot.on_message((filters.command("axdar") | (filters.private & (filters.text | filters.forwarded))) & ~filters.command("start"))
async def master_scan(c, m):
    target_id = None

    # 1. Forwarded mesajdan ID götürmək
    if m.forward_from:
        target_id = str(m.forward_from.id)
    
    # 2. Komanda və ya mətn daxilindən ID/Username tapmaq
    else:
        args = m.command if m.command else m.text.split()
        if len(args) > 1 and m.command: # /axdar 12345
            query = args[1]
        elif not m.command: # Şəxsi çatda birbaşa yazılan
            query = args[0]
        else:
            return await m.reply_text("ℹ️ **İstifadə:** `/axdar 12345` və ya `/axdar @username`")

        if query.replace("-", "").isdigit():
            target_id = query
        elif query.startswith("@"):
            try:
                tmp = await userbot.get_users(query)
                target_id = str(tmp.id)
            except:
                return await m.reply_text("❌ Username tapılmadı.")
        else:
            return

    status = await m.reply_text("📡 **Bütün arxivlər sinxronizasiya edilir...**")

    try:
        # --- ÜSUL 1: SERVER ENTITY ---
        u_info = await userbot.get_users(int(target_id))
        c_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()
        
        # --- ÜSUL 2: SANGMATA (PRYAMOY SORĞU) ---
        arc_bot = "SangMata_BOT"
        await userbot.send_message(arc_bot, target_id)
        await asyncio.sleep(6) 
        
        global_history = "❌ Qlobal arxivdə keçmiş iz tapılmadı."
        async for msg in userbot.get_chat_history(arc_bot, limit=3):
            if msg.text and (target_id in msg.text or "Name" in msg.text):
                global_history = msg.text.replace("SangMata", "Pro-Arxeoloq")
                break

        # --- ÜSUL 3: LOCAL DB ---
        cursor.execute("SELECT history FROM users WHERE uid=?", (int(target_id),))
        db_data = cursor.fetchone()
        local_display = db_data[0] if db_data else "Bot bu adamı ilk dəfə görür (Lokal qeyd yoxdur)."

        # --- FİNAL HESABAT ---
        final_text = (
            f"👤 **AD:** `{c_name}`\n"
            f"🆔 **ID:** `{target_id}`\n"
            "──────────────────────\n"
            "📜 **HESAB YARANANDAN BƏRİ (Global):**\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            "📂 **BOTUN QRUPLARDAN YIĞDIĞI (Local):**\n"
            f"_{local_display}_\n"
            "──────────────────────\n"
            "✨ _Deep Scan: Forward + Group Tracker + OSINT_"
        )
        await status.edit_text(final_text)

    except Exception as e:
        await status.edit_text(f"⚠️ **Xəta:** Məlumat çəkilə bilmədi. (ID səhv ola bilər)")

async def main():
    await bot.start()
    await userbot.start()
    print("🚀 Mega Detektor Qruplarda İşləməyə Hazırdır!")
    await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
