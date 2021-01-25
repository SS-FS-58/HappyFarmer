#!C:\Users\Misha\AppData\Local\Programs\Python\Python39\python.exe
# coding: utf8

import subprocess, sys

print("""╔╗╔╗─────────╔══╗
║╚╝╠═╗╔═╦═╦╦╗║═╦╩╗╔╦╦══╦═╦╦╗
║╔╗║╬╚╣╬║╬║║║║╔╣╬╚╣╔╣║║║╩╣╔╝
╚╝╚╩══╣╔╣╔╬╗║╚╝╚══╩╝╚╩╩╩═╩╝
──────╚╝╚╝╚═╝""")

while True:
    process = subprocess.Popen([sys.executable, "main.py"])
    process.wait()
