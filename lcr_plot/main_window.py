from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QVBoxLayout
from PyQt6.QtCore import QSettings, Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvas, NavigationToolbar2QT
import numpy as np
import pandas as pd
from os.path import dirname, basename
from .ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__ui = Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__ui.open_file_action.triggered.connect(self.open_file)
        self.__ui.exit_app_action.triggered.connect(self.exit_app)

        self.__figure = Figure()
        self.__canvas = FigureCanvas(self.__figure)
        self.__ax = self.__canvas.figure.subplots()
        self.__ax.grid()
        self.__ax.set_xlabel("время")
        self.__ax.set_ylabel("C, pF")

        layout = QVBoxLayout(self.__ui.centralwidget)
        layout.addWidget(self.__canvas)

        toolbar = NavigationToolbar2QT(self.__canvas, self)
        self.addToolBar(toolbar)
        toolbar.setAllowedAreas(Qt.ToolBarArea.AllToolBarAreas)

        self.__data = None
        self.__grouped = None

    def open_file(self):
        self.__ui.statusbar.clearMessage()

        settings = QSettings()

        default_dir = settings.value("default_dir")
        file = QFileDialog.getOpenFileName(
            self, "Открыть файл", default_dir, "Файлы txt (*.txt)")
        file_path = file[0]
        if not file_path:
            return

        self.__ui.statusbar.showMessage(f"Открыт: file_path")

        new_dir = dirname(file_path)
        if new_dir != default_dir:
            settings.setValue("default_dir", new_dir)

        self.__data = pd.read_csv(file_path,
                                  sep=",",
                                  header=None,
                                  names=["datetime", "C", 2, 3],
                                  usecols=["datetime", "C"],
                                  decimal=".",
                                  parse_dates=["datetime"],
                                  dtype={"datetime": "str", "C": np.float64})

        self.__data["C"] = self.__data["C"] * 1e12

        if len(self.__ax.lines) > 0:
            self.__ax.lines.clear()

        self.__ax.plot(self.__data["datetime"], self.__data["C"])
        self.__ax.set_title(basename(file_path))

        # self.__average_by_block(60.)

        # self.__ax.plot(self.__grouped["datetime"], self.__grouped["C"])

        # сброс лимитов по осям
        self.__ax.relim()
        # сброс перебора цветов графиков
        self.__ax.set_prop_cycle(None)
        # self.__ax.autoscale(enable=True, axis="both")
        self.__canvas.draw_idle()

    def exit_app(self):
        QApplication.quit()

    def __get_by_block_grouping_function(self, block_duration: pd.Timedelta):
        def by_block_grouping_function(i):
            t_i = self.__data.iloc[i, self.__data.columns.get_loc("datetime")]
            t_start = self.__data.iloc[0,
                                       self.__data.columns.get_loc("datetime")]
            dt = t_i-t_start
            return dt // block_duration
        return by_block_grouping_function

    def __avg_datetimes(self, datetimes):
        return datetimes.mean()

    def __average_by_block(self, block_duration: float, drop_last_value=True):
        block_timedelta = pd.Timedelta(seconds=block_duration)
        self.__grouped = self.__data.groupby(
            by=self.__get_by_block_grouping_function(block_timedelta)).agg({"datetime": self.__avg_datetimes, "C": "mean"})

        if drop_last_value:
            self.__grouped.drop(self.__grouped.index[-1], inplace=True)
