import sys, glob, importlib, logging, logging.config, pytz, asyncio, os
from pathlib import Path

# Logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import idle
from info import *
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server

from TechVJ.bot import TechVJBot, TechVJBackUpBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)

# START BOTS
TechVJBot.start()
TechVJBackUpBot.start()

loop = asyncio.get_event_loop()


async def start():
    print('\n🚀 Starting CodeX OTT Stream Bot...\n')

    await initialize_clients()

    # Load plugins
    for name in files:
        patt = Path(name)
        plugin_name = patt.stem
        import_path = f"plugins.{plugin_name}"
        spec = importlib.util.spec_from_file_location(import_path, name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[import_path] = module
        print("✅ Loaded Plugin =>", plugin_name)

    # Ping (optional)
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Restart log message
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    await TechVJBot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(today, time)
    )

    # 🌐 WEB SERVER START (FINAL FIX)
    app = web.AppRunner(await web_server())
    await app.setup()

    bind_address = "0.0.0.0"
    port = int(os.environ.get("PORT", 8080))  # ✅ Render FIX

    await web.TCPSite(app, bind_address, port).start()
    print(f"🌐 Server running on port {port}")

    # KEEP RUNNING
    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('❌ Bot Stopped')