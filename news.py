# -*- coding: utf-8 -*-
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import csv
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import csv, threading, time
from tkinter import messagebox

#Папка для расположения базы данных
folder = "./data/"
#Имя базы данных
basa = "base.db"
#полный путь к базе './data/base.db'
bd = folder + basa
#Знак разделителя между меню и субменю
separator = " - "
#выводить именя подзаголовков или нет (1 - выводим, 0 - не выводим) ????????????????
submenu = 1

separator_menu = " : "
# создаем потоки для функций. Перед функцией надо поставить @thread
def thread(my_func):
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

menu_all = []
#Получаем словарь из пункта меню название меню (ключ) и ссылки (значение) с учетом субменю
def menu_all_url():
	url_site = 'https://news.yandex.ru/' #Ссылка на сайт с новостями - главная страница
	html = requests.get(url_site)
	html_code = html.content
	soup = BeautifulSoup(html_code, 'lxml')
	
	menu = soup.find_all('a', class_='link link_theme_dark i-bem')
	menu_all = []
	#Прогрессбар ---------------
	x_cont=0
	pb_load['maximum'] = len(menu) #Максимальное значение для прогрессбара
	
	#Прогрессбар ---------------///
	for item in menu:
		url_item_menu = 'https://news.yandex.ru' + item.get('href')
		text_item_menu = item.text

		xx = text_item_menu, url_item_menu
		menu_all.append(xx)
		#Прогрессбар ---------------
		x_cont +=1 #увеличиваем на 1
		pb_load['value'] = x_cont #Передаем значение 0 для обнуления
		#Прогрессбар ---------------///

		# получаем субменю -------------------------
		url_site = url_item_menu #Ссылка на сайт с новостями - главная страница
		html = requests.get(url_site)
		html_code = html.content
		soup = BeautifulSoup(html_code, 'lxml')
		try:
			ul = soup.find('ul', class_='tabs-menu tabs-menu_theme_black tabs-menu_size_x tabs-menu_layout_horiz tabs-menu_parent_nav-by-rubrics tabs-menu_nav i-bem')
			sub_menu = ul.find_all('a', class_='link link_theme_black i-bem')

			for item in sub_menu:
				url_item_sub_menu = 'https://news.yandex.ru' + item.get('href')
				text_item_sub_menu = text_item_menu + separator +  item.text
				xxx = text_item_sub_menu, url_item_sub_menu
				menu_all.append(xxx)
		except AttributeError:
			pass

	#создаем базу данных
	con =sqlite3.connect(bd)
	#Созжаем таблицу меню в базе
	cur = con.cursor()
	cur.execute('CREATE TABLE IF NOT EXISTS menu_url(my_id INTEGER, menu TEXT, url TEXT)')
 
	my_id = 0
	for menu in menu_all:
		my_id += 1
		menu_zag = menu[0]
		url = menu[1]
		data = [my_id,menu_zag,url]
		cur.execute('INSERT INTO menu_url VALUES(?,?,?)', data)

	con.commit()
	cur.close()
	con.close()
	pb_load['value'] = 0 #Передаем значение 0 для обнуления
	#print(menu_all)
	cotent_menu(menu_all) #Передаем сиписок меню в функцию парсинга новостей
	return menu_all
	
#----------------------------------------------------------------------------------------------
#@thread #создаем отдельный поток
def cotent_menu(menu_all):
	# print('------------')
	# print(len(menu_all))
	# print('------------')

	x_cont = 0
	pb_load['maximum'] = len(menu_all) #Максимальное значение для прогрессбара
	for my_content in menu_all:
		dict_read = [] #Пустой список
		html_content = requests.get(my_content[1])
		html_code_content = html_content.content
		soup_content = BeautifulSoup(html_code_content, 'lxml')
		content_all = soup_content.find_all('h2', class_='story__title')

		x_cont +=1 #увеличиваем на 1
		pb_load['value'] = x_cont #Передаем значение 0 для обнуления

		for item_news in content_all:
			item_news = item_news.text

			xxx = my_content[0], item_news
			dict_read.append(xxx)
			data = [my_content[0],item_news]
			#создаем соединение с базой данных
			con =sqlite3.connect(bd)
			cur = con.cursor()
			#Создаем таблицу меню в базе
			cur.execute('CREATE TABLE IF NOT EXISTS news_item(cat_menu TEXT, item TEXT)')
			cur.execute('INSERT INTO news_item VALUES(?,?)', data)
			con.commit()
			cur.close()
			con.close()

	pb_load['value'] = 0 #Передаем значение pb_len виджету pb (прогрессбар)

