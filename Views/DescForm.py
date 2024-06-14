import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt

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

class Descriptor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menu')
        self.setStyleSheet("background-color: #FFFFFF;")

        # Creamos el layout vertical principal
        main_layout = QVBoxLayout(self)

        # Agregamos el botón con texto "Nuevo Puesto de Trabajo"
        btn = addBtn('Nuevo Puesto de Trabajo')
        main_layout.addWidget(btn)

        # Creamos un widget para las filas con encabezados
        rows_widget = QWidget(self)
        rows_widget.setStyleSheet("background-color: #F3FAF3; max-height: 50px; min-height: 37px;")  # Color de fondo para las filas
        rows_layout = QHBoxLayout(rows_widget)

        # Agregamos los encabezados con estilo
        headers = ['Encabezado 1', 'Encabezado 2', 'Encabezado 3', 'Encabezado 4']
        for header_text in headers:
            header_label = QLabel(header_text)
            #aliniar arriba del widget
            header_label.setAlignment(Qt.AlignTop)            
            header_label.setStyleSheet("font-weight: bold; font-size: 18px;")# Texto en negrita y tamaño 18
            rows_layout.addWidget(header_label)
            rows_layout.addStretch()

        # Agregamos el widget de las filas al layout principal pero con un stretch de 1
        main_layout.addWidget(rows_widget)
        main_layout.addStretch()

    def get_widget(self):
        return self

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Descriptor()
    form.show()
    sys.exit(app.exec_())
