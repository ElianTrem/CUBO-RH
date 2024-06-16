import psycopg2
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QScrollArea, QWidget

class DescriptionDialog(QDialog):
    def __init__(self, nombre_puesto, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Descripción del Puesto')
        self.setModal(True)

        # Obtener la descripción del puesto
        descripcion = self.obtener_descripcion_puesto(nombre_puesto)

        # Crear QLabel para mostrar la descripción
        self.label_description = QLabel(descripcion, self)
        self.label_description.setWordWrap(True)  # Para que el texto pueda ajustarse en varias líneas

        # Crear QDialogButtonBox para los botones del diálogo
        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)

        # Layout del diálogo
        layout = QVBoxLayout()
        scrollarea = QScrollArea()
        scrollcontent = QWidget(scrollarea)
        scrollarea.setWidgetResizable(True)  # El contenido se redimensiona con el scroll

        scroll_layout = QVBoxLayout(scrollcontent)
        scrollcontent.setLayout(scroll_layout)

        scroll_layout.addWidget(self.label_description)
        # Agregamos el widget del contenido al QScrollArea
        scrollarea.setWidget(scrollcontent)

        # Agregamos el QScrollArea al layout principal
        layout.addWidget(scrollarea)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def obtener_descripcion_puesto(self, nombre_puesto):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',  # Cambia esto si tu base de datos está en otro servidor
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT descripcion_markdown FROM puestos WHERE nombre = %s", (nombre_puesto,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                return 'Descripción no encontrada.'
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return 'Error al conectar a la base de datos.'
