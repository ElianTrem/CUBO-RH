import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, QWidget, QPushButton,
    QLabel, QLineEdit, QMessageBox, QMenu, QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QSize, QRegExp
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from dialog import QuickAlert  # Importar libreria de diálogos


class ContentReceiver(QObject):
    def __init__(self):
        super().__init__()
        self.conn = psycopg2.connect(
            dbname='BDCUBO',
            user='postgres',
            password='postgres123',
            host='localhost',
            port='5432'
        )
        self.cursor = self.conn.cursor()

    @pyqtSlot(str)
    def receiveContent(self, content):
        print("Content received from CKEditor:", content)
        # Verificar si se ha ingresado el nombre del puesto
        if window.job_title_input.text() == "":
            error_dialog = QuickAlert(
                'error', 'Error', 'Por favor, Ingrese el nombre del puesto.')
            error_dialog.exec_()
        else:
            nombre = window.job_title_input.text()
            email = window.email_input.text()
            telefono = window.phone_input.text()
            puesto_nombre = window.puestos_dropdown.text()
            departamento_nombre = window.departamentos_dropdown.text()
            titulo_academico_nombre = window.titulos_dropdown.text()
            estado_nombre = window.estados_dropdown.text()

            # Obtener el ID del puesto seleccionado
            self.cursor.execute(
                "SELECT id FROM puestos WHERE nombre = %s", (puesto_nombre,))
            puesto_id = self.cursor.fetchone()[0]

            # Obtener el ID del departamento seleccionado
            self.cursor.execute(
                "SELECT id FROM departamentos WHERE nombre = %s", (departamento_nombre,))
            departamento_id = self.cursor.fetchone()[0]

            # Obtener el ID del título académico seleccionado
            self.cursor.execute(
                "SELECT id FROM titulos_academicos WHERE titulo = %s", (titulo_academico_nombre,))
            titulo_academico_id = self.cursor.fetchone()[0]

            # Obtener el ID del estado seleccionado
            self.cursor.execute(
                "SELECT id FROM estados WHERE estado = %s", (estado_nombre,))
            estado_id = self.cursor.fetchone()[0]

            # Guardar el contenido en la tabla candidatos
            self.cursor.execute(
                """
                INSERT INTO candidatos (nombre, email, telefono, puesto_id, departamento_id, titulo_academico_id, resumen_postulacion, estado_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (nombre, email, telefono, puesto_id, departamento_id,
                 titulo_academico_id, content, estado_id)
            )
            self.conn.commit()
            success_dialog = QuickAlert(
                'success', 'Éxito', 'El candidato se ha guardado correctamente.')
            success_dialog.exec_()
            # Cerrar la ventana
            window.close()


class DropDown(QPushButton):
    def __init__(self, text, parent=None, query=None, db_params=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 500px;
                min-width: 200px;
                max-height: 50px;
                min-height: 37px;
            }
            QPushButton:hover {
                background-color: #9ED7A2;
            }
            QPushButton:pressed {
                background-color: #5CAB6D;
            }
            QPushButton::menu-indicator {
                subcontrol-position: right center;
            }
        """)
        self.options = []
        if query and db_params:
            self.load_options(query, db_params)
        self.menu = QMenu()
        self.actions = []
        for option in self.options:
            action = QAction(option, self)
            action.triggered.connect(
                lambda checked, text=option: self.on_triggered(text))
            self.actions.append(action)
            self.menu.addAction(action)
        self.menu.setStyleSheet("""
            QMenu {                
                background-color: #FFFFFF;  /* Color de fondo del menú */
                color: #000000;
                border-radius: 12px;
                max-width: 300px; 
                min-width: 300px;
            }
            QMenu::item {
                background-color: #FFFFFF;
                color: #000000;
                max-width: 300px; 
                min-width: 300px;
            }
            QMenu::item:selected {
                background-color: #9ED7A2;
            }
        """)
        self.setMenu(self.menu)

    def load_options(self, query, db_params):
        try:
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()
            cursor.execute(query)
            self.options = [option[0] for option in cursor.fetchall()]
            conn.close()
            print("Opciones cargadas:", self.options)
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def on_triggered(self, text):
        print(f"Opción seleccionada: {text}")
        self.setText(text)
        self.setChecked(False)