@thread #создаем отдельный поток
def view():
	#Очищаем все списки в LISTBOX
	lis1.delete(0,lis1.size())
	lis2.delete(0,lis2.size())
	lis3.delete(0,lis3.size())
	poetry = "Выбрано разделов - 0  Выведено записей - 0"
	label2.configure(text=poetry)
	b2.configure(state=DISABLED) #Кнопка добавить все (диактивируем)
	b3.configure(state=DISABLED)
	b4.configure(state=DISABLED) #Кнопка добавить выделенное (диактивируем)
	b5.configure(state=DISABLED)
	b6.configure(state=DISABLED)
	check1.configure(state=DISABLED)
	check2.configure(state=DISABLED)
	#Проверяем существованваие папки к базе данных и создаем если ее нет
	if not os.path.isdir(folder):
		os.mkdir(folder)
	try:
		con =sqlite3.connect(bd)
		cur = con.cursor()
		cur.execute('DELETE FROM news_item')
		con.commit()
		cur.execute('DELETE FROM menu_url')
		con.commit()
		cur.close()
		con.close()
	except Exception:
		con =sqlite3.connect(bd)
		cur = con.cursor()
		cur.execute('CREATE TABLE IF NOT EXISTS news_item(cat_menu TEXT, item TEXT)')
		con.commit()
		cur.execute('CREATE TABLE IF NOT EXISTS menu_url(my_id INTEGER, menu TEXT, url TEXT)')
		con.commit()
		cur.close()
		con.close()
	try:
		menu_all_url()
		#заполняем lis1 данными
		lis1_load()
		b1.configure(text='Получить данные')


	except Exception:
		messagebox.showerror("Ошибка", "Проверьте подключение к интернету!")
		b1.configure(text='Получить данные')
	
#Операции с ListBox -------------------------------------------------------------
#Удалить все из lis2, виджет ListBox
@thread #Создаем отдельный поток
def lis2_del():
	lis2.delete(0,lis2.size())
	lis1.delete(0,lis1.size())
	for line in read_menu_url():
		lis1.insert(END,str(line[1]))
	b_del_lis3.configure(state=DISABLED) #деактивация клавиши элемента lis3 удалить выбранное
	b_restore_lis3.configure(state=DISABLED) #деактивация клавиши элемента lis3 удалить выбранное

	result() #Обновляем результат в lis3
	desable_element() #Дизактивируем элементы управления
	button_save() #диактивируем или активируем кнопку сохранить

#Добавить все из lis1 в lis2 виджета ListBox
@thread #Создаем отдельный поток
def lis1_all_copy():
	for i in lis1.get(0,lis1.size()):
		lis2.insert(END,str(i))
	lis1.delete(0,lis1.size())
	result() #Обновляем результат в lis3
	enable_b3b5() #Активируем клавиши добавить все, добавить и чекбоксы
	button_save() #диактивируем или активируем кнопку сохранить

#Добавляем выделенный элемент из списока lis1 в lis2 виджета ListBox
@thread #Создаем отдельный поток
def lis1_add_lis2():
	for num in lis1.curselection():
		n = lis1.get(num)
		lis2.insert(END,str(n))
	for num_del in reversed(lis1.curselection()):
		lis1.delete(num_del)
	result() #Обновляем результат в lis3
	enable_b3b5() #Активируем клавиши добавить все, добавить и чекбоксы
	button_save() #диактивируем или активируем кнопку сохранить


