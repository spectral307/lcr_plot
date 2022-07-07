from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, QDir
from os.path import exists
import sys
from .main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("lcr_plot")
    app.setOrganizationName("GTLab")
    app.setOrganizationDomain("gtlab.pro")

    settings = QSettings()

    if settings.value("default_dir") is None:
        settings.setValue("default_dir", QDir.home().absolutePath())

    main_win = MainWindow()
    main_win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
