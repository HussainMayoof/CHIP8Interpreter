import sys
import tkinter.filedialog
from pathlib import Path

from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QFileDialog

from main import main


class EmulatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("CHIP-8 Interpreter")
        self.setWindowIcon(QtGui.QIcon('./assets/c8.png'))
        self.resize(640, 320)

        button = QPushButton("Choose game")
        button.clicked.connect(self.start_game)

        self.setCentralWidget(button)

    def start_game(self) -> None:
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select CHIP-8 Game")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        default_dir = Path.home() / "Downloads"
        if not default_dir.exists():
            default_dir = Path.home()

        file_dialog.setDirectory(str(default_dir))

        if file_dialog.exec():
            file = file_dialog.selectedFiles()[0]
            main(file)

def gui() -> None:
    app = QApplication([])
    window = EmulatorWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    gui()
