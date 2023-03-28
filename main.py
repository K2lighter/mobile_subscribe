import datetime
import sqlite3

subscribe_month = 0
count = 0
day = int(datetime.datetime.now().day)
month = int(datetime.datetime.now().month)
year = int(datetime.datetime.now().year)


class DataBase:
    """Класс для работы с базой данных"""

    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file)
        self.cur = self.con.cursor()

    def create_table(self, sql_q):
        """Создание таблицы"""
        with self.con:
            self.cur.execute(sql_q)
            self.con.commit()
            return True

    def insert_user(self, user_name, balance, tariff, activity):
        """Создание пользователя"""
        with self.con:
            result = self.cur.execute("""SELECT User_name FROM mobile_users""").fetchall()
            if user_name not in (user[0] for user in result):
                self.cur.execute("""INSERT INTO 'mobile_users'
                ('User_name', 'Balance', 'Mobile_tariff_ref', 'Activity') VALUES(?, ?, ?, ?);""",
                                 (user_name, balance, tariff, activity,))
                self.con.commit()
                print(f'Создан новый пользователь по имени: {user_name}')
                return True
            else:
                print("Пользователь с таким именем уже существует")
                return False

    def insert_tariff(self, tariff, price):
        """Создание тарифа"""
        with self.con:
            result = self.cur.execute("""SELECT Tariff FROM mobile_tariff""").fetchall()
            if tariff not in (tar[0] for tar in result):
                self.cur.execute("""INSERT INTO 'mobile_tariff'
                                ('Tariff', 'Price') VALUES(?, ?);""",
                                 (tariff, price))
                self.con.commit()
                print(f'Создан новый тариф: {tariff}')
                return True
            else:
                print("Тариф с таким названием уже существует")
                return False

    def drop_table(self, data):
        """Удаление таблицы"""
        with self.con:
            self.cur.execute(f"""DROP TABLE {data}""")
            self.con.commit()
            print(f"Удаление таблицы {data}")
            return True

    def payment(self):
        with self.con:
            result = self.cur.execute("""
            SELECT UserID, User_name, Balance, Activity, Tariff, Price FROM mobile_users
            JOIN mobile_tariff ON mobile_users.Mobile_tariff_ref = mobile_tariff.TariffID;""").fetchall()
            for user in result:
                user_id = user[0]
                user_name = user[1]
                balance = user[2]
                activity = user[3]
                tariff = user[4]
                price = user[5]
                if activity == "Yes":
                    if balance >= price:
                        self.cur.execute(
                            f"""UPDATE mobile_users SET Balance = {balance - price} WHERE UserID = {user_id}""")
                        print(f"{user_name}, по вашему тарифу: {tariff}, было списано: {price}")
                        self.con.commit()
                    else:
                        print(f"{user_name} на вашем счету недостаточно средств")
                        self.cur.execute(f"""UPDATE mobile_users SET Activity = 'No' WHERE Balance < {price}""")
                        self.con.commit()


def subscribe_period():
    try:
        global subscribe_month
        subscribe_month = int(input("Введите период расчета: "))
        if subscribe_month <= 0:
            print("Вы ввели недопустимое количество месяцев")
            subscribe_period()
        else:
            return True

    except ValueError:
        print("Вы ввели недопустимое значение")
        subscribe_period()


def last_month(sub):
    if month + sub > 12:
        m = (month + sub) % 12
        y = year + (month + sub) // 12
        return datetime.date(y, m, day)
    else:
        m = month + sub
        return datetime.date(year, m, day)


def main():
    global count
    last_date = subscribe_period()
    print(f'Тариф действует до {last_date}')
    data = DataBase('mobile.db')
    data.create_table("""
    CREATE TABLE IF NOT EXISTS mobile_users(
    UserID INTEGER PRIMARY KEY AUTOINCREMENT,
    User_name TEXT NOT NULL,
    Balance INTEGER NOT NULL,
    Mobile_tariff_ref INTEGER NOT NULL,
    Activity Text NOT NULL);""")

    data.create_table("""
    CREATE TABLE IF NOT EXISTS mobile_tariff(
    TariffID INTEGER PRIMARY KEY AUTOINCREMENT,
    Tariff TEXT NOT NULL,
    Price INTEGER NOT NULL);""")

    data.insert_user("User1", 10000, 2, "Yes")
    data.insert_user("User2", 10000, 3, "Yes")
    data.insert_user("User3", 10000, 1, "Yes")

    data.insert_tariff("Standard", 500)
    data.insert_tariff("VIP", 1000)
    data.insert_tariff("Premium", 1500)

    while True:
        if datetime.date.today() > last_month(subscribe_month):
            print("Период подписки закончен")
            return False
        else:
            if datetime.date.today() == last_month(count):
                print(f"Сегодня: {last_month(count)} день оплаты")
                data.payment()
                count += 1
                if subscribe_month - count > 0:
                    print(f"Следующее списание: {last_month(count)}")
                else:
                    print("Это последний месяц действия подписки")


if __name__ == "__main__":
    main()
