#!C:\Users\Misha\AppData\Local\Programs\Python\Python39\python.exe
# coding: utf8

from func import *

if __name__ == "__main__":

    try:
        def ScriptController():
            def menu():
                print(
                    '\nСписок комманд:\n./addData\n./addRefCodeAndApiKey\n./updRefCode\n'
                    './updApiKey\n./createSession\n./startLtcBot\n./startFarming\n./checkBalance\n./withdrawBalance')
                command = input('\nКомманда: ')
                if command == './addData':
                    def inputData():
                        startTyping = input('\nНачать ввод данных y/n: ')
                        if startTyping == 'y':
                            phoneNumber = input('Введите номер телефона Telegram: ')
                            apiId = input('Введите  Telegram Api Id: ')
                            apiHash = input('Введите Telegram Api Hash: ')
                            confirm = input(f'\nНомер телефона: {phoneNumber}\nApi Id: {apiId}\nApi Hash: {apiHash}\n'
                                            f'Данные введены верно y/n: ')
                            if confirm == 'y':
                                try:
                                    db.cursor.execute(f'''INSERT INTO account_information 
                                (PHONE_NUMBER, API_ID, API_HASH) VALUES ("{phoneNumber}", "{apiId}", "{apiHash}")''')
                                    db.connection.commit()
                                except sqlite3.IntegrityError:
                                   print('Этот аккаунт уже добавлен.')
                                   inputData()
                                else:
                                    print(f'Аккаунт {phoneNumber} успешно добавлен.')
                                    inputData()
                            else:
                                print('\nПопробуйте ещё раз.')
                                inputData()
                        else:
                            menu()
                    inputData()
                elif command == './createSession':
                    startCreating = input('\nНачать создание сессий y/n: ')
                    if startCreating == 'y':
                        LitecoinBot.CreateSession()
                    else:
                        menu()
                elif command == './startLtcBot':
                    LitecoinBot.StartLitecoinBot()
                elif command == './addRefCodeAndApiKey':
                    if db.cursor.execute('''SELECT ID FROM settings WHERE ID = 1''').fetchone() is None:
                        if input('\nНачать ввод данных: y/n: ') == 'y':
                            refCode = input('\nВведите свой реферальный код: ')
                            blockIoApiKey = input('Введите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                            print(f'\nРеферальный код: {refCode}\nApi ключ: {blockIoApiKey}')
                            confirmInput = input('\nПодтвердить ввод y/n: ')
                            if confirmInput == 'y':
                                db.cursor.execute(
                                    f'''INSERT INTO settings
                                     (REFFERAL_CODE, BLOCKIO_API_KEY) VALUES ("{refCode}", "{blockIoApiKey}")''')
                                db.connection.commit()
                                print('\nApi ключ и реферальный код успешно добавлены.')
                            else:
                                menu()
                        else:
                            menu()
                    else:
                        print('\nВы уже добавили реферальный код и Api ключ. Воспользуйтесь коммандами\n./updRefCode'
                              ' и ./updBlockIoApiKey для их обновления.')
                        menu()
                elif command == './updRefCode':
                    if db.cursor.execute(f'''SELECT ID FROM settings WHERE ID = 1''').fetchone() is None:
                        print('\nРеферальный код не найден. Выполните комманду ./addRefCodeAndApiKey')
                        menu()
                    else:
                        refCode = input('\nВведите свой реферальный код: ')
                        confirmInput = input('\nПодтвердить ввод y/n: ')
                        if confirmInput == 'y':
                            db.cursor.execute(
                                f'''UPDATE settings SET REFFERAL_CODE = "{refCode}" WHERE ID = 1''')
                            db.connection.commit()
                            print('\nРеферальный код успешно обновлён.')
                        else:
                            menu()
                elif command == './updApiKey':
                    if db.cursor.execute(f'''SELECT ID FROM settings WHERE ID = 1''').fetchone() is None:
                        print('\nApi ключ для не найден. Выполните комманду ./addRefCodeAndApiKey')
                        menu()
                    else:
                        blockIoApiKey = input(
                            '\nВведите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                        confirmInput = input('\nПодтвердить ввод y/n: ')
                        if confirmInput == 'y':
                            db.cursor.execute(
                                f'''UPDATE settings SET BLOCKIO_API_KEY = "{blockIoApiKey}" WHERE ID = 1''')
                            db.connection.commit()
                            print('\nApi ключ успешно обновлён.')
                        else:
                            menu()
                elif command == './startFarming':
                    print('\nФерма запущена.\n'
                          '================================================================================')
                    p = multiprocessing.Process(target=LitecoinBot.TimeToExit)
                    p.start()
                    while True:
                        LitecoinBot.JoinChannel()
                        LitecoinBot.SubscribeBot()
                        LitecoinBot.VisitSites()
                elif command == './checkBalance':
                    LitecoinBot.CheckBalance()
                elif command == './withdrawBalance':
                    LitecoinBot.WithdrawBalance()
                else:
                    print('\nКомманда не распознана.')
                    menu()
            menu()
        ScriptController()
    except sqlite3.OperationalError:
        print('\nПохоже, вы не создали таблицы в базе данных.\nВведите команду ./createDataTable\n')















