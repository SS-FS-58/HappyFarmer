#!C:\Users\Misha\AppData\Local\Programs\Python\Python39\python.exe
# coding: utf8

import subprocess, sys, platform

if platform.system()=="Windows":
    subprocess.Popen("cls", shell=True).communicate()
else:
    print("\033c", end="")

print("""\n╔╗╔╗─────────╔══╗
║╚╝╠═╗╔═╦═╦╦╗║═╦╩╗╔╦╦══╦═╦╦╗
║╔╗║╬╚╣╬║╬║║║║╔╣╬╚╣╔╣║║║╩╣╔╝
╚╝╚╩══╣╔╣╔╬╗║╚╝╚══╩╝╚╩╩╩═╩╝
──────╚╝╚╝╚═╝""")


while True:
    process = subprocess.Popen([sys.executable, "main.py"])
    process.wait()

