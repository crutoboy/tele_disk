import os

import telebot
from telebot import types

from config import welcome_message, help_message, token, root_path
import db_working
import file_working



bot = telebot.TeleBot(token, 'MARKDOWN')
dict_with_active_explorers = {}



@bot.message_handler(commands=['start'])
def start(message):
    db_working.new_user(message)
    bot.send_message(message.from_user.id, welcome_message)
    help(message)
    open_new_explorer (message)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, help_message)


@bot.message_handler(commands=['explorer'])
def open_new_explorer (message):
    root, dir, space, visible, admin, fovorite = db_working.get_database(message.from_user.id)

    try:
        bot.delete_message(message.from_user.id, dict_with_active_explorers[message.from_user.id][0])
        bot.delete_message(message.from_user.id, dict_with_active_explorers[message.from_user.id][1])
    except KeyError:
        ...

    keaboard = types.InlineKeyboardMarkup()
    lstdir = file_working.getfiles(file_working.get_path_to_file(dir.text, space, message.from_user.id))
    tmp = True
    if len(lstdir[0]) > 0 or len(lstdir[1]) > 0:
        tmp = False
    for i in lstdir[0]:
        btn = types.InlineKeyboardButton(text = str(i), callback_data = f'cd|{i[2:]}')
        keaboard.add(btn)
    if visible:
        for i in lstdir[1]:
            btn = types.InlineKeyboardButton(text = str(i), callback_data = f'file|{i}')
            keaboard.add(btn)
    if dir.text != '/' and tmp and (space or admin):
        btn = types.InlineKeyboardButton(text = 'Удалить текущую папку', callback_data = 'remove_dir')
        keaboard.add(btn)
    tmp1 = bot.send_message(message.from_user.id, dir.text, reply_markup = keaboard)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if space: tmp = '🏢'
    else: tmp = '🏠'
    markup.add(types.KeyboardButton('⬆'), types.KeyboardButton('🔄'), types.KeyboardButton('⭐'), types.KeyboardButton(tmp), row_width=4)
    markup.add(types.KeyboardButton('➕Создать папку'))
    if (space or admin) and dir.text != '/': markup.add(types.KeyboardButton('✍Переименовать папку'))
    markup.add(types.KeyboardButton('🔎Поиск'))
    markup.add(types.KeyboardButton('🔎Расширенный поиск'))
    if visible: tmp = 'Скрыть файлы'
    else: tmp = 'Отобразить файлы'
    markup.add(types.KeyboardButton(tmp))
    tmp2 = bot.send_message(message.from_user.id, dir.text, reply_markup = markup)

    dict_with_active_explorers.update([(message.from_user.id, [tmp1.message_id, tmp2.message_id])])


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '⬆':
        dir = db_working.get_database(message.from_user.id)[1]
        if dir.text != '/':
            message.update({'data': 'cd_back_keyboard|..'})
            callback_worker(message)
        else:
            open_new_explorer (message)
    elif message.text == '🔄':
        open_new_explorer (message)
    elif message.text == '⭐':
        bot.send_message(message.from_user.id, 'Пока в разработке')
        # tree = xml.parse(db_users)
        # root = tree.getroot()
        # dir_in_db = root.findall("./User[ID='"+ str(message.from_user.id) +"']/FavoritesDir")
        # print(dir_in_db)
        # keaboard = types.InlineKeyboardMarkup()
        # for i in dir_in_db:
        #     print(i)
    elif message.text == '🏠' or message.text == '🏢':
        root, dir, space = db_working.get_database(message.from_user.id, booling_return=False)[:3]
        dir.text = '/'
        if message.text == '🏠':
            space.text = 'local'
        else:
            space.text = 'global'
        db_working.save_db(root)
        open_new_explorer(message)
    elif message.text == '➕Создать папку':
        bot.send_message(message.from_user.id, f'Напишите имя папки\nОтмена /cansel')
        bot.register_next_step_handler(message, create_new_folder)
    elif message.text == '✍Переименовать папку':
        bot.send_message(message.from_user.id, f'Напишите имя папки\nОтмена /cansel')
        bot.register_next_step_handler(message, create_new_folder, True)

def create_new_folder (message, rename: bool = False):
    root, dir, space = db_working.get_database(message.from_user.id)[:3]
    dst = file_working.normpath(f'{dir.text}/{message.text}')
    if rename:
        dst = f"{'/'.join(dir.text.split('/')[:-1])}/{message.text}"
    if message.text == '/cansel':
        bot.send_message(message.from_user.id, 'Действие отменено')
    elif os.path.isdir(file_working.get_path_to_file(dst, space, message.from_user.id)):
        bot.send_message(message.from_user.id, 'Такая папка уже есть, выберете и введите другое название\nОтмена /cansel')
        bot.register_next_step_handler(message, create_new_folder)
    else:
        if rename:
            os.rename(file_working.get_path_to_file(dir.text, space, message.from_user.id),
                      file_working.get_path_to_file(dst, space, message.from_user.id))
        else:
            os.mkdir(file_working.get_path_to_file(dst, space, message.from_user.id))
        dir.text = dst
        db_working.save_db(root)
        tmp = 'Папка создана'
        if rename:
            tmp = 'Папка переименована'
        bot.send_message(message.from_user.id, tmp)
        open_new_explorer (message)


@bot.message_handler(content_types=['document', 'audio', 'video', 'voice', 'photo'])
def addfile(message):
    path, space = db_working.get_database(message.from_user.id)[1:3]
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        file_name = file_info.file_path.split('/')[-1]
    else:
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name
    downloaded_file = bot.download_file(file_info.file_path)
    absolute_path = f'{file_working.get_path_to_file(path.text, space, message.from_user.id)}/{file_name}'
    absolute_path, file_name = file_working.repeat_name_file(absolute_path)
    with open(absolute_path, 'wb') as f:
        f.write(downloaded_file)
    bot.reply_to(message, f'Файл был загружен по пути: {file_working.normpath(f"{path.text}/{file_name}")}')
    # bot.edit_message_text('загружено', message.from_user.id, message.message_id)
    # bot.send_message(message.from_user.id, f'Файл был загружен по пути: {file_working.normpath(f"{path.text}/{file_name}")}', None, reply_to_message_id = message.message_id)







if __name__ == '__main__':
    os.chdir(root_path)
    db_working.check_db()
    bot.polling(non_stop=True, interval=0)
    # bot.infinity_polling()
