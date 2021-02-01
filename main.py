# coding: utf8

import multiprocessing
from allfoo import CreateSession, StartLitecoinBot, VisitSites, JoinChannel, StartBot, CheckBalance, WithdrawBalance, \
    TimeToExit, db, datetime, InstallPackage

db.createTableAccountInformation()
db.createTableBotBlacklist()
db.createTableChannelInfo()
db.createTableSettings()

if __name__ == "__main__":
    def ScriptController():
        def Menu():
            print(
                '\nСписок комманд:\n./installPackage\n./inputData\n./addRefCodeAndApiKey\n./updRefCode\n'
                './updApiKey\n./createSession\n./startLtcBot\n./startFarming\n./checkBalance\n./withdrawBalance')
            command = input('\nКомманда: ')
            if command == './installPackage':
                InstallPackage()
            elif command == './inputData':
                def inputData():
                    startTyping = input('\nНачать ввод данных y/n: ')
                    if startTyping == 'y':
                        phoneNumber = input('\nВведите номер телефона Telegram: ')
                        apiId = input('Введите  Telegram Api Id: ')
                        apiHash = input('Введите Telegram Api Hash: ')
                        confirm = input('\nНомер телефона: {0}\nApi Id: {1}\nApi Hash: {2}\n'
                                        '\nДанные введены верно y/n: '.format(phoneNumber, apiId, apiHash))
                        if confirm == 'y':
                            try:
                                db.cursor.execute('INSERT INTO account_information '
                                                  '(PHONE_NUMBER, '
                                                  'API_ID, '
                                                  'API_HASH) '
                                                  'VALUES ("{0}", "{1}", "{2}")'.format(phoneNumber, apiId, apiHash))
                                db.connection.commit()
                            except:
                               print('\nАккаунт {0} уже есть в базе данных.'.format(phoneNumber))
                               inputData()
                            else:
                                print('\nАккаунт {0} успешно добавлен.'.format(phoneNumber))
                                inputData()
                        else:
                            print('\nПопробуйте ещё раз.')
                            inputData()
                    else:
                        Menu()
                inputData()
            elif command == './createSession':
                startCreating = input('\nНачать создание сессий y/n: ')
                if startCreating == 'y':
                    CreateSession()
                    Menu()
                else:
                    Menu()
            elif command == './startLtcBot':
                StartLitecoinBot()
            elif command == './addRefCodeAndApiKey':
                if db.cursor.execute('SELECT REFFERAL_CODE '
                                     'FROM settings').fetchone() is None:
                    if input('\nНачать ввод данных: y/n: ') == 'y':
                        refCode = input('\nВведите свой реферальный код: ')
                        blockIoApiKey = input('Введите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                        print('\nРеферальный код: {0}\nApi ключ: {1}'.format(refCode, blockIoApiKey))
                        confirmInput = input('\nПодтвердить ввод y/n: ')
                        if confirmInput == 'y':
                            db.cursor.execute('INSERT INTO settings '
                                              '(REFFERAL_CODE, '
                                              'BLOCKIO_API_KEY) '
                                              'VALUES '
                                              '("{0}", "{1}")'.format(refCode, blockIoApiKey))
                            db.connection.commit()
                            print('\nApi ключ и реферальный код успешно добавлены.')
                            Menu()
                        else:
                            Menu()
                    else:
                        Menu()
                else:
                    print('\nВы уже добавили реферальный код и Api ключ. Воспользуйтесь коммандами\n./updRefCode'
                          ' и ./updBlockIoApiKey для их обновления.')
                    Menu()
            elif command == './updRefCode':
                if db.cursor.execute('SELECT REFFERAL_CODE '
                                     'FROM settings').fetchone() is None:
                    print('\nРеферальный код не найден. Выполните комманду ./addRefCodeAndApiKey')
                    Menu()
                else:
                    refCode = input('\nВведите свой реферальный код: ')
                    confirmInput = input('\nПодтвердить ввод y/n: ')
                    if confirmInput == 'y':
                        db.cursor.execute('UPDATE settings '
                                          'SET REFFERAL_CODE = "{0}"'.format(refCode))
                        db.connection.commit()
                        print('\nРеферальный код успешно обновлён.')
                        Menu()
                    else:
                        Menu()
            elif command == './updApiKey':
                if db.cursor.execute('SELECT REFFERAL_CODE '
                                     'FROM settings').fetchone() is None:
                    print('\nApi ключ для не найден. Выполните комманду ./addRefCodeAndApiKey')
                    Menu()
                else:
                    blockIoApiKey = input(
                        '\nВведите Api ключ для Litecoin кошелька с сайта https://block.io/: ')
                    confirmInput = input('\nПодтвердить ввод y/n: ')
                    if confirmInput == 'y':
                        db.cursor.execute('UPDATE settings '
                                          'SET BLOCKIO_API_KEY = "{0}"'.format(blockIoApiKey))
                        db.connection.commit()
                        print('\nApi ключ успешно обновлён.')
                        Menu()
                    else:
                        Menu()
            elif command == './startFarming':
                print('\n[{0}] Ферма запущена.\n'.format(datetime.datetime.now().strftime("%H:%M:%S")))
                p = multiprocessing.Process(target=TimeToExit)
                p.start()
                while True:
                    VisitSites()
                    JoinChannel()
                    StartBot()
            elif command == './checkBalance':
                CheckBalance()
            elif command == './withdrawBalance':
                WithdrawBalance()
            elif command == './test':
                InstallPackage()
            else:
                print('\nКомманда не распознана.')
                Menu()
        Menu()
    ScriptController()





