#Удаляем выделенный элемент из списока lis2 и возвращаем в lis2 виджета ListBox
@thread #Создаем отдельный поток
def lis2_add_lis1():
	for num in lis2.curselection():
		n = lis2.get(num)
		lis1.insert(END,str(n))
	for num_del in reversed(lis2.curselection()):
		lis2.delete(num_del)
	result() #Обновляем результат в lis3
	desable_element() #Дизактивируем элементы управления
	button_save() #диактивируем или активируем кнопку сохранить

#Заполняем lis1 (ListBox) данными
@thread #Создаем отдельный поток
def lis1_load():
	#Выводим данные базы из таблицы menu_url________SQL запрос
	try:
		lis1.delete(0,lis1.size())
		for line in read_menu_url():
			lis1.insert(END,str(line[1]))
			#активируем кнопки и др виджеты при загрузке
			enable_element() #Активируем и дизактивируем элементы управления
	except Exception:
		pass

@thread #Создаем отдельный поток		
def lis3_del_select():
	x_cont=0
	pb_lis3['maximum'] = len(lis3.curselection()) #Максимальное значение для прогрессбара

	for num_del in reversed(lis3.curselection()):
		lis3.delete(num_del)
		b_restore_lis3.configure(state=NORMAL)
		#действие для прогрессбара
		x_cont +=1 #увеличиваем на 1
		pb_lis3['value'] = x_cont #Передаем значение 0 для обнуления

	pb_lis3['value'] = 0 #Передаем значение 0 для обнуления
	global poetry
	menu_count = "Выбрано разделов - " + str(lis2.size())
	item_count = "Выведено записей - " + str(lis3.size())
	menu_item_count = menu_count + "  " + item_count
	#Изменяем label2
	poetry = menu_item_count
	label2.configure(text=str(menu_item_count))
	b_del_lis3.configure(state=DISABLED) #Деактивировать клавишу
@thread #Создаем отдельный поток
def button_save(): #диактивируем или активируем кнопку сохранить
	if lis2.size()==0:
		b6.configure(state=DISABLED) #Диактивируем клавишу сохранить
	else:
		b6.configure(state=NORMAL) #Диактивируем клавишу сохранить



#Выводим данные в lis3 на основе выбранных пунктов списка lis2
@thread #создаем отдельный поток
def result():
	#Удаляем все в списке lis3
	lis3.delete(0,lis3.size())

	x_cont=0
	pb_lis3['maximum'] = lis2.size() #Максимальное значение для прогрессбара

	for item_lis2 in lis2.get(0,lis2.size()):
		#Соединяемся с базой и создаем запрос выборки данных
		con =sqlite3.connect(bd)
		cur = con.cursor()
		#Создаем запрос чтения к таблице news_item
		cur.execute('SELECT * FROM news_item WHERE cat_menu LIKE ?',(item_lis2,))
		data_news_item = cur.fetchall()#помещаем запрос в переменную

		#действие для прогрессбара
		x_cont +=1 #увеличиваем на 1
		pb_lis3['value'] = x_cont #Передаем значение 0 для обнуления

		#Добавляем в lis3 результат выборки запроса к базе данных
		for line in data_news_item:
			#Выводим в lis3 либо поное меню с подзаголовками либо короткое галка в check1(Checkbutton)
			if var1.get()==0:
				#'Галка есть'
				mini = line[0].split(' - ')
			if var1.get()==1:
				# 'Галки нет'
				mini = line
			#Выводим в lis3 либо заглавными буквами если стоит галка в check2(Checkbutton)
			if var2.get()==0:
				lis3.insert(END,str(mini[0].upper()) + separator_menu + str(line[1]))
			else:
				lis3.insert(END,str(mini[0]) + separator_menu + str(line[1]))

		my_count() #Количество выбраных элементов при добавлении в реальном времени

		con.commit()
		cur.close()
		con.close()
	my_count() #Количество выбраных элементов
	#-----------------------------------------
	pb_lis3['value'] = 0 #Передаем значение 0 для обнуления
	b_del_lis3.configure(state=DISABLED) #Деактивация клавиши удалить для lis3

