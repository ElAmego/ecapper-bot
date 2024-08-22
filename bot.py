from telebot import types
from threading import Thread
from utils.utils import *
from parser import activate_parser


def activate_tg_bot(sports, bot, collection_matches, collection_users, collection_config):
    @bot.message_handler(commands=['start'])
    def start(message):
        check_user(collection_users, message.chat.id)
        bot.send_message(message.chat.id, f'Добро пожаловать {message.from_user.first_name} '
                                          f'{message.from_user.last_name}!')

    @bot.message_handler(commands=['commands'])
    def commands(message):
        bot.send_message(message.chat.id, '/commands - Список всех команд бота\n/deviation - Просмотр и изменение '
                                          'deviation\n/clear_db - Очистка матчей которые прошли (раз в неделю)')

    @bot.message_handler(commands=['deviation'])
    def commands(message):
        deviation_from_the_db = get_deviation(collection_config)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Изменить?', callback_data='change_deviation'))
        bot.send_message(message.chat.id, f'Текущий deviation: {deviation_from_the_db}', reply_markup=markup)

    @bot.message_handler(commands=['clear_db'])
    def clear_db(message):
        bot.send_message(message.chat.id, f'Удаление лишних матчей в базе данных, ожидайте.')
        is_clear = clear_database(collection_matches)
        if is_clear:
            bot.send_message(message.chat.id, f'Удаление завершено успешно.')
        else:
            bot.send_message(message.chat.id, f'При удалении произошла ошибка.')

    @bot.callback_query_handler(func=lambda callback: True)
    def callback_message(callback):
        if callback.data == 'change_deviation':
            msg = bot.send_message(callback.from_user.id, 'Введите число(например 0.5):')
            bot.register_next_step_handler(msg, change_deviation)

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

    def polling():
        bot.polling(none_stop=True)

    def parser():
        while True:
            activate_parser(sports, bot, collection_matches, collection_users, collection_config)

    polling_thread = Thread(target=polling)
    parser_thread = Thread(target=parser)
    polling_thread.start()
    parser_thread.start()
