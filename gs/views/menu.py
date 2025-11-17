from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtGui import QAction
import webbrowser


class AppMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_menu = self.addMenu("&File")

        self.action_load = QAction("Load Measurement...", self)
        self.action_load.setShortcut("Ctrl+O")

        self.action_save = QAction("Save Results", self)
        self.action_save.setShortcut("Ctrl+S")

        self.action_exit = QAction("Exit", self)

        self.file_menu.addAction(self.action_load)
        self.file_menu.addAction(self.action_save)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)

        ## Settings
        self.settings_menu = self.addMenu("&Settings")
        self.action_settings = QAction("Settings", self)
        self.settings_menu.addAction(self.action_settings)

        ## Help
        self.help_menu = self.addMenu("&Help")
        self.action_about = QAction("About", self)

        self.action_about.triggered.connect(
            lambda: webbrowser.open("http://www.google.com")
        )

        self.help_menu.addAction(self.action_about)
