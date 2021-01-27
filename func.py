#!C:\Users\Misha\AppData\Local\Programs\Python\Python39\python.exe
# coding: utf8

import time
import datetime
import re
import requests
import telethon
import sqlite3
import bs4
import json
import logging
import multiprocessing
from pycoingecko import CoinGeckoAPI
from telethon.sync import TelegramClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telethon import  functions
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest, StartBotRequest, DeleteChatUserRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError, UserDeactivatedBanError, \
    StartParamInvalidError, UserNotParticipantError, PeerIdInvalidError, UsernameNotOccupiedError
from telethon.sessions import StringSession

waitTime = 1

logging.basicConfig(filename="TelegramFarmErrors.log", level=logging.ERROR)

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('telethon').setLevel('CRITICAL')
logging.getLogger('selenium').setLevel('CRITICAL')

class SQLite:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def createTableAccountInformation(self):
        with self.connection:
            return self.cursor.execute('''CREATE TABLE IF NOT EXISTS account_information
                                    (ID INTEGER PRIMARY KEY NOT NULL, 
                                    PHONE_NUMBER TEXT UNIQUE,
                                    API_ID TEXT UNIQUE,
                                    API_HASH TEXT UNIQUE,
                                    STRING_SESSION TEXT UNIQUE,
                                    ACCOUNT_ID TEXT UNIQUE,
                                    ADDRESS TEXT UNIQUE)''')

    def createTableBotBlacklist(self):
        with self.connection:
            return self.cursor.execute('''CREATE TABLE IF NOT EXISTS bot_blacklist
                                    (ID INTEGER PRIMARY KEY NOT NULL,
                                    URL TEXT UNIQUE)''')

    def createTableChannelInfo(self):
        with self.connection:
            return  self.cursor.execute('''CREATE TABLE IF NOT EXISTS channel_info
                                        (CHANNEL_ID TEXT, 
                                        TIME_LEAVE TEXT,
                                        ACCOUNT_ID TEXT)''')

    def createTableSettings(self):
        with self.connection:
            return self.connection.execute('''CREATE TABLE IF NOT EXISTS settings
                                            (ID INTEGER PRIMARY KEY NOT NULL,
                                            REFFERAL_CODE TEXT UNIQUE,
                                            BLOCKIO_API_KEY TEXT UNIQUE)''')

    def selectAccount(self, ID):
        with self.connection:
            return self.cursor.execute(f'SELECT * FROM account_information WHERE ID = {ID}').fetchone()

db = SQLite('telegram_farm.db')
db.createTableAccountInformation()
db.createTableBotBlacklist()
db.createTableChannelInfo()
db.createTableSettings()

