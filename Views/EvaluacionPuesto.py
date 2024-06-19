import sys
import psycopg2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QRadioButton, QPushButton, QButtonGroup, QMessageBox, QGroupBox, QScrollArea
from Preguntas import cuestionarios
from dialog import QuickAlert  # Importar libreria de diálogos


class Cuestionario(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.nombre = None  # Inicializar el nombre del empleado
        self.id_empleado = None  # Inicializar el ID del empleado
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Titulo del cuestionario
        self.titulo, self.preguntas = self.cargar_cuestionario(self.id)

        titulo_label = QLabel(self.titulo)
        titulo_label.setStyleSheet(
            "font-weight: bold; font-size: 24px; color: #ffffff; background-color: #0073e6; padding: 10px; border-radius: 8px;")
        layout.addWidget(titulo_label)

        # Opciones de respuesta
        self.opciones = [
            "1 - Debe Mejorar",
            "2 - Malo",
            "3 - Neutro",
            "4 - Bueno",
            "5 - Muy bueno"
        ]

        self.button_groups = []
        for i, pregunta in enumerate(self.preguntas):
            pregunta_label = QLabel(pregunta)
            color = "#f0f0f0" if i % 2 == 0 else "#d0d0d0"
            pregunta_label.setStyleSheet(
                f"font-weight: bold; font-size: 20px; background-color: {color}; padding: 5px; border-radius: 5px;")

            button_group = QButtonGroup(self)
            self.button_groups.append(button_group)
            opciones_layout = QHBoxLayout()
            for opcion in self.opciones:
                radio_btn = QRadioButton(opcion)
                radio_btn.setStyleSheet("font-size: 16px;")
                opciones_layout.addWidget(radio_btn)
                button_group.addButton(radio_btn)

            group_box = QGroupBox()
            group_box_layout = QVBoxLayout()
            group_box_layout.addWidget(pregunta_label)
            group_box_layout.addLayout(opciones_layout)
            group_box.setLayout(group_box_layout)
            group_box.setStyleSheet(
                "background-color: #e6f7ff; border: 1px solid #0073e6; border-radius: 5px; padding: 10px;")
            layout.addWidget(group_box)

        # Botón de envío
        submit_button = QPushButton('Enviar', self)
        submit_button.setStyleSheet(
            "font-size: 18px; padding: 10px; background-color: #0073e6; color: #ffffff; border-radius: 5px;")
        submit_button.clicked.connect(self.enviar_respuestas)
        layout.addWidget(submit_button)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.setWindowTitle('Cuestionario de Evaluación')
        self.show()

    def cargar_cuestionario(self, id):
        nombre_puesto, self.nombre, self.id_empleado = self.identificar_puesto_y_nombre(
            id)
        if nombre_puesto is not None:
            if nombre_puesto in cuestionarios:
                titulo = nombre_puesto
                preguntas = cuestionarios[nombre_puesto]
                return titulo, preguntas
            else:
                info_dialog = QuickAlert(
                    'info', 'Información', f'No se encontró el cuestionario para el puesto "{nombre_puesto}".')
        else:
            QMessageBox.warning(
                self, 'Advertencia', 'No se encontró el puesto del usuario en la base de datos.')
        return None, []

    def identificar_puesto_y_nombre(self, id):
        nombre_puesto = None
        nombre = None
        id_empleado = None
        try:
            conn = psycopg2.connect(
                dbname="BDCUBO",
                user="postgres",
                password="postgres123",
                host="localhost",
                port="5432",
            )
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT e.puesto_trabajo, e.nombre, e.id
                FROM empleados e
                JOIN usuarios u ON e.id = u.id_empleado
                WHERE u.id = {id};
                """
            )
            result = cursor.fetchone()
            if result is not None:
                nombre_puesto, nombre, id_empleado = result
            else:
                print(f"No se encontró el puesto y nombre para el ID {id}.")
            conn.close()
        except psycopg2.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
        return nombre_puesto, nombre, id_empleado

    def enviar_respuestas(self):
        respuestas = []
        resultado = 0

        for button_group in self.button_groups:
            selected_button = button_group.checkedButton()
            if selected_button is not None:
                respuesta_texto = selected_button.text()
                respuestas.append(respuesta_texto)

                # Calcular la puntuación basada en la opción seleccionada
                if "1 - Debe Mejorar" in respuesta_texto:
                    resultado += 0.2
                elif "2 - Malo" in respuesta_texto:
                    resultado += 0.4
                elif "3 - Neutro" in respuesta_texto:
                    resultado += 0.6
                elif "4 - Bueno" in respuesta_texto:
                    resultado += 0.8
                elif "5 - Muy bueno" in respuesta_texto:
                    resultado += 1.0
            # redondear a 2 decimales
            resultado = round(resultado, 2)
        if self.id_empleado is not None:
            try:
                conn = psycopg2.connect(
                    dbname="BDCUBO",
                    user="postgres",
                    password="postgres123",
                    host="localhost",
                    port="5432",
                )
                cursor = conn.cursor()

                # Insertar el resultado en la tabla evaluaciones
                cursor.execute(
                    """
                    INSERT INTO evaluaciones (nombre, resultado, id_empleado)
                    VALUES (%s, %s, %s)
                    """, (self.nombre, resultado, self.id_empleado)
                )
                conn.commit()
                conn.close()
                success_dialog = QuickAlert(
                    'success', 'Éxito', 'Evaluación guardada exitosamente.')
            except psycopg2.Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                error_dialog = QuickAlert(
                    'error', 'Error', 'No se pudo guardar la evaluación.')
        else:
            error_dialog = QuickAlert(
                'error', 'Error', 'No se pudo encontrar el ID del empleado.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    ex = Cuestionario(2)
    sys.exit(app.exec_())
