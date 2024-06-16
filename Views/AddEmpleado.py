import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QDateEdit, QGridLayout, QMessageBox
)
from PyQt5.QtCore import QDate


class DropDown(QPushButton):
    def __init__(self, text, parent=None):
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
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agregar Empleado")
        self.setFixedSize(800, 600)
        self.conn = psycopg2.connect(
            dbname='BDCUBO',
            user='postgres',
            password='postgres123',
            host='localhost',
            port='5432'
        )
        self.cursor = self.conn.cursor()

        layout = QVBoxLayout()

        grid_layout = QGridLayout()

        # Nombre (candidatos)
        nombre_label = QLabel("Nombre:")
        grid_layout.addWidget(nombre_label, 0, 0)
        self.nombre_button = DropDown("Seleccionar Nombre")
        self.nombre_button.clicked.connect(self.show_nombres)
        grid_layout.addWidget(self.nombre_button, 0, 1)

        # Departamento
        depto_label = QLabel("Departamento:")
        grid_layout.addWidget(depto_label, 1, 0)
        self.depto_button = DropDown("Seleccionar Departamento")
        self.depto_button.clicked.connect(self.show_deptos)
        grid_layout.addWidget(self.depto_button, 1, 1)

        # Puesto de trabajo
        puesto_label = QLabel("Puesto de trabajo:")
        grid_layout.addWidget(puesto_label, 2, 0)
        self.puesto_button = DropDown("Seleccionar Puesto")
        self.puesto_button.clicked.connect(self.show_puestos)
        grid_layout.addWidget(self.puesto_button, 2, 1)

        # Fecha de ingreso
        fecha_label = QLabel("Fecha de ingreso:")
        grid_layout.addWidget(fecha_label, 3, 0)
        self.fecha_edit = QDateEdit()
        self.fecha_edit.setDate(QDate.currentDate())
        self.fecha_edit.setCalendarPopup(True)
        grid_layout.addWidget(self.fecha_edit, 3, 1)

        layout.addLayout(grid_layout)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_employee)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_nombres(self):
        try:
            self.cursor.execute("SELECT nombre FROM candidatos")
            nombres = [nombre[0] for nombre in self.cursor.fetchall()]
            if nombres:
                self.nombre_button.setMenu(QMenu(self.nombre_button))
                for nombre in nombres:
                    self.nombre_button.menu().addAction(nombre)
            else:
                QMessageBox.warning(self, "Advertencia",
                                    "No se encontraron nombres de candidatos.")
        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Error", f"Error al obtener nombres de candidatos: {e}")

    def show_deptos(self):
        try:
            self.cursor.execute("SELECT nombre FROM departamentos")
            departamentos = [depto[0] for depto in self.cursor.fetchall()]
            if departamentos:
                self.depto_button.setMenu(QMenu(self.depto_button))
                for depto in departamentos:
                    self.depto_button.menu().addAction(depto)
            else:
                QMessageBox.warning(self, "Advertencia",
                                    "No se encontraron departamentos.")
        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Error", f"Error al obtener departamentos: {e}")

    def show_puestos(self):
        try:
            self.cursor.execute("SELECT nombre FROM puestos")
            puestos = [puesto[0] for puesto in self.cursor.fetchall()]
            if puestos:
                self.puesto_button.setMenu(QMenu(self.puesto_button))
                for puesto in puestos:
                    self.puesto_button.menu().addAction(puesto)
            else:
                QMessageBox.warning(self, "Advertencia",
                                    "No se encontraron puestos de trabajo.")
        except psycopg2.Error as e:
            QMessageBox.critical(
                self, "Error", f"Error al obtener puestos de trabajo: {e}")

    def save_employee(self):
        # Aquí iría el código para guardar el empleado en la base de datos
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
