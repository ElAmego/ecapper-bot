import requests
from bs4 import BeautifulSoup
import datetime


def check_user(users, user):
    try:
        is_exist = list(users.find({'user': user}))

        if len(is_exist) == 0:
            users.insert_one({'user': user})

    except Exception as ex:
        print(f'The error in the check_user function: {ex}')


def connection(link: str):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'
    }

    try:
        req = requests.get(link, headers=headers)
    except Exception as ex:
        print(f'The error from the "connection" function: {ex}')
    else:
        src = req.text
        return BeautifulSoup(src, 'lxml')


def get_all_games_id(kind_of_sports: dict) -> dict:
    all_links = {
        'soccer': [],
        'basketball': []
    }

    for sport_name, link in kind_of_sports.items():
        page_with_matches = connection(link)
        try:
            rows_of_matches = page_with_matches.find_all('tr', class_='a_link')
        except Exception as ex:
            print(f'The error from the "get_all_games_id" function(find_one): {ex}')
            continue
        else:
            for match in rows_of_matches:
                if sport_name == 'soccer':
                    all_links['soccer'].append(match['game_id'])
                elif sport_name == 'basketball':
                    all_links['basketball'].append(match['game_id'])

    all_links['soccer'] = set(all_links['soccer']) if len(all_links['soccer']) != 0 else None
    all_links['basketball'] = set(all_links['basketball']) if len(all_links['basketball']) != 0 else None
    # The bug on the website. It's a fix.
    return all_links


def get_list_of_links(games_id_list: dict) -> dict:
    pages_links = {
        'soccer': {
            'soccer_1x2': [],
            'total': []
        },

        'basketball': {
            'basketball_total': [],
            'handicap': []
        }
    }

    for kind_of_game, games_id in games_id_list.items():
        if games_id:
            for game_id in games_id:
                if kind_of_game == 'soccer':
                    for type_of_page in pages_links['soccer'].keys():
                        if type_of_page == 'soccer_1x2':
                            pages_links['soccer'][type_of_page].append(
                                f'https://ecapper.ru/lc/event.php?id={game_id}')
                        elif type_of_page == 'total':
                            pages_links['soccer'][type_of_page].append(
                                f'http://ecapper.ru/lc/event.php?id={game_id}&t='
                                f'total')
                elif kind_of_game == 'basketball':
                    for type_of_page in pages_links['basketball'].keys():
                        if type_of_page == 'basketball_total':
                            pages_links['basketball'][type_of_page].append(
                                f'http://ecapper.ru/lc/basketball/event.php?'
                                f'id={game_id}&t=total_points')
                        elif type_of_page == 'handicap':
                            pages_links['basketball'][type_of_page].append(
                                f'http://ecapper.ru/lc/basketball/event.php?'
                                f'id={game_id}&t=spread')

    return pages_links


def check_match_in_the_db(link: str, data_match: dict, db_collection_matches) -> dict:
    match = None
    try:
        match = db_collection_matches.find_one({'link': link})
    except Exception as ex:
        print(f'The error from the "check_match_in_the_db" function(find_one): {ex}')

    if match is None:
        try:
            current_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            db_collection_matches.insert_one({'link': link, 'row_quantity': data_match['row_quantity'],
                                              'date': current_date, 'signals_quantity': 0})
        except Exception as ex:
            print(f'The error from the "check_match_in_the_db" function(insert_one): {ex}')
    else:
        return match


def get_data_match(link: str) -> dict:
    data_page = connection(link)
    try:
        match_blocks = data_page.find_all('div', class_='matchinfo')
        league = match_blocks[len(match_blocks) - 1].find('h3').text
        opponents = match_blocks[len(match_blocks) - 1].find('h1').text
        rows = data_page.find('div', class_='tablediv').find_all('tr')
    except Exception as ex:
        print(f'The error from the "count_rows" function: {ex}')
        return get_data_match(link)
    else:
        return {
            'row_quantity': len(rows),
            'last_row': rows[len(rows) - 1].find_all('td'),
            'opponents': opponents,
            'league': league
        }


def update_data_in_the_db(link: str, row_quantity: int, db_collection_matches):
    try:
        db_collection_matches.update_one({'link': link}, {'$set': {'row_quantity': row_quantity}})
    except Exception as ex:
        print(f'The error from the "count_rows" function: {ex}')


def get_handicap(link: str, db_collection_matches) -> dict:
    try:
        match = db_collection_matches.find_one({'link': link})
    except Exception as ex:
        print(f'The error from the "get_handicap" function: {ex}')
    else:
        if 'handicap' in match:
            return match['handicap']


def insert_handicap(link: str, handicap: float, db_collection_matches):
    if len(str(handicap)) <= 4:
        try:
            db_collection_matches.update_one({'link': link}, {'$set': {'handicap': handicap}})
        except Exception as ex:
            print(f'The error from the "insert_handicap" function: {ex}')


def get_all_users(collection_users) -> list:
    try:
        users_list = list(collection_users.find())
    except Exception as ex:
        print(f'The error from the "get_all_users" function: {ex}')
    else:
        return users_list


def get_deviation(collection_config) -> float:
    try:
        deviation = list(collection_config.find())[0]
    except Exception as ex:
        print(f'The error from the "get_deviation" function: {ex}')
    else:
        return deviation['deviation']


def change_deviation_in_the_db(collection_config, new_deviation: float) -> bool:
    try:
        collection_config.update_one({}, {'$set': {'deviation': new_deviation}})
    except Exception as ex:
        print(f'The error from the "get_deviation" function: {ex}')
    else:
        return True


def clear_database(collection_matches) -> bool:
    try:
        current_date = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        collection_matches.delete_many({'date': {'$lt': current_date}})
    except Exception as ex:
        print(f'The error from the "clear_database" function: {ex}')
    else:
        return True


def change_signals_quantity(collection_matches, link: str, action: str):
    try:
        match action:
            case 'plus':
                collection_matches.update_one({'link': link}, {'$inc': {'signals_quantity': 1}})

            case 'zero':
                collection_matches.update_one({'link': link}, {'$set': {'signals_quantity': 0}})
    except Exception as ex:
        print(f'The error from the "change_signals_quantity" function: {ex}')


def get_signals_quantity_from_the_db(collection_matches, link: str) -> int:
    try:
        data = collection_matches.find_one({'link': link}, {'_id:': False, 'link': False, 'date': False,
                                                            'row_quantity': False, 'handicap': False})

    except Exception as ex:
        print(print(f'The error from the "get_signals_quantity_from_the_db" function: {ex}'))

    else:
        return data['signals_quantity']
