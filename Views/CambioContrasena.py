import sys
import psycopg2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QErrorMessage, QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import Qt

from dialog import QuickAlert

class ChangePasswordForm(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Cambiar Contraseña')

        # Fijar el ancho del widget
        self.setFixedWidth(400)

        # Crear widgets
        self.label_current_password = QLabel('Contraseña Actual')
        self.label_new_password = QLabel('Nueva Contraseña')
        self.label_confirm_password = QLabel('Confirmar Nueva Contraseña')

        self.line_edit_current_password = QLineEdit()
        self.line_edit_new_password = QLineEdit()
        self.line_edit_confirm_password = QLineEdit()

        self.line_edit_current_password.setEchoMode(QLineEdit.Password)
        self.line_edit_new_password.setEchoMode(QLineEdit.Password)
        self.line_edit_confirm_password.setEchoMode(QLineEdit.Password)

        # Aplicar estilo a los QLineEdit
        style = """
        QLineEdit {
            background-color: #F5F5F5;
            border: 2px solid #CCCCCC;
            border-radius: 4px;
            padding: 8px;
            font-size: 16px;
            margin-left: 100px;
        }
        QLabel{
            margin-left: 100px;
        }
        QLineEdit:focus {
            border-color: #66AFE9;
        }
        QCheckBox{
            margin-left: 100px;
        }
        QPushButton{
            margin-left: 100px;
        }
        """
        self.line_edit_current_password.setStyleSheet(style)
        self.line_edit_new_password.setStyleSheet(style)
        self.line_edit_confirm_password.setStyleSheet(style)
        self.label_confirm_password.setStyleSheet(style)
        self.label_current_password.setStyleSheet(style)
        self.label_new_password.setStyleSheet(style)

        self.button_change_password = addBtn('Cambiar Contraseña')
        self.button_change_password.setStyleSheet(style)

        # Checkboxes para mostrar/ocultar contraseña
        self.checkbox_show_current_password = QCheckBox('Mostrar Contraseña')
        self.checkbox_show_new_password = QCheckBox('Mostrar Contraseña')
        self.checkbox_show_confirm_password = QCheckBox('Mostrar Contraseña')
        self.checkbox_show_confirm_password.setStyleSheet(style)
        self.checkbox_show_current_password.setStyleSheet(style)
        self.checkbox_show_new_password.setStyleSheet(style)

        self.checkbox_show_current_password.stateChanged.connect(
            lambda: self.toggle_password_visibility(self.line_edit_current_password, self.checkbox_show_current_password)
        )
        self.checkbox_show_new_password.stateChanged.connect(
            lambda: self.toggle_password_visibility(self.line_edit_new_password, self.checkbox_show_new_password)
        )
        self.checkbox_show_confirm_password.stateChanged.connect(
            lambda: self.toggle_password_visibility(self.line_edit_confirm_password, self.checkbox_show_confirm_password)
        )

        # Configurar layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_current_password)
        layout.addWidget(self.line_edit_current_password)
        layout.addWidget(self.checkbox_show_current_password)
        layout.addWidget(self.label_new_password)
        layout.addWidget(self.line_edit_new_password)
        layout.addWidget(self.checkbox_show_new_password)
        layout.addWidget(self.label_confirm_password)
        layout.addWidget(self.line_edit_confirm_password)
        layout.addWidget(self.checkbox_show_confirm_password)
        layout.addWidget(self.button_change_password)
        layout.addStretch()
        layout.setAlignment(Qt.AlignCenter)  # Centrar el layout vertical
        self.setLayout(layout)

        # Conectar el botón a la función de cambio de contraseña
        self.button_change_password.clicked.connect(self.change_password)

    def toggle_password_visibility(self, line_edit, checkbox):
        if checkbox.isChecked():
            line_edit.setEchoMode(QLineEdit.Normal)
        else:
            line_edit.setEchoMode(QLineEdit.Password)

    def change_password(self):
        current_password = self.line_edit_current_password.text()
        new_password = self.line_edit_new_password.text()
        confirm_password = self.line_edit_confirm_password.text()

        if not current_password or not new_password or not confirm_password:
            error_dialog = QuickAlert(
                'error', 'Error', 'Por favor, complete todos los campos.')
            error_dialog.exec_()
            return

        if new_password != confirm_password:
            error_dialog = QuickAlert(
                'error', 'Error', 'Las nuevas contraseñas no coinciden.')
            error_dialog.exec_()
            return

        # Conectar a la base de datos y verificar la contraseña actual
        try:
            conn = psycopg2.connect(
                dbname='BDCUBO',
                user='postgres',
                password='postgres123',
                host='localhost',  # Cambia esto si tu base de datos está en otro servidor
                port='5432'
            )
            cursor = conn.cursor()

            # Verificar la contraseña actual
            cursor.execute("SELECT contrasena FROM usuarios WHERE id=%s", (self.user_id,))
            result = cursor.fetchone()
            if not result or result[0] != current_password:
                error_dialog = QuickAlert(
                'error', 'Error', 'La contraseña actual es incorrecta.')
                error_dialog.exec_()
                conn.close()
                return

            # Actualizar la contraseña en la base de datos
            cursor.execute("UPDATE usuarios SET contrasena=%s WHERE id=%s", (new_password, self.user_id))
            conn.commit()
            conn.close()

            success_dialog = QuickAlert(
                'success', 'Éxito', 'La contraseña ha sido cambiada exitosamente.')
            success_dialog.exec_()

        except psycopg2.Error as e:
            error_dialog = QuickAlert(
                'error', 'Error', f'Error al conectar a la base de datos: {e}')
            error_dialog.exec_()

    def show_error_message(self, message):
        error_dialog = QErrorMessage()
        error_dialog.showMessage(message)
        error_dialog.exec_()

    def show_success_message(self, message):
        success_dialog = QMessageBox()
        success_dialog.setIcon(QMessageBox.Information)
        success_dialog.setWindowTitle('Éxito')
        success_dialog.setText(message)
        success_dialog.exec_()

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

def main():
    app = QApplication(sys.argv)
    # Asumiendo que el user_id del usuario actual es 1
    ex = ChangePasswordForm(user_id=1)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
