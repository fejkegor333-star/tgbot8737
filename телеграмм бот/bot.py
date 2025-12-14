import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# Импортируем наши функции обработки изображений
from image_processor import improve_image, simple_sharpen, get_image_info

# ВАЖНО: Вставьте сюда ваш токен
TOKEN = "8599657970:AAGWTeBW20GFFRn2357RG0TjxAA5Zv1ZJ4g"  # ВАШ ТОКЕН ЗДЕСЬ

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение при первом запуске"""
    
    user = update.effective_user
    
    # Создаем большую кнопку "Начать"
    keyboard = [
        [KeyboardButton("🚀 НАЧАТЬ РАБОТУ")],
        [KeyboardButton("📖 Как это работает?")],
        [KeyboardButton("⚙️ Настройки")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    # Приветственное сообщение
    welcome_text = f"""
    👋 *Приветствую, {user.first_name}!*

    🖼️ *Добро пожаловать в Image Sharpener Bot!*
    
    *Я — ваш личный помощник для улучшения качества изображений.*
    
    ⚡ *Что я умею:*
    • Увеличивать резкость размытых фото
    • Улучшать контраст и яркость
    • Убирать цифровой шум
    • Автоматически обрабатывать любое изображение
    
    🎯 *Просто отправьте мне фото — я сделаю его лучше!*
    
    *Чтобы начать, нажмите кнопку ниже* 👇
    """
    
    # Отправляем фото-приветствие (опционально)
    try:
        # Можно добавить приветственное изображение
        await update.message.reply_photo(
            photo="https://i.imgur.com/example.jpg",  # Замените на свою картинку или удалите эту строку
            caption=welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    except:
        # Если нет фото, отправляем просто текст
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    # Сохраняем, что пользователь видел приветствие
    context.user_data['first_time'] = False
async def how_it_works(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Объяснение работы бота"""
    
    explanation = """
    🤖 *Как работает бот?*
    
    *Процесс обработки:*
    
    1. *Получение изображения* — вы отправляете фото
    2. *Анализ* — бот определяет тип размытия
    3. *Обработка* — применяются алгоритмы улучшения:
       - **Фильтр Винера** — для движения камеры
       - **Unsharp Mask** — для общей резкости
       - **CLAHE** — для контраста
       - **Шумоподавление** — чистка изображения
    4. *Результат* — возвращается улучшенная версия
    
    🧠 *Используемые технологии:*
    • OpenCV — компьютерное зрение
    • NumPy — математические вычисления
    • Pillow — работа с изображениями
    
    ⏱️ *Время обработки:*
    • Быстрый режим: 2-5 секунд
    • Качественный режим: 5-15 секунд
    
    *Результат гарантирован!* 😊
    """
    
    await update.message.reply_text(
        explanation,
        parse_mode='Markdown'
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    *Помощь по использованию бота:*
    
    📤 *Отправьте изображение* - бот автоматически обработает его
    
    ⚙️ *Режимы обработки:*
    • Стандартный режим (по умолчанию)
    • Быстрый режим
    
    ⚠️ *Ограничения:*
    • Максимальный размер: 20MB
    • Форматы: JPG, PNG, JPEG
    • Время обработки: 5-15 секунд
    
    Проблемы? Попробуйте:
    1. Отправить другое изображение
    2. Подождать несколько секунд
    3. Проверить размер файла
    
    Для выбора режима используйте /mode
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Команда /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = """
    *Информация о проекте:*
    
    🤖 *Image Sharpener Bot*
    Версия: 1.0
    
    *Цель проекта:* 
    Разработка телеграм-бота для автоматического улучшения резкости размытых изображений
    
    *Используемые технологии:*
    • Python 3.9+
    • OpenCV для обработки изображений
    • Pillow для работы с графикой
    • python-telegram-bot для API Telegram
    
    *Алгоритмы улучшения:*
    1. Фильтр повышения резкости (Unsharp Mask)
    2. Адаптивное выравнивание гистограммы (CLAHE)
    3. Подавление шумов
    
    Проект разработан для восстановления качества размытых изображений.
    """
    await update.message.reply_text(info_text, parse_mode='Markdown')

# Команда /mode
async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор режима обработки"""
    keyboard = [
        ["🔧 Стандартная обработка"],
        ["⚡ Быстрая обработка"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Выберите режим обработки:\n\n"
        "🔧 *Стандартная* - более качественная обработка, но медленнее\n"
        "⚡ *Быстрая* - базовая обработка за несколько секунд",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

## Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    

# Проверяем, какая кнопка была нажата
    if text == "🚀 НАЧАТЬ РАБОТУ" or text == '/start':
    # УДАЛИТЬ эту строку: await how_it_works
        await update.message.reply_text(
        'Работа начата! Отправьте фото для обработки.', 
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[['Отправить изображение']],
            resize_keyboard=True
        )
    )
    
    elif text == "📖 Как это работает?":
        await how_it_works(update, context)
    
    elif text == "⚙️ Настройки":
        await mode_command(update, context)
    
    elif text == "📤 Отправить изображение":
        await update.message.reply_text(
            "📸 *Отправьте мне изображение для обработки!*\n\n"
            "Можно отправить как фото из галереи, так и сделать новое.",
            parse_mode='Markdown'
        )
    
    elif text == "⚡ Быстрая обработка":
        context.user_data['mode'] = 'fast'
        await update.message.reply_text(
            "✅ *Установлен быстрый режим обработки*\n\n"
            "Изображения будут обрабатываться за 2-5 секунд.",
            parse_mode='Markdown'
        )
    
    elif text == "🔧 Качественная обработка":
        context.user_data['mode'] = 'standard'
        await update.message.reply_text(
            "✅ *Установлен качественный режим обработки*\n\n"
            "Будет применен полный комплекс алгоритмов (5-15 секунд).",
            parse_mode='Markdown'
        )
    
    elif text == "📊 Статистика":
        stats = context.user_data.get('stats', {'processed': 0})
        await update.message.reply_text(
            f"📈 *Ваша статистика:*\n\n"
            f"• Обработано изображений: {stats['processed']}\n"
            f"• Текущий режим: {context.user_data.get('mode', 'standard')}\n"
            f"• Лицензия: Активна 🟢",
            parse_mode='Markdown'
        )
    
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    
    else:
        await update.message.reply_text(
            "Нажмите кнопку '🚀 НАЧАТЬ РАБОТУ' чтобы начать!\n"
            "Или используйте команды:\n"
            "/start - Перезапустить бота\n"
            "/help - Получить помощь",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🚀 НАЧАТЬ РАБОТУ")]], resize_keyboard=True)
        )

# Основной обработчик изображений

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученное изображение"""
    # Обновляем статистику
    if 'stats' not in context.user_data:
        context.user_data['stats'] = {'processed': 0}
    context.user_data['stats']['processed'] += 1
    try:
        
        
        # Отправляем сообщение о начале обработки
        status_msg = await update.message.reply_text("🔄 Начинаю обработку изображения...")
        
        # Получаем файл изображения
        photo_file = await update.message.photo[-1].get_file()
        
        # Скачиваем изображение в память
        image_bytes = await photo_file.download_as_bytearray()
        
        # Получаем информацию об изображении
        info = get_image_info(bytes(image_bytes))
        await status_msg.edit_text(f"📊 Информация об изображении:\n"
                                  f"Размер: {info['size'][0]}x{info['size'][1]}\n"
                                  f"Формат: {info['format']}\n\n"
                                  f"⏳ Обрабатываю...")
        
        # Выбираем режим обработки (по умолчанию стандартный)
        mode = context.user_data.get('mode', 'standard')
        
        # Обрабатываем изображение
        await status_msg.edit_text("🔧 Применяю алгоритмы улучшения...")
        
        if mode == 'fast':
            processed_bytes = simple_sharpen(bytes(image_bytes))
            mode_text = "быстром режиме"
        else:
            processed_bytes = improve_image(bytes(image_bytes))
            mode_text = "стандартном режиме"
        
        # Отправляем обработанное изображение
        await status_msg.edit_text(f"✅ Обработка завершена в {mode_text}!\n"
                                  f"📤 Отправляю результат...")
        
        # Конвертируем байты в файл для отправки
        processed_image = Image.open(io.BytesIO(processed_bytes))
        
        # Сохраняем во временный файл
        output = io.BytesIO()
        processed_image.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        # Отправляем результат
        await update.message.reply_photo(
            photo=output,
            caption=f"✨ Готово! Изображение улучшено в {mode_text}.\n"
                   f"Для повторной обработки отправьте новое изображение.\n\n"
                   f"Используйте /mode для смены режима."
        )
        
        # Удаляем сообщение о статусе
        await status_msg.delete()
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке изображения.\n"
            "Попробуйте:\n"
            "1. Отправить другое изображение\n"
            "2. Проверить формат (JPG/PNG)\n"
            "3. Уменьшить размер файла\n\n"
            f"Ошибка: {str(e)}"
        )

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логирует ошибки"""
    logger.warning(f"Update {update} caused error {context.error}")
    
    try:
        await update.message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте снова или используйте /help"
        )
    except:
        pass

# Главная функция
def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("mode", mode_command))
    
    # Регистрируем обработчик изображений
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    
    # Регистрируем обработчик текста
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Регистрируем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
    print("📞 Перейдите в Telegram и найдите своего бота по имени")
    
    application.run_polling()

if __name__ == '__main__':
    main()