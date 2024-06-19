import sys
import psycopg2
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QLineEdit, QSpacerItem, QSizePolicy, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from DescPuesto_modal import DescriptionDialog
from puesto import AddPuesto
from AddNomina import AddNomina

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
            SELECT 
                e.nombre AS nombre_empleado,
                n.dias_laburados,
                n.pago_mensual,
                n.descuentos,
                n.prestaciones
            FROM 
                nominas n
            JOIN 
                empleados e ON n.empleado_id = e.id;
        """)
        rows = cursor.fetchall()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
    return rows

class EmpleadoNominas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Menu')
        self.setStyleSheet("background-color: #FFFFFF;")

        layout = QVBoxLayout(self)

        # Creamos el layout de la cuadrícula principal
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes internos

        # Fila 0: Barra de búsqueda y botón de búsqueda
        self.search_edit = QLineEdit()
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #F0F0F0;
                font-size: 18px;
                color: #000000;
                border-radius: 12px;
                border: 1px solid #000000;
                max-width: 200px;
                max-height: 50px;
                min-height: 37px;
                padding: 5px;  /* Añadir un pequeño relleno para separar del borde */
            }
        """)
        self.search_edit.setPlaceholderText('Buscar...')
        button_buscar = addBtn('Buscar')
        button_buscar.clicked.connect(self.buscar_nomina)

        self.grid_layout.addWidget(self.search_edit, 0, 0)
        self.grid_layout.addWidget(button_buscar, 0, 1)

        # Fila 1: Cuatro botones en una sola fila
        button_nueva_nomina = addBtn('Nueva Nómina')
        button_exportar_excel = addBtn('Exportar a Excel')
        button_nomina_mensual = addBtn('Nómina Mensual')
        button_nomina_anual = addBtn('Nómina Anual')
        self.grid_layout.addWidget(button_nueva_nomina, 1, 0)
        self.grid_layout.addWidget(button_exportar_excel, 1, 1)
        self.grid_layout.addWidget(button_nomina_mensual, 1, 2)
        self.grid_layout.addWidget(button_nomina_anual, 1, 3)

        # Conectar el botón de exportación a la función correspondiente
        button_exportar_excel.clicked.connect(self.export_to_excel)

        # Conectar el botón de nueva nómina a la función correspondiente
        button_nueva_nomina.clicked.connect(self.show_add_nomina)

        # Fila 2: Agregamos los encabezados obtenidos de la base de datos
        headers = ["Empleado", "Días Laburados", "Pago Mensual", "Descuentos", "Prestaciones"]
        self.widths = [200, 150, 150, 100, 100]  # Anchos fijos para cada columna
        headers_widget = QWidget(self)
        headers_widget.setStyleSheet(
            "background-color: #F3FAF3; max-height: 50px; min-height: 37px; border-radius: 8px; margin: 0; padding: 0;")
        headers_layout = QGridLayout(headers_widget)

        for index, (header_text, width) in enumerate(zip(headers, self.widths)):
            header_label = QLabel(header_text)
            header_label.setAlignment(Qt.AlignCenter)  # Alineado al centro
            header_label.setStyleSheet(
                "font-weight: bold; font-size: 18px; width: {}px; margin: 0; padding: 0;".format(width))
            headers_layout.addWidget(header_label, 0, index)

        self.grid_layout.addWidget(headers_widget, 2, 0, 1, 4)

        # Filas siguientes: Obtener las filas de la base de datos y agregar cada fila
        self.rows = get_rows_from_database()
        self.display_rows(self.rows)

        layout.addLayout(self.grid_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def display_rows(self, rows):
        # Limpiar filas existentes
        for i in range(3, self.grid_layout.rowCount()):
            for j in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(i, j)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

        # Agregar nuevas filas
        for row_index, row in enumerate(rows):
            grayrow_widget = QWidget(self)
            grayrow_widget.setStyleSheet(
                "background-color: #F5F5F5; max-height: 50px; min-height: 37px; margin: 0; padding: 0;")
            grayrow_layout = QGridLayout(grayrow_widget)

            for index, (item, width) in enumerate(zip(row, self.widths)):
                if index == 0:  # Si es el primer elemento de la fila
                    item_label = ClickableLabel(str(item))
                    item_label.clicked.connect(
                        lambda item=item: self.on_label_click(item))
                else:
                    item_label = QLabel(str(item))

                item_label.setAlignment(Qt.AlignCenter)
                item_label.setStyleSheet(
                    "font-size: 16px; width: {}px; margin: 0; padding: 0;".format(width))
                grayrow_layout.addWidget(item_label, 0, index)

            self.grid_layout.addWidget(grayrow_widget, row_index + 3, 0, 1, 4)

    def buscar_nomina(self):
        texto_busqueda = self.search_edit.text().lower()
        filas_filtradas = [row for row in self.rows if texto_busqueda in row[0].lower()]
        self.display_rows(filas_filtradas)

    def export_to_excel(self):
        # Crear un DataFrame con los datos
        df = pd.DataFrame(self.rows, columns=["Empleado", "Días Laburados", "Pago Mensual", "Descuentos", "Prestaciones"])
        
        # Mostrar un cuadro de diálogo para seleccionar la ubicación del archivo
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos Excel (*.xlsx);;Todos los archivos (*)", options=options)
        if file_path:
            # Guardar el DataFrame en un archivo Excel
            df.to_excel(file_path, index=False)
            print(f"Datos exportados a {file_path}")

    def on_label_click(self, nombre_puesto):
        self.show_description_dialog(nombre_puesto)

    def show_description_dialog(self, nombre_puesto):
        dialog = DescriptionDialog(nombre_puesto, self)
        dialog.exec_()

    def show_add_nomina(self):
        dialog = AddNomina()
        dialog.exec_()

    def get_widget(self):
        return self

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = EmpleadoNominas()
    form.show()
    sys.exit(app.exec_())
