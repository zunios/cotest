import os
import io
import asyncio
import functions_framework
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from .process_image import process_image

# Токен берем из переменных среды
TOKEN = os.environ.get('TELEGRAM_TOKEN')

async def handle_any(update, context):
    if not update.message:
        return
        
    if update.message.document:
        print("doc")
        doc = update.message.document
        file = await doc.get_file()
    elif update.message.photo:
        print("photo")
        photo = update.message.photo[-1]
        file = await photo.get_file()
    elif (sticker := update.message.sticker) and not sticker.is_animated and not sticker.is_video:
        print("sticker / lifted image")
        file = await sticker.get_file()
    else:
        await update.message.reply_text("Unsupported input type.")
        return

    data = io.BytesIO(await file.download_as_bytearray())
    composed = process_image(data)
    output = io.BytesIO()
    composed.save(output, format="PNG")
    output.seek(0)
    await update.message.reply_photo(photo=output)

async def process_update(request_json):
    """Инициализируем локальное приложение под конкретный запрос"""
    # Создаем экземпляр строго внутри асинхронного цикла
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_any))
    
    async with app:
        # Инициализируем внутренние компоненты PTB
        await app.initialize()
        update = Update.de_json(data=request_json, bot=app.bot)
        await app.process_update(update)
        await app.shutdown()

@functions_framework.http
def telegram_webhook(request):
    """Главный HTTP-обработчик для Google Cloud Run"""
    if request.method == "POST":
        request_json = request.get_json(silent=True)
        if request_json:
            # Запускаем обработку события в изолированном цикле
            asyncio.run(process_update(request_json))
            
    return 'ok', 200
