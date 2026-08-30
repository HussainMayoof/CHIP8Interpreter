from pathlib import Path
from typing import cast

from PyQt6 import QtGui
from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from main import SUPPORTED_PLATFORMS, get_game_data, get_rom_data, main, resource_path
from settings import COLOURS, DEFAULT_SETTINGS


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
        game_data = get_game_data(str(file))
        rom_data = get_rom_data(str(file))

        if game_data is None or rom_data is None:
            super().__init__(
                parent,
                [
                    file.stem,
                    "Unknown",
                    "Unknown",
                    "Unknown",
                ],
            )
        else:
            platform = "Unsupported"
            for item in rom_data["platforms"]:
                if item in SUPPORTED_PLATFORMS:
                    platform = item
                    break
            super().__init__(
                parent,
                [
                    game_data["title"],
                    game_data["authors"][0],
                    platform,
                    game_data["release"],
                ],
            )

        self.file = file
        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)

    def run_game(self):
        main(str(self.file), self.settings.value("gameSettings"))
        self.setSelected(False)


# ROM list
class GameList(QTreeWidget):
    def __init__(self) -> None:
        super().__init__()

        self.setColumnCount(3)
        self.setHeaderLabels(["Name", "Author", "Platform", "Release Date"])
        self.setRootIsDecorated(False)
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)

        self.setColumnWidth(0, 300)

        header = self.header()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)

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

    def mousePressEvent(self, e: QtGui.QMouseEvent | None):
        # If click was a left click and the item was already selected, start the game
        if e and e.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(e.pos())
            if isinstance(item, GameItem):
                was_selected = item is not None and item.isSelected()
                super().mousePressEvent(e)

                if item is not None and was_selected:
                    item.run_game()
        else:
            super().mousePressEvent(e)


# General settings
class GeneralSettings(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)

        # Layout
        layout = QGridLayout()
        self.setLayout(layout)

        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 1)

        layout.setRowStretch(0, 4)
        layout.setRowStretch(1, 1)

        # Settings box
        settings_widget = QFrame()

        settings_widget.setFrameShape(QFrame.Shape.Box)
        settings_widget.setLineWidth(2)

        settings_layout = QGridLayout()
        settings_widget.setLayout(settings_layout)

        layout.addWidget(settings_widget, 0, 0, 1, 2)

        # Colours setting
        settings_layout.addWidget(QLabel("Colours"), 0, 0)

        self.colours_combo_box = QComboBox()
        self.colours_combo_box.addItems(colour["Name"] for colour in COLOURS)
        self.colours_combo_box.activated.connect(self.change_colour)

        settings_layout.addWidget(self.colours_combo_box, 0, 1)

        self.refresh_settings()

        # Reset to defaults button
        reset_button = QPushButton("Reset to Default Settings")
        reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(reset_button, 1, 1)

    def change_colour(self, index):
        current_settings = self.settings.value("gameSettings")
        current_settings["Colours"] = COLOURS[index]
        self.settings.setValue("gameSettings", current_settings)

    def refresh_settings(self):
        self.colours_combo_box.setCurrentIndex(
            COLOURS.index(self.settings.value("gameSettings")["Colours"])
        )

    def reset_settings(self):
        current_settings = self.settings.value("gameSettings")
        current_settings["Colours"] = DEFAULT_SETTINGS["Colours"]
        self.settings.setValue("gameSettings", current_settings)
        self.refresh_settings()


