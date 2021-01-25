## Мануал по работа со скриптом

***Предварительная подготовка.***

```Шаг 1.```  
Загрузка файлов из репозитория.  
Делается это следующим образом: переходите на главную страницу проекта https://github.com/Mtchuikov/HappyFarmer, нажимаете кнопку "Code". Далее выбираете способ загрузки. Рекомендую скачивать сразу архивом. После загрузки архива, необходимо распаковать архивные файлы в папку.

---

```Шаг 2.```  
Установка интерпретатора Python. Инструкция по установке Python: https://python-scripts.com/install-python

---

```Шаг 3.```  
Установка PIP (python installer package). Инструкция по установке PIP: https://pythonru.com/baza-znanij/ustanovka-pip-dlja-python-i-bazovye-komandy  

---

```Шаг 4.```  
Установка Goolge Chrome и ChromeDriver.   
Версия ChromeDriver и Google Chrome должны совпадать. Что бы узнать версию Google, а следовательно и ChromeDriber нужно: открыть Google => открыть настройки браузера => перейти во вкладку "О браузере".  
Ссылка на скачивание ChromeDriver: https://chromedriver.chromium.org/

---

```Шаг 5.```  
Указание пути до интерпретатора Python.  
Открываете с помощью блокнота скачанные ранее файлы start.py, main.py, func.py В самом верху каждого файла увидите строку #!C:\Users\Misha\AppData\Local\Programs\Python\Python39\python.exe Удаляете всё до #! и указываете свой путь до python.exe (до интерпретатора)

---

```Шаг 6.```  
Указание пути до ChromeDriver.  
Открываете файл func.py, ищете строку browserChrome = webdriver.Chrome(r'C:\Users\Misha\Desktop\bot_v2\chromedriver.exe',options=chromeOptions). Вместо C:\Users\Misha\Desktop\bot_v2\chromedriver.exe указываете свой путь до ChromeDriver.exe

Предварительная подготовка закончена. 

***Запуск и работа со скриптом.***
