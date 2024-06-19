import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QComboBox, QPushButton, QHBoxLayout, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def get_attendance_data(empleado_id, year, month):
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
            """
            SELECT fecha, entrada, salida, horas_trabajadas
            FROM asistencias
            WHERE empleado_id = %s AND EXTRACT(YEAR FROM fecha) = %s AND EXTRACT(MONTH FROM fecha) = %s
            """, (empleado_id, year, month)
        )
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows

def get_employee_info(nombre_empleado):
    empleado_info = None
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
            "SELECT id, puesto_trabajo FROM empleados WHERE nombre = %s", (nombre_empleado,)
        )
        result = cursor.fetchone()
        if result:
            empleado_info = {"id": result[0], "puesto_trabajo": result[1]}
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return empleado_info

class AttendanceView(QWidget):
    def __init__(self, nombre_empleado):
        super().__init__()
        self.nombre_empleado = nombre_empleado
        empleado_info = get_employee_info(nombre_empleado)
        if not empleado_info:
            QMessageBox.critical(self, "Error", f"No se encontró al empleado: {nombre_empleado}")
            return

        self.empleado_id = empleado_info["id"]
        self.puesto_trabajo = empleado_info["puesto_trabajo"]

        self.setWindowTitle(f'Asistencias de {nombre_empleado}')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(self)

        # Información del empleado
        self.employee_info = QLabel(f"{nombre_empleado}\n{self.puesto_trabajo}")
        self.employee_info.setFont(QFont('Arial', 20))
        self.employee_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.employee_info)

        # Selector de año y mes
        controls_layout = QHBoxLayout()
        self.year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(2019, current_year + 1):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(current_year))
        controls_layout.addWidget(self.year_combo)

        self.month_combo = QComboBox()
        month_names = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        for month in month_names:
            self.month_combo.addItem(month)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        controls_layout.addWidget(self.month_combo)

        self.export_button = QPushButton("Exportar a PDF")
        self.export_button.clicked.connect(self.export_to_pdf)
        controls_layout.addWidget(self.export_button)

        layout.addLayout(controls_layout)

        # Tabla de asistencias
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Fecha", "Entrada", "Salida", "Horas trabajadas"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.year_combo.currentTextChanged.connect(self.load_data)
        self.month_combo.currentIndexChanged.connect(self.load_data)

        self.load_data()

    def load_data(self):
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1
        data = get_attendance_data(self.empleado_id, year, month)

        self.table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

    def export_to_pdf(self):
        year = int(self.year_combo.currentText())
        month = self.month_combo.currentIndex() + 1
        month_name = self.month_combo.currentText()
        data = get_attendance_data(self.empleado_id, year, month)

        file_name = f"Asistencias_{self.nombre_empleado.replace(' ', '_')}_{year}_{month_name}.pdf"
        c = canvas.Canvas(file_name, pagesize=letter)
        c.setFont("Helvetica", 12)

        c.drawString(30, 750, f"Asistencias de {self.nombre_empleado}")
        c.drawString(30, 735, f"Mes: {month_name} Año: {year}")

        x_offset = 30
        y_offset = 700
        row_height = 20

        c.drawString(x_offset, y_offset, "Fecha")
        c.drawString(x_offset + 100, y_offset, "Entrada")
        c.drawString(x_offset + 200, y_offset, "Salida")
        c.drawString(x_offset + 300, y_offset, "Horas laborales")

        for row in data:
            y_offset -= row_height
            c.drawString(x_offset, y_offset, str(row[0]))
            c.drawString(x_offset + 100, y_offset, str(row[1]))
            c.drawString(x_offset + 200, y_offset, str(row[2]))
            c.drawString(x_offset + 300, y_offset, str(row[3]))

        c.save()
        print(f"Archivo PDF guardado como {file_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AttendanceView("Carlos Lopez")
    window.show()
    sys.exit(app.exec_())
