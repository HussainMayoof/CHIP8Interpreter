from pathlib import Path

from PyQt6 import QtGui
from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QFileDialog,
    QGridLayout,
    QPushButton, QListWidget, QListWidgetItem,
)

from main import main

# Individual item in the ROM list
class GameItem(QListWidgetItem):
    def __init__(self, file: Path, parent: QListWidget) -> None:
        super().__init__(file.stem, parent)

        self.file = file

    def run_game(self):
        main(str(self.file))

# ROM list
class GameList(QListWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.itemActivated.connect(self.activate_item)

    @staticmethod
    def activate_item(item: QListWidgetItem) -> None:
        if isinstance(item, GameItem):
            item.run_game()

    def mousePressEvent(self, event: QtGui.QMouseEvent | None):
        # If click was a left click and the item was already selected, start the game
        if event and event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())

            was_selected = item is not None and item.isSelected()
            super().mousePressEvent(event)

            if item is not None and was_selected:
                item.run_game()
        else:
            super().mousePressEvent(event)

class EmulatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # Window settings, title, icon and size
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)
        self.setWindowTitle("HelloCHIP")
        self.setWindowIcon(QtGui.QIcon('./assets/c8.png'))
        size = self.settings.value("size", QSize(640, 320)) # Default window size is 640 x 320
        self.resize(size)

        # Window styles
        self.setStyleSheet(
            "padding: 4px;"
        )

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

        QApplication.instance().installEventFilter(self)

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
                # Create game list
                game_list = GameList()
                self.layout.addWidget(game_list)
                self.roms_widget = game_list

                for file in rom_dir.rglob("*.ch8"):
                    # Add each game to the game list
                    GameItem(file, game_list)
            else:
                self.settings.remove("romDir")
                self.get_roms()
        else:
            # Create a button to choose a directory for ROMs
            choose_dir_button = QPushButton("Choose a ROM directory")
            choose_dir_button.clicked.connect(self.choose_dir)
            self.layout.addWidget(choose_dir_button)
            self.roms_widget = choose_dir_button

    def eventFilter(self, obj, event):
        if (
                event.type() == QtGui.QMouseEvent.Type.MouseButtonPress
                and isinstance(self.roms_widget, GameList)
        ):
            global_pos = event.globalPosition().toPoint()
            local_pos = self.roms_widget.mapFromGlobal(global_pos)
            if not self.roms_widget.rect().contains(local_pos):
                self.roms_widget.clearSelection()
        return super().eventFilter(obj, event)


def gui() -> None:
    app = QApplication([])
    window = EmulatorWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    gui()
