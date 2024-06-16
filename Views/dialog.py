import sys
import time
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget
)
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class GifAnimationWidget(QLabel):
    def __init__(self, gif_file, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150)
        self.movie = QMovie(gif_file)
        self.setMovie(self.movie)
        self.movie.start()


class QuickAlert(QDialog):
    def __init__(self, alert_type, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(500, 250)
        self.setWindowFlag(Qt.FramelessWindowHint)  # Quita la barra de título
        self.setStyleSheet("background-color: white;")  # bg a blanco

        layout = QVBoxLayout(self)  # Layout principal
        self.setLayout(layout)

        # GIF Widget
        animation_widget = GifAnimationWidget(
            f'gifs/{alert_type}_animation.gif')
        layout.addWidget(animation_widget, alignment=Qt.AlignCenter)

        # Message Label
        message_label = QLabel(message)
        # Lo cambia a negrita
        message_label.setFont(QFont("Arial", weight=QFont.Bold))
        message_label.setAlignment(Qt.AlignCenter)  # Lo centra
        layout.addWidget(message_label)

        # Buttons Layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.setStyleSheet(
            "border-radius: 4px; color: white; border: 0px; height: 40px; width: 100px;")
        ok_button.setFont(QFont("Arial", weight=QFont.Bold)
                          )  # Lo cambia a negrita
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancelar')
        cancel_button.setStyleSheet(
            "border-radius: 4px; color: white; border: 0px; height: 40px; width: 100px;")
        # Lo cambia a negrita
        cancel_button.setFont(QFont("Arial", weight=QFont.Bold))
        cancel_button.clicked.connect(self.reject)

        # Coloca el color en base al tipo de alerta
        if alert_type == 'error':
            ok_button.setStyleSheet(
                "background-color: red;" + ok_button.styleSheet())
            cancel_button.setStyleSheet(
                "background-color: gray;" + cancel_button.styleSheet())
        elif alert_type == 'success':
            ok_button.setStyleSheet(
                "background-color: green;" + ok_button.styleSheet())
            cancel_button.setStyleSheet(
                "background-color: gray;" + cancel_button.styleSheet())
        elif alert_type == 'info':
            ok_button.setStyleSheet(
                "background-color: blue;" + ok_button.styleSheet())
            cancel_button.setStyleSheet(
                "background-color: gray;" + cancel_button.styleSheet())

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)


class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cargando...')
        self.setFixedSize(300, 150)
        self.setWindowFlag(Qt.FramelessWindowHint)  # Quita la barra de título
        self.setStyleSheet("background-color: white;")  # bg a blanco

        layout = QVBoxLayout(self)  # Main layout for the dialog
        self.setLayout(layout)

        # GIF Widget
        animation_widget = GifAnimationWidget(
            'gifs/loading_animation.gif')  # navegar a la carpeta gifs
        layout.addWidget(animation_widget, alignment=Qt.AlignCenter)

        # Message Label
        message_label = QLabel('Espere por favor...')
        # Lo cambia a negrita
        message_label.setFont(QFont("Arial", weight=QFont.Bold))
        message_label.setAlignment(Qt.AlignCenter)  # Lo centra
        layout.addWidget(message_label)


class WorkerThread(QThread):
    threadSignal = pyqtSignal(bool)

    def __init__(self, operation_func):
        super().__init__()
        self.operation_func = operation_func

    def run(self):
        # Correr la operación larga y emitir la señal con el resultado que es un booleano
        result = self.operation_func()
        self.threadSignal.emit(result)


def main():
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.setWindowTitle('Main Window')
    main_window.setGeometry(100, 100, 800, 600)

    layout = QVBoxLayout(main_window)

    loading_button = QPushButton('Iniciar Operación')
    loading_button.clicked.connect(start_loading)
    layout.addWidget(loading_button, alignment=Qt.AlignCenter)

    main_window.setLayout(layout)
    main_window.show()
    sys.exit(app.exec_())


def start_loading():
    def long_running_operation():
        #  Simular una operación larga (Se cambiará por la operación necesaria)
        time.sleep(5)
        return True  # Retornar True para indicar éxito

    loading_dialog = LoadingDialog()
    worker = WorkerThread(long_running_operation)
    worker.threadSignal.connect(loading_dialog.accept)
    worker.start()
    loading_dialog.exec_()


if __name__ == '__main__':
    main()
