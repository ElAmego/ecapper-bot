import telebot
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bot import activate_tg_bot

# Bot
bot = telebot.TeleBot('BOT_TOKEN')

# Database
db_url = "DB_URL"
client = MongoClient(db_url, server_api=ServerApi('1'))
db = client.ecapper
collection_matches = db.matches
collection_users = db.users
collection_config = db.config

# Kind of sports for the parse
sports = {
    'soccer': 'http://ecapper.ru/lc/',
    'basketball': 'http://ecapper.ru/lc/basketball/'
    }


def main():
    activate_tg_bot(sports, bot, collection_matches, collection_users, collection_config)


if __name__ == '__main__':
    main()
