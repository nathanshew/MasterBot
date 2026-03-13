from telegram.ext import CommandHandler


async def hi(update, context):
    await update.message.reply_text("Hello Newest")


def register(app):
    app.add_handler(CommandHandler("hi", hi))
