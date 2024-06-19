import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QComboBox, QHBoxLayout, QGridLayout, QDateEdit, QSpacerItem, QSizePolicy, QMenu, QAction,
    QCompleter
)
from PyQt5.QtCore import QSize, QDate
import psycopg2

from dialog import QuickAlert

class Descuentos_Pestaciones(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcular prestaciones")
        self.setFixedSize(QSize(600, 650))

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  # Ajustar márgenes del layout
        layout.setSpacing(0)  # Ajustar espacio entre widgets

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)  # Ajustar márgenes del layout de la cuadrícula
        grid_layout.setSpacing(5)  # Ajustar espacio entre widgets

        # Buscar empleado
        self.search_employee_input = QLineEdit()
        self.search_employee_input.setPlaceholderText("Buscar empleado...")
        nombres = self.obtener_nombres_desde_bd()

        # Configurar el completer con el modelo de datos
        completer = QCompleter(nombres)
        self.search_employee_input.setCompleter(completer)

        # Conectar la señal de edición completada para manejar la selección del usuario
        completer.activated.connect(self.on_completer_activated)
        self.search_employee_input.setFixedHeight(30)
        grid_layout.addWidget(self.search_employee_input, 0, 0, 1, 2)

        self.label_salario = QLabel("Ingrese su salario mensual")
        self.label_salario.setStyleSheet("QLabel { font-size: 28px; font-family:Times New Roman; }")
        grid_layout.addWidget(self.label_salario, 1, 0, 1, 2)

        # Ingresar salario
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("Ingresa el salario:")
        self.salary_input.setText("$0.00")
        self.salary_input.setFixedHeight(30)
        self.salary_input.setFixedWidth(190)
        grid_layout.addWidget(self.salary_input, 2, 0)

        self.label_tiempo = QLabel("¿Cuánto tiempo tiene trabajando en la empresa?")
        self.label_tiempo.setStyleSheet("QLabel { margin: 0; padding: 0; }")
        grid_layout.addWidget(self.label_tiempo, 3, 0, 1, 2)

        self.tiempo_combo = DropDown("1 a 3 años", ["Menos de un año", "1 a 3 años", "3 a 10 años", "Mas de 10 años"], parent=self)
        grid_layout.addWidget(self.tiempo_combo, 4, 0, 1, 2)

        self.label_tiempo = QLabel("Ingrese la fecha en la que entró a trabajar")
        grid_layout.addWidget(self.label_tiempo, 5, 0, 1, 2)
        self.label_tiempo.setVisible(False)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        grid_layout.addWidget(self.date_edit, 6, 0, 1, 2)
        self.date_edit.setVisible(False)


        # Botones
        self.calculate_button = addBtn('Calcular')
        self.calculate_button.setFixedWidth(90)
        self.clear_button = addBtn('Borrar')
        self.clear_button.setFixedWidth(90)
        grid_layout.addWidget(self.calculate_button, 7, 0)
        grid_layout.addWidget(self.clear_button, 7, 1)

        # Resultados de cálculos
        self.results_layout = QGridLayout()
        self.results_layout.setContentsMargins(90, 10, 0, 0)  # Ajustar márgenes del layout de resultados
        self.results_layout.setSpacing(10)  # Ajustar espacio entre widgets

        results_titles = [
            "Cálculo de salario:", "PRESTACIONES", "AFP Patronal:", "ISSS patronal:", 
            "INSAFORP:","DESCUENTOS", "ISSS laboral:", "AFP laboral:", "Impuesto sobre la renta:",
            "Descuento total:", "TOTALES","Salario líquido:", "Vacaciones:", 
            "Es decir el mes de vacaciones luego de impuestos se te pagará:",
            "Aguinaldo:"
        ]
        
        self.results_labels = {}
        for i, title in enumerate(results_titles):
            label = QLabel(title)
            
            if i == 1 or i == 5 or i == 10:
                label.setStyleSheet("QLabel { margin: 0 auto; padding: 0; }")
                self.results_layout.addWidget(label, i, 0)
                pass
            else:
                label.setStyleSheet("QLabel { margin: 0; padding: 0; }")
                self.results_layout.addWidget(label, i, 0)
                self.results_labels[title] = QLineEdit("$0.00")
                self.results_labels[title].setReadOnly(True)
                self.results_layout.addWidget(self.results_labels[title], i, 1)

        # Añadir widgets al layout principal
        layout.addLayout(grid_layout)
        layout.addLayout(self.results_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Conectar señales
        self.calculate_button.clicked.connect(self.calculate_benefits)
        self.clear_button.clicked.connect(self.clear_fields)

        self.setStyleSheet("""
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
            }
            QComboBox {
                background-color: white;
                border: 1px solid gray;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }
            QComboBox:editable {
                background: white;
            }
            QComboBox:!editable, QComboBox::drop-down:editable {
                background: white;
            }
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                background: white;
            }
            QComboBox:on {
                padding-top: 3px;
                padding-left: 4px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)
    
    def obtener_nombres_desde_bd(self):
        # Aquí deberías hacer la consulta a tu base de datos y obtener los nombres
        nombres = []
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM empleados")
            nombres = [row[0] for row in cursor.fetchall()]  # Obtener todos los nombres como una lista
            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
        
        return nombres

    def on_completer_activated(self, text):
        # Manejar la selección del usuario aquí
        salary_str = self.obtener_salario_empleado(self.search_employee_input.text())
        self.salary_input.setText(f"${salary_str:.2f}")

    def calculate_benefits(self):
        salary_str = self.salary_input.text().replace("$", "").replace(",", "")
        try:
            salario_base = float(salary_str)
            AFP_Patronal = round(salario_base*0.0875, 2)
            ISSS_Patronal = round(salario_base*0.075, 2)
            Insaforp = round(ISSS_Patronal*0.01, 2)
            ISSS_Laboral = round(salario_base*0.03,2)
            AFP_Laboral = round(salario_base*0.0725,2)
            SalarioDesc_sin_renta = salario_base - ISSS_Laboral - AFP_Laboral
            Renta = self.Calcular_Renta(SalarioDesc_sin_renta)
            Descuento_Total = ISSS_Laboral + AFP_Laboral + Renta
            Salario_liquido = SalarioDesc_sin_renta - Renta
            Vacaciones = round((salario_base/2)*0.3,2)
            Salario_Vaca_Desc = salario_base+Vacaciones - round((salario_base+Vacaciones)*0.03,2) - round((salario_base+Vacaciones)*0.0725,2)
            Salario_Vaca = Salario_Vaca_Desc - self.Calcular_Renta(Salario_Vaca_Desc)
            SalarioDiario = round(salario_base/30)
            if self.tiempo_combo.text() == "1 a 3 años":
                Mult_Aguinaldo = 15
            elif self.tiempo_combo.text() == "3 a 10 años":
                Mult_Aguinaldo = 19
            elif self.tiempo_combo.text() == "Mas de 10 años":
                Mult_Aguinaldo = 21
            else:
                Mult_Aguinaldo = 0
            Aguinaldo = SalarioDiario * Mult_Aguinaldo

            if self.tiempo_combo.text() == "Menos de un año":
                dias = self.obtener_cantidad_asistencias(self.obtener_id_empleado(self.search_employee_input.text()))
                if dias >= 200:
                    Aguinaldo = SalarioDiario * 15
                else:
                    Aguinaldo = (dias/365)*(SalarioDiario * 15)

            self.results_labels["Cálculo de salario:"].setText(f"${salario_base:.2f}")
            self.results_labels["AFP Patronal:"].setText(f"${AFP_Patronal:.2f}")
            self.results_labels["ISSS patronal:"].setText(f"${ISSS_Patronal:.2f}")
            self.results_labels["INSAFORP:"].setText(f"${Insaforp:.2f}")
            self.results_labels["ISSS laboral:"].setText(f"${ISSS_Laboral:.2f}")
            self.results_labels["AFP laboral:"].setText(f"${AFP_Laboral:.2f}")
            self.results_labels["Descuento total:"].setText(f"${Descuento_Total:.2f}")
            self.results_labels["Vacaciones:"].setText(f"${Vacaciones:.2f}")
            self.results_labels["Es decir el mes de vacaciones luego de impuestos se te pagará:"].setText(f"${Salario_Vaca:.2f}")
            self.results_labels["Impuesto sobre la renta:"].setText(f"${Renta:.2f}")
            self.results_labels["Salario líquido:"].setText(f"${Salario_liquido:.2f}")
            self.results_labels["Aguinaldo:"].setText(f"${Aguinaldo:.2f}")

        except ValueError:
            error_dialog = QuickAlert('error', 'Error', 'El salario debe ser una cantidad numerica valida')
            error_dialog.exec_()
    
    def Calcular_Renta(self, cantidad):
        if cantidad <= 472.00:
                Exceso = 0
                CuotaFija = 0
                Por_Desc = 0
        elif cantidad <= 895.24:
                Exceso = 472.00
                CuotaFija = 17.67
                Por_Desc = 0.1
        elif cantidad <= 2038.10:
                Exceso = 895.24
                CuotaFija = 60
                Por_Desc = 0.2
        elif cantidad > 2038.10:
                Exceso = 2038.10
                CuotaFija = 288.57
                Por_Desc = 0.3
        
        Renta = (cantidad - Exceso) * (Por_Desc) + CuotaFija
        return Renta
    
    def obtener_salario_empleado(self, nombre_empleado):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT salario FROM empleados WHERE nombre = %s", (nombre_empleado,))
            empleado_salario = cursor.fetchone()
            conn.close()
            if empleado_salario:
                return empleado_salario[0]
            else:
                return None
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None
    
    def obtener_id_empleado(self, nombre_empleado):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM empleados WHERE nombre = %s", (nombre_empleado,))
            empleado_id = cursor.fetchone()
            conn.close()
            if empleado_id:
                return empleado_id[0]
            else:
                return None
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def obtener_cantidad_asistencias(self, empleado_id):
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',
                port='5432'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cantidad_asistencias FROM asistencias WHERE empleado_id = %s", (empleado_id,))
            cantidad_asistencias = cursor.fetchone()[0]
            conn.close()
            return cantidad_asistencias
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None
    
    def Calcular_Tiempo(self):
        id = self.obtener_id_empleado(self.search_employee_input.text())
        asistencias = self.obtener_cantidad_asistencias(id)
        return asistencias

    def clear_fields(self):
        self.search_employee_input.clear()
        self.salary_input.setText("$0.00")
        self.tiempo_combo.setText("1 a 3 años")
        self.date_edit.setVisible(False)
        self.label_tiempo.setVisible(False)
        for label in self.results_labels.values():
            label.setText("$0.00")

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
                background-color: #E0E0E0;
            }
        """)

class DropDown(QPushButton):
    def __init__(self, text, opciones, parent=None):
        super().__init__(text, parent)
        self.parent_widget = parent
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                font-size: 14px;
                color: #000000;
                border-radius: 12px;
                max-width: 300px;
                max-height: 50px;
                min-height: 37px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
            QPushButton:pressed {
                background-color: #9ED7A2;
            }
            QPushButton::menu-indicator {
                subcontrol-position: right center;
            }
        """)
        # cargo los departamentos desde la base de datos
        self.opcion = opciones
        self.menu = QMenu()
        self.actions = []
        for opcion in self.opcion:
            action = QAction(opcion, self)
            action.triggered.connect(
                lambda checked, text=opcion: self.on_triggered(text))
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
                background-color: #F0F0F0;
                color: #000000;
                max-width: 300px; 
                min-width: 300px;
            }
            QMenu::item:selected {
                background-color: #9ED7A2;
            }
        """)
        self.setMenu(self.menu)

    def on_triggered(self, text):
        self.setText(text)
        self.setChecked(False)
        if text == "Menos de un año" and self.parent_widget.search_employee_input.text() == "":  # "Menos de un año" seleccionado
            self.parent_widget.date_edit.setVisible(True)
            self.parent_widget.label_tiempo.setVisible(True)

        else:  # "Un año o más" seleccionado
            self.parent_widget.date_edit.setVisible(False)
            self.parent_widget.label_tiempo.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    desc = Descuentos_Pestaciones()
    desc.show()
    sys.exit(app.exec_())
