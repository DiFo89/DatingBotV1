import sqlite3
import time
import datetime
import random
import os
import telebot
from config import token
from telebot import types
from threading import Thread

bot = telebot.TeleBot(token)

keyboard_menu = types.InlineKeyboardMarkup(row_width=2)
btn_browse = types.InlineKeyboardButton(text="Посмотреть анкеты", callback_data="browse")
keyboard_menu.add(btn_browse)

keyboard_menu_adm = types.InlineKeyboardMarkup(row_width=1)
btn_adm = types.InlineKeyboardButton(text="Вызвать админ меню", callback_data="admin")
keyboard_menu_adm.add(btn_browse, btn_adm)

keyboard_adm = types.InlineKeyboardMarkup(row_width=2)
add_adm = types.InlineKeyboardButton(text="Добавить админа", callback_data="add_adm")
delete_adm = types.InlineKeyboardButton(text="Удалить админа", callback_data="delete_adm")
keyboard_adm.add(add_adm, delete_adm)

keyboard_anketa = types.InlineKeyboardMarkup(row_width=2)
btn_select = types.InlineKeyboardButton(text="Выбрать", callback_data="select")
btn_next = types.InlineKeyboardButton(text="Следующая анкета", callback_data="next")
btn_back = types.InlineKeyboardButton(text="Назад", callback_data="back")
keyboard_anketa.add(btn_select, btn_next, btn_back)

keyboard_pay = types.InlineKeyboardMarkup(row_width=1)
btn_pay = types.InlineKeyboardButton(text="Оплатить", callback_data="pay", url="https://my.qiwi.com/Dmytryi-FuK6TTerEq")
btn_payback = types.InlineKeyboardButton(text="Назад", callback_data="payback")
keyboard_pay.add(btn_pay, btn_payback)


class Obj:
    def __init__(self, name, sname, patronymic, img, info, id=None):
        self.name = name
        self.sname = sname
        self.patronymic = patronymic
        self.img = img
        self.info = info
        self.id = id

    def __str__(self) -> str:
        if self.id != None:
            return "Имя: " + self.name + "\nФамилия: " + self.sname + "\nОтчество: " + self.patronymic + "\nКартинка: " + self.img + "\nОписание: " + self.info + "\nID: " + self.id
        else:
            return "Имя: " + self.name + "\nФамилия: " + self.sname + "\nОтчество: " + self.patronymic + "\nКартинка: " + self.img + "\nОписание: " + self.info


class ObjBox:
    count = 0

    def __init__(self):
        self.Box = []

    def update(self):
        self.Box.clear()
        con = sqlite3.connect(using_DB)
        cur = con.cursor()
        res = cur.execute("SELECT * from variants")

        for row in res:
            obj = Obj(row[1], row[2], row[3], row[4], row[5], str(row[0]))
            self.Box.append(obj)
        con.close()

    def addObj(self, obj):

        objs = [
            (obj.name, obj.sname, obj.patronymic, obj.img, obj.info)
        ]
        cntr = 0
        while (True):
            con = sqlite3.connect(using_DB)
            cur = con.cursor()
            try:
                cur.executemany("INSERT INTO variants (name, surname, patronymic, img, info) VALUES (?, ? , ? , ? , ?)",
                                objs)
                con.commit()
            except Exception as er:
                print("Error: ", er)
                time.sleep(4)
                cntr += 1
                if cntr >= 10:
                    print("Запись не удалось вставить")
                    break
                continue
            finally:
                con.close()
            print("Запись вставлена")
            ObjBox.update(self)
            break

    def get_num_obj(self, num):
        return self.Box[num]

    def del_obj(self, index):
        con = sqlite3.connect(using_DB)
        cur = con.cursor()
        textreq = "SELECT * FROM variants WHERE id =" + str(index)
        try:
            res = cur.execute(textreq).fetchone()
        except:
            return "Пиши цифрами"
        print(res)
        if res != None:
            try:
                cur.execute(f"DELETE FROM variants WHERE id = {index}")
                con.commit()
                ObjBox.update(self)
                return "Анкета была успешно удалена"
            except Exception as er:
                return "Ошибка: " + str(er)
        print("не найдено")
        con.close()
        return "Анкеты с таким ID не найдено"

    def getRnd(self):
        random_index = random.randrange(len(self.Box))
        return self.Box[random_index]

    def getnum(self):
        if (self.count >= len(self.Box)):
            self.count = -1
        self.count += 1
        return self.Box[self.count]

    def __str__(self) -> str:
        result = ""
        for i in self.Box:
            result += str(i) + "\n\n-----------\n\n\n"
        return result

    def __len__(self):
        return len(self.Box)


