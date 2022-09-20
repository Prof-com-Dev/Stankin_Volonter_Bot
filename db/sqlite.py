import sqlite3
from sqlite3 import Error
import json
from config import Config


class SQLInteract:
    """в values_of_this_table можно использовать только ключевые слова PRIMARY KEY (помимо самих имен столбцов).
    заметка на завтра в values_of_this_table указывать что хочешь, а нужную часть для generate_dict() обозначать особыми символами
    filename_db=cfg.config["path"] + '/db/users.db' по стандарту ставь"""

    # внизу чисто аргументы пишешь и все,
    # по моей задумке для каждой таблицы ты создаешь новый объект класса, и взаимодействуешь с ним в рамках класса
    def __init__(self, filename_db, table_name="employees",
                 values_of_this_table="(id, name, password, "
                                      "post, tests)", init_values="()"):
        self.filename_db = filename_db
        self.table_name = table_name
        self.values_of_this_table = values_of_this_table
        self.values = self.generating_values()
        self.db_connection = self.sql_connect(self.filename_db)
        self.cursor_obj = sqlite3.Cursor(self.db_connection)
        self.init_values = init_values

    @staticmethod
    def sql_connect(filename_Db):
        try:
            con = sqlite3.connect(filename_Db)
            return con
        except sqlite3.Error as err:
            print(err)

    def sql_add_new_user(self, user_obj):
        try:
            user_obj[0] = self.search_max_int_field() + 1
            self.cursor_obj.execute(
                f'''INSERT INTO {self.table_name}{self.values_of_this_table} VALUES{self.values}''', user_obj)
            self.db_connection.commit()
            return True
        except sqlite3.Error as err:
            print(err)
            return False

    def sql_create_new_table(self):
        """После инициализации нужно один раз ручками создать таблицу, ну вот надо так.
        Создается она на основании данных заполненных при инициализации класса"""
        self.cursor_obj.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} {self.init_values}")
        self.db_connection.commit()

    def sql_delete_one(self, search_name="id", need_value_of_name="DEfault VaLue123Qwcsa"):
        """ with no args delete max(id)
         real default need_value_of_name = f'(SELECT MAX(id) FROM {self.table_name})'"""

        if need_value_of_name == "DEfault VaLue123Qwcsa":
            need_value_of_name = f"(SELECT MAX(id) FROM {self.table_name})"
        self.cursor_obj.execute(f"DELETE FROM {self.table_name} WHERE {search_name}={need_value_of_name}")
        self.db_connection.commit()

    def sql_update_one_by_id(self, update_field, update_value, search_id):
        try:
            """if type update_value == str: update_value must be quotes in quotes new_text = "'some text'" """
            if type(update_value) == str:
                update_value = update_value.replace('"', "'")
                self.cursor_obj.execute(f'''UPDATE {self.table_name} SET {update_field} = "{update_value}"'''
                                        f'''WHERE id = {search_id}''')
            else:
                self.cursor_obj.execute(
                    f'''UPDATE {self.table_name} SET {update_field} = {update_value}'''  # разница в кавычках
                    f'''WHERE id = {search_id}''')
            self.db_connection.commit()
            return True
        except sqlite3.Error as err:
            print(err)
            return False

    def sql_free_command(self, command):
        self.cursor_obj.execute(command)
        self.db_connection.commit()

    def sql_get_user_with_namePass(self, name, password):
        try:
            if str(type(password)) == "<class 'str'>":
                self.cursor_obj.execute(f'''SELECT * FROM {self.table_name} WHERE name = "{name}"'''
                                        f''' AND password = "{password}"''')
            else:
                self.cursor_obj.execute(f'''SELECT * FROM {self.table_name} WHERE name = "{name}"'''
                                        f''' AND password = {password}''')
            row = self.cursor_obj.fetchone()
            if (row is not None) and (row != False):
                dict_row = self.generate_dict(row)
                return dict_row
            else:
                return False
        except sqlite3.Error as e:
            print(e)
            return False

    def sql_get_user_with_id(self, input_id):
        try:
            self.cursor_obj.execute(f'''SELECT * FROM {self.table_name} WHERE id = {input_id}''')
            row = self.cursor_obj.fetchone()
            dict_row = self.generate_dict(row)
            dict_row["tests"] = self.get_all_tests(user=dict_row)
            return dict_row
        except sqlite3.Error as e:
            print(e)

    # def sql_rewrite_user(self, id, ):
    #     pass

    def return_full_table(self, name_of_table="0", revert=False, to_dict=False, element_for_transform="tests") -> list:
        """with no arguments just return table list
        revert will be True or False, if True return sorted on date"""
        if name_of_table == "0":  # если ничего юзер не указал, то выводим всю таблицу указанную при инициализации
            # класса
            name_of_table = self.table_name
        with self.db_connection:
            self.cursor_obj.execute(f"SELECT * FROM {name_of_table}")
            rows = self.cursor_obj.fetchall()
            if to_dict:
                for i in range(len(rows)):
                    rows[i] = self.generate_dict(rows[i])
                    rows[i][element_for_transform] = self.get_all_tests(value=rows[i][element_for_transform],
                                                                        need_value=element_for_transform)
            if revert:
                return rows[::-1]
            else:
                return rows

    def generating_values(self):
        count_comma = self.values_of_this_table.count(",")
        values_str = "(?" + (", ?" * count_comma) + ")"
        return values_str

    def search_max_int_field(self, search_name="id"):  # поиск максимального инт значения в дб для создания нового юзера
        self.cursor_obj.execute(
            f"SELECT * FROM {self.table_name} WHERE {search_name}=(select max({search_name}) from {self.table_name})")
        max_id = self.cursor_obj.fetchall()
        if len(max_id) == 0:
            return 0
        else:
            return max_id[0][0]

    def generate_dict(self, user):
        values = self.values_of_this_table[1:-1].replace('PRIMARY KEY', '').replace('(', '') \
            .replace(')', '').replace(' ', '').split(',')
        dict_of_user = []
        for i in range(len(values)):
            dict_of_user.append([values[i], user[i]])
        dict_of_user = dict(dict_of_user)
        return dict_of_user

    @staticmethod
    def get_all_tests(value='', need_value="tests", user_id=None) -> list:
        """из строки(json) делает dict"""
        # if value != '':
        #     got_user = value
        # # elif user_id is not None:
        # #     got_user = self.sql_get_user_with_id(user_id)
        # else:
        #     return None
        return json.loads(value.replace("'", '"'))

    def all_tables_name(self):
        self.cursor_obj.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return self.cursor_obj.fetchall()

    def drop_table(self):
        self.cursor_obj.execute(f"DROP TABLE {self.table_name}")


