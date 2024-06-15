import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from dialog import QuickAlert  # Importar libreria de diálogos
from Menu import MenuForm

class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None  # Mantener referencia al hilo de trabajo
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login Form')

        # Crear widgets
        label_email = QLabel('Correo electrónico')
        label_password = QLabel('Contraseña')
        self.line_edit_email = QLineEdit()
        self.line_edit_password = QLineEdit()
        self.line_edit_password.setEchoMode(QLineEdit.Password)  # Ocultar texto de la contraseña
        self.line_edit_email.setPlaceholderText('Ingrese su correo electrónico')
        self.line_edit_password.setPlaceholderText('Ingrese su contraseña')

        button_login = QPushButton('Iniciar sesión')

        # Configurar colores para los campos de entrada, sin borde y con elevación
        self.line_edit_email.setStyleSheet("background-color: #F5F5F5; border-radius: 4px; border: 0px solid #CCCCCC; height: 40px;")
        self.line_edit_password.setStyleSheet("background-color: #F5F5F5; border-radius: 4px; border: 0px solid #CCCCCC; height: 40px;")
        label_email.setStyleSheet("color: #000000; font-weight: bold; font-size: 16px; height: 10px;")
        label_password.setStyleSheet("color: #000000; font-weight: bold; font-size: 16px; height: 10px;")

        # Configurar layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(main_layout)
        # Agregamos color de fondo
        self.setStyleSheet("background-color: #FFFFFF;")

        # Crear tarjeta con elevación y de un tamaño máximo de 1229 por 729
        card_widget = QWidget()
        card_widget.setStyleSheet("background-color: white; border-radius: 8px; ")

        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(20, 20, 20, 20)  # Agregar márgenes al layout de la tarjeta
        card_widget.setLayout(card_layout)

        # Configurar layout de la imagen y formulario dentro de la tarjeta
        login_layout = QHBoxLayout()
        login_layout.setSpacing(20)  # Agregar espacio entre la imagen y el formulario
        card_layout.addLayout(login_layout)

        # Cargar imagen desde archivo local
        pixmap = QPixmap('img/image.png')  # Ruta de la imagen
        label_image = QLabel()
        # Ampliar la imagen a 541x217 y mejorar la calidad de la imagen
        label_image.setPixmap(pixmap.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        login_layout.addWidget(label_image)

        # Crear un contenedor de formulario para aplicar estilo
        form_container = QWidget()
        form_container.setStyleSheet("background-color: #FfFfFf; border-radius: 8px;")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)  # Agregar márgenes al layout del formulario
        form_layout.setSpacing(20)  # Aumentar espacio entre los elementos del formulario
        login_layout.addWidget(form_container)

        form_layout.addWidget(label_email)
        form_layout.addWidget(self.line_edit_email)
        form_layout.addWidget(label_password)
        form_layout.addWidget(self.line_edit_password)

        # Configurar botón de inicio de sesión
        button_login.setStyleSheet("""
            QPushButton {
                background-color: #9ED7A2;
                font-size: 20px;
                font-weight: bold;
                color: #000000;
                border-radius: 6px;
                border: none;
                min-width: 150px;
                max-height: 50px;
            }
            QPushButton:hover {
                background-color: #7fb48b;
            }
            QPushButton:pressed {
                background-color: #609770;
            }
        """)

        button_login.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Prevent the button from expanding

        button_layout = QHBoxLayout()  # Crear un nuevo layout horizontal para el botón
        button_layout.addStretch()  # Add stretch to the left
        button_layout.addWidget(button_login)  # Agregar el botón al layout horizontal
        button_layout.addStretch()  # Add stretch to the right
        form_layout.addLayout(button_layout)  # Agregar el layout horizontal al layout del formulario

        main_layout.addWidget(card_widget)
        button_login.clicked.connect(self.start_loading)

    def start_loading(self):
        email = self.line_edit_email.text()
        password = self.line_edit_password.text()

        if not email or not password:
            error_dialog = QuickAlert('error', 'Error', 'Por favor, complete todos los campos.')
            error_dialog.exec_()
            return

        def long_running_operation():
            # Conectar a la base de datos y verificar credenciales
            try:
                conn = psycopg2.connect(
                    dbname='BDCUBO',
                    user='postgres',
                    password='postgres123',
                    host='localhost',  # Cambia esto si tu base de datos está en otro servidor
                    port='5432'
                )
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND contrasena=%s", (email, password))
                user = cursor.fetchone()
                conn.close()
                if user:
                    return True
                else:
                    return False
            except psycopg2.Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                return False

        self.worker_thread = WorkerThread(long_running_operation)
        self.worker_thread.threadSignal.connect(self.handle_login_result)
        self.worker_thread.start()

    def handle_login_result(self, success):
        if success:
            success_dialog = QuickAlert('success', 'Éxito', 'Inicio de sesión exitoso')
            success_dialog.exec_()
            self.main_window = MenuForm()  # Crear una instancia de la ventana principal
            self.main_window.showMaximized()  # Mostrar la ventana principal maximizada
            self.close()  # Cerrar la ventana actual de inicio de sesión
        else:
            error_dialog = QuickAlert('error', 'Error', 'Correo electrónico o contraseña incorrectos.')
            error_dialog.exec_()

    def closeEvent(self, event):
        # Asegurarse de detener el hilo antes de cerrar la ventana
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        event.accept()

class WorkerThread(QThread):
    threadSignal = pyqtSignal(bool)

    def __init__(self, operation_function, parent=None):
        super().__init__(parent)
        self.operation_function = operation_function

    def run(self):
        # Ejecutar la operación larga y emitir la señal con el resultado que es un booleano
        result = self.operation_function()
        self.threadSignal.emit(result)  # Emite la señal con el resultado de la operación

def main():
    app = QApplication(sys.argv)
    ex = LoginForm()
    ex.showMaximized()  
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
