import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QGridLayout,
)
import threading
import time
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from AddCandidato import AddCandidato


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()


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
                SELECT p.nombre AS puesto, d.nombre AS departamento, COALESCE(COUNT(pc.candidato_id), 0) AS cantidad_candidatos
                FROM puestos p
                JOIN puestos_departamentos pd ON p.id = pd.puesto_id
                JOIN departamentos d ON pd.departamento_id = d.id
                LEFT JOIN puestos_candidatos pc ON p.id = pc.puesto_id
                GROUP BY p.nombre, d.nombre;
            """
        )
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows


class Reclutamiento(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.setStyleSheet("background-color: #FFFFFF;")

        main_layout = QVBoxLayout(self)

        btn_widget = QWidget()  # Widget para contener el botón
        btn_layout = QVBoxLayout(btn_widget)

        self.btn_postulacion = QPushButton("Nueva postulacion")
        self.btn_postulacion.setStyleSheet(
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
        self.btn_postulacion.clicked.connect(self.open_AddCandidato)
        btn_layout.addWidget(self.btn_postulacion)

        # Agregar el widget del botón al diseño principal
        main_layout.addWidget(btn_widget)

        self.headers = ["Puesto", "Departamento", "Candidatos"]
        # Anchos fijos para cada columna
        self.widths = [50, 200, 200, 200, 100]

        self.load_data()  # Cargar los datos al inicio

    def open_AddCandidato(self):
        dialog = AddCandidato()
        dialog.exec_()

    def load_data(self):
        # Limpiar la ventana principal
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        main_layout = self.layout()

        # Agregar el widget del botón
        btn_widget = QWidget()  # Widget para contener el botón
        btn_layout = QVBoxLayout(btn_widget)
        btn_layout.addWidget(self.btn_postulacion)
        main_layout.addWidget(btn_widget)

        # Agregar encabezados
        headers_widget = QWidget(self)
        headers_widget.setStyleSheet(
            "background-color: #F3FAF3; max-height: 50px; min-height: 37px; border-radius: 8px;"
        )
        headers_layout = QGridLayout(headers_widget)

        for index, (header_text, width) in enumerate(zip(self.headers, self.widths)):
            header_label = QLabel(header_text)
            header_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
            header_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; width: {}px;".format(
                    width)
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

            for index, (item, width) in enumerate(zip(row, self.widths)):
                if index == 0:  # Si es el primer elemento de la fila
                    item_label = ClickableLabel(str(item))
                    item_label.clicked.connect(
                        lambda item=item: self.on_label_click(item))
                else:
                    item_label = QLabel(str(item))
                item_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
                item_label.setStyleSheet(
                    "font-size: 16px; width: {}px;".format(width)
                )
                grayrow_layout.addWidget(item_label, 0, index)

            main_layout.addWidget(grayrow_widget)

        main_layout.addStretch()

    def on_label_click(self, id_empleado):
        print(f"ID del empleado: {id_empleado}")
        dialog = EmpleadoDialog(id_empleado)
        dialog.exec_()

    def get_widget(self):
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Reclutamiento()
    form.show()
    sys.exit(app.exec_())
