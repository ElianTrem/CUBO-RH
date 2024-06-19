import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from Asistencias_Empleado import AttendanceView  # Asegúrate de que el archivo esté en el mismo directorio

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()

def get_rows_from_database(departamento):
    rows = []
    try:
        conn = psycopg2.connect(
            dbname="BDCUBO",
            user="postgres",
            password="postgres123",
            host="localhost",
            port="5432",
        )
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre, puesto_trabajo FROM empleados WHERE departamento = %s", (departamento,))
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows

class Empleado_Asis(QWidget):
    def __init__(self, departamento):
        super().__init__()
        self.child_windows = []
        self.setStyleSheet("background-color: #FFFFFF;")
        self.departamento = departamento
        self.setWindowTitle('Listado de Empleados')
        self.setStyleSheet('background-color: #FFFFFF; border-radius: 15px;')
        self.setFixedSize(400, 600)  # Ajusta el tamaño de la ventana

        # Asigna un layout a este widget
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.load_data()

    def load_data(self):
        # Limpiar la ventana principal
        for i in reversed(range(self.main_layout.count())):
            widget = self.main_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Obtener las filas de la base de datos y agregar cada fila
        rows = get_rows_from_database(self.departamento)
        for row in rows:
            grayrow_widget = QWidget(self)
            grayrow_widget.setStyleSheet(
                "background-color: #F5F5F5; max-height: 70px; min-height: 37px; margin-bottom: 5px;"
            )
            grayrow_layout = QVBoxLayout(grayrow_widget)

            nombre_label = ClickableLabel(row[0])
            nombre_label.setFont(QFont('Arial', 16))
            nombre_label.setAlignment(Qt.AlignCenter)
            nombre_label.clicked.connect(
                lambda name=row[0]: self.on_label_click(name))

            puesto_label = QLabel(row[1])
            puesto_label.setFont(QFont('Arial', 12))
            puesto_label.setAlignment(Qt.AlignCenter)
            puesto_label.setStyleSheet('color: #7D7D7D;')

            grayrow_layout.addWidget(nombre_label)
            grayrow_layout.addWidget(puesto_label)

            self.main_layout.addWidget(grayrow_widget)
        self.main_layout.addStretch()

    def on_label_click(self, name):
        form = AttendanceView(name)
        self.child_windows.append(form)  # Mantén una referencia a la ventana
        form.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Empleado_Asis(departamento="Recursos Humanos")
    form.show()
    sys.exit(app.exec_())