#Активация или деактивация клавищи удалить выделеное в lis3
def button_del_lis3(event):
	# if lis3.size()==0:
	if len(lis3.curselection())==0:
		b_del_lis3.configure(state=DISABLED)
	else:
		b_del_lis3.configure(state=NORMAL)

#Активация или деактивация клавищи восстановить в lis3
def button_restore_lis3():
	if lis3.size()==0:
		b_restore_lis3.configure(state=DISABLED)
	else:
		b_restore_lis3.configure(state=NORMAL)
#Деактивация и переход к функции выводу результата восстановить в lis3
def restore():
		b_restore_lis3.configure(state=DISABLED) #Деактивация клавиши востановить для lis3
		result()

def enable_element(): #Активируем и дизактивируем элементы управления
	if lis1.size()>0:
		b2.configure(state=NORMAL)
		b4.configure(state=NORMAL)
	else:
		#дективируем кнопки и др виджеты при загрузке
		b2.configure(state=DISABLED)
		b3.configure(state=DISABLED)
		b4.configure(state=DISABLED)
		b5.configure(state=DISABLED)
		check1.configure(state=DISABLED)
		check2.configure(state=DISABLED)

def desable_element(): #дективируем кнопки и др виджеты при загрузке
	if lis2.size()==0:
		b3.configure(state=DISABLED)
		b5.configure(state=DISABLED)
		check1.configure(state=DISABLED)
		check2.configure(state=DISABLED)
	else:
		b5.configure(state=NORMAL)
		b3.configure(state=NORMAL)	
		check1.configure(state=NORMAL)
		check2.configure(state=NORMAL)


def enable_b3b5(): #Активируем добавить все и чекбоусы
		b3.configure(state=NORMAL)
		b5.configure(state=NORMAL)
		check1.configure(state=NORMAL)
		check2.configure(state=NORMAL)

#Диалоговое окно сохранения
@thread #Создаем отдельный поток
def saveasfile():
	try:
		# pb['value'] = 0
		save_item = [] #пустой словарь
		for i in lis3.get(0,lis3.size()):
			x = i.split(separator_menu)
			save_item.append(x)

		file_name = filedialog.asksaveasfilename(confirmoverwrite=False, defaultextension = '.csv', filetypes=(("CSV Файл","*.csv"),("Все файлы","*.*")))
		with open(file_name, 'w', encoding='utf-8', newline='') as f:

			pb_len=0 #Переменная для прогрессбара
			pb['maximum'] = lis3.size()
			for item in save_item:
				pb_len+=1 #Увелчиваем значение на 1
				t = csv.writer(f)
				t.writerow(item) #Градусы

				pb['value'] += pb_len #Передаем значение pb_len виджету pb (прогрессбар)
			pb['value'] = 0 #Передаем значение 0 виджету pb (прогрессбар)
	except Exception:
		pass
#Выводим количество выбранной информации
# @thread #Создаем отдельный поток
def my_count():
	global poetry
	menu_count = "Выбрано разделов - " + str(lis2.size())
	item_count = "Выведено записей - " + str(lis3.size())
	menu_item_count = menu_count + "  " + item_count
	#Изменяем label2
	poetry = menu_item_count
	label2.configure(text=str(menu_item_count))
	return menu_item_count

def mini_munu_item():
	result() #Выводим данные в lis3 на основе выбранных пунктов списка lis2

#Запросы к базе данных-----------------------------------------------------------

#читаем таблицу news_item
def read_news_item():
	con =sqlite3.connect(bd)
	cur = con.cursor()
	#Создаем запрос чтения к таблице news_item
	cur.execute('SELECT cat_menu,item FROM news_item')
	data_news_item = cur.fetchall()#помещаем запрос в переменную
	con.commit()
	cur.close()
	con.close()
	return data_news_item

