from utils.utils import *

import datetime


def activate_parser(sports, bot, collection_matches, collection_users, collection_config):
    users = get_all_users(collection_users)
    list_of_games_id = get_all_games_id(sports)
    list_of_links = get_list_of_links(list_of_games_id)
    print(list_of_links)

    for kind_of_sport, types_of_match in list_of_links.items():
        for type_of_match, urls in types_of_match.items():
            for url in urls:
                data_match = get_data_match(url)
                if data_match:
                    data_match_from_the_db = check_match_in_the_db(url, data_match, collection_matches)

                    if data_match_from_the_db and (data_match_from_the_db['row_quantity'] == data_match['row_quantity']):
                        continue

                    last_row = data_match['last_row']
                    msg = None

                    match type_of_match:
                        case 'soccer_1x2':
                            # 3-home, 6-away
                            print(url + ' : soccer_1x2')
                            if len(last_row) != 0 and ('red2' in last_row[3]['class'] or 'red3' in last_row[3]['class']):  # Red signal
                                print('Signal red HOME')
                                msg = (f'🏆{data_match["league"]}\n⚽{data_match["opponents"]}\n'
                                       f'⏰{data_match["last_row"][1].text}\n🔎Signal red HOME\n➡️{url}')

                            elif len(last_row) != 0 and ('red2' in last_row[6]['class'] or 'red3' in last_row[6]['class']):
                                print('Signal red AWAY')
                                msg = (f'🏆{data_match["league"]}\n⚽{data_match["opponents"]}\n'
                                       f'⏰{data_match["last_row"][1].text}\n🔎Signal red AWAY\n➡️{url}')

                        case 'total':
                            # 9-column 'red'
                            print(url + ' : total')
                            if len(last_row) and (last_row[9].text != ('0-1' or '1-0')):
                                handicap_from_the_db = get_handicap(url, collection_matches)
                                handicap = float(last_row[4].text) if len(str(last_row[4].text)) <= 4 else None
                                if handicap_from_the_db and handicap and (handicap - float(handicap_from_the_db) < 1):
                                    deviation = get_config(collection_config)['deviation']
                                    if last_row[6].text != '' and float(last_row[6].text) >= deviation:  # DEVIATION
                                        print('Signal deviation')
                                        msg = (f'🏆{data_match["league"]}\n⚽{data_match["opponents"]}\n'
                                               f'⏰{data_match["last_row"][1].text}\n🔎Deviation>{deviation} | '
                                               f'Handicap<1\n➡️{url}')

                                insert_handicap(url, last_row[4].text, collection_matches)

                        case 'basketball_total':
                            print(url + ' : basketball_total')
                            if len(last_row) != 0 and ('red3' in last_row[3]['class']) and ('green3' in last_row[4]['class']):
                                print('Red signal basketball_total')
                                msg = (f'🏆{data_match["league"]}\n🏀{data_match["opponents"]}\n'
                                       f'⏰{data_match["last_row"][1].text}\n'
                                       f'🔎Red and Green signal in the Basketball_total\n➡️{url}')

                        case 'handicap':
                            print(url + ' : handicap')
                            if len(last_row) != 0 and ('red3' in last_row[3]['class']) and ('green3' in last_row[4]['class']):
                                print('Red signal handicap')
                                msg = (f'🏆{data_match["league"]}\n🏀{data_match["opponents"]}\n'
                                       f'⏰{data_match["last_row"][1].text}\n'
                                       f'🔎Red and Green signal in the Handicap\n➡️{url}')

                    if msg:
                        signals_quantity = get_signals_quantity_from_the_db(collection_matches, url)
                        print(signals_quantity)
                        if signals_quantity is not None and (signals_quantity < 6):
                            change_signals_quantity(collection_matches, url, 'plus')
                            msg += f'\n🔢{data_match["scores"]}'
                            msg += f'\n🔁{data_match_from_the_db["signals_quantity"]}' if data_match_from_the_db else '\n🔁0'
                            for user in users:
                                try:
                                    bot.send_message(user['user'], msg)
                                except Exception:
                                    pass
                    else:
                        change_signals_quantity(collection_matches, url, 'zero')
                    update_data_in_the_db(url, data_match['row_quantity'], collection_matches)
