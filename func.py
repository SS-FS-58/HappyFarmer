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
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest, StartBotRequest
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError, FloodWaitError, UserDeactivatedBanError, \
    StartParamInvalidError, UserNotParticipantError
from telethon.sessions import StringSession

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
                                        (CHANNEL_NAME TEXT, 
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
                                f'\nВведите код, отправленный на аккаунт {phoneNumber}: '))
                        except PhoneCodeInvalidError:
                            print('Введён неправильный код подтверждения.')
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
                            db.cursor.execute(f'UPDATE account_information SET STRING_SESSION = "{stringSession}", '
                                          f'ACCOUNT_ID = "{userId}", ADDRESS = "{addressLiteCoin}" WHERE ID = "{x}"')
                            db.connection.commit()
                            clientTelegram.disconnect()
                            print(f'Вход в аккаунт {phoneNumber} выполнен успешно.')
                            print(
                                '================================================================================')
                            x += 1
                            break
                        except KeyError:
                            print('Добавьте Api ключ с сайта https://block.io/')
                            break
            except UserDeactivatedBanError:
                print(f'Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
        print('\nСессии для всех аккаунтов созданы успешно.')

    @staticmethod
    def TryLogIn():
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION FROM account_information').fetchall():
            phoneNumber = accountInformation[0]; apiId = accountInformation[1]
            apiHash = accountInformation[2]; stringSession = accountInformation[3]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            if clientTelegram.is_user_authorized() is False:
                print(f'Вход в аккаунт {phoneNumber} не выполнен.')
                print('================================================================================')
                clientTelegram.disconnect()
                return False

    @staticmethod
    def StartLitecoinBot():
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION FROM account_information').fetchall():
            phoneNumber = accountInformation[0]; apiId = accountInformation[1]
            apiHash = accountInformation[2]; stringSession = accountInformation[3]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            try:
                try:
                    clientTelegram(functions.messages.StartBotRequest(
                        bot='a',
                        peer='https://t.me/Litecoin_click_bot',
                        start_param=str(
                            db.cursor.execute('''SELECT REFFERAL_CODE FROM settings WHERE ID = 1''').fetchone()[1])))
                    print(f'Аккаунт {phoneNumber} подписан на @Litecoin_click_bot.')
                    print('================================================================================')
                except:
                    print('\nДобавьте реферальный код.')
                clientTelegram.disconnect()
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
            except StartParamInvalidError:
                print('Введён неверный реферальный код. Попробуйте ещё раз.')

    @staticmethod
    def VisitSites():
        x = 1
        while True:
            try:
                phoneNumber = db.selectAccount(x)[1];apiId = db.selectAccount(x)[2]
                apiHash = db.selectAccount(x)[3]; stringSession = db.selectAccount(x)[4]
            except:
                print('Посещение сайтов - круг пройден.')
                print('================================================================================')
                break
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            print(f'Аккаунт {phoneNumber} в работе. Функция: просмотр сайтов.')
            print('================================================================================')
            try:
                for i in clientTelegram.get_dialogs():
                    if i.title == 'LTC Click Bot':
                        LTC = i
                        break
                clientTelegram.send_message(LTC, '/visit')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.disconnect()
                        print(f'Для аккаунта {phoneNumber} нет доступных заданий. Переходим на другой аккаунт.')
                        print('================================================================================')
                        x += 1
                        break
                    elif 'Press the "Visit website"' in getMessage[0].message:
                        time.sleep(1)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        chromeOptions = Options(); chromeOptions.add_argument('--headless',)
                        browserChrome = webdriver.Chrome(r'C:\Users\Misha\Desktop\bot_v2\chromedriver.exe',
                                                   options=chromeOptions)
                        try:
                            browserChrome.get(url=url)
                        except:
                            print('Возникла ошибка при открытии браузера.')
                            print('================================================================================')
                            logging.error('Возникла ошибка при открытии браузера.')
                            logging.debug(
                                '================================================================================')
                            browserChrome.quit()
                            time.sleep(1)
                            clientTelegram.send_message(LTC, '/visit')
                            while True:
                                time.sleep(1)
                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                if 'Press the "Visit website" button to earn LTC' in getMessage[0].message:
                                    time.sleep(1)
                                    buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                    messageId = getMessage[0].id
                                    time.sleep(1)
                                    clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                    break
                            break
                        while True:
                            time.sleep(2)
                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                            if 'You earned' in getMessage[0].message or 'You earned' in  getMessage[1].message:
                                browserChrome.quit()
                                print(f'Получили награду на аккаунте {phoneNumber} за посещение сайта.')
                                print('================================================================================')
                                x += 1
                                break
                        break
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанет. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def SubscribeBot():
        x, y = 1, 0
        while True:
            try:
                phoneNumber = db.selectAccount(x)[1];apiId = db.selectAccount(x)[2]
                apiHash = db.selectAccount(x)[3]; stringSession = db.selectAccount(x)[4]
                accountId = db.selectAccount(x)[5]
            except:
                print('Запуск ботов - круг пройден.')
                print('================================================================================')
                break
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            if y == 0:
                print(f'Аккаунт {phoneNumber} в работе. Функция: запуск ботов.')
                print('================================================================================')
            y = 1
            try:
                for i in clientTelegram.get_dialogs():
                    if i.title == 'LTC Click Bot':
                        LTC = i
                        break
                clientTelegram.send_message(LTC, '/bots')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.disconnect()
                        print( f'Для аккаунта {phoneNumber} нет доступных заданий. Переходим на другой аккаунт.')
                        print('================================================================================')
                        x += 1
                        y = 0
                        break
                    elif 'Press the "Message bot" botton below' in getMessage[0].message:
                        time.sleep(1)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        try:
                            requestsPost = requests.post(url)
                        except TimeoutError:
                            time.sleep(2)
                            clientTelegram.send_message(LTC, '/bots')
                            while True:
                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                if 'Press the "Message bot" botton below' in getMessage[0].message:
                                    buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                    messageId = getMessage[0].id
                                    clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                    break
                                break
                        beautifulSoup = bs4.BeautifulSoup(requestsPost.text, 'lxml')
                        tgLink = beautifulSoup.find(attrs={'name':'twitter:app:url:googleplay'}).get('content')
                        for i in db.cursor.execute('SELECT URL FROM bot_blacklist'):
                            urlBlackList = str(i[0])
                            if tgLink in urlBlackList:
                                blackList = True
                                break
                            else:
                                blackList = False
                        if blackList is True:
                            time.sleep(1)
                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                            buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                            messageId = getMessage[0].id
                            time.sleep(1)
                            clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                            break
                        else:
                            botName = beautifulSoup.find(class_='tgme_page_extra').get_text(strip=True)
                            botTitle = beautifulSoup.find(attrs={'property':'og:title'}).get('content')
                            try:
                                time.sleep(1)
                                clientTelegram(StartBotRequest(bot=botName, peer=tgLink, start_param='0'))
                            except:
                                time.sleep(1)
                                clientTelegram.send_message(LTC, '/bots')
                                while True:
                                    time.sleep(1)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Forward a message to me from the bot to earn LTC.' in getMessage[0].message:
                                        time.sleep(1)
                                        buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                        messageId = getMessage[0].id
                                        time.sleep(1)
                                        clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                        break
                                break
                            counter = 0
                            while True:
                                time.sleep(1)
                                getMessage = clientTelegram.get_messages(botTitle, limit=3)
                                if counter == 20:
                                    print(f'Превышено время ожидания ответа от бота {botName}.')
                                    print(
                                    '================================================================================')
                                    db.cursor.execute(f'INSERT INTO bot_blacklist (URL) VALUES ("{tgLink}")')
                                    db.connection.commit()
                                    time.sleep(1)
                                    clientTelegram.delete_dialog(botTitle)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                    messageId = getMessage[0].id
                                    time.sleep(1)
                                    clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                    break
                                elif accountId not in str(getMessage[0].from_id):
                                    time.sleep(1)
                                    messageId = getMessage[0].id
                                    time.sleep(1)
                                    clientTelegram.forward_messages(LTC, messageId, botTitle)
                                    time.sleep(1)
                                    clientTelegram.delete_dialog(botTitle)
                                    print(f'Получили награду на аккаутне {phoneNumber} за запуск бота.')
                                    print(
                                    '================================================================================')
                                    x += 1
                                    y = 0
                                    break
                                counter += 1
                                time.sleep(1)
                            break
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def JoinChannel():
        x, y = 1, 0
        while True:
            try:
                phoneNumber = db.selectAccount(x)[1]; apiId = db.selectAccount(x)[2]
                apiHash = db.selectAccount(x)[3]; stringSession = db.selectAccount(x)[4]
                accountId = db.selectAccount(x)[5]
            except:
                print('Подписка на каналы - круг пройден.')
                print('================================================================================')
                break
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            if y == 0:
                print(f'Аккаунт {phoneNumber} в работе. Функция: подписка на каналы.')
                print('================================================================================')
            y = 1
            try:
                for i in clientTelegram.get_dialogs():
                    if i.title == 'LTC Click Bot':
                        LTC = i
                        break
                clientTelegram.send_message(LTC, '/join')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Sorry, there are no new ads available' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.disconnect()
                        print( f'Для аккаунта {phoneNumber} нет доступных заданий. Переходим на другой аккаунт.')
                        print('================================================================================')
                        x += 1
                        y = 0
                        break
                    elif 'Sorry, that task is no longer valid' in getMessage[0].message:
                        time.sleep(1)
                        clientTelegram.send_message(LTC, '/join')
                    elif 'Press the "Go to channel" button below' in getMessage[0].message or \
                            'Press the "Go to group" button' in getMessage[0].message:
                        time.sleep(1)
                        url = getMessage[0].reply_markup.rows[0].buttons[0].url
                        requestsGet = requests.get(url)
                        beautifulSoup = bs4.BeautifulSoup(requestsGet.text, 'lxml')
                        findChannelName = beautifulSoup.find('title').get_text(strip=True)
                        channelName = findChannelName.replace('Telegram: Contact ', '')
                        try:
                            time.sleep(1)
                            clientTelegram(JoinChannelRequest(channelName))
                        except FloodWaitError:
                            print(f'Аккаунт {phoneNumber} временно заблокирован за флуд.')
                            print('================================================================================')
                            logging.error(
                                f'Аккаунт {phoneNumber} временно заблокирован за флуд.')
                            logging.error(
                                 '================================================================================')
                            x +=1
                            break
                        except:
                            print(f'Канала {channelName} не существует. Пропускаем задание.')
                            print('================================================================================')
                            while True:
                                time.sleep(2)
                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                if accountId not in str(getMessage[0].from_id):
                                    time.sleep(2)
                                    buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                    messageId = getMessage[0].id
                                    clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                    break
                                break
                        while True:
                            time.sleep(2)
                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                            if 'Press the "Go to channel" button below' or \
                                    'Press the "Go to group" button below' in \
                                    getMessage[0].message or getMessage[1].message:
                                time.sleep(1)
                                buttons = getMessage[0].reply_markup.rows[0].buttons[1].data
                                messageId = getMessage[0].id
                                clientTelegram(GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                while True:
                                    time.sleep(1)
                                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                                    if 'Success' in getMessage[1].message:
                                        time.sleep(1)
                                        print(f'На аккаунте {phoneNumber} успешно выполнено задание по '
                                            f'подписке на канал {channelName}.')
                                        print(
                                    '================================================================================')
                                        copyMessage = getMessage[1].message; searchPattern = re.compile(r'\d{1,2}')
                                        findTime = searchPattern.search(copyMessage)
                                        time_ = findTime.group()
                                        timeJoin = datetime.datetime.now()
                                        timeDelta = datetime.timedelta(hours=int(time_))
                                        timeLeave = timeJoin + timeDelta
                                        db.cursor.execute(f'''INSERT INTO channel_info 
                                                            (CHANNEL_NAME, TIME_LEAVE, ACCOUNT_ID)
                                                            VALUES (?, ?, ?)''', (channelName, timeLeave, accountId))
                                        db.connection.commit()
                                        x += 1
                                        y = 0
                                        break
                                    elif 'If this message persists' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram(LeaveChannelRequest(channelName))
                                        time.sleep(1)
                                        clientTelegram.send_message(LTC, '/join')
                                        while True:
                                            time.sleep(1)
                                            getMessage = clientTelegram.get_messages(LTC, limit=3)
                                            if 'After joining, press the "Joined" button to earn LTC.' in \
                                                    getMessage[0].message:
                                                time.sleep(1)
                                                buttons = getMessage[0].reply_markup.rows[1].buttons[1].data
                                                messageId = getMessage[0].id
                                                time.sleep(1)
                                                clientTelegram(
                                                    GetBotCallbackAnswerRequest(LTC, messageId, data=buttons))
                                                break
                                        break
                                    elif 'Please press the "🔎 Go to channel" button' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(LTC, '/join')
                                        break
                                    elif 'Sorry, that task is no longer valid. 😟' in getMessage[0].message:
                                        time.sleep(1)
                                        clientTelegram.send_message(LTC, '/join')
                                        break
                                    else:
                                        pass
                                break
                        break
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()
                x += 1

    @staticmethod
    def TimeToExit():
        while True:
            try:
                for i in db.cursor.execute('SELECT TIME_LEAVE FROM channel_info').fetchall():
                    timeLeave = datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')
                    timeNow = datetime.datetime.now()
                    compareTime = timeLeave < timeNow
                    if compareTime is True:
                        accountId = db.cursor.execute(f'SELECT ACCOUNT_ID'
                                                      f' FROM channel_info WHERE TIME_LEAVE = "{i[0]}" ').fetchone()
                        channelName = db.cursor.execute(f'SELECT CHANNEL_NAME '
                                                        f'FROM channel_info WHERE TIME_LEAVE = "{i[0]}"').fetchone()
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
                            try:
                                clientTelegram(LeaveChannelRequest(channelName[0]))
                            except UserNotParticipantError:
                                pass
                            finally:
                                db.cursor.execute(f'DELETE FROM channel_info WHERE TIME_LEAVE = "{i[0]}"')
                                db.connection.commit()
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ!Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def CheckBalance():
        x = 1
        overallRubBalance = 0
        overallLTCBalance = 0
        while True:
            try:
                phoneNumber = db.selectAccount(x)[1]; apiId = db.selectAccount(x)[2]
                apiHash = db.selectAccount(x)[3];stringSession = db.selectAccount(x)[4]
            except:
                print(f'Общий баланс {round(overallRubBalance, 2)} руб. или {round(overallLTCBalance, 8)} LTC.')
                print('================================================================================')
                break
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            try:
                for i in clientTelegram.get_dialogs():
                    if i.title == 'LTC Click Bot':
                        LTC = i
                        break
                clientTelegram.send_message(LTC, '/balance')
                while True:
                    time.sleep(1)
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Available balance' in getMessage[0].message:
                        time.sleep(1)
                        copyMessage = getMessage[0].message; searchPattern = re.compile(r'\d.\d{1,9}')
                        findBalance = searchPattern.search(copyMessage); balanceLitecoin = findBalance.group()
                        CoinGecko = CoinGeckoAPI()
                        balanceRubles = int(CoinGecko.get_price(
                            ids='litecoin', vs_currencies='rub')['litecoin']['rub'])*float(balanceLitecoin)
                        overallRubBalance += balanceRubles
                        overallLTCBalance += float(balanceLitecoin)
                        print(f'\nБаланс аккаунта {phoneNumber}: {round(balanceRubles, 2)} руб '
                              f'или {round(float(balanceLitecoin), 8)} LTC.')
                        print('================================================================================')
                        clientTelegram.disconnect()
                        x += 1
                        break
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()

    @staticmethod
    def WithdrawBalance():
        for accountInformation in db.cursor.execute(
                f'SELECT PHONE_NUMBER, API_ID, API_HASH, STRING_SESSION, ADDRESS FROM account_information').fetchall():
            phoneNumber = accountInformation[0]; apiId = accountInformation[1]
            apiHash = accountInformation[2]; stringSession = accountInformation[3]
            litecoinAddress = accountInformation[4]
            clientTelegram = TelegramClient(StringSession(stringSession), apiId, apiHash)
            clientTelegram.connect()
            try:
                for i in clientTelegram.get_dialogs():
                    if i.title == 'LTC Click Bot':
                        LTC = i
                        break
                clientTelegram.send_message(LTC, '/balance')
                while True:
                    getMessage = clientTelegram.get_messages(LTC, limit=3)
                    if 'Available balance' in getMessage[0].message:
                        copyMessageWithBalance = getMessage[0].message; templateSearch = re.compile(r'\d.\d{1,9}')
                        findBalance = templateSearch.search(copyMessageWithBalance); balanceLitecoin = findBalance.group()
                        if float(balanceLitecoin) == 0.0003 or float(balanceLitecoin) > 0.0004:
                            print(f'Функция вывода средств на аккаунте {phoneNumber} активирована.')
                            print('================================================================================')
                            clientTelegram.send_message(LTC, '/withdraw')
                            while True:
                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                if 'To withdraw, enter your Litecoin address' in getMessage[0].message:
                                    time.sleep(1)
                                    clientTelegram.send_message(LTC, litecoinAddress)
                                    while True:
                                        getMessage = clientTelegram.get_messages(LTC, limit=3)
                                        if 'Enter the amount to withdraw' in getMessage[0].message:
                                            time.sleep(1)
                                            clientTelegram.send_message(LTC, balanceLitecoin)
                                            while True:
                                                getMessage = clientTelegram.get_messages(LTC, limit=3)
                                                if 'Are you sure you want to send' in getMessage[0].message:
                                                    time.sleep(1)
                                                    clientTelegram.send_message(LTC, '✅ Confirm')
                                                    break
                                            break
                                    break
                            break
                        else:
                            print(f'На аккаунте {phoneNumber} недостаточно средств для вывода.')
                            print('================================================================================')
                            break
            except UserDeactivatedBanError:
                print(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.\n'
                      f'================================================================================')
                logging.error(f'ВНИМАНИЕ! Аккаунт {phoneNumber} забанен. Удаляем данные об аккаунте из базы.')
                logging.error('================================================================================')
                db.cursor.execute(f'DELETE FROM account_information WHERE PHONE_NUMBER = {phoneNumber}')
                db.connection.commit()





