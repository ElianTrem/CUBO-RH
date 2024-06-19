import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dialog import QuickAlert  # Importar libreria de diálogos


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def mousePressEvent(self, event):
        self.clicked.emit()


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
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #9ED7A2;
            }
        """)


def get_rows_from_database():
    rows = []
    try:
        conn = psycopg2.connect(
            dbname='BDCUBO',
            user='postgres',
            password='postgres123',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("""
            select id, nombre, resultado from evaluaciones
        """)
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows


class RepEvaluacion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menu')
        self.setStyleSheet("background-color: #FFFFFF;")

        # Creamos el layout vertical principal
        main_layout = QVBoxLayout(self)

        # Agregamos el botón con texto "Generar PDF"
        btn = addBtn('Generar PDF')
        main_layout.addWidget(btn)
        # Generamos el PDF cuando se hace clic en el botón
        btn.clicked.connect(self.generate_pdf)

        # Agregamos los encabezados obtenidos de la base de datos
        headers = ["id", "Nombre", "Resultado De la evaluacion"]
        widths = [200, 200, 100, 50]  # Anchos fijos para cada columna

        # Agregamos un widget para los encabezados con cuadrícula
        headers_widget = QWidget(self)
        headers_widget.setStyleSheet(
            "background-color: #F3FAF3; max-height: 50px; min-height: 37px; border-radius: 8px;")
        headers_layout = QGridLayout(headers_widget)

        for index, (header_text, width) in enumerate(zip(headers, widths)):
            header_label = QLabel(header_text)
            header_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
            header_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; width: {}px;".format(width))
            headers_layout.addWidget(header_label, 0, index)

        main_layout.addWidget(headers_widget)

        # Obtener las filas de la base de datos y agregar cada fila
        self.rows = get_rows_from_database()
        for row in self.rows:
            grayrow_widget = QWidget(self)
            grayrow_widget.setStyleSheet(
                "background-color: #F5F5F5; max-height: 50px; min-height: 37px;")
            grayrow_layout = QGridLayout(grayrow_widget)

            for index, (item, width) in enumerate(zip(row, widths)):
                if index == 0:  # Si es el primer elemento de la fila
                    item_label = ClickableLabel(str(item))
                    item_label.clicked.connect(
                        lambda item=item: self.on_label_click(item))
                else:
                    item_label = QLabel(str(item))

                item_label.setAlignment(Qt.AlignCenter)
                item_label.setStyleSheet(
                    "font-size: 16px; width: {}px;".format(width))
                grayrow_layout.addWidget(item_label, 0, index)

            main_layout.addWidget(grayrow_widget)

        main_layout.addStretch()

    def on_label_click(self, item):
        print(f"Label clicked: {item}")

    def generate_pdf(self):
        pdf_filename = "evaluaciones.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        c.setFont("Helvetica", 12)
        c.drawString(30, height - 40, "Reporte de Evaluaciones")

        # Table headers
        headers = ["ID", "Nombre", "Resultado"]
        y = height - 80
        for row in headers:
            c.drawString(30 + headers.index(row) * 100, y, row)

        # Table rows
        for row in self.rows:
            y = height - 120 - 20 * self.rows.index(row)
            for index, item in enumerate(row):
                c.drawString(30 + index * 100, y, str(item))

        c.save()
        print(f"PDF generado: {pdf_filename}")
        success_dialog = QuickAlert(
            'success', 'Éxito', f"PDF generado: {pdf_filename}")

    def get_widget(self):
        return self


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = RepEvaluacion()
    form.show()
    sys.exit(app.exec_())
