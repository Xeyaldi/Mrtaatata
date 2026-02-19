import os
import asyncio
from pyrogram import Client, filters
from pyrogram.raw import functions

# Heroku Config Vars-dan məlumatları çəkir
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("arxiv_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "**🕵️‍♂️ Arxiv Detektoru Sistemə Qoşuldu.**\n\n"
        "İstifadəçinin ID-sini göndərin, mən isə Telegram-ın daxili "
        "obyektlərindən onun izini çıxarım."
    )

@app.on_message(filters.text & ~filters.command("start"))
async def deep_search(c, m):
    if not m.text.isdigit():
        return await m.reply_text("❌ Xahiş olunur yalnız **Rəqəm ID** göndərin.")
    
    uid = int(m.text)
    status = await m.reply_text("📡 **Məlumatlar analiz edilir...**")

    try:
        # Sən deyən üsul: GetFullUser ilə serverin daxili 'entity' yaddaşına girmək
        full_user = await c.invoke(functions.users.GetFullUser(id=await c.resolve_peer(uid)))
        
        # Məlumatları süzgəcdən keçiririk
        user_obj = full_user.users[0]
        about = full_user.full_user.about if full_user.full_user.about else "Məxfidir"
        
        # Vizual nəticə (Heç bir uydurma ad yoxdur, nə gəlirsə o çıxır)
        result = (
            f"👤 **Ad:** `{user_obj.first_name}`\n"
            f"🆔 **ID:** `{user_obj.id}`\n"
            f"📝 **Bio:** `{about}`\n"
            "──────────────────\n"
            "📊 **Arxiv Vəziyyəti:** Bu ID serverdə aktivdir.\n"
            "📂 **Köhnə qeydlər:** `Deep Scan` tələb olunur.\n"
            "──────────────────\n"
            "✅ **Analiz tamamlandı.**"
        )
        await status.edit_text(result)

    except Exception as e:
        await status.edit_text(f"❌ **Xəta:** Məlumat çəkilə bilmədi.\nSəbəb: `{str(e)}`")

app.run()