class DBName:
    def __init__(self, name, id=None):
        self.name = name
        self.id = id

    def __str__(self) -> str:
        if id != None:
            return "ID: " + str(self.id) + "\nНазвание: " + self.name
        else:
            return "Название: " + self.name


class DBNameBox:
    def __init__(self):
        self.DBBox = []

    def __str__(self) -> str:
        res = ""
        for i in self.DBBox:
            res += str(i) + "\n\n-----------\n\n\n"
        return res

    def change_db(self, index):
        global using_DB
        try:
            index = int(index)
        except Exception as er:
            return "Ошибка: " + str(er)
        for dbobj in self.DBBox:
            if dbobj.id == index:
                using_DB = dbobj.name
                objbox.update()
                return "База данных изменена на: " + dbobj.name
        return "Такой базы данных нет"

    def update_db(self):
        self.DBBox.clear()
        con = sqlite3.connect("DataBases.db")
        cur = con.cursor()
        res = cur.execute("SELECT * FROM DB_list")
        for row in res:
            dbobj = DBName(name=row[1], id=row[0])
            self.DBBox.append(dbobj)
        con.close()

    def get_text_databases(self) -> str:
        textmsg = ""
        for dbobj in self.DBBox:
            textmsg += str(dbobj.id) + " - " + dbobj.name
            if dbobj.name == using_DB:
                textmsg += " - используемая БД"
            textmsg += "\n\n"
        return textmsg

    def add_new_db(self, name):
        alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                    "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_"]
        for i in name:
            if i not in alphabet:
                return "Неверный синтаксис"

        try:
            con = sqlite3.connect("DataBases.db")
            cur = con.cursor()
            res = cur.execute("SELECT * FROM DB_list")
            for row in res:
                if row[1] == name + ".db" or row[1] == "DataBases.db":
                    return "Такое название БД уже есть"
            data = [
                (name + ".db")
            ]
            cur.execute("INSERT INTO DB_list(name) VALUES (?)", data)
            con.commit()
            con.close()
        except Exception as er:
            return "Ошибка: " + str(er) + " 1"

        try:
            con = sqlite3.connect(name + ".db")
            cur = con.cursor()
            cur.execute("""CREATE TABLE variants(id INTEGER PRIMARY KEY,
             name TEXT, 
             surname TEXT, 
             patronymic TEXT, 
             img TEXT, 
             info TEXT)
             """)
            cur.execute("""CREATE TABLE admins(id INTEGER PRIMARY KEY,
             user_id TEXT,
             level TEXT)""")
            cur.execute("""CREATE TABLE logs(id INTEGER PRIMARY KEY,
             fname TEXT,
             lname TEXT,
             text TEXT,
             button TEXT,
             time)""")
            cur.execute("""CREATE TABLE logs_admin(id INTEGER PRIMARY KEY,
             fname TEXT, 
             lname TEXT,
             num TEXT,
             time TEXT)""")
            data = []
            for row in king_list:
                data.append((row, 0))
                data.append((row, 1))
            cur.executemany("INSERT INTO admins(user_id, level) VALUES(?, ?)", data)
            data = []
            for row in admin_list:
                data.append((row, 1))
            cur.executemany("INSERT INTO admins(user_id, level) VALUES(?, ?)", data)
            con.commit()
            con.close()
            DBNameBox.update_db(self)
            return name + ".db" + " создана"
        except Exception as er:
            return "Ошибка: " + str(er) + " 2"


