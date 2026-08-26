from pathlib import Path

from PyQt6 import QtGui
from PyQt6.QtCore import QSettings, QSize
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QFileDialog,
    QGridLayout,
    QLabel,
    QScrollArea,
    QPushButton,
)

from main import main


class GameLabel(QLabel):
    def __init__(self, file: Path) -> None:
        super().__init__()

        self.file = file
        self.setText(Path(file).stem)

    def mousePressEvent(self, ev: QtGui.QMouseEvent|None) -> None:
        main(str(self.file))

class EmulatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # Window settings, title, icon and size
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)
        self.setWindowTitle("HelloCHIP")
        self.setWindowIcon(QtGui.QIcon('./assets/c8.png'))
        size = self.settings.value("size", QSize(640, 320)) # Default window size is 640 x 320
        self.resize(size)

        # GUI layout
        self.layout = QGridLayout()

        self.roms_widget = None

        # Menu bar
        menu = self.menuBar()
        assert menu is not None
        file_menu = menu.addMenu("&File")
        assert file_menu is not None

        choose_game = QAction("Choose &game...", self)
        choose_game.triggered.connect(self.choose_game)
        file_menu.addAction(choose_game)

        choose_rom_dir = QAction("Choose ROM &directory...", self)
        choose_rom_dir.triggered.connect(self.choose_dir)
        file_menu.addAction(choose_rom_dir)

        # Container widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.get_roms()

    # Save window size when GUI is closed
    def closeEvent(self, a0: QtGui.QCloseEvent|None) -> None:
        self.settings.setValue("size", self.size())

    # Choose a game from a file
    def choose_game(self) -> None:
        # Open file dialogue
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select CHIP-8 Game")
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        # Default location to open dialogue
        default_dir = self.settings.value("fileSelectDir", Path.home() / "Downloads")
        if not default_dir.exists():
            default_dir = Path.home()

        file_dialog.setDirectory(str(default_dir))

        # Run game from selected file
        if file_dialog.exec():
            file = file_dialog.selectedFiles()[0]
            self.settings.setValue("fileSelectDir", Path(file).parent) # Save directory to be used next time
            main(file)

    # Choose a ROM directory
    def choose_dir(self) -> None:
        default_dir = self.settings.value("romDir", str(Path.cwd()))

        # File dialogue
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select a ROM directory",
            str(default_dir)
        )

        if folder_path and Path(folder_path).is_dir():
            self.settings.setValue("romDir", folder_path)
            self.get_roms()

    # Get list of ROMs in directory
    def get_roms(self) -> None:
        # Remove previous widgets
        if self.roms_widget is not None:
            self.roms_widget.deleteLater()
            self.roms_widget = None

        rom_path = self.settings.value("romDir", "")
        if rom_path:
            rom_dir = Path(rom_path)
            if rom_dir.is_dir():
                # Scroll area
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                self.layout.addWidget(scroll_area)
                self.roms_widget = scroll_area

                scroll_content = QWidget()
                scroll_layout = QGridLayout(scroll_content)
                scroll_area.setWidget(scroll_content)

                for file in rom_dir.rglob("*.ch8"):
                    rom_widget = GameLabel(file)
                    scroll_layout.addWidget(rom_widget)
            else:
                self.settings.remove("romDir")
                self.get_roms()
        else:
            choose_dir_button = QPushButton("Choose a rom directory")
            choose_dir_button.clicked.connect(self.choose_dir)
            self.layout.addWidget(choose_dir_button)
            self.roms_widget = choose_dir_button


def gui() -> None:
    app = QApplication([])
    window = EmulatorWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    gui()
