from telegram.ext import CommandHandler


def register(app, checker):
    async def query(update, context):
        await update.message.reply_text("Running attendance check...")
        await checker.run(force=True)

    app.add_handler(CommandHandler("queryOpenJio", query))