class AddCandidato(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agregar Candidato")
        self.setFixedSize(QSize(800, 600))

        # Create the WebView
        self.webview = QWebEngineView()
        self.load_ckeditor()

        # Create a Save button
        self.save_button = QPushButton("Guardar")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #9ED7A2;
                font-size: 16px;
                color: #FFFFFF;
                border-radius: 12px;
                max-width: 200px;
                max-height: 50px;
                min-height: 37px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #7FC88B;
            }
            QPushButton:pressed {
                background-color: #5CAB6D;
            }
        """)
        self.save_button.clicked.connect(self.save_content)

        # Create a QLineEdit for job title input
        self.job_title_input = QLineEdit()
        self.job_title_input.setPlaceholderText("Nombre del Candidato")
        self.mail_input = QLineEdit()
        self.mail_input.setPlaceholderText("Correo Electrónico")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Número de Teléfono")
        # validamos que el correo sea correcto
        self.mail_input.setValidator(QRegExpValidator(
            QRegExp(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")))
        self.phone_input.setValidator(QIntValidator())
        # aplicamos estilos a los inputs
        for input in [self.job_title_input, self.mail_input, self.phone_input]:
            input.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    font-size: 14px;
                    color: #000000;
                    border-radius: 12px;
                    max-height: 50px;
                    min-height: 37px;
                }
            """)

        # Create labels
        self.puesto_label = QLabel("Puestos:")
        self.departments_label = QLabel("Departamento:")
        self.title_label = QLabel("Titulo Academico:")
        self.estado_label = QLabel("Estado del candidato:")
        self.resumen_label = QLabel("Resumen de la postulación")

        # Set bold font for labels
        for label in [self.puesto_label, self.departments_label, self.title_label, self.estado_label, self.resumen_label]:
            label.setStyleSheet("font-weight: bold;")

        # Database connection parameters
        db_params = {
            'dbname': 'BDCUBO',
            'user': 'postgres',
            'password': 'postgres123',
            'host': 'localhost',
            'port': '5432'
        }

        # Dropdowns
        self.puestos_dropdown = DropDown(
            "Seleccionar Puesto", query="SELECT nombre FROM puestos", db_params=db_params)
        self.departamentos_dropdown = DropDown(
            "Seleccionar Departamento", query="SELECT nombre FROM departamentos", db_params=db_params)
        self.titulos_dropdown = DropDown(
            "Seleccionar Título Académico", query="SELECT titulo FROM titulos_academicos", db_params=db_params)
        self.estados_dropdown = DropDown(
            "Seleccionar Estado", query="SELECT estado FROM estados", db_params=db_params)

        # Layout
        grid_layout = QGridLayout()

        grid_layout.addWidget(self.puesto_label, 0, 0)
        grid_layout.addWidget(self.puestos_dropdown, 0, 1)
        grid_layout.addWidget(self.departments_label, 0, 2)
        grid_layout.addWidget(self.departamentos_dropdown, 0, 3)

        grid_layout.addWidget(self.title_label, 1, 0)
        grid_layout.addWidget(self.titulos_dropdown, 1, 1)
        grid_layout.addWidget(self.estado_label, 1, 2)
        grid_layout.addWidget(self.estados_dropdown, 1, 3)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.job_title_input)
        main_layout.addWidget(self.mail_input)
        main_layout.addWidget(self.phone_input)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.resumen_label)
        main_layout.addWidget(self.webview)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

        # Create a QWebChannel and register content receiver object
        self.channel = QWebChannel()
        self.content_receiver = ContentReceiver()
        self.channel.registerObject("pywebchannel", self.content_receiver)
        self.webview.page().setWebChannel(self.channel)

    def load_ckeditor(self):
        # Load content from 'Ejemplo.txt'
        with open("tx/vacio.txt", "r", encoding="utf-8") as file:
            content = file.read()

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.ckeditor.com/ckeditor5/34.0.0/classic/ckeditor.js"></script>
            <script src="qrc:/qtwebchannel/qwebchannel.js"></script> <!-- Path to qwebchannel.js -->
        </head>
        <body>
            <textarea name="editor1" id="editor1" rows="10" cols="80">
                {content}
            </textarea>
            <script>
                ClassicEditor
                    .create(document.querySelector("#editor1"))
                    .then(editor => {{
                        window.editor = editor; // Save editor instance to window for access
                    }})
                    .catch(error => {{
                        console.error('Error initializing CKEditor:', error);
                    }});

                // Create the QWebChannel object and connect to Python
                var channel = new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.pywebchannel = channel.objects.pywebchannel;
                }});

                function sendContentToPython() {{
                    const editor = window.editor;
                    if (editor) {{
                        const content = editor.getData();
                        pywebchannel.receiveContent(content);  // Send content to Python
                    }} else {{
                        console.error('Editor not initialized.');
                    }}
                }}
            </script>
        </body>
        </html>
        """
        self.webview.setHtml(html_content)

    def save_content(self):
        # Verificar que todos los campos estén llenos
        if (
            self.job_title_input.text() == "" or
            self.mail_input.text() == "" or
            self.phone_input.text() == "" or
            self.puestos_dropdown.text() == "Seleccionar Puesto" or
            self.departamentos_dropdown.text() == "Seleccionar Departamento" or
            self.titulos_dropdown.text() == "Seleccionar Título Académico" or
            self.estados_dropdown.text() == "Seleccionar Estado"
        ):
            error_dialog = QuickAlert(
                'error', 'Error', 'Por favor, complete todos los campos antes de guardar.')
            error_dialog.exec_()
        else:
            # Run JavaScript function to get content from CKEditor and send it to Python
            self.webview.page().runJavaScript("sendContentToPython()")


def show_add_candidato():
    dialog = AddCandidato()
    dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    show_add_candidato()
    sys.exit(app.exec_())