objbox = ObjBox()
dbnameobj = DBNameBox()

king_list = []
admin_list = []
formobj = Obj("", "", "", "", "")

using_DB = "otsosDB.db"


def update_adm_lists():
    con = sqlite3.connect(using_DB)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM admins")
    for row in res:
        if row[2] == "0":
            king_list.append(int(row[1]))
        else:
            admin_list.append(int(row[1]))
    con.close()


def add_new_admin(admid):
    try:
        con = sqlite3.connect(using_DB)
        cur = con.cursor()
        check = cur.execute(f"SELECT * FROM admins WHERE user_id ={admid}").fetchone()
        if check != None:
            con.close()
            return "Такой ID уже есть"
        cur.execute(f"INSERT INTO admins(user_id, level) VALUES ({admid}, {1})")
        con.commit()
        con.close()
        update_adm_lists()
        return "Админ успешно добавлен"
    except Exception as er:
        return "Ошибка: " + str(er)


def del_admin(admid):
    try:
        con = sqlite3.connect(using_DB)
        cur = con.cursor()
        check = cur.execute(f"SELECT * FROM admins WHERE user_id ={admid}").fetchone()
        if check == None:
            con.close()
            return "Такого ID нет"
        cur.execute(f"DELETE FROM admins WHERE user_id ={admid} and level ={1}")
        con.commit()
        con.close()
        update_adm_lists()
        return "Админ успешно удален"
    except Exception as er:
        return "Ошибка: " + str(er)


'''def get_text_databases() -> str:
    textmsg = ""
    for k, v in databases.items():
        textmsg += str(k) + " - " + v
        if v == using_DB:
            textmsg += " - используемая БД"
        textmsg += "\n\n"
    return textmsg

def change_db(index):
    global using_DB
    try:
        index = int(index)
    except Exception as er:
        return "Ошибка: " + str(er)
    for k, v in databases.items():
        if k == index:
            using_DB = v
            objbox.update()
            return "База данных изменена на: " + v
    return "Такой базы данных нет нет"

def add_new_db(name):
    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_"]
    nums = 0
    for i in name:
        if i not in alphabet:
            return "Неверный синтаксис"
    for k, v in databases.items():
        nums += 1
        if name + ".db" == v:
            return "Такое название БД уже есть"

    databases[nums + 1] = name + ".db"
    try:
        con = sqlite3.connect(name + ".db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE variants(id INTEGER PRIMARY KEY,
         name TEXT, 
         surname TEXT, 
         patronymic TEXT, 
         img TEXT, 
         info TEXT)
         """)
        cur.execute("""CREATE TABLE admins(id INTEGER PRIMARY KEY,
         user_id TEXT,
         level TEXT)""")
        cur.execute("""CREATE TABLE logs(id INTEGER PRIMARY KEY,
         fname TEXT,
         lname TEXT,
         text TEXT,
         button TEXT,
         time)""")
        cur.execute("""CREATE TABLE logs_admin(id INTEGER PRIMARY KEY,
         fname TEXT, 
         lname TEXT,
         num TEXT,
         time TEXT)""")
        data = []
        for row in king_list:
            data.append((row, 0))
            data.append((row, 1))
        cur.executemany("INSERT INTO admins(user_id, level) VALUES(?, ?)", data)
        data = []
        for row in admin_list:
            data.append((row, 1))
        cur.executemany("INSERT INTO admins(user_id, level) VALUES(?, ?)", data)
        con.commit()
        con.close()

        return name + ".db" + " создана"
    except Exception as er:
        return "Ошибка: " + str(er)'''


def send_message(id, message, keyboard=None):
    bot.send_message(id, text=message, reply_markup=keyboard)


