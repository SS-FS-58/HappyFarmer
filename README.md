# Happy Farmer #

***О скрипте.***   

Скрипт создан для абуза @Litecoin_click_bot в Telegram. Если приложить немного усилий, его можно адаптировать под работу с @BTC_click_bot, @BCH_click_bot, @Doge_click_bot.   Но, как я убедился на практике, это бесполезно. Нормально платят только в @Litecoin_click_bot.   
 
Скрипт написан на Python 3.9
  
***Архитектура проекта.***  

В общих чертах расскажу об архитектуре поекта.   

```start.py``` - запускает работу срипта и перезапускает его, если он по  каким-либо причинам упал.  

```main.py``` содержит в себе функцию-контроллер скрипта. С помощью этого контроллера пользователь осуществляет взаимодействие со скриптом.

```allfoo.py``` - это "мозг" скрипта. В файле находятся все функции, необходимые для абуза @Litecoin_click_bot.  

```database.py``` - файл для работы с базой данных.  

```config.py``` - файл конфигурации. В нём указывается путь до ChromeDriver.  

```telegram_farm.db``` - база данных.  

```TelegramFarmErrors.log``` - файл-лог, куда заносятся отчёты о банах аккаунтов и прочих неприятностях.

```manual.md``` - краткая инструкция по использоваию скрипта.

```command_description.md``` - содержит описание всех комманд, с помощью которых происходит взаимодействие со скриптом.

```patchnote``` - в этом файле публикуются уведомления об обновлении скрипта.
  
  
***Обратная связь.***   

Есть предложения по улучшению проекта? Есть замечания по коду? Возникли вопросы? Пишите мне в   VK: https://vk.com/mtchuikov или Telegram: https://t.me/mtchuikov.  
  
  
***Поддержать автора.***  
BNB (bep20): 0xa4ca77291e6a7532d527b0d3efbe265ae4eceec0  
TRX: TTdXB7RbydKQpxs3wXJx4GBm9r9EqKuBaW  
LTC: Lgp4w1ubkAgcQEVVBSiAN788FUHmZyh5c9  
Qiwi nickname: MTCHUIKOV
