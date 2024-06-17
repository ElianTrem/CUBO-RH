import sys
import psycopg2
import re
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QWidget, QPushButton,
    QLabel, QDateEdit, QGridLayout, QLineEdit, QCheckBox, QMenu, QAction
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from dialog import QuickAlert  # Importar libreria de diálogos


class DropDown(QPushButton):
    def __init__(self, text, query, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 300px;
                max-height: 50px;
                min-height: 37px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #9ED7A2;
            }
            QPushButton::menu-indicator {
                subcontrol-position: right center;
            }
        """)
        self.items = []
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute(query)
            self.items = cursor.fetchall()
            conn.close()
            print(f"Items cargados para {text}:", self.items)
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

        self.menu = QMenu()
        self.actions = []
        for item in self.items:
            action = QAction(item[0], self)
            action.triggered.connect(
                lambda checked, text=item[0]: self.on_triggered(text))
            self.actions.append(action)
            self.menu.addAction(action)
        self.menu.setStyleSheet("""
            QMenu {                
                background-color: #9ED7A2;
                color: #000000;
                border-radius: 12px;
                max-width: 300px;
                min-width: 300px;
            }
            QMenu::item {
                background-color: #FFFFFF;
                color: #000000;
                max-width: 300px;
                min-width: 300px;
            }
            QMenu::item:selected {
                background-color: #9ED7A2;
            }
        """)
        self.setMenu(self.menu)

    def on_triggered(self, text):
        print(f"Item seleccionado: {text}")
        self.setText(text)
        self.setChecked(False)


class EmpleadoDialog(QDialog):
    guardado = pyqtSignal(bool)

    def __init__(self, employee_id=None):
        super().__init__()
        self.setWindowTitle(
            "Agregar Empleado" if not employee_id else "Editar Empleado")
        self.employee_id = employee_id

        layout = QVBoxLayout()  # Elimina container y usa layout directamente
        grid_layout = QGridLayout()

        # Nombre (candidatos)
        nombre_label = QLabel("Nombre:")
        nombre_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(nombre_label, 0, 0)
        self.nombre_button = DropDown(
            "Seleccionar Nombre", "SELECT nombre FROM candidatos")
        grid_layout.addWidget(self.nombre_button, 1, 0)
        if employee_id:
            self.nombre_button.setEnabled(False)

        # Departamento
        depto_label = QLabel("Departamento:")
        depto_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(depto_label, 0, 1)
        self.depto_button = DropDown(
            "Seleccionar Departamento", "SELECT nombre FROM departamentos")
        grid_layout.addWidget(self.depto_button, 1, 1)

        # Puesto de trabajo
        puesto_label = QLabel("Puesto de trabajo:")
        puesto_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(puesto_label, 2, 0)
        self.puesto_button = DropDown(
            "Seleccionar Puesto", "SELECT nombre FROM puestos")
        grid_layout.addWidget(self.puesto_button, 3, 0)

        # Fecha de ingreso
        fecha_label = QLabel("Fecha de ingreso:")
        fecha_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(fecha_label, 2, 1)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        if employee_id:
            self.fecha_edit.setReadOnly(True)
        self.fecha_edit.setStyleSheet("""
            QDateEdit {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 300px;
                max-height: 50px;
                min-height: 37px;
            }
            QDateEdit::drop-down {
                subcontrol-position: right center;
            }
        """)
        grid_layout.addWidget(self.fecha_edit, 3, 1)

        # Correo electrónico
        email_label = QLabel("Correo electrónico:")
        email_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(email_label, 4, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ingrese el correo electrónico")
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 300px;
                max-height: 50px;
                min-height: 37px;
            }
        """)
        grid_layout.addWidget(self.email_input, 5, 0)

        # Estado activo/inactivo
        active_label = QLabel("Estado activo:")
        active_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        grid_layout.addWidget(active_label, 4, 1)
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 16px;
                max-width: 300px;
                max-height: 50px;
                min-height: 37px;
            }
        """)
        grid_layout.addWidget(self.active_checkbox, 5, 1)

        layout.addLayout(grid_layout)
        layout.addStretch()

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_employee)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if employee_id:
            self.load_employee_data(employee_id)

    def load_employee_data(self, employee_id):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nombre, departamento, puesto_trabajo, fecha_ingreso, email, activo FROM empleados WHERE id = %s", (employee_id,))
            employee_data = cursor.fetchone()
            conn.close()

            if employee_data:
                self.nombre_button.setText(employee_data[0])
                self.depto_button.setText(employee_data[1])
                self.puesto_button.setText(employee_data[2])
                self.fecha_edit.setDate(QDate.fromString(
                    employee_data[3], "yyyy-MM-dd"))
                self.email_input.setText(employee_data[4])
                self.active_checkbox.setChecked(employee_data[5])
            else:
                error_dialog = QuickAlert(
                    'error', 'Error', 'Empleado no encontrado.')
                error_dialog.exec_()
                self.close()
        except psycopg2.Error as e:
            error_dialog = QuickAlert(
                'error', 'Error', f"Error al cargar empleado: {e}")
            error_dialog.exec_()

    def save_employee(self):
        nombre = self.nombre_button.text()
        departamento = self.depto_button.text()
        puesto_trabajo = self.puesto_button.text()
        fecha_ingreso = self.fecha_edit.date().toString("yyyy-MM-dd")
        email = self.email_input.text()
        activo = self.active_checkbox.isChecked()

        if not self.validate_email(email):
            error_dialog = QuickAlert(
                'error', 'Error', 'Por favor, ingrese un correo electrónico válido.')
            error_dialog.exec_()
            return

        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            if self.employee_id:
                cursor.execute("""
                    UPDATE empleados
                    SET departamento = %s, puesto_trabajo = %s, fecha_ingreso = %s, email = %s, activo = %s
                    WHERE id = %s
                """, (departamento, puesto_trabajo, fecha_ingreso, email, activo, self.employee_id))
            else:
                cursor.execute("""
                    INSERT INTO empleados (nombre, departamento, puesto_trabajo, fecha_ingreso, email, activo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, departamento, puesto_trabajo, fecha_ingreso, email, activo))

            conn.commit()
            conn.close()

            succeess_dialog = QuickAlert(
                'success', 'Éxito', 'Empleado guardado correctamente.')
            succeess_dialog.exec_()
            self.close()
        except psycopg2.Error as e:
            error_dialog = QuickAlert(
                'error', 'Error', f"Error al guardar empleado: {e}")
            error_dialog.exec_()

    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmpleadoDialog(employee_id=4)
    window.show()
    sys.exit(app.exec_())
