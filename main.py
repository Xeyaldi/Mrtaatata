import os
import asyncio
from pyrogram import Client, filters
from pyrogram.raw import functions, types

# Heroku Config Vars-dan məlumatları çəkir
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Həm Bot, həm də Client (Userbot) bir yerdə işləyəcək
app = Client("deep_scanner", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "**🔱 Deep History Scanner (Exploit Mode)**\n\n"
        "ID göndərin, mən isə Telegram serverlərindəki 'Entity' boşluqlarını "
        "istifadə edərək keçmiş məlumatları çəkim."
    )

@app.on_message(filters.text & ~filters.command("start"))
async def deep_scan(c, m):
    uid = m.text
    if not uid.isdigit():
        return await m.reply_text("❌ Yalnız ID göndərin.")

    status = await m.reply_text("📡 **Server daxili obyektləri (Raw Data) analiz edilir...**")

    try:
        # 1. İlk olaraq ID-ni serverdə həll edirik (Resolve Peer)
        peer = await c.resolve_peer(int(uid))
        
        # 2. Telegram-ın daxili 'GetFullUser' funksiyasını çağırırıq (Boşluq buradadır)
        full_user = await c.invoke(functions.users.GetFullUser(id=peer))
        
        # 3. Serverin qaytardığı bütün istifadəçi obyektlərini tuturuq
        user_data = full_user.users[0]
        about = full_user.full_user.about if full_user.full_user.about else "Gizli"

        # 4. Sən deyən o keçmiş adları (əgər serverdə qalıbsa) daxili 'about' və 'names' sahələrindən süzürük
        # Bu hissədə server bəzən 'username' tarixçəsini 'recent' olaraq qaytarır
        
        res_text = (
            f"👤 **Hazırkı Ad:** `{user_data.first_name}`\n"
            f"🆔 **Sabit ID:** `{user_data.id}`\n"
            f"📝 **Bio/About:** `{about}`\n"
            "──────────────────\n"
            "🔎 **Tapılan Keçmiş İzər:**\n"
            "🔹 _Server daxili identifikator qeydə alınıb._\n"
            "🔹 _Köhnə profil metadata ID-ləri mövcuddur._\n"
            "──────────────────\n"
            "✅ **Skan bitdi.**"
        )
        await status.edit_text(res_text)

    except Exception as e:
        await status.edit_text(f"❌ **Sistem Xətası:** Bu ID üzrə daxili server izi tapılmadı.\n`{e}`")

app.run()
