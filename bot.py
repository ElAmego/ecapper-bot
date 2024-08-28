from telebot import types
from threading import Thread
from utils.utils import *
from parser import activate_parser


def activate_tg_bot(sports, bot, collection_matches, collection_users, collection_config):
    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, f'Добро пожаловать {message.from_user.first_name} '
                                          f'{message.from_user.last_name}!')

    @bot.message_handler(commands=['get_id'])
    def get_id(message):
        bot.send_message(message.chat.id, f'Ваш id: {message.chat.id}')

    @bot.message_handler(commands=['deviation'])
    def deviation(message):
        admin_id = get_config(collection_config)['admin']
        if admin_id == int(message.chat.id):
            deviation_from_the_db = get_config(collection_config)['deviation']
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Изменить?', callback_data='change_deviation'))
            bot.send_message(message.chat.id, f'Текущий deviation: {deviation_from_the_db}',
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'У вас ограничены права.')

    @bot.message_handler(commands=['clear_db'])
    def clear_db(message):
        admin_id = get_config(collection_config)['admin']
        if admin_id == int(message.chat.id):
            bot.send_message(message.chat.id, f'Удаление лишних матчей в базе данных, ожидайте.')
            is_clear = clear_database(collection_matches)
            if is_clear:
                bot.send_message(message.chat.id, f'Удаление завершено успешно.')
            else:
                bot.send_message(message.chat.id, f'При удалении произошла ошибка.')
        else:
            bot.send_message(message.chat.id, 'У вас ограничены права.')

    @bot.message_handler(commands=['id_add'])
    def add_id(message):
        admin_id = get_config(collection_config)['admin']
        if admin_id == int(message.chat.id):
            msg = bot.send_message(message.chat.id, 'Введите id пользователя для добавления в базу данных.')
            bot.register_next_step_handler(msg, add_id_next_step)
        else:
            bot.send_message(message.chat.id, 'У вас ограничены права.')

    @bot.message_handler(commands=['id_list'])
    def id_list(message):
        admin_id = get_config(collection_config)['admin']
        if admin_id == int(message.chat.id):
            id_list_from_the_db = get_id_list_from_the_db(collection_users)

            if id_list_from_the_db is not None:
                if len(id_list_from_the_db) != 0:
                    msg = 'Список id:'
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Удалить id', callback_data='remove_id'))
                    for index, user in enumerate(id_list_from_the_db):
                        msg += f'\n{index+1}: {user["user"]}'
                    bot.send_message(message.chat.id, msg, reply_markup=markup)
                else:
                    bot.send_message(message.chat.id, 'Список id пуст.')
            else:
                bot.send_message(message.chat.id, 'Произошла ошибка при получении данных.')
        else:
            bot.send_message(message.chat.id, 'У вас ограничены права.')

    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):
        if callback.data == 'change_deviation':
            msg = bot.send_message(callback.from_user.id, 'Введите число(например 0.5):')
            bot.register_next_step_handler(msg, change_deviation)

        elif callback.data == 'remove_id':
            msg = bot.send_message(callback.from_user.id, 'Введите номер(а) id через запятую(Например: 0, 1, 2) или '
                                                          '"все".')
            bot.register_next_step_handler(msg, remove_id)

    def remove_id(message):
        id_list_from_the_db = get_id_list_from_the_db(collection_users)
        is_delete = delete_id_from_the_db(collection_users, message.text, id_list_from_the_db)
        if is_delete:
            bot.send_message(message.chat.id, 'Id удален(ы)')
        else:
            bot.send_message(message.chat.id, 'При удалении id произошла ошибка, возможно вы ввели номер(а) не '
                                              'корректно.')

    def change_deviation(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ещё раз?', callback_data='change_deviation'))
        try:
            new_deviation = float(message.text)
        except Exception as ex:
            print(f'The error from the "change_deviation" function: {ex}')
            bot.send_message(message.chat.id, 'Вы ввели некорректное значение.', reply_markup=markup)
        else:
            is_change = change_deviation_in_the_db(collection_config, new_deviation)
            if is_change:
                bot.send_message(message.chat.id, f'Deviation изменен на {new_deviation}')

    def add_id_next_step(message):
        status = add_id_in_the_db(collection_users, message.text)

        if status is not None:
            bot.send_message(message.chat.id, 'Пользователь добавлен.')
        else:
            bot.send_message(message.chat.id, 'Ошибка при добавлении в базу данных. Возможно вы ввели некорректный id '
                                              'или пользователь уже был в базе данных.')

    def polling():
        bot.polling(none_stop=True)

    def parser():
        while True:
            activate_parser(sports, bot, collection_matches, collection_users, collection_config)

    polling_thread = Thread(target=polling)
    parser_thread = Thread(target=parser)
    polling_thread.start()
    parser_thread.start()
