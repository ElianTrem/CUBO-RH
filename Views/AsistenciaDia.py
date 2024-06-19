import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont
import datetime

from dialog import QuickAlert

def get_connection():
    return psycopg2.connect(
        dbname="BDCUBO",
        user="postgres",
        password="postgres123",
        host="localhost",
        port="5432",
    )

def get_attendance_status(empleado_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT entrada, salida
            FROM asistencias
            WHERE empleado_id = %s AND fecha = CURRENT_DATE
            """, (empleado_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def mark_entry(empleado_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().replace(microsecond=0)  # Remover microsegundos
        cursor.execute(
            """
            INSERT INTO asistencias (empleado_id, fecha, dia, entrada)
            VALUES (%s, CURRENT_DATE, %s, %s)
            """, (empleado_id, now.strftime('%A'), now.time()))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

def mark_exit(empleado_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().replace(microsecond=0)  # Remover microsegundos
        cursor.execute(
            """
            UPDATE asistencias
            SET salida = %s,
                horas_trabajadas = EXTRACT(EPOCH FROM (TIME %s - entrada)) / 3600
            WHERE empleado_id = %s AND fecha = CURRENT_DATE
            """, (now.time(), now.time(), empleado_id))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")

class AttendanceWidget(QWidget):
    def __init__(self, empleado_id):
        super().__init__()
        self.empleado_id = empleado_id
        self.setWindowTitle('Marcado de Asistencia')
        self.setFixedSize(950, 600)
        self.init_ui()
        self.update_status()
        self.update_datetime()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.datetime_label = QLabel(self)
        self.datetime_label.setFont(QFont('Arial', 44))
        self.datetime_label.setAlignment(Qt.AlignCenter)

        style = """
        QLabel{
            margin-left: 100px;
            margin-bottom: 100px;
        }
        QPushButton{
            margin-left: 100px;
            margin-bottom: 100px;
            background-color: #9ED7A2;
        }
        """

        self.label = QLabel('Bienvenido, por favor marque su asistencia', self)
        self.label.setFont(QFont('Arial', 44))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(style)
        self.datetime_label.setStyleSheet(style)

        self.button = QPushButton('Marcar Entrada', self)
        self.button.setFont(QFont('Arial', 32))
        self.button.clicked.connect(self.on_button_click)
        self.button.setStyleSheet(style)

        self.layout.addWidget(self.datetime_label)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)
        self.layout.addStretch()

        # Actualiza la fecha y hora cada segundo
        timer = QTimer(self)
        timer.timeout.connect(self.update_datetime)
        timer.start(1000)

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString('yyyy-MM-dd hh:mm:ss'))

    def update_status(self):
        status = get_attendance_status(self.empleado_id)
        if status:
            entrada, salida = status
            if entrada and not salida:
                self.label.setText('Marque su salida')
                self.button.setText('Marcar Salida')
            elif entrada and salida:
                self.label.setText('Ya ha marcado sus asistencias')
                self.button.setEnabled(False)
        else:
            self.label.setText('Marque su entrada')
            self.button.setText('Marcar Entrada')

    def on_button_click(self):
        status = get_attendance_status(self.empleado_id)
        if status:
            entrada, salida = status
            if entrada and not salida:
                mark_exit(self.empleado_id)
                success_dialog = QuickAlert(
                'success', 'Asistencia', 'Salida marcada exitosamente.')
                success_dialog.exec_()
            elif entrada and salida:
                success_dialog = QuickAlert(
                'error', 'Asistencia', 'Ya ha marcado sus asistencias.')
                success_dialog.exec_()
        else:
            mark_entry(self.empleado_id)
            success_dialog = QuickAlert(
            'success', 'Asistencia', 'Entrada marcada exitosamente.')
            success_dialog.exec_()
        self.update_status()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    empleado_id = 1  # ID del empleado (puedes obtener esto de otra parte de tu aplicación)
    widget = AttendanceWidget(empleado_id)
    widget.show()
    sys.exit(app.exec_())
