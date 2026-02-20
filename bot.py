import os, asyncio, sqlite3, datetime
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIG ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

# --- DATABASE SETUP ---
db = sqlite3.connect("mega_archive.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, history TEXT, last_name TEXT)")
db.commit()

bot = Client("master_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("master_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# Müvəqqəti yaddaş (SangMata-dan gələn qorumalı mesajı tutmaq üçün)
found_data = {}

# --- SANGMATA-DAN GƏLƏN MESAJI HAVADA TUTMAQ ---
@userbot.on_message(filters.chat("SangMata_BOT"))
async def catch_protected_msg(c, m):
    text = m.text or m.caption
    if text:
        for uid in found_data.keys():
            if str(uid) in text or "Name" in text:
                found_data[uid] = text
                break

# --- START MESAJI (Yalnız düymə ilə) ---
@bot.on_message(filters.command("start"))
async def start_handler(c, m):
    btn = InlineKeyboardMarkup([[
        InlineKeyboardButton("➕ Məni Qrupunuza Əlavə Edin", url=f"https://t.me/{(await c.get_me()).username}?startgroup=true")
    ]])
    await m.reply_text("**🔱 Sistem Aktivdir.**", reply_markup=btn)

# --- QRUPDA AD İZLƏMƏ ---
@bot.on_message(filters.group & ~filters.service & ~filters.command(["axdar", "start"]))
async def group_monitor(c, m):
    if m.from_user:
        uid = m.from_user.id
        name = f"{m.from_user.first_name} {m.from_user.last_name or ''}".strip()
        cursor.execute("SELECT last_name FROM users WHERE uid=?", (uid,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO users (uid, history, last_name) VALUES (?, ?, ?)", (uid, f"📍 {name}", name))
        elif row[0] != name:
            cursor.execute("UPDATE users SET history=history || ?, last_name=? WHERE uid=?", (f"\n└ {name}", name, uid))
        db.commit()

# --- ƏSAS SKANER (/axdar komandası) ---
@bot.on_message((filters.command("axdar") | (filters.private & (filters.text | filters.forwarded))) & ~filters.command("start"))
async def master_scan(c, m):
    target_id = None
    if m.forward_from: target_id = str(m.forward_from.id)
    else:
        args = m.command if m.command else m.text.split()
        if len(args) > 0:
            query = args[1] if m.command and len(args) > 1 else args[0]
            if query.replace("-", "").isdigit(): target_id = query
            elif query.startswith("@"):
                try:
                    u = await userbot.get_users(query)
                    target_id = str(u.id)
                except: return
    
    if not target_id: return
    status = await m.reply_text("📡 **Sinxronizasiya edilir...**")
    
    try:
        u_info = await userbot.get_users(int(target_id))
        c_name = f"{u_info.first_name} {u_info.last_name or ''}".strip()

        uid_int = int(target_id)
        found_data[uid_int] = None
        await userbot.send_message("SangMata_BOT", target_id)
        
        for _ in range(10): # 10 saniyə gözləmə
            if found_data[uid_int]: break
            await asyncio.sleep(1)
            
        global_history = found_data[uid_int] or "❌ Arxivdən məlumat çəkilə bilmədi."
        del found_data[uid_int]

        cursor.execute("SELECT history FROM users WHERE uid=?", (uid_int,))
        db_data = cursor.fetchone()
        local_display = db_data[0] if db_data else "İz tapılmadı."

        final_text = (
            f"👤 **AD:** `{c_name}`\n🆔 **ID:** `{target_id}`\n"
            "──────────────────────\n"
            f"```{global_history}```\n"
            "──────────────────────\n"
            f"📂 **Lokal:** _{local_display}_"
        )
        await status.edit_text(final_text)
    except:
        await status.edit_text("⚠️ **Xəta.**")

async def main():
    await bot.start(); await userbot.start(); await idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
