import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QLabel, QLineEdit, QMessageBox, QMenu, QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
import psycopg2

class ContentReceiver(QObject):
    @pyqtSlot(str)
    def receiveContent(self, content):
        print("Content received from CKEditor:", content)
        # Verificar si se ha ingresado el nombre del puesto
        if window.job_title_input.text() == "":
            QMessageBox.critical(window, "Error", "Por favor ingrese el nombre del puesto antes de guardar.")
        else:
            # Guardar el contenido en un archivo
            job_title = window.job_title_input.text()
            with open(f"../../tx/{job_title}.txt", "w", encoding="utf-8") as file:
                file.write(content)
                QMessageBox.information(window, "Éxito", "Contenido guardado correctamente.")
#Creamos una clase dropdown para mostrar los departamentos
class DropDown(QPushButton):
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
        #cargo los departamentos desde la base de datos
        self.departamentos = []
        try:
            conn = psycopg2.connect(
            dbname='BDCUBO',
            user='postgres',
            password='postgres123',
            host='localhost',
            port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM departamentos")
            self.departamentos = cursor.fetchall()
            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
        self.menu = QMenu()
        for departamento in self.departamentos:
            self.menu.addAction(departamento[0])
        self.setMenu(self.menu)
        self.menu.triggered.connect(self.on_triggered)
    def on_triggered(self, action):
        print(f"Departamento seleccionado: {action.text()}")
        self.setText(action.text())
        self.setChecked(False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agregar Puesto")

        # Create the WebView
        self.webview = QWebEngineView()
        self.load_ckeditor()

        # Create a Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_content)

        # Create a QLineEdit for job title input
        self.job_title_label = QLabel("Nombre del Puesto:")
        self.job_title_input = QLineEdit()

        # Create a dropdown for departments
        self.departments_label = QLabel("Departamento:")
        self.departments_dropdown = DropDown("Seleccionar Departamento")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.job_title_label)
        layout.addWidget(self.job_title_input)
        layout.addWidget(self.departments_label)
        layout.addWidget(self.departments_dropdown)
        layout.addWidget(self.webview)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Create a QWebChannel and register content receiver object
        self.channel = QWebChannel()
        self.content_receiver = ContentReceiver()
        self.channel.registerObject("pywebchannel", self.content_receiver)
        self.webview.page().setWebChannel(self.channel)

    def load_ckeditor(self):
        # Load content from 'Ejemplo.txt'
        with open("Ejemplo.txt", "r", encoding="utf-8") as file:
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
        # Verificar si se ha ingresado el nombre del puesto y departamento antes de guardar
        if self.job_title_input.text() == "":
            QMessageBox.critical(self, "Error", "Por favor ingrese el nombre del puesto antes de guardar.")
        elif self.departments_dropdown.text() == "Seleccionar Departamento":
            QMessageBox.critical(self, "Error", "Por favor seleccione un departamento antes de guardar.")
        else:
            # Run JavaScript function to get content from CKEditor and send it to Python
            self.webview.page().runJavaScript("sendContentToPython()")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
