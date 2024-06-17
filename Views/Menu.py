import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
import xml.etree.ElementTree as ET
from DescForm import Descriptor
from Expediente_Form import Expediente


class OpcionMenu(QPushButton):
    def __init__(self, text, contenedor_layout, parent=None):
        super().__init__(text, parent)
        # Guardar el contenedor_layout como atributo
        self.contenedor_layout = contenedor_layout
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                min-width: 200px;
                max-height: 35px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:checked {
                background-color: #9ED7A2;
            }
        """)
        self.clicked.connect(self.on_clicked)
        self.timer = None

    def on_clicked(self):
        # Desmarcar todos los botones del grupo
        for button in button_group:
            button.setChecked(False)
        # Marcar el botón actual
        self.setChecked(True)
        # Registrar el botón presionado
        print(f"Botón '{self.text()}' presionado")

        # Eliminar todos los widgets del contenedor dinámico
        while self.contenedor_layout.count():
            child = self.contenedor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Detener el temporizador si ya existe
        if self.timer and self.timer.isActive():
            self.timer.stop()

        # Agregar el widget correspondiente y configurar el temporizador
        if self.text() == "Descriptor de puestos":
            widget = Descriptor()
            self.contenedor_layout.addWidget(widget)
            self.start_timer("Descriptor")
        elif self.text() == "Expediente de trabajadores":
            widget = Expediente()
            self.contenedor_layout.addWidget(widget)
            self.start_timer("Expediente")
        else:
            # Agregar un widget vacío en caso de que no coincida con ninguna opción
            self.contenedor_layout.addWidget(QWidget())

    def start_timer(self, widget_type):
        # Crear un temporizador para actualizar el widget cada cierto tiempo
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_widget(widget_type))
        self.timer.start(5000)  # Intervalo de 5000 ms (5 segundos)

    def update_widget(self, widget_type):
        # Eliminar el widget actual
        while self.contenedor_layout.count():
            child = self.contenedor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Crear y agregar una nueva instancia del widget
        if widget_type == "Descriptor":
            widget = Descriptor()
        elif widget_type == "Expediente":
            widget = Expediente()
        else:
            widget = QWidget()
        self.contenedor_layout.addWidget(widget)
        print(f"Actualizando widget: {widget_type}")


class cerrarSesion(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                border: 1px solid #E11313;
                min-width: 20px;
                max-height: 50px;
                min-height: 37px;
            }
            QPushButton:hover {
                background-color: #E11313;
            }
            QPushButton:pressed {
                background-color: #CA4040;
            }
        """)


class MenuForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menu')
        self.setStyleSheet("background-color: #F5F5F5;")

        # Crear la "card"
        card_widget = QWidget(self)
        card_widget.setStyleSheet(
            "background-color: white; border-radius: 8px; ")
        card_layout = QHBoxLayout(card_widget)

        # Agregar dos widgets (Navbar y ContenedorDinamico) a la "card" con sus propios layouts
        Navbar = QWidget()
        ContenedorDinamico = QWidget()

        # Ajustar el tamaño de Navbar y ContenedorDinamico
        Navbar.setMinimumSize(320, self.height())
        Navbar.setMaximumWidth(320)
        ContenedorDinamico.setMinimumSize(600, self.height())

        # Crear layouts para Navbar y ContenedorDinamico
        navbar_layout = QVBoxLayout(Navbar)
        navbar_layout.setSpacing(8)  # Espacio de 20 px entre elementos
        # Alinear elementos en la parte superior
        navbar_layout.setAlignment(Qt.AlignTop)
        self.contenedor_layout = QVBoxLayout(ContenedorDinamico)

        # Cargar el menú desde el archivo XML
        menu_items = self.load_menu_from_xml('Menus/Admin.xml')
        self.generate_menu_buttons(
            menu_items, navbar_layout, self.contenedor_layout)

        card_layout.addWidget(Navbar)
        card_layout.addWidget(ContenedorDinamico)

        # Establecer el layout principal de la ventana
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(card_widget)
        self.setLayout(main_layout)

    def load_menu_from_xml(self, file_path):
        menu_items = []
        tree = ET.parse(file_path)
        root = tree.getroot()
        for section in root.findall('section'):
            title = section.get('title')
            menu_items.append({'title': title, 'options': []})
            for option in section.findall('option'):
                menu_items[-1]['options'].append(option.text)
        return menu_items

    def generate_menu_buttons(self, menu_items, layout, contenedor_layout):
        global button_group  # Variable global para el grupo de botones
        button_group = []  # Inicializar el grupo de botones
        for section in menu_items:
            title_label = QLabel(section['title'])
            title_label.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #000000;")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            for option in section['options']:
                # Pasar contenedor_layout como parámetro
                button = OpcionMenu(option, contenedor_layout)
                layout.addWidget(button)
                button_group.append(button)  # Agregar botón al grupo

        layout.addWidget(cerrarSesion("Cerrar Sesión"))
        layout.addStretch()  # Agregar un stretch al final para empujar los elementos hacia arriba


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MenuForm()
    form.showMaximized()
    form.show()
    sys.exit(app.exec_())