def send_anceta(user_id, tempobj=None):
    if len(objbox) == 0:
        send_message(user_id, "Пусто")
        return
    a = 0
    if tempobj == None:
        tempobj = objbox.getRnd()
        a = 1
    src = "imgs/" + tempobj.img
    img = open(src, 'rb')
    bot.send_photo(user_id, img)
    if a == 1:
        send_message(user_id,
                     tempobj.name + " " + tempobj.sname + " " + tempobj.patronymic + "\nг.Ставрополь\n" + tempobj.info,
                     keyboard_anketa)
    else:
        send_message(user_id,
                     tempobj.name + " " + tempobj.sname + " " + tempobj.patronymic + "\nг.Ставрополь\n" + tempobj.info + "\nID: " + tempobj.id)


def send_all_anketa(user_id):
    if len(objbox) == 0:
        send_message(user_id, "Пусто")
    for i in range(0, len(objbox)):
        send_anceta(user_id, objbox.get_num_obj(i))


def send_menu(user_id):
    if user_id in admin_list:
        tempkeyboard = keyboard_menu_adm
    else:
        tempkeyboard = keyboard_menu
    send_message(user_id, "Главное меню", tempkeyboard)


def logmessage(call):
    print("\nСообщение: ", call.text, "\nПользователь: ", call.from_user.first_name, " ", call.from_user.last_name,
          "\n\n")
    con = sqlite3.connect(using_DB)
    cur = con.cursor()
    content = [
        (call.from_user.first_name, call.from_user.last_name, call.text, datetime.datetime.now())
    ]
    cur.executemany("INSERT INTO logs(fname, lname, text, time) VALUES(?, ?, ?, ?)", content)
    con.commit()
    con.close()


def logbutton(call):
    print("\nКнопка: ", call.data, "\nПользователь: ", call.from_user.first_name, " ", call.from_user.last_name, "\n\n")
    con = sqlite3.connect(using_DB)
    cur = con.cursor()
    content = [
        (call.from_user.first_name, call.from_user.last_name, call.data, datetime.datetime.now())
    ]
    cur.executemany("INSERT INTO logs(fname, lname, button, time) VALUES(?, ?, ?, ?)", content)
    con.commit()
    con.close()


@bot.message_handler(commands=['start'])
def start_message(message):
    logmessage(message)
    user_id = message.from_user.id
    send_message(user_id, "Привет, это бот для знакомств!")
    send_menu(user_id)


@bot.message_handler(commands=['help'])
def give_help(message):
    logmessage(message)
    user_id = message.from_user.id
    if user_id in admin_list:
        send_message(user_id, "Список команд:\n/fill\n/delete\n/show_all\n/add_admin\n/change_db\n/add_db")


@bot.message_handler(content_types=['text'])
def get_any_msg(message):
    logmessage(message)
    user_id = message.from_user.id
    msg = message.text.lower()
    print(message)
    if msg == "некис":
        send_message(user_id, "/gaba")
    elif msg == "/fill" and user_id in admin_list:
        send_message(user_id, "Заполнять аккуратно")
        send_message(message.from_user.id, "Имя: ")
        bot.register_next_step_handler(message, get_fname)
    elif msg == "/delete" and user_id in king_list:
        send_message(user_id, "Введи ID анкеты, которую хочешь удалить:")
        bot.register_next_step_handler(message, get_del_id)
    elif msg == "/show_all" and user_id in admin_list:
        Thread(target=send_all_anketa(user_id)).start()
    elif msg == "/add_admin" and user_id in king_list:
        send_message(user_id, "Введи ID пользователя:")
        bot.register_next_step_handler(message, get_adm_id_add)
    elif msg == "/delete_admin" and user_id in king_list:
        send_message(user_id, "Введи ID пользователя:")
        bot.register_next_step_handler(message, get_adm_id_del)
    elif msg == "/change_db" and user_id in king_list:
        send_message(user_id, dbnameobj.get_text_databases() + "\nВведи номер базы данных:")
        bot.register_next_step_handler(message, get_db)
    elif msg == "/add_db" and user_id in king_list:
        send_message(user_id, "Введи название новой бд:")
        bot.register_next_step_handler(message, get_name_db)
    else:
        send_message(user_id, "Такого варианта не предусмотрено")


