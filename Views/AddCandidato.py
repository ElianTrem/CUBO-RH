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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent
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
        # Verificar si se está editando un candidato existente o creando uno nuevo
        if self.window.candidato_id:  # Si candidato_id está presente, se está editando un candidato existente
            self.update_candidato(content)
        else:  # Si no hay candidato_id, se está creando un nuevo candidato
            self.insert_candidato(content)

    def insert_candidato(self, content):
        # Lógica para insertar un nuevo candidato en la base de datos
        nombre = self.window.job_title_input.text()
        email = self.window.mail_input.text()
        telefono = self.window.phone_input.text()
        puesto_nombre = self.window.puestos_dropdown.text()
        departamento_nombre = self.window.departamentos_dropdown.text()
        titulo_academico_nombre = self.window.titulos_dropdown.text()
        estado_nombre = self.window.estados_dropdown.text()

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

        # Insertar el nuevo candidato en la tabla candidatos
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
            'success', 'Éxito', 'El candidato se ha guardado correctamente.'
        )
        success_dialog.exec_()

    def update_candidato(self, content):
        # Lógica para actualizar un candidato existente en la base de datos
        nombre = self.window.job_title_input.text()
        email = self.window.mail_input.text()
        telefono = self.window.phone_input.text()
        estado_nombre = self.window.estados_dropdown.text()

        # Obtener el ID del estado seleccionado
        self.cursor.execute(
            "SELECT id FROM estados WHERE estado = %s", (estado_nombre,))
        estado_id = self.cursor.fetchone()[0]

        # Actualizar los datos del candidato en la tabla candidatos
        self.cursor.execute(
            """
            UPDATE candidatos
            SET nombre = %s, email = %s, telefono = %s, resumen_postulacion = %s, estado_id = %s
            WHERE id = %s
            """,
            (nombre, email, telefono, content, estado_id, self.window.candidato_id)
        )
        self.conn.commit()
        success_dialog = QuickAlert(
            'success', 'Éxito', 'El candidato se ha actualizado correctamente.'
        )
        success_dialog.exec_()
        # Cerrar la ventana
        self.window.close()


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
    # Modificar la inicialización para aceptar candidato_id
    def __init__(self, candidato_id=None):
        super().__init__()
        self.candidato_id = candidato_id
        # if para poner el titulo de la ventana dependiendo si se va a agregar o editar un candidato
        if candidato_id:
            self.setWindowTitle("Editar Candidato")
        else:
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
        if candidato_id:
            self.load_candidato_data(candidato_id)

        # Create a QWebChannel and register content receiver object
        self.channel = QWebChannel()
        self.content_receiver = ContentReceiver(self)
        self.channel.registerObject("pywebchannel", self.content_receiver)
        self.webview.page().setWebChannel(self.channel)

    def load_ckeditor(self):
        # cargamos el contenido vacio o traido desde la bd al ckeditor
        content = ""

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

    def load_candidato_data(self, candidato_id):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()

            # Obtener los datos del candidato utilizando el ID proporcionado
            cursor.execute("""
                SELECT c.nombre, c.email, c.telefono, c.puesto_id, c.departamento_id,
                c.titulo_academico_id, c.resumen_postulacion, c.estado_id,
                p.nombre AS puesto_nombre, d.nombre AS departamento_nombre,
                t.titulo AS titulo_academico_nombre, e.estado AS estado_nombre
                FROM candidatos c
                JOIN puestos p ON c.puesto_id = p.id
                JOIN departamentos d ON c.departamento_id = d.id
                JOIN titulos_academicos t ON c.titulo_academico_id = t.id
                JOIN estados e ON c.estado_id = e.id
                WHERE c.id = %s
            """, (candidato_id,))
            candidato_data = cursor.fetchone()

            if candidato_data:  # Si se encontraron datos para el candidato
                # Cargar los datos en los widgets correspondientes de la vista
                self.job_title_input.setText(candidato_data[0])
                self.mail_input.setText(candidato_data[1])
                self.phone_input.setText(candidato_data[2])
                self.puestos_dropdown.setText(candidato_data[8])
                self.departamentos_dropdown.setText(candidato_data[9])
                self.titulos_dropdown.setText(candidato_data[10])
                self.estados_dropdown.setText(candidato_data[11])

                # Deshabilitar la edición en los campos que no deben ser modificados
                self.job_title_input.setReadOnly(True)
                self.mail_input.setReadOnly(True)
                self.puestos_dropdown.setEnabled(False)
                self.departamentos_dropdown.setEnabled(False)
                self.titulos_dropdown.setEnabled(False)

                # Cargar el contenido del candidato en el CKEditor
                self.load_ckeditor_with_content(candidato_data[6])
            else:
                # Mostrar un mensaje de error si no se encontraron datos para el candidato
                error_dialog = QuickAlert(
                    'error', 'Error', 'No se encontraron datos para el candidato.')

            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def load_ckeditor_with_content(self, content):
        # cargamos el contenido existente del candidato en el ckeditor
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


# Ejemplo de uso de la clase AddCandidato
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddCandidato(candidato_id=1)
    window.show()
    sys.exit(app.exec_())
