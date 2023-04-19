from _token._token import TOKEN, PASSWORD
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
    file_name = "files/" + str(update.effective_chat.id)
    chat_id = update.effective_chat.id
    await file.download_to_drive(file_name)
    await context.bot.send_message(chat_id=chat_id, text="Файл получен")

    try:
        put_text(file_name)
        await context.bot.send_document(
            chat_id=chat_id, document=file_name + ".png"
        )
    except Exception:
        await context.bot.send_message(
            chat_id=chat_id, text="Ошибка обработки"
        )
        return None


async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.document)
    await handle_file(file, update, context)


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.photo[-1].file_id)
    await handle_file(file, update, context)


async def add_admin_to_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user["id"]
    password = " ".join(context.args)
    chat_id = update.effective_chat.id

    if password == PASSWORD:
        admins.append(uid)
        await context.bot.send_message(chat_id=chat_id, text="Теперь вы админ")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Неверный пароль")


async def print_help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user["id"]
    chat_id = update.effective_chat.id
    info = "Вы "
    if uid in admins:
        info += "админ"
    else:
        info += "пользователь"
    info += "\n"
    info += "/login - для авторизации админов\n"
    info += "/help - вся информация\n"
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

    phrases.append(text)

    return ConversationHandler.END


async def remove_text_from_db(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    index = int(update.message.text) - 1

    if index < 0 or index >= len(phrases):
        return ConversationHandler.END

    phrases.pop(index)

    return ConversationHandler.END


async def cancel_add_text_conversation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    file_handler = MessageHandler(filters.Document.ALL, file_handler)
    application.add_handler(file_handler)

    photo_handler_instance = MessageHandler(filters.PHOTO, photo_handler)
    application.add_handler(photo_handler_instance)

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