def get_fname(message):
    global formobj
    formobj.name = message.text
    send_message(message.from_user.id, "Фамилия: ")
    bot.register_next_step_handler(message, get_lname)


def get_lname(message):
    global formobj
    formobj.sname = message.text
    send_message(message.from_user.id, "Отчество: ")
    bot.register_next_step_handler(message, get_patr)


def get_patr(message):
    global formobj
    formobj.patronymic = message.text
    send_message(message.from_user.id, "Фото: ")
    bot.register_next_step_handler(message, get_img)


def get_info(message):
    global formobj
    formobj.info = message.text
    Thread(target=objbox.addObj(formobj)).start()
    send_menu(message.from_user.id)


def get_del_id(message):
    delid = message.text
    send_message(message.from_user.id, objbox.del_obj(delid))


def get_adm_id_add(message):
    newadm = message.text
    send_message(message.from_user.id, add_new_admin(newadm))


def get_adm_id_del(message):
    deladm = message.text
    send_message(message.from_user.id, del_admin(deladm))


def get_db(message):
    newdb = message.text
    send_message(message.from_user.id, dbnameobj.change_db(newdb))
    # bot.register_next_step_handler(message, get_any_msg)


def get_name_db(message):
    newdb = message.text
    send_message(message.from_user.id, dbnameobj.add_new_db(newdb))


@bot.message_handler(content_types=['text'])
def get_img(message):
    global formobj
    if message.content_type == 'photo':
        file_photo = bot.get_file(message.photo[-1].file_id)
        filename, file_extention = os.path.splitext(file_photo.file_path)
        download_file = bot.download_file(file_photo.file_path)
        src = 'imgs/' + file_photo.file_id + file_extention
        with open(src, 'wb') as new_file:
            new_file.write(download_file)
        try:
            formobj.img = file_photo.file_id + file_extention
            send_message(message.from_user.id, "Описание: ")
            bot.register_next_step_handler(message, get_info)
        except:
            send_message(message.from_user.id, "Нужно вставлять фотографию (не файл)")
            bot.register_next_step_handler(message, get_any_msg)


@bot.callback_query_handler(func=lambda call: True)
def get_callback(call):
    print(call)
    data = call.data
    user_id = call.from_user.id
    bot.delete_message(call.from_user.id, call.message.id)
    logbutton(call)
    if data == "browse":
        send_anceta(user_id)
    if data == "back":
        send_menu(user_id)
    if data == "next":
        send_anceta(user_id)
    if data == "select":
        send_message(user_id, "Чтобы продолжить нужна оплата", keyboard_pay)
    if data == "payback":
        send_message(user_id, "Очень прискорбно")
        send_menu(user_id)
    if data == "pay":
        send_message(user_id, "Платеж прошел, скоро с вами свяжутся")
        send_menu(user_id)
    if data == "admin":
        send_message(user_id, "Это панель админа", keyboard_adm)
    if data == "add_adm":
        send_message(user_id, "Разрешены только символы русского алфавита")
        send_message(call.from_user.id, "Имя: ")
        # bot.register_next_step_handler(chat_id=call.from_user.id, callback=get_fname)
    if data == "delete_adm":
        if user_id in king_list:
            send_message(user_id, "Не реализовано")
            # bot.register_next_step_handler_by_chat_id(chat_id=call.from_user.id, callback=)


def main():
    print("start")
    Thread(target=bot.polling).start()
    objbox.update()
    update_adm_lists()
    dbnameobj.update_db()
    print(objbox)
    print(dbnameobj)


if __name__ == '__main__':
    main()

