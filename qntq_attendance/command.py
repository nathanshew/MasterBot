import traceback
from telegram.ext import CommandHandler


def register(app, checker):
    async def query(update, context):
        await update.message.reply_text("Running attendance check...")
        try:
            await checker.run(force=True)
        except Exception:
            await update.message.reply_text(f"Error:\n```\n{traceback.format_exc()}\n```", parse_mode='Markdown')

    app.add_handler(CommandHandler("queryOpenJio", query))
