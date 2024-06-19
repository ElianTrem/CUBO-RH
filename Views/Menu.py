import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
import xml.etree.ElementTree as ET
from DescForm import Descriptor
from Expediente_Form import Expediente
from Descuentos_Prestaciones import Descuentos_Pestaciones
from Calculadora import Calcu
from Reclutamiento import Reclutamiento
from CambioContrasena import ChangePasswordForm
from Asistencias import Asistencias

class OpcionMenu(QPushButton):
    def __init__(self, text, contenedor_layout, id_user, parent=None):
        super().__init__(text, parent)
        self.id_user = id_user
        self.texto = text
        self.contenedor_layout = contenedor_layout
        self.parent = parent
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

    def on_clicked(self):
        # Desmarcar todos los botones del grupo
        for button in button_group:
            button.setChecked(False)
        # Marcar el botón actual
        self.setChecked(True)

        # Eliminar todos los widgets del contenedor dinámico
        while self.contenedor_layout.count():
            child = self.contenedor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Agregar el widget correspondiente
        if self.text() == "Descriptor de puestos":
            widget = Descriptor()
        elif self.text() == "Expediente de trabajadores":
            widget = Expediente()
        elif self.text() == "Reclutamiento":
            widget = Reclutamiento()
        elif self.text() == "Calcular prestaciones y descuentos":
            widget = Descuentos_Pestaciones()
            self.contenedor_layout.addWidget(widget)
        elif self.text() == "Calculadora prestaciones y descuentos":
            widget = Calcu()
            self.contenedor_layout.addWidget(widget)
        elif self.text() == "Cambiar contraseña":
            widget = ChangePasswordForm(self.id_user)
            self.contenedor_layout.addWidget(widget)
        elif self.text() == "Asistencias":
            widget = Asistencias(self.id_user)
            self.contenedor_layout.addWidget(widget)
        else:
            # Agregar un widget vacío en caso de que no coincida con ninguna opción
            widget = QWidget()
        self.contenedor_layout.addWidget(widget)

        # Actualizar el widget activo en el padre
        self.parent.set_active_widget(self.texto, widget)

    def start_timer(self, widget_type):
        # Crear un temporizador para actualizar el widget cada cierto tiempo
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_widget(widget_type))
        self.timer.start(5000)  # Intervalo de 5000 ms (5 segundos) 

    def update_widget(self, widget_type):
        print("Hola")
        #self.parent.update_active_widget()


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
    def __init__(self, id_user, rol):
        super().__init__()
        self.id_user = id_user
        self.rol = rol
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
        navbar_layout.setSpacing(8)  # Espacio de 8 px entre elementos
        # Alinear elementos en la parte superior
        navbar_layout.setAlignment(Qt.AlignTop)
        self.contenedor_layout = QVBoxLayout(ContenedorDinamico)

        # Inicializar el widget activo
        self.active_widget = None
        self.active_widget_type = None

        # Cargar el menú desde el archivo XML
        if self.rol == "admin":
            menu_items = self.load_menu_from_xml('Menus/Admin.xml')
        else:
            menu_items = self.load_menu_from_xml("Menus/Usuario.xml")
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
                # Pasar contenedor_layout y self como parámetros
                button = OpcionMenu(option, contenedor_layout, self.id_user, self)
                layout.addWidget(button)
                button_group.append(button)  # Agregar botón al grupo

        # Añadir el botón de "Actualizar"
        update_button = QPushButton("Actualizar")
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                min-width: 200px;
                max-height: 35px;
                min-height: 35px;
                border: 1px solid #4361EF;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #4361EF;
            }
        """)
        update_button.clicked.connect(self.update_active_widget)
        layout.addWidget(update_button)

        layout.addWidget(cerrarSesion("Cerrar Sesión"))
        layout.addStretch()  # Agregar un stretch al final para empujar los elementos hacia arriba

    def set_active_widget(self, widget_type, widget_instance):
        self.active_widget_type = widget_type
        self.active_widget = widget_instance

    def update_active_widget(self):
        # Eliminar el widget actual
        while self.contenedor_layout.count():
            child = self.contenedor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Crear y agregar una nueva instancia del widget activo
        if self.active_widget_type == "Descriptor de puestos":
            widget = Descriptor()
        elif self.active_widget_type == "Expediente de trabajadores":
            widget = Expediente()
        elif self.active_widget_type == "Reclutamiento":
            widget = Reclutamiento()
        elif self.active_widget_type == "Calcular prestaciones y descuentos":
            widget = Descuentos_Pestaciones()
        else:
            widget = QWidget()
        self.contenedor_layout.addWidget(widget)
        print(f"Actualizando widget: {self.active_widget_type}")
        # Actualizar la referencia del widget activo
        self.active_widget = widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MenuForm(id_user=1, rol="admin")
    form.showMaximized()
    form.show()
    sys.exit(app.exec_())
