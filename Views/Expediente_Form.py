import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QGridLayout,
)
from PyQt5.QtCore import Qt


class addBtn(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet(
            """
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
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #9ED7A2;
            }
        """
        )


def get_rows_from_database():
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
                SELECT e.id AS "ID", e.nombre AS "Nombre", d.nombre AS "Departamento", e.fecha_ingreso AS "Fecha de Inicio", 
                CASE WHEN e.activo THEN 'Activo' ELSE 'Inactivo' END AS "Estado"
                FROM empleados e
                JOIN departamentos d ON e.departamento = d.nombre;
            """
        )
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows


class Expediente(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.setStyleSheet("background-color: #FFFFFF;")

        main_layout = QVBoxLayout(self)

        btn = addBtn("Nuevo Empleado")
        main_layout.addWidget(btn)

        headers = ["ID", "Nombre", "Departamento", "Fecha de Inicio", "Estado"]
        widths = [50, 200, 200, 200, 100]  # Anchos fijos para cada columna

        # Agregamos un widget para los encabezados con cuadrícula
        headers_widget = QWidget(self)
        headers_widget.setStyleSheet(
            "background-color: #F3FAF3; max-height: 50px; min-height: 37px; border-radius: 8px;"
        )
        headers_layout = QGridLayout(headers_widget)

        for index, (header_text, width) in enumerate(zip(headers, widths)):
            header_label = QLabel(header_text)
            header_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
            header_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; width: {}px;".format(width)
            )
            headers_layout.addWidget(header_label, 0, index)

        main_layout.addWidget(headers_widget)

        # Obtener las filas de la base de datos y agregar cada fila
        rows = get_rows_from_database()
        for row in rows:
            grayrow_widget = QWidget(self)
            grayrow_widget.setStyleSheet(
                "background-color: #F5F5F5; max-height: 50px; min-height: 37px;"
            )
            grayrow_layout = QGridLayout(grayrow_widget)

            for index, (item, width) in enumerate(zip(row, widths)):
                item_label = QLabel(str(item))
                item_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
                item_label.setStyleSheet("font-size: 16px; width: {}px;".format(width))
                grayrow_layout.addWidget(item_label, 0, index)

            main_layout.addWidget(grayrow_widget)

        main_layout.addStretch()

    def get_widget(self):
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Expediente()
    form.show()
    sys.exit(app.exec_())