class LitecoinBot:

    @staticmethod
    def CreateSession():
        x = 1
        if db.cursor.execute(f'''SELECT ID FROM settings WHERE ID = 1''').fetchone() is None:
            print(f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                  f'Перед тем, как создать сессии, добавьте реферальный код и Api ключ.\n'
                  'Выполните комманду ./addRefCodeAndApiKey')
        else:
            for accountInformation in db.cursor.execute(
                    f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION FROM account_information').fetchall():
                phoneNumber = accountInformation[0]; apiId = accountInformation[1]
                apiHash = accountInformation[2]; stringSession = accountInformation[3]
                clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
                clientTelegram.connect()
                try:
                    if clientTelegram.is_user_authorized():
                        x += 1
                    else:
                        while True:
                            clientTelegram.send_code_request(phoneNumber)
                            try:
                                clientTelegram.sign_in(phoneNumber, input(
                                    f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                    f'Введите код, отправленный на аккаунт {phoneNumber}: '))
                            except PhoneCodeInvalidError:
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Введён неправильный код подтверждения.')
                                print('================================================================================')
                                break
                            stringSession = StringSession.save(clientTelegram.session)
                            userIdStr = str(clientTelegram.get_me('id')); templateSearch = re.compile(r'\d.\d{1,12}')
                            findUserId = templateSearch.search(userIdStr); userId = findUserId.group()
                            blockIoApiKey = db.cursor.execute(
                                '''SELECT BLOCKIO_API_KEY FROM settings WHERE ID = 1''').fetchone()[0]
                            requestsGetToBlockIo = requests.get(
                                f'https://block.io/api/v2/get_new_address/?api_key={blockIoApiKey}')
                            answerJsonFromBlockIo = json.loads(requestsGetToBlockIo.text)
                            try:
                                addressLiteCoin = answerJsonFromBlockIo['data']['address']
                            except KeyError:
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Введён неверный Api ключ с сайта https://block.io/ Выполните комманду\n'
                                      './updApiKey')
                                break
                            else:
                                db.cursor.execute(f'UPDATE account_information SET STRING_SESSION = "{stringSession}", '
                                              f'ACCOUNT_ID = "{userId}", ADDRESS = "{addressLiteCoin}" WHERE ID = "{x}"')
                                db.connection.commit()
                                clientTelegram.disconnect()
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Вход в аккаунт {phoneNumber} выполнен успешно.')
                                print(
                                    '================================================================================')
                                x += 1
                                break
                except UserDeactivatedBanError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                          f'Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                          f'================================================================================')
                    logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                    logging.error('================================================================================')
                    db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                    db.connection.commit()
            print('\nСессии для всех аккаунтов созданы успешно.')

    @staticmethod
    def StartLitecoinBot():
        if db.cursor.execute(f'''SELECT ID FROM settings WHERE ID = 1''').fetchone() is None:
            print(f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                  f'Перед началом работы добавьте реферальный код и Api ключ.\n'
                  'Выполните комманду ./addRefCodeAndApiKey')
        else:
            for accountInformation in db.cursor.execute(
                    f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION FROM account_information').fetchall():
                phoneNumber = accountInformation[0]; apiId = accountInformation[1]
                apiHash = accountInformation[2]; stringSession = accountInformation[3]
                clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
                clientTelegram.connect()
                try:
                    clientTelegram(functions.messages.StartBotRequest(
                        bot='Litecoin_click_bot',
                        peer='https://t.me/Litecoin_click_bot',
                        start_param=str(
                            db.cursor.execute('''SELECT REFFERAL_CODE FROM settings WHERE ID = 1''').fetchone()[0])))
                except UserDeactivatedBanError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                          f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                          f'================================================================================')
                    logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                    logging.error('================================================================================')
                    db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                    db.connection.commit()
                except StartParamInvalidError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                          f'Введён неверный реферальный код. Попробуйте ещё раз.')
                else:
                    print(
                        f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                        f'Аккаунт {phoneNumber} подписан на @Litecoin_click_bot.')
                    print('================================================================================')
                    clientTelegram.disconnect()

    @staticmethod
    def VisitSites():
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION FROM account_information').fetchall():
            phoneNumber = accountInformation[0];apiId = accountInformation[1]
            apiHash = accountInformation[2];stringSession = accountInformation[3]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                  f'Аккаунт {phoneNumber} в работе. Функция: посещение сайтов.')
            print('================================================================================')
            try:
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        LTC = dialogs
                        break
                try:
                    clientTelegram.send_message(LTC, '/visit')
                except UnboundLocalError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Проверьте, выполнили ли вы комманду'
                          f'./startLtcBot')
                    break
                while True:
                    time.sleep(waitTime)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.disconnect()
                        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'Для аккаунта {phoneNumber} нет доступных заданий по посещению сайтов. '
                              f'Переходим на другой аккаунт.')
                        print('================================================================================')
                        break
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/visit')
                        time.sleep(waitTime)
                    elif 'There is a new /join' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/visit')
                        time.sleep(waitTime)
                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/visit')
                        time.sleep(waitTime)
                    elif 'Press the "Visit website"' in getMessage[0].message:
                        time.sleep(waitTime)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        chromeOptions = Options(); chromeOptions.add_argument('--headless',)
                        browserChrome = webdriver.Chrome(r'C:\Users\Misha\Desktop\bot_v2\chromedriver.exe',
                                                   options=chromeOptions)
                        try:
                            browserChrome.get(url=url)
                        except:
                            print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'Возникла ошибка при открытии браузера.')
                            print('================================================================================')
                            logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                          f'Возникла ошибка при открытии браузера.')
                            logging.debug(
                                '================================================================================')
                            browserChrome.quit()
                            time.sleep(waitTime)
                            clientTelegram.send_message(LTC, '/visit')
                            while True:
                                try:
                                    time.sleep(waitTime)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Press the "Visit website" button to earn LTC' in getMessage[0].message:
                                        time.sleep(waitTime)
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(waitTime)
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    clientTelegram.send_message(LTC, '/visit')
                                    time.sleep(waitTime)
                            break
                        while True:
                            time.sleep(waitTime)
                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                            if 'You earned' in getMessage[0].message or 'You earned' in  getMessage[1].message:
                                browserChrome.quit()
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Получили награду на аккаунте {phoneNumber} за посещение сайта.')
                                print('================================================================================')
                                break
                        break
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанет. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
            except PeerIdInvalidError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}]'
                      f' @Litecoin_click_bot на запущен на аккаунте {phoneNumber}. '
                      f'Выполните комманду ./startLtcBot')
                break
        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Посещение сайтов - круг пройден.')
        print('================================================================================')

    @staticmethod
    def SubscribeBot():
        y = 0
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION, ACCOUNT_ID FROM account_information').fetchall():
            phoneNumber = accountInformation[0];apiId = accountInformation[1]
            apiHash = accountInformation[2];stringSession = accountInformation[3]
            accountId = accountInformation[4]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            if y == 0:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'Аккаунт {phoneNumber} в работе. Функция: запуск ботов.')
                print('================================================================================')
            y = 1
            try:
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        LTC = dialogs
                        break
                try:
                    clientTelegram.send_message(LTC, '/bots')
                except UnboundLocalError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Проверьте, выполнили ли вы комманду'
                          f'./startLtcBot')
                    break
                while True:
                    time.sleep(waitTime)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.disconnect()
                        print( f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                               f'Для аккаунта {phoneNumber} нет доступных заданий по запуску ботов'
                               f'. Переходим на другой аккаунт.')
                        print('================================================================================')
                        y = 0
                        break
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/bots')
                        time.sleep(waitTime)
                    elif 'There is a new /join' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/bots')
                        time.sleep(waitTime)
                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                        clientTelegram.send_message(LTC, '/bots')
                        time.sleep(waitTime)
                    elif 'Press the "Message bot" botton below' in getMessage[0].message:
                        time.sleep(waitTime)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        try:
                            requestsPost = requests.post(url)
                        except TimeoutError:
                            clientTelegram.send_message(LTC, '/bots')
                            time.sleep(waitTime)
                            while True:
                                try:
                                    time.sleep(waitTime)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Press the "Message bot" botton below' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        break
                                except AttributeError:
                                    clientTelegram.send_message(LTC, '/bots')
                                    time.sleep(waitTime)
                                break
                        beautifulSoup = bs4.BeautifulSoup(requestsPost.text, 'lxml')
                        tgLink = beautifulSoup.find(attrs={'name':'twitter:app:url:googleplay'}).get('content')
                        blackList = False
                        for i in db.cursor.execute('SELECT URL FROM bot_blacklist'):
                            urlBlackList = str(i[0])
                            if tgLink in urlBlackList:
                                blackList = True
                                break
                        if blackList is True:
                            time.sleep(waitTime)
                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                            messageId = getMessage[0].id
                            time.sleep(waitTime)
                            clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                            break
                        else:
                            try:
                                botName = beautifulSoup.find(class_='tgme_page_extra').get_text(strip=True)
                                botTitle = beautifulSoup.find(attrs={'property':'og:title'}).get('content')
                            except AttributeError:
                                clientTelegram.send_message(LTC, '/bots')
                                time.sleep(waitTime)
                                while True:
                                    try:
                                        time.sleep(waitTime)
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        if 'Press the "Message bot" botton below' in getMessage[0].message:
                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                            messageId = getMessage[0].id
                                            clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                            break
                                    except AttributeError:
                                        clientTelegram.send_message(LTC, '/bots')
                                        time.sleep(waitTime)
                            try:
                                time.sleep(waitTime)
                                clientTelegram(StartBotRequest(bot=botName, peer=tgLink, start_param='0'))
                            except:
                                clientTelegram.send_message(LTC, '/bots')
                                time.sleep(waitTime)
                                while True:
                                    try:
                                        time.sleep(waitTime)
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        if 'Forward a message to me from the bot to earn LTC.' in getMessage[0].message:
                                            time.sleep(waitTime)
                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                            messageId = getMessage[0].id
                                            time.sleep(waitTime)
                                            clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                            break
                                    except AttributeError:
                                        clientTelegram.send_message(LTC, '/bots')
                                        time.sleep(waitTime)
                                break
                            counter = 0
                            while True:
                                try:
                                    time.sleep(waitTime)
                                    getMessage = clientTelegram.get_messages(botTitle, limit=3)
                                    if counter == 20:
                                        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                              f'Превышено время ожидания ответа от бота {botName}.')
                                        print(
                                        '================================================================================')
                                        db.cursor.execute(f'INSERT INTO bot_blacklist (URL) VALUES ("{tgLink}")')
                                        db.connection.commit()
                                        time.sleep(waitTime)
                                        clientTelegram.delete_dialog(botTitle)
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(waitTime)
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        break
                                    elif accountId not in str(getMessage[0].from_id):
                                        time.sleep(waitTime)
                                        messageId = getMessage[0].id
                                        time.sleep(waitTime)
                                        clientTelegram.forward_messages(LTC, messageId, botTitle)
                                        time.sleep(waitTime)
                                        clientTelegram.delete_dialog(botTitle)
                                        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                              f'Получили награду на аккаутне {phoneNumber} за запуск бота.')
                                        print(
                                        '================================================================================')
                                        y = 0
                                        break
                                    counter += 2
                                    time.sleep(waitTime)
                                except AttributeError:
                                    clientTelegram.send_message(LTC, '/bots')
                                    time.sleep(waitTime)
                            break
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Запуск ботов - круг пройден.')
        print('================================================================================')

    @staticmethod
    def JoinChannel():
        y = 0
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION, ACCOUNT_ID FROM account_information').fetchall():
            phoneNumber = accountInformation[0];apiId = accountInformation[1]
            apiHash = accountInformation[2]; stringSession = accountInformation[3]
            accountId = accountInformation[4]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            if y == 0:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'Аккаунт {phoneNumber} в работе. Функция: подписка на каналы.')
                print('================================================================================')
            y = 1
            x = 1
            try:
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        LTC = dialogs
                        break
                try:
                    clientTelegram.send_message(LTC, '/join')
                except UnboundLocalError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Проверьте, выполнили ли вы комманду'
                          f'./startLtcBot')
                    break
                while True:
                    time.sleep(waitTime)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.disconnect()
                        print( f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                               f'Для аккаунта {phoneNumber} нет доступных заданий. Переходим на другой аккаунт.')
                        print('================================================================================')
                        y = 0
                        break
                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.send_message(LTC, '/join')
                    elif 'In the past hour, you earned' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.send_message(LTC, '/join')
                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.send_message(LTC, '/join')
                    elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                        time.sleep(waitTime)
                        clientTelegram.send_message(LTC, '/join')
                    elif 'Press the "Go to channel" button below' in getMessage[0].message or \
                            'Press the "Go to group" button' in getMessage[0].message:
                        time.sleep(waitTime)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        requestsGet = requests.get(url)
                        beautifulSoup = bs4.BeautifulSoup(requestsGet.text, 'lxml')
                        try:
                            findChannelName = beautifulSoup.find('title').get_text(strip=True)
                            findChannelTitle = beautifulSoup.find(class_="tgme_page_title").get_text(strip=True)
                            channelName = findChannelName.replace('Telegram: Contact ', '')
                        except AttributeError:
                            clientTelegram.send_message(LTC, '/join')
                            time.sleep(waitTime)
                            while True:
                                try:
                                    time.sleep(waitTime)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Press the "Go to channel" button below' in getMessage[0].message or \
                            'Press the "Go to group" button' in getMessage[0].message:
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        time.sleep(waitTime)
                                        break
                                except AttributeError:
                                    clientTelegram.send_message(LTC, '/join')
                                    time.sleep(waitTime)
                        else:
                            try:
                                time.sleep(waitTime)
                                clientTelegram(JoinChannelRequest(channelName))
                            except FloodWaitError:
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Аккаунт {phoneNumber} временно заблокирован за флуд.')
                                print('================================================================================')
                                logging.error(
                                    f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                    f'Аккаунт {phoneNumber} временно заблокирован за флуд.')
                                logging.error(
                                     '================================================================================')
                                break
                            except:
                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                      f'Канала {channelName} не существует. Пропускаем задание.')
                                print('================================================================================')
                                while True:
                                    try:
                                        time.sleep(waitTime)
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        if accountId not in str(getMessage[0].from_id):
                                            time.sleep(waitTime)
                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                            messageId = getMessage[0].id
                                            clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                            time.sleep(waitTime)
                                            break
                                    except AttributeError:
                                        clientTelegram.send_message(LTC, '/join')
                                        time.sleep(waitTime)
                                    break
                            while True:
                                time.sleep(waitTime)
                                try:
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Press the "Go to channel" button below' or \
                                            'Press the "Go to group" button below' in \
                                            getMessage[0].message or getMessage[1].message:
                                        time.sleep(waitTime)
                                        buttons = getMessage[0].reply_markup.rows[0].buttons[1].data
                                        messageId = getMessage[0].id
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        while True:
                                            time.sleep(waitTime)
                                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                                            if 'Success' in getMessage[1].message:
                                                time.sleep(waitTime)
                                                for dialogs in clientTelegram.get_dialogs():
                                                    if dialogs.title == findChannelTitle:
                                                        channelId = dialogs.id
                                                        break
                                                copyMessage = getMessage[1].message; searchPattern = re.compile(r'\d{1,2}')
                                                findTime = searchPattern.search(copyMessage)
                                                time_ = findTime.group()
                                                timeJoin = datetime.datetime.now()
                                                timeDelta = datetime.timedelta(hours=int(time_))
                                                timeLeave = timeJoin + timeDelta
                                                db.cursor.execute(f'''INSERT INTO channel_info 
                                                                    (CHANNEL_ID, TIME_LEAVE, ACCOUNT_ID)
                                                                    VALUES (?, ?, ?)''', (channelId, timeLeave, accountId))
                                                db.connection.commit()
                                                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                                      f'На аккаунте {phoneNumber} успешно выполнено задание по '
                                                      f'подписке на канал {channelName}.')
                                                print(
                                                    '================================================================================')
                                                y = 0
                                                x = 0
                                                break
                                            elif 'If this message persists' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram(LeaveChannelRequest(channelName))
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                while True:
                                                    try:
                                                        time.sleep(waitTime)
                                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                                        if 'After joining, press the "Joined" button to earn LTC.' in \
                                                                getMessage[0].message:
                                                            time.sleep(waitTime)
                                                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                                            messageId = getMessage[0].id
                                                            time.sleep(waitTime)
                                                            clientTelegram(
                                                                GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                                            break
                                                    except AttributeError:
                                                        clientTelegram.send_message(LTC, '/join')
                                                        time.sleep(waitTime)
                                                break
                                            elif 'Please press the "🔎 Go to channel" button' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            elif 'Sorry, that task is no longer valid. 😟' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                for dialogs in clientTelegram.iter_dialogs():
                                                    if str(channelId) in str(dialogs.id):
                                                        dialogs.delete()
                                                        break
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            elif 'In the past hour, you earned' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                                                time.sleep(waitTime)
                                                clientTelegram.send_message(LTC, '/join')
                                                break
                                            else:
                                                pass
                                        break
                                    elif 'There is a new site for you to /visit! 🖥' in getMessage[0].message:
                                        time.sleep(waitTime)
                                        clientTelegram.send_message(LTC, '/join')
                                    elif 'In the past hour, you earned' in getMessage[0].message:
                                        time.sleep(waitTime)
                                        clientTelegram.send_message(LTC, '/join')
                                    elif 'There is a new /bot for you to message! 🤖' in getMessage[0].message:
                                        time.sleep(waitTime)
                                        clientTelegram.send_message(LTC, '/join')
                                    elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                                        time.sleep(waitTime)
                                        clientTelegram.send_message(LTC, '/join')
                                except AttributeError:
                                    clientTelegram.send_message(LTC, '/join')
                                    time.sleep(waitTime)
                            if x == 0:
                                break
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Подписка на каналы - круг пройден.')
        print('================================================================================')

    @staticmethod
    def TimeToExit():
        while True:
            try:
                for time_ in db.cursor.execute('SELECT TIME_LEAVE FROM channel_info').fetchall():
                    timeLeave = datetime.datetime.strptime(time_[0], '%Y-%m-%d %H:%M:%S.%f')
                    timeNow = datetime.datetime.now()
                    compareTime = timeLeave < timeNow
                    if compareTime is True:
                        accountId = db.cursor.execute(f'SELECT ACCOUNT_ID'
                                                      f' FROM channel_info WHERE TIME_LEAVE = "{time_[0]}" ').fetchone()
                        channelID = db.cursor.execute(f'SELECT CHANNEL_ID '
                                                        f'FROM channel_info WHERE TIME_LEAVE = "{time_[0]}"').fetchone()
                        for accountInformation in db.cursor.execute(f'SELECT PHONE_NUMBER, '
                                                                    f'API_ID, '
                                                                    f'API_HASH, '
                                                                    f'STRING_SESSION '
                                                                    f'FROM account_information '
                                                                    f'WHERE ACCOUNT_ID = "{accountId[0]}"').fetchall():
                            phoneNumber = accountInformation[0]; apiId = accountInformation[1]
                            apiHash = accountInformation[2]; stringSession = accountInformation[3]
                            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
                            clientTelegram.connect()
                            time.sleep(waitTime)
                            try:
                                time.sleep(waitTime)
                                for dialogs in clientTelegram.iter_dialogs():
                                    if str(channelID) in str(dialogs.id):
                                        dialogs.delete()
                            except:
                                pass
                            finally:
                                db.cursor.execute(f'DELETE FROM channel_info WHERE TIME_LEAVE = "{time_[0]}"')
                                db.connection.commit()
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ!Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def CheckBalance():
        x = 1
        overallRubBalance = 0
        overallLTCBalance = 0
        print(f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] Получаем балансы...\n')
        while True:
            try:
                phoneNumber = db.selectAccount(x)[1]; apiId = db.selectAccount(x)[2]
                apiHash = db.selectAccount(x)[3];stringSession = db.selectAccount(x)[4]
            except:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'Общий баланс {round(overallRubBalance, 2)} руб. или {round(overallLTCBalance, 8)} LTC.')
                print('================================================================================')
                break
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            try:
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        LTC = dialogs
                        break
                try:
                    clientTelegram.send_message(LTC, '/balance')
                except UnboundLocalError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Проверьте, выполнили ли вы комманду'
                          f'./startLtcBot')
                    break
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Available balance' in getMessage[0].message:
                        time.sleep(1)
                        copyMessage = getMessage[0].message; searchPattern = re.compile(r'\d.\d{1,9}')
                        findBalance = searchPattern.search(copyMessage); balanceLitecoin = findBalance.group()
                        CoinGecko = CoinGeckoAPI()
                        balanceRubles = float(CoinGecko.get_price(
                            ids='litecoin', vs_currencies='rub')['litecoin']['rub'])*float(balanceLitecoin)
                        overallRubBalance += balanceRubles
                        overallLTCBalance += float(balanceLitecoin)
                        print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'Баланс аккаунта {phoneNumber}: {round(balanceRubles, 2)} руб '
                              f'или {balanceLitecoin} LTC.')
                        print('================================================================================')
                        clientTelegram.disconnect()
                        x += 1
                        break
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def WithdrawBalance():
        print(f'\n[{datetime.datetime.now().strftime("%H:%M:%S")}] Полуачем балансы...\n')
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION, ADDRESS FROM account_information').fetchall():
            phoneNumber = accountInformation[0]; apiId = accountInformation[1]
            apiHash = accountInformation[2]; stringSession = accountInformation[3]
            litecoinAddress = accountInformation[4]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            try:
                for dialogs in clientTelegram.get_dialogs():
                    if dialogs.title == 'LTC Click Bot':
                        LTC = dialogs
                        break
                try:
                    clientTelegram.send_message(LTC, '/balance')
                except UnboundLocalError:
                    print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] Проверьте, выполнили ли вы комманду'
                          f'./startLtcBot')
                    break
                while True:
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Available balance' in getMessage[0].message:
                        copyMessageWithBalance = getMessage[0].message; templateSearch = re.compile(r'\d.\d{1,9}')
                        findBalance = templateSearch.search(copyMessageWithBalance); balanceLitecoin = findBalance.group()
                        if float(balanceLitecoin) == 0.0003 or float(balanceLitecoin) > 0.0004:
                            print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'Функция вывода средств на аккаунте {phoneNumber} активирована.')
                            print('================================================================================')
                            clientTelegram.send_message(LTC, '/withdraw')
                            while True:
                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                if 'To withdraw, enter your Litecoin address' in getMessage[0].message:
                                    time.sleep(waitTime)
                                    clientTelegram.send_message(LTC, litecoinAddress)
                                    while True:
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        if 'Enter the amount to withdraw' in getMessage[0].message:
                                            time.sleep(waitTime)
                                            clientTelegram.send_message(LTC, balanceLitecoin)
                                            while True:
                                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                                if 'Are you sure you want to send' in getMessage[0].message:
                                                    time.sleep(waitTime)
                                                    clientTelegram.send_message(LTC, '✅ Confirm')
                                                    break
                                            break
                                    break
                            break
                        else:
                            print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                                  f'На аккаунте {phoneNumber} недостаточно средств для вывода.')
                            print('================================================================================')
                            break
            except UserDeactivatedBanError:
                print(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                      f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'[{datetime.datetime.now().strftime("%H:%M:%S")}] '
                              f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
            except PeerIdInvalidError:
                print(f'@Litecoin_click_bot на запущен на аккаунте {phoneNumber}. '
                      f'Выполните комманду ./startLtcBot')
                break






