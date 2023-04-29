from _token._token import TOKEN, PASSWORD
import db.db
from db.db import admins, phrases
from utils.utils import put_text

from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
)


###############################################################################
async def unknown_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Привет, загрузи фотографию"
    )


async def handle_file(
    file, update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    uid = update.message.from_user["id"]
    try:
        if uid not in db.db.position:
            db.db.position[uid] = (0.3, 0.7)
        file_name = "files/" + str(update.effective_chat.id)
        await file.download_to_drive(file_name)
        await context.bot.send_message(chat_id=chat_id, text="Файл получен")
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка получения файла:\n" + str(e)
        )
        return None

    try:
        put_text(file_name, db.db.position[uid])
        if db.db.sendType == "document":
            await context.bot.send_document(
                chat_id=chat_id, document=file_name + ".png"
            )
        else:
            await context.bot.send_photo(
                chat_id=chat_id, photo=open(file_name + ".png", "rb")
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка обработки:\n" + str(e)
        )
        return None


async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.document)
    await handle_file(file, update, context)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    await handle_file(file, update, context)


async def add_admin_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        uid = update.message.from_user["id"]
        password = " ".join(context.args)
        chat_id = update.effective_chat.id

        if password == PASSWORD:
            admins.append(uid)
            await context.bot.send_message(
                chat_id=chat_id, text="Теперь вы админ"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id, text="Неверный пароль"
            )
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return None


async def print_help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user["id"]
    chat_id = update.effective_chat.id
    info = "Вы "
    if uid in admins:
        info += "админ"
    else:
        info += "пользователь"
    info += "\n"
    info += "/login {пароль} - для авторизации админов\n"
    info += "/help - вся информация\n"
    info += "/add - добавить текст в базу данных\n"
    info += "/remove - удалить текст из базы данных\n"
    info += "/setfont - загрузить шрифт\n"
    info += "/setfontsize - установить размер шрифта\n"
    info += "/setsendtype - установить тип сообщения (photo или document)\n"
    info += "/cancel - отмена команды\n"
    info += (
        "/setposition - установить место для текста (x, y), x и y в [0, 1]\n"
    )
    await context.bot.send_message(chat_id=chat_id, text=info)


TEXT_STATE = 1


async def ask_for_rights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user["id"]
    chat_id = update.effective_chat.id

    if uid not in admins:
        await context.bot.send_message(chat_id=chat_id, text="Вы не админ")
        return ConversationHandler.END

    return TEXT_STATE


async def ask_for_rights_and_print_phrases(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    uid = update.message.from_user["id"]
    chat_id = update.effective_chat.id

    if uid not in admins:
        await context.bot.send_message(chat_id=chat_id, text="Вы не админ")
        return ConversationHandler.END

    info = ""
    for i in range(len(phrases)):
        info += str(i + 1) + ":\n" + phrases[i] + "\n"

    await context.bot.send_message(chat_id=chat_id, text=info)

    return TEXT_STATE


async def add_text_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    def convert_(s):
        res = ""
        for i in range(len(s)):
            if s[i] == "$":
                res += "\n"
            else:
                res += str(s[i])
        return res

    for x in text.split("\n"):
        phrases.append(convert_(x))

    return ConversationHandler.END


async def set_fontsize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    try:
        db.db.fontsize = int(text)
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def set_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    uid = update.message.from_user["id"]

    try:
        vals = text.split(" ")
        x, y = float(vals[0]), float(vals[1])
        assert 0 <= x <= 1 and 0 <= y <= 1, "x и y должны лежать в [0, 1]"
        db.db.position[uid] = (x, y)
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return ConversationHandler.END

    await context.bot.send_message(chat_id=chat_id, text="готово")
    return ConversationHandler.END


async def do_nothing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return TEXT_STATE


async def set_sendtype(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id

    try:
        db.db.sendType = text
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return ConversationHandler.END

    return ConversationHandler.END


async def remove_text_from_db(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    try:
        index = int(update.message.text) - 1
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return ConversationHandler.END

    if index < 0 or index >= len(phrases):
        return ConversationHandler.END

    phrases.pop(index)

    return ConversationHandler.END


async def cancel_add_text_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    return ConversationHandler.END


async def set_font(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    try:
        file = await context.bot.get_file(update.message.document)
        file_name = "files/font_" + str(update.effective_chat.id) + ".ttf"
        await file.download_to_drive(file_name)
        await context.bot.send_message(chat_id=chat_id, text="Файл получен")
        db.db.font = file_name
        return ConversationHandler.END
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка: \n" + str(e)
        )
        return None


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    """
    Work with bot.
    """
    add_admin_handler = CommandHandler("login", add_admin_to_db)
    application.add_handler(add_admin_handler)

    print_help_info_handler = CommandHandler("help", print_help_info)
    application.add_handler(print_help_info_handler)

    add_text_conversation = ConversationHandler(
        entry_points=[CommandHandler("add", ask_for_rights)],
        states={TEXT_STATE: [MessageHandler(filters.TEXT, add_text_to_db)]},
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(add_text_conversation)

    remove_text_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("remove", ask_for_rights_and_print_phrases)
        ],
        states={
            TEXT_STATE: [MessageHandler(filters.TEXT, remove_text_from_db)]
        },
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(remove_text_conversation)

    set_font_handler = ConversationHandler(
        entry_points=[CommandHandler("setfont", ask_for_rights)],
        states={TEXT_STATE: [MessageHandler(filters.Document.ALL, set_font)]},
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(set_font_handler)

    set_fontsize_handler = ConversationHandler(
        entry_points=[CommandHandler("setfontsize", ask_for_rights)],
        states={TEXT_STATE: [MessageHandler(filters.TEXT, set_fontsize)]},
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(set_fontsize_handler)

    set_position_handler = ConversationHandler(
        entry_points=[CommandHandler("setposition", do_nothing)],
        states={TEXT_STATE: [MessageHandler(filters.TEXT, set_position)]},
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(set_position_handler)

    set_sendtype_handler = ConversationHandler(
        entry_points=[CommandHandler("setsendtype", ask_for_rights)],
        states={TEXT_STATE: [MessageHandler(filters.TEXT, set_sendtype)]},
        fallbacks=[CommandHandler("cancel", cancel_add_text_conversation)],
    )
    application.add_handler(set_sendtype_handler)

    """
    Work with user.
    """

    file_handler = MessageHandler(filters.Document.ALL, file_handler)
    application.add_handler(file_handler)

    photo_handler_instance = MessageHandler(filters.PHOTO, photo_handler)
    application.add_handler(photo_handler_instance)

    """
    For unknown:
    """
    unknown_handler_for_text = MessageHandler(filters.TEXT, unknown_handler)
    application.add_handler(unknown_handler_for_text)

    unknown_handler_for_command = MessageHandler(
        filters.COMMAND, unknown_handler
    )
    application.add_handler(unknown_handler_for_command)

    application.run_polling()
