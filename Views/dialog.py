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
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove title bar
        self.setStyleSheet("background-color: white;")  # Set white background

        layout = QVBoxLayout(self)  # Main layout for the dialog
        self.setLayout(layout)

        # GIF Widget
        animation_widget = GifAnimationWidget(f'gifs/{alert_type}_animation.gif')  # Path to your GIF file
        layout.addWidget(animation_widget, alignment=Qt.AlignCenter)

        # Message Label
        message_label = QLabel(message)
        message_label.setFont(QFont("Arial", weight=QFont.Bold))  # Set bold font
        message_label.setAlignment(Qt.AlignCenter)  # Align text center
        layout.addWidget(message_label)

        # Buttons Layout
        button_layout = QHBoxLayout()
        ok_button = QPushButton('OK')
        ok_button.setStyleSheet("border-radius: 4px; color: white; border: 0px; height: 40px; width: 100px;")
        ok_button.setFont(QFont("Arial", weight=QFont.Bold))  # Set bold font
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancelar')
        cancel_button.setStyleSheet("border-radius: 4px; color: white; border: 0px; height: 40px; width: 100px;")
        cancel_button.setFont(QFont("Arial", weight=QFont.Bold))  # Set bold font
        cancel_button.clicked.connect(self.reject)

        # Set button color based on alert type
        if alert_type == 'error':
            ok_button.setStyleSheet("background-color: red;" + ok_button.styleSheet())
            cancel_button.setStyleSheet("background-color: gray;" + cancel_button.styleSheet())
        elif alert_type == 'success':
            ok_button.setStyleSheet("background-color: green;" + ok_button.styleSheet())
            cancel_button.setStyleSheet("background-color: gray;" + cancel_button.styleSheet())
        elif alert_type == 'info':
            ok_button.setStyleSheet("background-color: blue;" + ok_button.styleSheet())
            cancel_button.setStyleSheet("background-color: gray;" + cancel_button.styleSheet())

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cargando...')
        self.setFixedSize(300, 150)
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove title bar
        self.setStyleSheet("background-color: white;")  # Set white background

        layout = QVBoxLayout(self)  # Main layout for the dialog
        self.setLayout(layout)

        # GIF Widget
        animation_widget = GifAnimationWidget('gifs/loading_animation.gif')  # Path to your GIF file
        layout.addWidget(animation_widget, alignment=Qt.AlignCenter)

        # Message Label
        message_label = QLabel('Espere por favor...')
        message_label.setFont(QFont("Arial", weight=QFont.Bold))  # Set bold font
        message_label.setAlignment(Qt.AlignCenter)  # Align text center
        layout.addWidget(message_label)

class WorkerThread(QThread):
    threadSignal = pyqtSignal(bool)

    def __init__(self, operation_func):
        super().__init__()
        self.operation_func = operation_func

    def run(self):
        # Execute the operation function and emit the result
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
        # Simulate a long-running operation
        time.sleep(5)
        return True  # Return True to indicate success

    loading_dialog = LoadingDialog()
    worker = WorkerThread(long_running_operation)
    worker.threadSignal.connect(loading_dialog.accept)
    worker.start()
    loading_dialog.exec_()

if __name__ == '__main__':
    main()
