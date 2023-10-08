import sys
import sqlite3
# from functools import wraps
from PyQt6 import uic, QtCore
from PyQt6 import QtWidgets as qtw
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import config

db_name = 'database.db'


def send_args_inside_func(func):
    def wrapper(*args, **kwargs):
        return lambda: func(*args, **kwargs)
    
    return wrapper


def get_data(db_name, table=None, query="SELECT * FROM {}"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    query = query.format(table) or query
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data


def get_headers(table):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    cursor.fetchall()
    data = [descr[0] for descr in cursor.description]
    conn.close()
    return data


def new_get_data(table=None, query=None):
    Query = QSqlQuery()
    if not query and not table:
        return None
    query = f"SELECT * FROM {table}"
    Query.exec(query)
    model = QSqlTableModel()
    model.setQuery(Query)
    return model


def show_data(table, query):
    model = new_get_data(table, query)
    view = qtw.QTableView()
    view.setModel(model)
    view.show()


class Window():
    def __init__(self, ui) -> None:
        # get all table names in self.tables
        Form, Window = uic.loadUiType(ui)
        self.window = Window()
        self.form = Form()
        self.form.setupUi(self.window)
        # window.show()
    
    def connect_db(self, db_name):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(db_name)
        if not db.open():
            print('Не удалось подключиться к базе')
            return False
        return db


class FilterWindow(Window):
    def __init__(self, ui) -> None:
        super().__init__(ui)
        self.meta = {"FOs": [""], "regions": [""], "cities": [""], "universities": [""]}
        self.query_template = """
        SELECT DISTINCT {select_column} 
        FROM Tp_nir JOIN VUZ ON Tp_nir.codvuz = VUZ.codvuz
        WHERE {column} = "{value}" """

        for data in get_data(db_name, query="SELECT DISTINCT region, oblname, city, z2 FROM VUZ"):
            self.meta['FOs'].append(data[0])    
            self.meta['regions'].append(data[1])    
            self.meta['cities'].append(data[2])    
            self.meta['universities'].append(data[3])    
        
        self.meta = {k: sorted(set(v)) for k, v in self.meta.items()}
        self.form.comboBoxFOs.addItems(self.meta['FOs'])
        self.form.comboBoxRegions.addItems(self.meta['regions'])
        self.form.comboBoxCities.addItems(self.meta['cities'])
        self.form.comboBoxUniversities.addItems(self.meta['universities'])
    
    def get_combobox_values(self, target_column):
        query = []
        for column, box_name in zip(["region", "oblname", "city", "VUZ.z2"],
                                    ["FOs", "Regions", "Cities", "Universities"]):
            if column == target_column:
                break
            value = getattr(self.form, f"comboBox{box_name}").currentText()
            print(value)
            if value:
                query.append(self.query_template.format(column=column,
                                                        value=value,
                                                        select_column=target_column))
        if query:
            query = "\nINTERSECT\n".join(set(query))
        else:
            query = f"SELECT DISTINCT {target_column} FROM VUZ"
        return sorted([element[0] for element in get_data(db_name, query=query)])
        
    
    def FO_filter(self):
        regions = self.get_combobox_values("oblname")
        self.meta['regions'] = [""] + regions
        self.form.comboBoxRegions.clear()
        self.form.comboBoxRegions.addItems(self.meta['regions'])

    def region_filter(self):
        cities = self.get_combobox_values("city")
        print(cities)
        self.meta['cities'] = [""] + cities
        self.form.comboBoxCities.clear()
        self.form.comboBoxCities.addItems(self.meta['cities'])
        # kregion = self.form.comboBoxRegions.currentText()
        # if region not in self.meta['regions']:
        #     return
        # self.region = region
        # cities = get_data(
        #     db_name, 
        #     query=f"SELECT DISTINCT city FROM VUZ WHERE oblname = '{region}'")
        # self.meta['cities'] = [""] + [city[0] for city in cities]
        # self.form.comboBoxCities.clear()
        # self.form.comboBoxCities.addItems(self.meta['cities'])
            
    def city_filter(self):
        universities = self.get_combobox_values("VUZ.z2")
        self.meta['universities'] = [""] + universities
        self.form.comboBoxUniversities.clear()
        self.form.comboBoxUniversities.addItems(self.meta['universities'])
        # city = self.form.comboBoxCities.currentText()
        # if city not in self.meta['cities']:
        #     return
        # self.city = city
        # universities = get_data(
        #     db_name, 
        #     query=f"SELECT DISTINCT z2 FROM VUZ WHERE city = '{city}'")
        # self.meta['universities'] = [""] + [university[0] for university in universities]
        # self.form.comboBoxUniversities.clear()
        # self.form.comboBoxUniversities.addItems(self.meta['universities'])

    @send_args_inside_func
    def apply_filter(self, main_window):
        query_template = """
        SELECT Tp_nir.* 
        FROM Tp_nir JOIN VUZ ON Tp_nir.codvuz = VUZ.codvuz
        WHERE {column} = "{value}"
        """
        query = []
        for column, box_name in zip(["region", "oblname", "city", "z2"],
                                    ["FOs", "Regions", "Cities", "Universities"]):
            value = getattr(self.form, f"comboBox{box_name}").currentText()
            if value:
                query.append(query_template.format(column=column, value=value))

        if not query:
            return
        
        data = get_data(main_window.db_name, query="\nINTERSECT\n".join(query))
        main_window.show_table('Tp_nir', 'Nir', 'Информация о НИР', config.TP_NIR_HEADERS,
                            config.TP_NIR_COLUMN_WIDTH, data)


class MainWindow(Window):
    def __init__(self, ui, db_name) -> None:
        if not self.connect_db(db_name):
            sys.exit(-1)

        print('Connection OK')
        self.db_name = db_name
        tables = get_data(db_name, 
                          query="SELECT * FROM sqlite_master WHERE type='table'")
        self.tables = [t[1] for t in tables]
        super().__init__(ui)

        

    def show_table(self, table, widgetname, title='', headers=None,
                   column_widths=None, data=None):
        # check if table exists in database
        if not data:
            data = get_data(self.db_name, table)

        getattr(self.form, f"{widgetname}ViewWidget").setRowCount(len(data))
        getattr(self.form, f"{widgetname}ViewWidget").setColumnCount(len(data[0]))
        for i in range(len(data)):
            for j in range(len(data[0])):
                item = qtw.QTableWidgetItem(str(data[i][j]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
                getattr(self.form, f"{widgetname}ViewWidget").setItem(i, j, item)

        if headers:
            getattr(self.form, f"{widgetname}ViewWidget").setHorizontalHeaderLabels(headers)

        if column_widths and len(column_widths) == len(data[0]):
            for column, width in enumerate(column_widths):
                getattr(self.form, f"{widgetname}ViewWidget").setColumnWidth(column, width)

        sort_enabled = False if widgetname == "Nir" else True
        getattr(self.form, f"{widgetname}ViewWidget").setSortingEnabled(sort_enabled)
        getattr(self.form, f"{widgetname}Label").setText(title) 


@send_args_inside_func
def sort_selected(window: MainWindow):
    item = window.form.comboBoxSort.currentText()
    if item.endswith('Кода'):
        if item == "Сортировка по Убыванию Кода":
            order = QtCore.Qt.SortOrder.DescendingOrder
        elif item == "Сортировка по Увеличению Кода":
            order = QtCore.Qt.SortOrder.AscendingOrder
        window.form.NirViewWidget.setSortingEnabled(False)
        column_names = ', '.join(get_headers('Tp_nir')[2:])
        data = get_data(db_name,
                        query=f"""SELECT codvuz || rnw AS clmn,  {column_names} 
                        FROM Tp_nir 
                        ORDER BY codvuz, clmn""")
        headers = ['Код + рнв ебень'] + list(config.TP_NIR_HEADERS[2:])
        window.show_table('Tp_nir', 'Nir', 'Информация о НИР', data=data, headers=headers)
        window.form.NirViewWidget.sortItems(0, order)
    else:
        sort_toggle = False if item == "Без сортировки" else True
        window.show_table('Tp_nir', 'Nir', 'Информация о НИР', headers=config.TP_NIR_HEADERS,
                            column_widths=config.TP_NIR_COLUMN_WIDTH)
        window.form.NirViewWidget.setSortingEnabled(sort_toggle)
        

    

def close_all():
    main_window.window.close()
    filter_window.window.close()
    exit_window.window.close()


app = qtw.QApplication([])
exit_window = Window('ex_aht.ui')
main_window = MainWindow('MainForm_layout.ui', db_name)
filter_window = FilterWindow('filtr.ui')
# main_window.show_table('VUZ', 'Vuz')
for values in zip(main_window.tables, config.widgetnames,
                    ['Информация о финансировании', 'Информация о ВУЗах',
                    'Информация о рубриках ГРНТИ', 'Информация о НИР', ],
                    [config.TP_FV_HEADERS, config.VUZ_HEADERS,
                    config.GRNTI_HEADERS, config.TP_NIR_HEADERS],
                    [config.TP_FV_COLUMN_WIDTH, config.VUZ_COLUMN_WIDTH,
                    config.GRNTI_COLUMN_WIDTH, config.TP_NIR_COLUMN_WIDTH], [None]*4):
    main_window.show_table(*values)


filter_window.form.comboBoxFOs.currentTextChanged.connect(filter_window.FO_filter)
filter_window.form.comboBoxRegions.currentTextChanged.connect(filter_window.region_filter)
filter_window.form.comboBoxCities.currentTextChanged.connect(filter_window.city_filter)
# filter_window.form.comboBoxUniversities.currentTextChanged.connect()
filter_window.form.filterButton.clicked.connect(filter_window.apply_filter(main_window))

main_window.form.comboBoxSort.currentTextChanged.connect(sort_selected(main_window))
main_window.form.filterButton.clicked.connect(filter_window.window.show)
filter_window.form.cancelButton.clicked.connect(filter_window.window.close)
main_window.window.show()
main_window.form.exitButton.clicked.connect(exit_window.window.show)
exit_window.form.agreeButton.clicked.connect(close_all)
exit_window.form.cancelButton.clicked.connect(exit_window.window.close)
exit(app.exec())
