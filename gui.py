import os
import sys
from datetime import datetime
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
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QStyle,
    QFrame,
)

from main import main


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Disable focus to remove outline from tree widget
class NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option = QStyleOptionViewItem(option)
        if option.state & QStyle.StateFlag.State_HasFocus:
            option.state &= ~QStyle.StateFlag.State_HasFocus
        super().paint(painter, option, index)


# Individual item in the ROM list
class GameItem(QTreeWidgetItem):
    def __init__(self, file: Path, parent: QTreeWidget) -> None:
        super().__init__(
            parent,
            [
                file.stem,
                f"{(file.stat().st_size / 1024):.1f} KB",
                datetime.fromtimestamp(file.stat().st_mtime).strftime("%d/%m/%Y"),
            ],
        )

        self.file = file

    def run_game(self):
        self.setSelected(False)
        main(str(self.file))


# ROM list
class GameList(QTreeWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(["Game Name", "File Size", "Modified"])
        self.setRootIsDecorated(False)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)

        self.setColumnWidth(0, 300)
        self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

        self.setStyleSheet("""
            QTreeWidget::item {
                padding: 6px;
            }
            QTreeWidget::item:selected {
                background-color: #3d7eff;
                color: white;
                outline: none;
                border: none;
            }
            QTreeWidget::item:focus {
                outline: none;
                border: none;
            }
            QHeaderView::section {
                padding: 4px;
                font-weight: bold;
            }
        """)

        self.setItemDelegate(NoFocusDelegate(self))
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.itemActivated.connect(self.activate_item)

    @staticmethod
    def activate_item(item: QTreeWidgetItem) -> None:
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
        self.setWindowIcon(QtGui.QIcon(resource_path("./assets/c8.png")))
        size = self.settings.value(
            "size", QSize(640, 320)
        )  # Default window size is 640 x 320
        self.resize(size)

        # GUI layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(16, 4, 16, 12)

        self.roms_widget = None

        # Menu bar
        self.menuBar().setStyleSheet("QMenuBar { padding-left: 12}")
        file_menu = self.menuBar().addMenu("&File")

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
    def closeEvent(self, a0: QtGui.QCloseEvent | None) -> None:
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
            self.settings.setValue(
                "fileSelectDir", Path(file).parent
            )  # Save directory to be used next time
            main(file)

    # Choose a ROM directory
    def choose_dir(self) -> None:
        default_dir = self.settings.value("romDir", str(Path.cwd()))

        # File dialogue
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select a ROM directory", str(default_dir)
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

                game_list.sortItems(0, Qt.SortOrder.AscendingOrder)
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
        if event.type() == QtGui.QMouseEvent.Type.MouseButtonPress and isinstance(
            self.roms_widget, GameList
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
