from telegram.ext import CommandHandler


async def hi(update, context):
    await update.message.reply_text("I am up!")


def register(app):
    app.add_handler(CommandHandler("heartbeat", hi))
