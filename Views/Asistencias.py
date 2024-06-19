import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QCompleter, QHBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import QSize, Qt
import psycopg2
import xml.etree.ElementTree as ET
from WidgetAsistencia import Empleado_Asis

class Asistencias(QWidget):
    def __init__(self, id_user):
        super().__init__()
        self.setFixedSize(QSize(800, 850))
        self.id_user = id_user

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(5)

        # Buscar empleado
        self.search_employee_input = QLineEdit()
        self.search_employee_input.setPlaceholderText("Buscar empleado...")
        nombres = self.obtener_nombres_desde_bd()

        completer = QCompleter(nombres)
        self.search_employee_input.setCompleter(completer)
        completer.activated.connect(self.on_completer_activated)
        self.search_employee_input.setFixedHeight(30)
        grid_layout.addWidget(self.search_employee_input, 0, 0, 1, 2)

        self.buscar_button = addBtn('Buscar')
        self.buscar_button.setFixedWidth(90)
        grid_layout.addWidget(self.buscar_button, 0, 2, 1, 2)

        layout.addLayout(grid_layout)

        menu_widget = MenuFormAsis(self.id_user)
        layout.addWidget(menu_widget)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setStyleSheet("""
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
            QComboBox {
                background-color: white;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:editable {
                background: white;
            }
            QComboBox:!editable, QComboBox::drop-down:editable {
                background: white;
            }
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                background: white;
            }
            QComboBox:on {
                padding-top: 3px;
                padding-left: 4px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)

    def obtener_nombres_desde_bd(self):
        nombres = []
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM empleados")
            nombres = [row[0] for row in cursor.fetchall()]
            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
        return nombres

    def on_completer_activated(self, text):
        print(f"Empleado seleccionado: {text}")

    def obtener_salario_empleado(self, nombre_empleado):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT salario FROM empleados WHERE nombre = %s", (nombre_empleado,))
            empleado_salario = cursor.fetchone()
            conn.close()
            if empleado_salario:
                return empleado_salario[0]
            else:
                return None
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def obtener_id_empleado(self, nombre_empleado):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM empleados WHERE nombre = %s", (nombre_empleado,))
            empleado_id = cursor.fetchone()
            conn.close()
            if empleado_id:
                return empleado_id[0]
            else:
                return None
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def obtener_cantidad_asistencias(self, empleado_id):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cantidad_asistencias FROM asistencias WHERE empleado_id = %s", (empleado_id,))
            cantidad_asistencias = cursor.fetchone()[0]
            conn.close()
            return cantidad_asistencias
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

class addBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 200px;
                max-height: 50px;
                min-height: 37px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)

class MenuFormAsis(QWidget):
    def __init__(self, id_user):
        super().__init__()
        self.id_user = id_user
        self.setStyleSheet("background-color: #F5F5F5;")

        card_widget = QWidget(self)
        card_widget.setStyleSheet("background-color: white; border-radius: 8px;")
        card_layout = QHBoxLayout(card_widget)

        Navbar = QWidget()
        ContenedorDinamico = QWidget()

        Navbar.setMinimumSize(320, self.height())
        Navbar.setMaximumWidth(320)
        ContenedorDinamico.setMinimumSize(400, self.height())

        navbar_layout = QVBoxLayout(Navbar)
        navbar_layout.setSpacing(8)
        navbar_layout.setAlignment(Qt.AlignTop)
        self.contenedor_layout = QVBoxLayout(ContenedorDinamico)

        self.active_widget = None
        self.active_widget_type = None

        self.crear_xml_departamentos(self.obtener_departamentos())
        menu_items = self.load_menu_from_xml("Menus/departamentos.xml")
        self.generate_menu_buttons(menu_items, navbar_layout, self.contenedor_layout)

        card_layout.addWidget(Navbar)
        card_layout.addWidget(ContenedorDinamico)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(card_widget)
        self.setLayout(main_layout)

    def obtener_departamentos(self):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM departamentos")
            departamentos = cursor.fetchall()
            conn.close()
            return [departamento[0] for departamento in departamentos]
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return []

    def crear_xml_departamentos(self, departamentos):
        menu = ET.Element('menu')
        section = ET.SubElement(menu, 'section', title="Departamentos")

        for departamento in departamentos:
            option = ET.SubElement(section, 'option')
            option.text = departamento

        tree = ET.ElementTree(menu)
        with open("Menus/departamentos.xml", "wb") as fh:
            tree.write(fh, encoding='utf-8', xml_declaration=True)

    def load_menu_from_xml(self, file_path):
        menu_items = []
        tree = ET.parse(file_path)
        root = tree.getroot()
        for section in root.findall('section'):
            title = section.get('title')
            menu_items.append({'title': title, 'options': []})
            for option in section.findall('option'):
                menu_items[-1]['options'].append(option.text)
        return menu_items

    def generate_menu_buttons(self, menu_items, layout, contenedor_layout):
        global button_group
        button_group = []
        for section in menu_items:
            title_label = QLabel(section['title'])
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            for option in section['options']:
                button = OpcionMenu(option, contenedor_layout, self.id_user, self)
                layout.addWidget(button)
                button_group.append(button)

class OpcionMenu(QPushButton):
    def __init__(self, text, contenedor_layout, id_user, parent=None):
        super().__init__(text, parent)
        self.id_user = id_user
        self.texto = text
        self.contenedor_layout = contenedor_layout
        self.parent = parent
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                min-width: 200px;
                max-height: 35px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:checked {
                background-color: #9ED7A2;
            }
        """)
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        for button in button_group:
            button.setChecked(False)
        self.setChecked(True)

        while self.contenedor_layout.count():
            child = self.contenedor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        widget = Empleado_Asis(self.text())
        self.contenedor_layout.addWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = Asistencias(id_user=1)
    main_win.show()
    sys.exit(app.exec_())
