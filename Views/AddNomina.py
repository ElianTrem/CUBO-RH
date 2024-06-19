import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QGridLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox
)
from PyQt5.QtCore import QSize, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from dialog import QuickAlert  # Importar libreria de diálogos


class AddNomina(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agregar Nómina")
        self.setFixedSize(QSize(800, 400))

        # Create Save button
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
        self.save_button.clicked.connect(self.save_nomina)

        # Create QLineEdits for input fields
        self.empleado_id_input = QLineEdit()
        self.empleado_id_input.setPlaceholderText("ID del Empleado")

        self.dias_laborados_input = QLineEdit()
        self.dias_laborados_input.setPlaceholderText("Días Laborados")

        self.pago_mensual_input = QLineEdit()
        self.pago_mensual_input.setPlaceholderText("Pago Mensual")

        self.descuentos_input = QLineEdit()
        self.descuentos_input.setPlaceholderText("Descuentos")

        self.prestaciones_input = QLineEdit()
        self.prestaciones_input.setPlaceholderText("Prestaciones")

        # Validators for input fields
        self.empleado_id_input.setValidator(QIntValidator())
        self.dias_laborados_input.setValidator(QIntValidator())
        self.pago_mensual_input.setValidator(QRegExpValidator(QRegExp(r"^\d+(\.\d{1,2})?$")))
        self.descuentos_input.setValidator(QRegExpValidator(QRegExp(r"^\d+(\.\d{1,2})?$")))
        self.prestaciones_input.setValidator(QRegExpValidator(QRegExp(r"^\d+(\.\d{1,2})?$")))

        # Apply styles to inputs
        for input in [self.empleado_id_input, self.dias_laborados_input, self.pago_mensual_input, self.descuentos_input, self.prestaciones_input]:
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

        # Labels
        self.empleado_id_label = QLabel("ID del Empleado:")
        self.dias_laborados_label = QLabel("Días Laborados:")
        self.pago_mensual_label = QLabel("Pago Mensual:")
        self.descuentos_label = QLabel("Descuentos:")
        self.prestaciones_label = QLabel("Prestaciones:")

        # Set bold font for labels
        for label in [self.empleado_id_label, self.dias_laborados_label, self.pago_mensual_label, self.descuentos_label, self.prestaciones_label]:
            label.setStyleSheet("font-weight: bold;")

        # Layout
        grid_layout = QGridLayout()

        grid_layout.addWidget(self.empleado_id_label, 0, 0)
        grid_layout.addWidget(self.empleado_id_input, 0, 1)
        grid_layout.addWidget(self.dias_laborados_label, 1, 0)
        grid_layout.addWidget(self.dias_laborados_input, 1, 1)
        grid_layout.addWidget(self.pago_mensual_label, 2, 0)
        grid_layout.addWidget(self.pago_mensual_input, 2, 1)
        grid_layout.addWidget(self.descuentos_label, 3, 0)
        grid_layout.addWidget(self.descuentos_input, 3, 1)
        grid_layout.addWidget(self.prestaciones_label, 4, 0)
        grid_layout.addWidget(self.prestaciones_input, 4, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

    def save_nomina(self):
        # Verify all fields are filled
        if (
            self.empleado_id_input.text() == "" or
            self.dias_laborados_input.text() == "" or
            self.pago_mensual_input.text() == "" or
            self.descuentos_input.text() == "" or
            self.prestaciones_input.text() == ""
        ):
            error_dialog = QuickAlert(
                'error', 'Error', 'Por favor, complete todos los campos antes de guardar.')
            error_dialog.exec_()
        else:
            empleado_id = int(self.empleado_id_input.text())
            dias_laborados = int(self.dias_laborados_input.text())
            pago_mensual = float(self.pago_mensual_input.text())
            descuentos = float(self.descuentos_input.text())
            prestaciones = float(self.prestaciones_input.text())

            try:
                conn = psycopg2.connect(
                    dbname='BDCUBO',
                    user='postgres',
                    password='postgres123',
                    host='localhost',
                    port='5432'
                )
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO nominas (empleado_id, dias_laburados, pago_mensual, descuentos, prestaciones)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (empleado_id, dias_laborados, pago_mensual, descuentos, prestaciones)
                )
                conn.commit()

                success_dialog = QuickAlert(
                    'success', 'Éxito', 'La nómina se ha guardado correctamente.'
                )
                success_dialog.exec_()
                self.close()
            except psycopg2.Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                error_dialog = QuickAlert(
                    'error', 'Error', f'Error al conectar a la base de datos: {e}')
                error_dialog.exec_()


# Ejemplo de uso de la clase AddNomina
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddNomina()
    window.show()
    sys.exit(app.exec_())