# Advanced settings
class AdvancedSettings(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.settings = QSettings("config.ini", QSettings.Format.IniFormat)

        # Layout
        layout = QGridLayout()
        self.setLayout(layout)

        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 4)
        layout.setRowStretch(2, 1)

        # Warning label
        warning_label = QLabel(
            "Only change these settings if you know what you are doing! (These settings will only apply to games not found in the database)"
        )
        warning_label.setStyleSheet("QLabel { color: red; }")
        layout.addWidget(warning_label, 0, 0)

        # Advanced settings box
        advanced_settings_widget = QFrame()

        advanced_settings_widget.setFrameShape(QFrame.Shape.Box)
        advanced_settings_widget.setLineWidth(2)

        advanced_settings_layout = QGridLayout()
        advanced_settings_widget.setLayout(advanced_settings_layout)

        layout.addWidget(advanced_settings_widget, 1, 0, 1, 2)

        # Shift setting
        advanced_settings_layout.addWidget(QLabel("Shift quirk (8XY6 and 8XYE)"), 0, 0)

        self.shift_combo_box = QComboBox()
        self.shift_combo_box.addItems(
            ["Take VX as input", "Take VY as input (Default)"]
        )
        self.shift_combo_box.activated.connect(
            lambda index: self.change_setting(index, "shift")
        )

        advanced_settings_layout.addWidget(self.shift_combo_box, 0, 1)

        # Memory increment by X setting
        advanced_settings_layout.addWidget(
            QLabel("Load/Store quirk: increment index register by X (FX55 and FX65)"),
            1,
            0,
        )

        self.memory_increment_by_x_combo_box = QComboBox()
        self.memory_increment_by_x_combo_box.addItems(
            ["Increment by X", "Increment by X + 1 (Default)"]
        )
        self.shift_combo_box.activated.connect(
            lambda index: self.change_setting(index, "memoryIncrementByX")
        )

        advanced_settings_layout.addWidget(self.memory_increment_by_x_combo_box, 1, 1)

        # Memory leave I unchanged setting
        advanced_settings_layout.addWidget(
            QLabel("Load/Store quirk: leave index register unchanged (FX55 and FX65)"),
            2,
            0,
        )

        self.memory_leave_i_unchanged_combo_box = QComboBox()
        self.memory_leave_i_unchanged_combo_box.addItems(
            ["Leave I unchanged", "Increment I (Default)"]
        )
        self.memory_leave_i_unchanged_combo_box.activated.connect(
            lambda index: self.change_setting(index, "memoryLeaveIUnchanged")
        )

        advanced_settings_layout.addWidget(
            self.memory_leave_i_unchanged_combo_box, 2, 1
        )

        # Wrap setting
        advanced_settings_layout.addWidget(
            QLabel("Wrap quirk (DXYN)"),
            3,
            0,
        )

        self.wrap_combo_box = QComboBox()
        self.wrap_combo_box.addItems(["Wrap sprites", "Clip sprites (Default)"])
        self.wrap_combo_box.activated.connect(
            lambda index: self.change_setting(index, "wrap")
        )

        advanced_settings_layout.addWidget(self.wrap_combo_box, 3, 1)

        # Jump setting
        advanced_settings_layout.addWidget(QLabel("Jump quirk (BNNN)"), 4, 0)

        self.jump_combo_box = QComboBox()
        self.jump_combo_box.addItems(["Jump with BXNN", "Jump with BNNN (Default)"])
        self.jump_combo_box.activated.connect(
            lambda index: self.change_setting(index, "jump")
        )

        advanced_settings_layout.addWidget(self.jump_combo_box, 4, 1)

        # vBlank setting
        advanced_settings_layout.addWidget(QLabel("vBlank quirk (DXYN)"), 5, 0)

        self.vblank_combo_box = QComboBox()
        self.vblank_combo_box.addItems(
            ["Wait for vertical blank", "Draw sprites immediately (Default)"]
        )
        self.vblank_combo_box.activated.connect(
            lambda index: self.change_setting(index, "vblank")
        )

        advanced_settings_layout.addWidget(self.vblank_combo_box, 5, 1)

        # Logic setting
        advanced_settings_layout.addWidget(
            QLabel("VF reset quirk (8XY1, 8XY2, and 8XY3)"), 6, 0
        )

        self.logic_combo_box = QComboBox()
        self.logic_combo_box.addItems(
            ["Set VF to 0 after execution", "Leave VF unchanged (Default)"]
        )
        self.logic_combo_box.activated.connect(
            lambda index: self.change_setting(index, "logic")
        )

        advanced_settings_layout.addWidget(self.logic_combo_box, 6, 1)

        self.refresh_settings()

        # Reset to defaults button
        reset_button = QPushButton("Reset to Default Settings")
        reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(reset_button, 2, 1)

    def change_setting(self, index, name):
        current_settings = self.settings.value("gameSettings")
        current_settings["Quirks"][name] = bool(index != 1)
        self.settings.setValue("gameSettings", current_settings)

    def refresh_settings(self):
        quirks = self.settings.value("gameSettings")["Quirks"]
        self.shift_combo_box.setCurrentIndex(0 if quirks["shift"] else 1)
        self.memory_increment_by_x_combo_box.setCurrentIndex(
            0 if quirks["memoryIncrementByX"] else 1
        )
        self.memory_leave_i_unchanged_combo_box.setCurrentIndex(
            0 if quirks["memoryLeaveIUnchanged"] else 1
        )
        self.wrap_combo_box.setCurrentIndex(0 if quirks["wrap"] else 1)
        self.jump_combo_box.setCurrentIndex(0 if quirks["jump"] else 1)
        self.vblank_combo_box.setCurrentIndex(0 if quirks["vblank"] else 1)
        self.logic_combo_box.setCurrentIndex(0 if quirks["logic"] else 1)

    def reset_settings(self):
        current_settings = self.settings.value("gameSettings")
        current_settings["Quirks"] = DEFAULT_SETTINGS["Quirks"]
        self.settings.setValue("gameSettings", current_settings)
        self.refresh_settings()


