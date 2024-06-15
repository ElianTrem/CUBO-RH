import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem
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

class Expediente(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menu')
        self.setStyleSheet("background-color: #FFFFFF;")

        # Creamos el layout vertical principal
        main_layout = QVBoxLayout(self)

        # Agregamos el botón con texto "Nuevo Puesto de Trabajo"
        btn = addBtn('Nuevo Empleado')
        main_layout.addWidget(btn)

        # Creamos un widget para las filas con encabezados
        rows_widget = QWidget(self)
        rows_widget.setStyleSheet("background-color: #F3FAF3; max-height: 50px; min-height: 37px;")  # Color de fondo para las filas
        rows_layout = QHBoxLayout(rows_widget)
        self.tableWidget = QTableWidget()
        main_layout.addWidget(self.tableWidget)

        self.setLayout(main_layout)
        
        # Cargar datos cuando se inicie la vista
        self.loadData()
        

        # Agregamos el widget de las filas al layout principal pero con un stretch de 1
        main_layout.addWidget(rows_widget)
        main_layout.addStretch()

    def get_widget(self):
        return self
    
    def loadData(self):
        # Conectar a la base de datos y obtener nombres de las columnas
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleados LIMIT 1")  # Consulta para obtener los nombres de las columnas
            col_names = [desc[0] for desc in cursor.description]

            # Configurar los encabezados de la tabla
            self.tableWidget.setColumnCount(len(col_names))
            self.tableWidget.setHorizontalHeaderLabels(col_names)
            
            # Obtener datos de la tabla
            cursor.execute("SELECT * FROM empleados")
            rows = cursor.fetchall()

            # Configurar filas de la tabla
            self.tableWidget.setRowCount(len(rows))
            
            # Llenar la tabla con los datos
            for row_idx, row in enumerate(rows):
                for col_idx, item in enumerate(row):
                    self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Expediente()
    form.show()
    sys.exit(app.exec_())