if __name__ == '__main__':
    # cfg = Config()
    # s = SQLInteract(table_name="testcase", filename_db=cfg.config["path"] + "/db/users.db")

    # s.sql_create_new_table()
    # s.drop_table()
    # user1 = (s.sql_get_user_with_namePass('ILYA3224', '1234'))
    # print(user1)
    # print(s.all_tables_name())

    # print(s.sql_get_user_with_id(3))
    # s.sql_delete_one()
    # print(s.return_full_table(to_dict=True, revert=True))
    # u = subprocess.run('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    # print(u.stdout, u.stderr, u.returncode)
    #     print(type('s') == str)
    # new_user = [0, "Rel", "123123", "Junior", "[]"]
    # new = {"sad": 1, "sasd": "123"}
    # for i in new:
    #     print(i)
    # user_dict = s.generate_dict(s.sql_get_user_with_namePass('Jim', '123123'))
    # print(user_dict)

    # s.sql_add_new_user(user_obj=new_user)

    # s.sql_update_one_by_id("name", "'Jim'", 3)

    # s.sql_delete_one(need_value_of_name=2)
    # print(s.return_full_table())
    # test_db = SQLInteract(table_name="tests", filename_db=cfg.config["path"] + "/db/users.db",
    #                       values_of_this_table="(id, name, theme, max_result, questions)",
    #                       init_values="(id int PRIMARY KEY, name text, theme text, max_result int, questions)")
    # # test_db.sql_create_new_table()
    # new_test = [0, "ЕГЭ по математике", "math", 100, "[]"]
    # # test_db.sql_add_new_user(new_test)
    # print(test_db.return_full_table(to_dict=True, element_for_transform="questions"))
    # print(test_db.all_tables_name())
    # # print(test_db.get_all_tests(need_value="questions", user=test_db.sql_get_user_with_id(1)))
    # print("except is work")
