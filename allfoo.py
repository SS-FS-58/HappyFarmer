# coding: utf8

import bs4
import re
import sys
import time
import numpy
import json
import datetime
import telethon
import logging
import requests
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest, StartBotRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.errors.rpcerrorlist import UserDeactivatedBanError, FloodWaitError, PhoneCodeInvalidError, \
    StartParamInvalidError, ApiIdInvalidError
from pycoingecko import CoinGeckoAPI
from config import chromeDriverPath
from database import db

logging.basicConfig(filename="TelegramFarmErrors.log", level=logging.ERROR)

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('telethon').setLevel('CRITICAL')
logging.getLogger('selenium').setLevel('CRITICAL')

def InstallPackage():
    print('\n[{0}] Функция установки пакетов активирована.\n'.format(
        datetime.datetime.now().strftime("%H:%M:%S")))
    packages = numpy.array(['telethon', 'pycoingecko', 'beautifulsoup4',
                            'lxml', 'selenium', 'requests'], dtype=str)
    for package in packages:
        subprocess.call([sys.executable, "-m", "pip", "install", package])

def CreateSession():
    stop = False
    successfulCompleted = True
    if db.cursor.execute('SELECT PHONE_NUMBER, API_ID, API_HASH FROM account_information').fetchone() is None:
        print('Перед созданием сессии добавьте данные об аккаунтах.\nВыполните комманду ./addData')
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID, '
                                                           'CREATE_SESSION '
                                                           'FROM account_information').fetchall())
    print('\n[{0}] Функция создания сессии активирована.'.format(datetime.datetime.now().strftime("%H:%M:%S")))
    for accountInformation in accountInformationList:
        if stop is True:
            break
        if accountInformation[5] == 1:
            pass
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            if clientTelegram.is_user_authorized():
                pass
            else:
                while True:
                    clientTelegram.send_code_request(accountInformation[0])
                    try:
                        clientTelegram.sign_in(
                            accountInformation[0], input('[{0}] Введите код, отправленный на аккаунт {1}: '.format(
                                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0])))
                    except PhoneCodeInvalidError:
                        print('[{0}] Введён неправильный код подтверждения.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S")))
                        print('================================================================================')
                        break
                    stringSession = StringSession.save(clientTelegram.session)
                    userIdStr = str(clientTelegram.get_me('id')); templateSearch = re.compile(r'\d.\d{1,12}')
                    findUserId = templateSearch.search(userIdStr); userId = findUserId.group()
                    blockIoApiKey = db.cursor.execute('SELECT BLOCKIO_API_KEY '
                                                      'FROM settings').fetchone()[0]
                    requestsGetToBlockIo = requests.get(
                        'https://block.io/api/v2/get_new_address/?api_key={0}'.format(blockIoApiKey))
                    answerJsonFromBlockIo = json.loads(requestsGetToBlockIo.text)
                    try:
                        addressLiteCoin = answerJsonFromBlockIo['data']['address']
                    except KeyError:
                        print('\n[{0}] Введён неверный Api ключ с сайта https://block.io/'
                              'Выполните комманду ./updApiKey'.format(datetime.datetime.now().strftime("%H:%M:%S")))
                        clientTelegram.disconnect()
                        stop = True
                        break
                    else:
                        db.cursor.execute('UPDATE account_information '
                                          'SET STRING_SESSION = "{0}",'
                                          'ACCOUNT_ID = "{1}",'
                                          'ADDRESS = "{2}" '
                                          'WHERE PHONE_NUMBER = "{3}"'.format(
                            stringSession, userId, addressLiteCoin, accountInformation[0]))
                        db.connection.commit()
                        db.cursor.execute('UPDATE account_information '
                                          'SET CREATE_SESSION = {0} '
                                          'WHERE PHONE_NUMBER = "{1}"'.format(
                            1, accountInformation[0]))
                        db.connection.commit()
                        clientTelegram.disconnect()
                        print('\n[{0}] Вход в аккаунт {1} выполнен успешно.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                        break
        except UserDeactivatedBanError:
            print('\n[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            clientTelegram.disconnect()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        except ApiIdInvalidError:
            print('\n[{0}] Не удаётся создать сессию. Для аккаунта {1} неправильный api id или api hash.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            successfulCompleted = False
    if successfulCompleted is False:
        print('\n[{0}] Не удалось создать сессии для всех аккаунтов. Проверьте введённые данные.'.format(
        datetime.datetime.now().strftime("%H:%M:%S")))
    else:
        print('\n[{0}] Сессии для всех аккаунтов успешно созданы.'.format(datetime.datetime.now().strftime("%H:%M:%S")))

def StartLitecoinBot():
    if db.cursor.execute('SELECT REFFERAL_CODE FROM settings').fetchone() is None:
        print('\n[{0}] Перед началом работы добавьте реферальный код и Api ключ.\n'
              'Выполните комманду ./addRefCodeAndApiKey'.format(datetime.datetime.now().strftime("%H:%M:%S")))
    print('\n[{0}] Функция подписки на @Litecoin_click_bot активирована.\n'.format(
        datetime.datetime.now().strftime("%H:%M:%S")))
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall(), dtype=str)
    for accountInformation in accountInformationList :
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            clientTelegram(StartBotRequest(
                bot='Litecoin_click_bot',
                peer='https://t.me/Litecoin_click_bot',
                start_param=str(
                    db.cursor.execute('SELECT REFFERAL_CODE '
                                      'FROM settings').fetchone()[0])))
        except UserDeactivatedBanError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            db.cursor.execute('DELETE FROM account_information '
                              'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
            db.connection.commit()
        except FloodWaitError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            clientTelegram.disconnect()
        except StartParamInvalidError:
            print('[{0}] Введён неверный реферальный код. Попробуйте ещё раз.'.format
                  (datetime.datetime.now().strftime("%H:%M:%S")))
            clientTelegram.disconnect()
            break
        else:
            print('[{0}] Аккаунт {1} подписан на @Litecoin_click_bot.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            clientTelegram.disconnect()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))

def VisitSites():
    print('[{0}] Функция посещения сайтов активирована.'.format(datetime.datetime.now().strftime("%H:%M:%S")))
    print(
        '==========================================='
        '============================================')
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall(), dtype=str)
    for accountInformation in accountInformationList:
        stop = False
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            print('[{0}] Аккаунт {1} в работе. Функция: посещение сайтов.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            while True:
                if stop is True:
                    break
                findLtc = False
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        Ltc = dialogs
                        findLtc = True
                        break
                if findLtc is False:
                    print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                        datetime.datetime.now().strftime("%H:%M:%S")))
                    print(
                        '==========================================='
                        '============================================')
                    clientTelegram.disconnect()
                    break
                time.sleep(1)
                clientTelegram.send_message(Ltc, '/visit')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.disconnect()
                        print('[{0}] Для аккаунта {1} нет доступных заданий по посещению сайтов.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0] ))
                        print(
                            '==========================================='
                            '============================================')
                        stop = True
                        break
                    elif 'Press the "Visit website"' in getMessage[0].message:
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        chromeOptions = Options()
                        chromeOptions.add_argument('--headless')
                        chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
                        browserChrome = webdriver.Chrome('{0}'.format(chromeDriverPath), options=chromeOptions)
                        try:
                            browserChrome.get(url=url)
                        except:
                            print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'Возникла ошибка при открытии браузера.')
                            print(
                                '==========================================='
                                '============================================')
                            browserChrome.close()
                            browserChrome.quit()
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/visit')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Visit website" button to earn LTC' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(1)
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/visit')
                            break
                        while True:
                            time.sleep(1)
                            getMessage = clientTelegram.get_messages(Ltc, limit=3)
                            if 'for visiting a site' in getMessage[0].message or getMessage[1].message \
                                    or getMessage[2].message:
                                browserChrome.close()
                                browserChrome.quit()
                                time.sleep(1)
                                clientTelegram.disconnect()
                                print('[{0}] Получили награду на аккаунте {1} за посещение сайта.'.format(
                                    datetime.datetime.now().strftime('%H:%M:%S'), accountInformation[0]))
                                print(
                                    '==========================================='
                                    '============================================')
                                stop = True
                                break
                        if stop is True:
                            break
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'New chat to /join' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/visit')
        except UserDeactivatedBanError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()
            db.cursor.execute('DELETE FROM account_information '
                              'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
            db.connection.commit()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        except FloodWaitError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()

def JoinChannel():
    print('[{0}] Функция подписки на каналы активированна.'.format(datetime.datetime.now().strftime("%H:%M:%S")))
    print(
        '==========================================='
        '============================================')
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall(), dtype=str)
    for accountInformation in accountInformationList :
        stop = False
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            print('[{0}] Аккаунт {1} в работе. Функция: подписка на каналы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            while True:
                if stop is True:
                    break
                findLtc = False
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        Ltc = dialogs
                        findLtc = True
                        break
                if findLtc is False:
                    time.sleep(1)
                    clientTelegram.disconnect()
                    print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                        datetime.datetime.now().strftime("%H:%M:%S")))
                    print(
                        '==========================================='
                        '============================================')
                    break
                time.sleep(1)
                clientTelegram.send_message(Ltc, '/join')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.disconnect()
                        print('[{0}] Для аккаунта {1} нет доступных заданий по подписке на каналы.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                        print(
                            '==========================================='
                            '============================================')
                        stop = True
                        break
                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/join')
                    elif 'Press the "Go to channel" button below' in getMessage[0].message or \
                            'Press the "Go to group" button' in getMessage[0].message:
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        try:
                            requestsGet = requests.get(url)
                        except:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/join')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Go to channel" button below' in getMessage[0].message or \
                                            'Press the "Go to group" button' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(1)
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/join')
                        beautifulSoup = bs4.BeautifulSoup(requestsGet.text, 'lxml')
                        try:
                            findChannelName = beautifulSoup.find('title').get_text(strip=True)
                            findChannelTitle = beautifulSoup.find(class_="tgme_page_title").get_text(strip=True)
                            channelName = findChannelName.replace('Telegram: Contact ', '')
                        except AttributeError:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/join')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Go to channel" button below' in getMessage[0].message or \
                                            'Press the "Go to group" button' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(1)
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/join')
                        else:
                            try:
                                time.sleep(1)
                                clientTelegram(JoinChannelRequest(channelName))
                            except:
                                print('[{0}] Канала не существует. Пропускаем задание.'.format(
                                    datetime.datetime.now().strftime("%H:%M:%S"), channelName))
                                print(
                                    '==========================================='
                                    '============================================')
                                while True:
                                    time.sleep(1)
                                    try:
                                        getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                        if accountInformation[4] not in str(getMessage[0].from_id):
                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                            messageId = getMessage[0].id
                                            time.sleep(1)
                                            clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                            break
                                    except AttributeError:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, '/join')
                                    break
                            while True:
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Go to channel" button below' or \
                                            'Press the "Go to group" button below' in \
                                            getMessage[0].message or getMessage[1].message:
                                        buttons = getMessage[0].reply_markup.rows[0].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        for dialogs in clientTelegram.get_dialogs():
                                            if dialogs.title == findChannelTitle:
                                                channelId = dialogs.id
                                                break
                                        while True:
                                            getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                            if 'Success' in getMessage[1].message:
                                                copyMessage = getMessage[1].message
                                                searchPattern = re.compile(r'\d{1,2}')
                                                findTime = searchPattern.search(copyMessage)
                                                time_ = findTime.group()
                                                timeJoin = datetime.datetime.now()
                                                timeDelta = datetime.timedelta(hours=int(time_))
                                                timeLeave = timeJoin + timeDelta
                                                db.cursor.execute(f'''INSERT INTO channel_info 
                                                                    (CHANNEL_ID, 
                                                                    TIME_LEAVE, 
                                                                    ACCOUNT_ID)
                                                                    VALUES (?, ?, ?)''', (
                                                    channelId, timeLeave, accountInformation[4]))
                                                db.connection.commit()
                                                time.sleep(1)
                                                clientTelegram.disconnect()
                                                print('[{0}] На аккаунте {1} успешно выполнено задание по '
                                                      'подписке на канал.'.format(
                                                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                                                print(
                                                    '==========================================='
                                                    '============================================')
                                                stop = True
                                                break
                                            elif 'If this message persists' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram(LeaveChannelRequest(channelName))
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                while True:
                                                    time.sleep(1)
                                                    try:
                                                        getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                                        if 'After joining, press the "Joined" button to earn LTC.' in \
                                                                getMessage[0].message:
                                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                                            messageId = getMessage[0].id
                                                            time.sleep(1)
                                                            clientTelegram(
                                                                GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                                            break
                                                    except AttributeError:
                                                        time.sleep(1)
                                                        clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'Please press the "🔎 Go to channel" button' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'Sorry, that task is no longer valid. 😟' in getMessage[0].message:
                                                for dialogs in clientTelegram.iter_dialogs():
                                                    if str(channelId) in str(dialogs.id):
                                                        time.sleep(1)
                                                        dialogs.delete()
                                                        break
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'In the past hour, you earned' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                            elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '/join')
                                                break
                                        break
                                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, '/join')
                                    elif 'In the past hour, you earned' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, '/join')
                                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, '/join')
                                    elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, '/join')
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/join')
                                break
                    if stop is True:
                        break
                break
        except UserDeactivatedBanError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()
            db.cursor.execute('DELETE FROM account_information '
                              'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
            db.connection.commit()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        except FloodWaitError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()

def StartBot():
    print('[{0}] Функция запуска ботов активирована.'.format(datetime.datetime.now().strftime("%H:%M:%S")))
    print(
        '==========================================='
        '============================================')
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall())
    for accountInformation in accountInformationList:
        stop = False
        clientTelegram = TelegramClient(StringSession(
            accountInformation[3]), accountInformation[1], accountInformation[2])
        clientTelegram.connect()
        print('[{0}] Аккаунт {1} в работе. Функция: запуск ботов.'.format(
            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        print(
            '==========================================='
            '============================================')
        while True:
            if stop is True:
                break
            try:
                findLtc = False
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        Ltc = dialogs
                        findLtc = True
                        break
                if findLtc is False:
                    print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                        datetime.datetime.now().strftime("%H:%M:%S")))
                    print(
                        '==========================================='
                        '============================================')
                    break
                try:
                    time.sleep(1)
                    clientTelegram.send_message(Ltc, '/bots')
                except UnboundLocalError:
                    print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                        datetime.datetime.now().strftime("%H:%M:%S")))
                    print(
                        '==========================================='
                        '============================================')
                    break
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        clientTelegram.disconnect()
                        print('[{0}] Для аккаунта {1} нет доступных заданий по запуску ботов.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                        print(
                            '==========================================='
                            '============================================')
                        stop = True
                        break
                    elif 'Press the "Message bot" botton below' in getMessage[0].message:
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        try:
                            requestsGet = requests.get(url)
                        except:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/bots')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Message bot" botton below' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/bots')
                        try:
                            beautifulSoup = bs4.BeautifulSoup(requestsGet.text, 'lxml')
                            tgLink = beautifulSoup.find(attrs={'name': 'twitter:app:url:googleplay'}).get('content')
                        except:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/bots')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Message bot" botton below' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    clientTelegram.send_message(Ltc, '/bots')
                        blackList = False
                        blackList_ = numpy.array(db.cursor.execute('SELECT URL '
                                                                   'FROM bot_blacklist').fetchall())
                        for i in blackList_:
                            urlBlackList = str(i[0])
                            if tgLink in urlBlackList:
                                blackList = True
                                break
                        if blackList is True:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/bots')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Message bot" botton below' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/bots')
                            break
                        try:
                            botName = beautifulSoup.find(class_='tgme_page_extra').get_text(strip=True)
                            botTitle = beautifulSoup.find(attrs={'property': 'og:title'}).get('content')
                        except AttributeError:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/bots')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Press the "Message bot" botton below' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/bots')
                        try:
                            time.sleep(1)
                            clientTelegram(StartBotRequest(bot=botName, peer=tgLink, start_param='0'))
                        except:
                            time.sleep(1)
                            clientTelegram.send_message(Ltc, '/bots')
                            while True:
                                time.sleep(1)
                                try:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Forward a message to me from the bot to earn LTC.' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/bots')
                            break
                        counter = 0
                        while True:
                            time.sleep(1)
                            try:
                                getMessage = clientTelegram.get_messages(botTitle, limit=3)
                                if counter >= 20:
                                    print('[{0}] Превышено время ожидания ответа от бота.'.format(
                                        datetime.datetime.now().strftime("%H:%M:%S"), botName))
                                    print(
                                        '==========================================='
                                        '============================================')
                                    db.cursor.execute('INSERT INTO bot_blacklist '
                                                      '(URL) VALUES ("{0}")'.format(tgLink))
                                    db.connection.commit()
                                    time.sleep(1)
                                    clientTelegram.delete_dialog(botTitle)
                                    time.sleep(1)
                                    clientTelegram.send_message(Ltc, '/bots')
                                    while True:
                                        time.sleep(1)
                                        try:
                                            getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                            if 'Press the "Message bot" botton below' in getMessage[0].message:
                                                buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                                messageId = getMessage[0].id
                                                clientTelegram(GetBotCallbackAnswerRequest(Ltc, messageId, data=buttons))
                                                break
                                        except AttributeError:
                                            time.sleep(1)
                                            clientTelegram.send_message(Ltc, '/bots')
                                    break
                                elif accountInformation[4] not in str(getMessage[0].from_id):
                                    messageId = getMessage[0].id
                                    time.sleep(1)
                                    clientTelegram.forward_messages(Ltc, messageId, botTitle)
                                    time.sleep(1)
                                    clientTelegram.delete_dialog(botTitle)
                                    time.sleep(1)
                                    clientTelegram.disconnect()
                                    print('[{0}] Получили награду на аккаутне {1} за запуск бота.'.format(
                                        datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                                    print(
                                        '==========================================='
                                        '============================================')
                                    stop = True
                                    break
                                counter += 1
                                time.sleep(1)
                            except AttributeError:
                                time.sleep(1)
                                clientTelegram.send_message(Ltc, '/bots')
                        if stop is True:
                            break
                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/bots')
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/bots')
                    elif 'new chat to /join' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(Ltc, '/bots')
            except UserDeactivatedBanError:
                print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                print(
                    '==========================================='
                    '============================================')
                clientTelegram.disconnect()
                db.cursor.execute('DELETE FROM account_information '
                                  'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
                db.connection.commit()
                logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            except FloodWaitError:
                print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                print(
                    '==========================================='
                    '============================================')
                clientTelegram.disconnect()

def TimeToExit():
    for accountId in numpy.array(db.cursor.execute('SELECT ACCOUNT_ID '
                                                   'FROM account_information').fetchall(), dtype=str):
        for time_ in numpy.array(db.cursor.execute('SELECT TIME_LEAVE '
                                                   'FROM channel_info '
                                                   'WHERE ACCOUNT_ID = {0}'.format(
                accountId[0])).fetchall(), dtype=str):
            try:
                timeLeave = datetime.datetime.strptime(time_[0], '%Y-%m-%d %H:%M:%S.%f')
                timeNow = datetime.datetime.now()
                compareTime = timeLeave < timeNow
                if compareTime is True:
                    channelId = numpy.array(db.cursor.execute('SELECT CHANNEL_ID '
                                                         'FROM channel_info '
                                                         'WHERE TIME_LEAVE = "{0}"'.format(
                        time_[0])).fetchone(), dtype=str)
                    accountInformation = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID,'
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information '
                                                           'WHERE ACCOUNT_ID = {0}'.format(
                        accountId[0])).fetchone(), dtype=str)
                    clientTelegram = TelegramClient(
                        StringSession(accountInformation[3]), accountInformation[1], accountInformation[2])
                    clientTelegram.connect()
                    for dialogs in clientTelegram.get_dialogs():
                        if str(channelId[0]) in str(dialogs.id):
                            dialogs.delete()
                            break
                    db.cursor.execute(f'DELETE FROM channel_info WHERE TIME_LEAVE = "{time_[0]}"')
                    db.connection.commit()
                    clientTelegram.disconnect()
            except UserDeactivatedBanError:
                print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                print(
                    '==========================================='
                    '============================================')
                clientTelegram.disconnect()
                db.cursor.execute('DELETE FROM account_information '
                                  'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
                db.connection.commit()
                logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            except FloodWaitError:
                print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                    datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                print(
                    '==========================================='
                    '============================================')
                clientTelegram.disconnect()

def CheckBalance():
    overallRubBalance = 0
    overallLTCBalance = 0
    print('\n[{0}] Функция проверки баланса @Litecoin_Click_bot активирована активирована.\n'.format(
        datetime.datetime.now().strftime("%H:%M:%S")))
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall(), dtype=str)
    for accountInformation in accountInformationList:
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            findLtc = False
            for dialogs in clientTelegram.get_dialogs():
                if dialogs.title == 'LTC Click Bot':
                    Ltc = dialogs
                    findLtc = True
                    break
            if findLtc is False:
                print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                    datetime.datetime.now().strftime("%H:%M:%S")))
                print(
                    '==========================================='
                    '============================================')
                break
            clientTelegram.send_message(Ltc, '/balance')
            while True:
                time.sleep(1)
                getMessage = clientTelegram.get_messages(Ltc, limit=3)
                if 'Available balance' in getMessage[0].message:
                    copyMessage = getMessage[0].message
                    searchPattern = re.compile(r'\d.\d{1,9}')
                    findBalance = searchPattern.search(copyMessage)
                    balanceLitecoin = findBalance.group()
                    CoinGecko = CoinGeckoAPI()
                    balanceRubles = float(CoinGecko.get_price(
                        ids='litecoin', vs_currencies='rub')['litecoin']['rub']) * float(balanceLitecoin)
                    overallRubBalance += balanceRubles
                    overallLTCBalance += float(balanceLitecoin)
                    print('[{0}] Баланс аккаунта {1}: {2} руб или {3} LTC.'.format
                          (datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0],
                           round(balanceRubles, 2), balanceLitecoin))
                    print('================================================================================')
                    clientTelegram.disconnect()
                    break
        except UserDeactivatedBanError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()
            db.cursor.execute('DELETE FROM account_information '
                              'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
            db.connection.commit()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        except FloodWaitError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()
    print('[{0}] Общий баланс {1} руб. или {2} LTC.'.format(
        datetime.datetime.now().strftime("%H:%M:%S"),
        round(overallRubBalance, 2), round(overallLTCBalance, 8)))
    print('================================================================================')

def WithdrawBalance():
    print('\n[{0}] Функция вывода средств с баланса @Litecoin_Click_bot активирована.\n'.format(
        datetime.datetime.now().strftime("%H:%M:%S")))
    accountInformationList = numpy.array(db.cursor.execute('SELECT PHONE_NUMBER, '
                                                           'API_ID, '
                                                           'API_HASH, '
                                                           'STRING_SESSION, '
                                                           'ACCOUNT_ID '
                                                           'FROM account_information').fetchall(), dtype=str)
    for accountInformation in accountInformationList:
        try:
            clientTelegram = TelegramClient(StringSession(
                accountInformation[3]), accountInformation[1], accountInformation[2])
            clientTelegram.connect()
            findLtc = False
            for dialogs in clientTelegram.get_dialogs():
                if dialogs.title == 'LTC Click Bot':
                    Ltc = dialogs
                    findLtc = True
                    break
            if findLtc is False:
                print('[{0}] Проверьте, выполнили ли вы комманду ./startLtcBot'.format(
                    datetime.datetime.now().strftime("%H:%M:%S")))
                print(
                    '==========================================='
                    '============================================')
                break
            clientTelegram.send_message(Ltc, '/balance')
            while True:
                getMessage = clientTelegram.get_messages(Ltc, limit=3)
                if 'Available balance' in getMessage[0].message:
                    copyMessageWithBalance = getMessage[0].message
                    templateSearch = re.compile(r'\d.\d{1,9}')
                    findBalance = templateSearch.search(copyMessageWithBalance)
                    balanceLitecoin = findBalance.group()
                    if float(balanceLitecoin) >= 0.0003:
                        print('[{0}] Функция вывода средств на аккаунте {1} активирована.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                        print('================================================================================')
                        clientTelegram.send_message(Ltc, '/withdraw')
                        while True:
                            getMessage = clientTelegram.get_messages(Ltc, limit=3)
                            if 'To withdraw, enter your Litecoin address' in getMessage[0].message:
                                time.sleep(1)
                                clientTelegram.send_message(Ltc, accountInformation[4])
                                while True:
                                    getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                    if 'Enter the amount to withdraw' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(Ltc, balanceLitecoin)
                                        while True:
                                            getMessage = clientTelegram.get_messages(Ltc, limit=3)
                                            if 'Are you sure you want to send' in getMessage[0].message:
                                                time.sleep(1)
                                                clientTelegram.send_message(Ltc, '✅ Confirm')
                                                break
                                        break
                                break
                        break
                    else:
                        print('[{0}] На аккаунте {1} недостаточно средств для вывода.'.format(
                            datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
                        print('================================================================================')
                        break
        except UserDeactivatedBanError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.\n'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()
            db.cursor.execute('DELETE FROM account_information '
                              'WHERE PHONE_NUMBER = {0}'.format(accountInformation[0]))
            db.connection.commit()
            logging.error('[{0}] ВНИМАНИЕ! Аккаунт {1} забанен. Удаляем данные об аккаунте из базы.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
        except FloodWaitError:
            print('[{0}] ВНИМАНИЕ! Аккаунт {1} временно заблокирован за флуд.'.format(
                datetime.datetime.now().strftime("%H:%M:%S"), accountInformation[0]))
            print(
                '==========================================='
                '============================================')
            clientTelegram.disconnect()






