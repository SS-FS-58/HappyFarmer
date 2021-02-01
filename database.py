# coding: utf8

import sqlite3

class SQLite:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def createTableAccountInformation(self):
        with self.connection:
            return self.cursor.execute('''CREATE TABLE IF NOT EXISTS account_information
                                        (PHONE_NUMBER TEXT UNIQUE, 
                                        API_ID TEXT UNIQUE,  
                                        API_HASH TEXT UNIQUE, 
                                        STRING_SESSION TEXT UNIQUE, 
                                        ACCOUNT_ID TEXT UNIQUE, 
                                        ADDRESS TEXT UNIQUE,
                                        CREATE_SESSION BOOLEAN)''')

    def createTableBotBlacklist(self):
        with self.connection:
            return self.cursor.execute('''CREATE TABLE IF NOT EXISTS bot_blacklist
                                    (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
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
                                            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                            REFFERAL_CODE TEXT UNIQUE,
                                            BLOCKIO_API_KEY TEXT UNIQUE)''')

db = SQLite('telegram_farm.db')