#читаем таблицу menu_url
def read_menu_url():
	con =sqlite3.connect(bd)
	cur = con.cursor()
	#Создаем запрос чтения к таблице news_item
	#cur.execute('SELECT my_id,menu,url FROM menu_url')
	cur.execute('CREATE TABLE IF NOT EXISTS menu_url(my_id INTEGER, menu TEXT, url TEXT)')
	cur.execute('SELECT my_id,menu FROM menu_url')
	data_menu_url = cur.fetchall()#помещаем запрос в переменную
	con.commit()
	cur.close()
	con.close()
	
	#---------------Удаляем заголовки меню со словом "Все" из списка
	list_del=[] #новый список 
	for i, n in data_menu_url:
		x = n.find("Все")
		if x > 1:
			list_del.append(i-1)

	for delete in reversed(list_del):
		data_menu_url.pop(delete)

	return data_menu_url
#----------------------------------------------------
# @thread #Создаем отдельный поток
def start_bd():
	b1.configure(text='Ждите результата') #Меняем название кнопки
	# b2.configure(state=DISABLED) #Кнопка добавить все (диактивируем)
	# b4.configure(state=DISABLED) #Кнопка добавить выделенное (диактивируем)
	view() #запуск заполнения базы (парсинг)
#-----------------------------------------------------

root = Tk()
root.title('Yandex новости для vMix (20.11.2018)')
root.minsize(660,490)
root.iconbitmap('data\\myicon.ico')

root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

l1 = ttk.LabelFrame(root,text='Список разделов')
l1.grid(row=0, column=0, padx=5, pady=5, sticky='enws')
#-----------------------
scrollbar1 = Scrollbar(l1, orient="vertical")
lis1 = Listbox(l1,relief=FLAT, width=35, height=8, selectmode=MULTIPLE, yscrollcommand=scrollbar1.set)
lis1.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)

#заполняем lis1 данными
lis1_load()

scrollbar1.config(command=lis1.yview)
scrollbar1.pack(side="left", fill="y")
#-----------------------
lf2 = Frame(l1)
lf2.pack(side=LEFT, fill=BOTH , expand=1, padx=5, pady=5)
b1 = ttk.Button(lf2, text='Получить данные', command=start_bd)
b1.pack(side=TOP,  fill=BOTH, expand=1, padx=5, pady=5)
# ll1 = ttk.Label(lf2,text='')
# ll1.pack(side=TOP,  fill=BOTH, expand=1, padx=5, pady=5)
pb_load = ttk.Progressbar(lf2, mode="determinate")
pb_load.pack(side=TOP,  fill=BOTH, expand=1, padx=5, pady=5)
b2 = ttk.Button(lf2, text='Добавить всё', command=lis1_all_copy)
b2.pack(side=TOP,  fill=BOTH, expand=1, padx=5, pady=5)
b3 = ttk.Button(lf2, width=10,  text='Удалить всё', command=lis2_del)
b3.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
b4 = ttk.Button(lf2, text='>>>', command=lis1_add_lis2)
b4.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
b5 = ttk.Button(lf2, text='<<<', command=lis2_add_lis1)
b5.pack(side=TOP, fill=BOTH, expand=1, padx=5, pady=5)
#-----------------------
scrollbar2 = Scrollbar(l1, orient="vertical")
lis2 = Listbox(l1,relief=FLAT, width=35, height=8, selectmode=MULTIPLE, yscrollcommand=scrollbar2.set)
lis2.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)

scrollbar2.config(command=lis2.yview)
scrollbar2.pack(side="right", fill="y")
#-----------------------
l2 = ttk.LabelFrame(root,text='Результат вывода')
l2.grid(row=1, column=0, padx=5, pady=5, sticky='enws')
#-----------------------Вывод новостей списком
scrollbar3 = Scrollbar(l2, orient="vertical")
lis3 = Listbox(l2,relief=FLAT, width=35, height=8, selectmode=MULTIPLE, yscrollcommand=scrollbar3.set)
lis3.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)

