# coding: utf8

from func import *

if __name__ == "__main__":

    try:
        def ScriptController():
            def menu():
                print(
                    '\nГлавное меню.\nВведите комманду:\n./addData\n./createSession\n'
                    './settings\n./subBot\n./startFarming\n./checkBalance\n./withdrawBalance')
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
                                else:
                                    print(f'Аккаунт {phoneNumber} успешно добавлен.')
                            else:
                                print('Попробуйте ещё раз.')
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
                elif command == './subBot':
                    LitecoinBot.StartLitecoinBot()
                elif command == './settings':
                    def settings():
                        print('\nРаздел настройки.\nВведите комманду:\n./addRefCode\n./updRefCode\n./addBlockIoApiKey\n'
                              './updBlockIoApiKey\n./back\n')
                        command_ = input('Комманда: ')
                        if command_ == './addRefCode':
                            refCode = input('\nВведите свой реферальный код: ')
                            confirmInput = input('\nПодтвердить ввод y/n: ')
                            if confirmInput == 'y':
                                db.cursor.execute(f'''INSERT INTO settings (REFFERAL_CODE) VALUES ("{refCode}")''')
                                db.connection.commit()
                                print('Реферальный код успешно добавлен.\n')
                            else:
                                settings()
                        elif command_ == './updRefCode':
                            try:
                                db.cursor.execute(f'''SELECT * FROM settings WHERE ID = 1''').fetchone()[2]
                            except:
                                print('\nРеферальный код не найден. Добавьте введите реферальный код.')
                                settings()
                            else:
                                refCode = input('\nВведите свой реферальный код: ')
                                confirmInput = input('\nПодтвердить ввод y/n: ')
                                if confirmInput == 'y':
                                    db.cursor.execute(
                                        f'''UPDATE settings SET REFFERAL_CODE = "{refCode}" WHERE ID = 1''')
                                    db.connection.commit()
                                    print('Реферальный код успешно обновлён.')
                                else:
                                    settings()
                            print('Реферальный код обновлён.\n')
                        elif command_ == './addBlockIoApiKey':
                            blockIoApiKey = input(
                                '\nВведите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                            confirmInput = input('\nПодтвердить ввод y/n: ')
                            if confirmInput == 'y':
                                db.cursor.execute(
                                    f'''INSERT INTO settings (BLOCKIO_API_KEY) VALUES ("{blockIoApiKey}")''')
                                db.connection.commit()
                                print('Api ключ успешно добавлен.')
                            else:
                                settings()
                        elif command_ == './updBlockIoApiKey':
                            try:
                                db.cursor.execute(f'''SELECT * FROM settings WHERE ID = 1''').fetchone()[2]
                            except:
                                print('\nApi ключ для Litecoin кошелька не найден. Введите Api ключ.')
                                settings()
                            else:
                                blockIoApiKey = input(
                                    '\nВведите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                                confirmInput = input('\nПодтвердить ввод y/n: ')
                                if confirmInput == 'y':
                                    db.cursor.execute(
                                        f'''UPDATE settings SET BLOCKIO_API_KEY = "{blockIoApiKey}" WHERE ID = 1''')
                                    db.connection.commit()
                                    print('Api ключ успешно обновлён.')
                                else:
                                    settings()
                        elif command_ == './back':
                            menu()
                        else:
                            print('\nКомманда не распознана.')
                            settings()
                    settings()
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