# Settings window
class SettingsWindow(QMainWindow):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        # Window title and size
        self.setWindowTitle("Settings")
        self.resize(QSize(640, 320))

        self.tabs = QTabWidget()
        self.tabs.addTab(GeneralSettings(self), "General")
        self.tabs.addTab(AdvancedSettings(self), "Advanced")
        self.tabs.currentChanged.connect(self.refresh_tab)

        self.setCentralWidget(self.tabs)

    def refresh_tab(self, index):
        refresh_settings = self.tabs.currentWidget().refresh_settings
        refresh_settings()


# Main window
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

        # Set default settings
        if not self.settings.contains("gameSettings"):
            self.settings.setValue("gameSettings", DEFAULT_SETTINGS)

        # GUI layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(16, 4, 16, 12)

        self.roms_widget = None

        # Menu bar
        menu_bar = self.menuBar()
        assert menu_bar is not None

        menu_bar.setStyleSheet("QMenuBar { padding-left: 12}")

        # File menu
        file_menu = menu_bar.addMenu("&File")
        assert file_menu is not None

        choose_game = QAction("Choose &game...", self)
        choose_game.triggered.connect(self.choose_game)
        file_menu.addAction(choose_game)

        choose_rom_dir = QAction("Choose ROM &directory...", self)
        choose_rom_dir.triggered.connect(self.choose_dir)
        file_menu.addAction(choose_rom_dir)

        # Settings action
        open_settings_button = QAction("&Settings", self)
        open_settings_button.triggered.connect(self.open_settings)
        menu_bar.addAction(open_settings_button)

        # Container widget
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.get_roms()

        application_instance = QApplication.instance()
        assert application_instance is not None
        application_instance.installEventFilter(self)

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
            main(file, self.settings.value("gameSettings"))

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

    def open_settings(self) -> None:
        settings_window = SettingsWindow(self)
        settings_window.show()

    def eventFilter(self, a0, a1):
        if (
            a1 is not None
            and a1.type() == QtGui.QMouseEvent.Type.MouseButtonPress
            and isinstance(self.roms_widget, GameList)
        ):
            mouse_event = cast(QtGui.QMouseEvent, a1)
            global_pos = mouse_event.globalPosition().toPoint()
            local_pos = self.roms_widget.mapFromGlobal(global_pos)
            if not self.roms_widget.rect().contains(local_pos):
                self.roms_widget.clearSelection()
        return super().eventFilter(a0, a1)


def gui() -> None:
    app = QApplication([])
    window = EmulatorWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    gui()
