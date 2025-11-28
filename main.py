import sqlite3
import telebot

API_TOKEN = '8343594079:AAEEU7flKHO-1kaZ-xfNy1X1HUNOaHGXQYo'
bot = telebot.TeleBot(API_TOKEN)

user_choices = {}

# ======================
# Получаем категории и подкатегории из базы
# ======================
def get_available_categories():
    conn = sqlite3.connect("education.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT program_name FROM programs")
    programs = [row[0] for row in cursor.fetchall()]

    category_to_subcats = {
        "IT": ["IT", "Программирование", "GameDev", "Инженерия"],
        "Media": ["Медиа", "SMM", "Журналистика", "Анимации"],
        "Fashion": ["Дизайн (графический)", "Дизайн (интерьер)", "Дизайн (одежда)", "UI/UX дизайн", "Стилист"],
        "Arts": ["Актёрство", "Музыка", "Живопись", "Театр"],
        "Architecture": ["Архитектура"]
    }

    filtered_categories = {}
    for cat, subcats in category_to_subcats.items():
        available_subs = [s for s in subcats if s in programs]
        if available_subs:
            filtered_categories[cat] = available_subs

    conn.close()
    return filtered_categories

# ======================
# Форматирование учебного заведения
# ======================
def format_institution(info):
    name, duration, price, site = info
    text = f"🎓 *{name}*\n"
    text += f"⏳ Срок обучения: {duration}\n"
    text += f"💰 Стоимость: {price}\n"
    text += f"🌐 Сайт: {site}\n"
    return text

# ======================
# Показываем категории
# ======================
def show_categories(chat_id, message_id=None):
    categories = get_available_categories()
    markup = telebot.types.InlineKeyboardMarkup()
    for cat in categories.keys():
        markup.add(telebot.types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
    if message_id:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                              text="Выбери категорию:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Выбери категорию:", reply_markup=markup)
    return categories

# ======================
# Показываем подкатегории
# ======================
def show_subcategories(chat_id, category, message_id):
    categories = get_available_categories()
    subcats = categories.get(category, [])

    markup = telebot.types.InlineKeyboardMarkup()
    for sub in sorted(subcats):
        markup.add(telebot.types.InlineKeyboardButton(sub, callback_data=f"sub_{sub}"))
    markup.add(
        telebot.types.InlineKeyboardButton("🏠 Домой", callback_data="home")
    )
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=f"Выбери направление в категории *{category}*:",
                          reply_markup=markup, parse_mode="Markdown")

# ======================
# Показываем формат обучения
# ======================
def show_education_options(chat_id, subcategory, message_id):
    formats = ["universities", "colleges", "courses"]
    markup = telebot.types.InlineKeyboardMarkup()
    for f in formats:
        markup.add(telebot.types.InlineKeyboardButton(f.capitalize(), callback_data=f"edu_{subcategory}_{f}"))
    markup.add(
        telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data="back"),
        telebot.types.InlineKeyboardButton("🏠 Домой", callback_data="home")
    )
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=f"Где хочешь учиться по направлению *{subcategory}*?",
                          reply_markup=markup, parse_mode="Markdown")

# ======================
# Получаем заведения из базы
# ======================
def get_options_from_db(subcategory, edu_type):
    conn = sqlite3.connect("education.db")
    cursor = conn.cursor()

    type_map = {"universities": "university", "colleges": "college", "courses": "course"}
    db_type = type_map.get(edu_type)
    if not db_type:
        return []

    cursor.execute("""
        SELECT i.name, i.duration, i.price, i.site
        FROM institutions i
        JOIN programs p ON i.id = p.institution_id
        WHERE i.type=? AND p.program_name=?
    """, (db_type, subcategory))

    results = cursor.fetchall()
    conn.close()
    return results

# ======================
# Callback handler
# ======================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    data = call.data
    if user_id not in user_choices:
        user_choices[user_id] = {}

    # Домой
    if data == "home":
        user_choices[user_id] = {}
        show_categories(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    # Назад
    if data == "back":
        category = user_choices[user_id].get("category")
        if category:
            show_subcategories(call.message.chat.id, category, call.message.message_id)
        bot.answer_callback_query(call.id)
        return

    # Категория
    if data.startswith("cat_"):
        category = data[4:]
        user_choices[user_id]["category"] = category
        bot.answer_callback_query(call.id)
        show_subcategories(call.message.chat.id, category, call.message.message_id)

    # Подкатегория
    elif data.startswith("sub_"):
        subcategory = data[4:]
        user_choices[user_id]["subcategory"] = subcategory
        bot.answer_callback_query(call.id)
        show_education_options(call.message.chat.id, subcategory, call.message.message_id)

    # Формат обучения
    # Формат обучения
    elif data.startswith("edu_"):
        parts = data.split("_")
        subcategory = "_".join(parts[1:-1])
        edu_type = parts[-1]
        user_choices[user_id]["education"] = edu_type

        options = get_options_from_db(subcategory, edu_type)
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("🏠 Домой", callback_data="home")
        )

        if not options:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Подходящих вариантов нет.",
                                  reply_markup=markup)
        else:
            text = ""
            for info in options:
                text += format_institution(info) + "\n\n"

            # Добавляем кнопки "Назад" и "Домой"
            markup.add(
                telebot.types.InlineKeyboardButton("⬅️ Назад", callback_data="back")
            )

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=text,
                                  reply_markup=markup,
                                  parse_mode="Markdown")

        bot.answer_callback_query(call.id)

# ======================
# Старт
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "✨🎓 *ОКУУ ТАП* 🎓✨\n\n"
        "Салам, дорогой друг!\n\n"
        "Здесь ты можешь найти *креативные профессии* и учебные заведения, "
        "которые помогут тебе раскрыть свой потенциал 🌟\n\n"
        "Выбирай категорию и начинай своё обучение уже сегодня! 🚀"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    show_categories(message.chat.id)

bot.polling()