scrollbar3.config(command=lis3.yview)
scrollbar3.pack(side="right", fill="y")
#-----------------------Прогрессбар
l3 = Frame(root)
l3.grid(row=3, column=0, padx=5, pady=5, sticky='enws')

poetry = "Выбрано разделов - 0  Выведено записей - 0"
label2 = ttk.Label(l3,text=poetry, justify=LEFT)
label2.pack(side=LEFT,  padx=5, pady=5, fill=BOTH) #, expand=1
label2.configure(width=44)

pb_lis3 = ttk.Progressbar(l3, mode="determinate")
pb_lis3.pack(side=LEFT,  fill=BOTH, expand=1, padx=5, pady=5)

b_del_lis3 = ttk.Button(l3, text='Удалить выделеное', command=lis3_del_select)
b_del_lis3.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)

b_restore_lis3 = ttk.Button(l3, text='Вернуть вывод', command=restore)
b_restore_lis3.pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5)

b_restore_lis3.configure(state=DISABLED) #Деактивация клавиши востановить для lis3
b_del_lis3.configure(state=DISABLED)
#button_del_lis3() #Активация или деактивация клавищи удалить выделеное в lis3 

#b_del_lis3.bind('<Button-1>', button_del_lis3)
#-----------------------
l4 = ttk.LabelFrame(root,text='Настройки')
l4.grid(row=4, column=0, padx=5, pady=5, sticky='enws')

var1 = IntVar()
var1.set(1) # присваиваем значение переменной 1- включено   0-выключено
check1 = ttk.Checkbutton(l4,text=u'Выводить список разделов без подразделов', variable=var1, onvalue=0,offvalue=1, command=mini_munu_item)
check1.pack(side=LEFT,  padx=5, pady=5)
#check1.grid(row=4, column=0, padx=5, pady=5, sticky='enws')

var2 = IntVar()
var2.set(1) # присваиваем значение переменной 1- включено   0-выключено
check2 = ttk.Checkbutton(l4,text=u'Выводить разделы заглавными буквами', variable=var2, onvalue=0,offvalue=1, command=mini_munu_item)
check2.pack(side=LEFT,  padx=5, pady=5)
#check2.grid(row=5, column=0, padx=5, pady=5, sticky='enws')

l5 = ttk.LabelFrame(root,text='Сохранение под vMix')
l5.grid(row=5, column=0, padx=5, pady=5, sticky='enws')

b6 = ttk.Button(l5, text='Сохранить результат в формате CSV',command=saveasfile)
b6.pack(side=LEFT,  fill=BOTH, expand=1, padx=5, pady=5)
#b6.grid(row=4, column=1, padx=5, pady=5, sticky='enws')

pb = ttk.Progressbar(l5, mode="determinate")
pb.pack(side=LEFT,  fill=BOTH, expand=1, padx=5, pady=5)
#pb.grid(row=4, column=2, padx=5, pady=5, sticky='enws')
lis3.bind("<<ListboxSelect>>", button_del_lis3)

#Диалоговое окно закрытия программы
def on_closing():
	if messagebox.askokcancel("Закрыть", "Вы действительно хоите закрыть программу?"):
		#sys.exit()
		root.destroy()
		root.quit()
root.protocol("WM_DELETE_WINDOW", on_closing)

b2.configure(state=DISABLED)
b3.configure(state=DISABLED)
b4.configure(state=DISABLED)
b5.configure(state=DISABLED)
b6.configure(state=DISABLED) #Диактивируем клавишу сохранить
check1.configure(state=DISABLED)
check2.configure(state=DISABLED)
enable_element() #Активируем и дизактивируем элементы управления


root.update()
root.mainloop()
if __name__=='__main__':
  	pass


