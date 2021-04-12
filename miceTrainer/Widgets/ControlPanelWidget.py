"""
creation date: 12-4-2021 10:015
last modified: 13-09-2019 18:30

@author: Bruno Correia - brunorisico@gmail.com

Starting menu

Notes:
Only tested on Windows and will probably only work on windows unless the search funtion for the ports outputs other stuff that is not COMx

"""

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QScrollArea, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QSplitter, QGroupBox, QStyle, QGridLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import matplotlib.pyplot as plt

class ControlPanelWidget(QWidget):
    """ 
    
    """
    def __init__(self, parent):
        super(ControlPanelWidget, self).__init__(parent)

        self.status_bar = parent.statusBar()

        # top left
        # group of buttons to control the experiment
        experiment_groupbox = QGroupBox("Experiment controls")

        # start button
        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedHeight(50)
        self.start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        #self.folder_location_open_btn.clicked.connect(self.load_data)

        # stop button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setFixedHeight(50)
        self.stop_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        #self.folder_location_open_btn.clicked.connect(self.load_data)

        # next trial button
        self.next_button = QPushButton('Next trial', self)
        self.next_button.setFixedHeight(50)
        self.next_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_DialogOpenButton')))
        #self.folder_location_open_btn.clicked.connect(self.load_data)

        # timer groupbox
        timer_groupbox = QGroupBox("Timer")

        # trials groupbox
        trials_groupbox = QGroupBox("Number of trials")


        experiment_control_layout = QGridLayout()
        experiment_control_layout.addWidget(self.start_button, 1, 0)
        experiment_control_layout.addWidget(self.stop_button, 1, 1)
        experiment_control_layout.addWidget(self.next_button, 1, 2)
        experiment_control_layout.addWidget(timer_groupbox, 2, 0)
        experiment_control_layout.addWidget(trials_groupbox, 3, 0)
        experiment_groupbox.setLayout(experiment_control_layout) 

        # top right
        self.histogram = HistogramWidget(self)
        
        # top split - left control buttons and timer - right the histogram
        self.left_right_splitter = QSplitter(Qt.Horizontal)
        self.left_right_splitter.addWidget(experiment_groupbox)
        self.left_right_splitter.addWidget(self.histogram)

        # ---- TERMINAL BOTTOM ------
        self.terminal = TerminalWidget(self)

        # make the terminal "scrollable"
        terminal_scroll_area = QScrollArea()
        terminal_scroll_area.setWidget(self.terminal)
        terminal_scroll_area.setWidgetResizable(True)
        
        # top and bottom screen splitter
        self.top_bottom_splitter = QSplitter(Qt.Vertical)
        self.top_bottom_splitter.addWidget(self.left_right_splitter)
        self.top_bottom_splitter.addWidget(terminal_scroll_area)
        self.top_bottom_splitter.setStretchFactor(5, 1)

        # left side splitter with scrollArea
        #self.control_panel = ControlWidget(self, self.terminal, self.plot)
  

        #self.left_side_splt = QSplitter(Qt.Horizontal)
        #self.left_side_splt.addWidget(ScrollArea)
        #self.left_side_splt.addWidget(self.right_side_splt)
        #self.left_side_splt.setStretchFactor(1, 3)

        layout = QHBoxLayout(self)
        layout.addWidget(self.top_bottom_splitter)
        self.setLayout(layout)


class TerminalWidget(QTextEdit):
    def __init__(self, parent):
        super(TerminalWidget, self).__init__(parent)
        
        self.setReadOnly(True)

        self.text_storage = []

        # Qcolors
        self.lightskyblue = QColor(35,206,250)
        self.setTextColor(self.lightskyblue)
  
    def resetText(self):
        self.text_storage = []
        self.setPlainText(''.join(self.text_storage))

    def storeText(self, newEntry):
        self.text_storage.insert(0, newEntry)

    def displayText(self):
        self.setPlainText('\n---------------------------------------------------------------------------------------------------------------------------------------------'.join(self.text_storage))


class HistogramWidget(QWidget):
    def __init__(self, parent):
        super(HistogramWidget, self).__init__(parent)
        plt.style.use('dark_background')

        self.figure = plt.figure(dpi=100)
        self.canvas = FigureCanvas(self.figure)

        self.axes = self.figure.add_subplot(111)
        self.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


    # def plot_hist(self, list_of_lists):
    #     # make sure figure is clear
    #     self.figure.clear()
    #     plt.style.use('seaborn-darkgrid')

    #     #sns.histplot(data=tips, x="day", hue="sex", multiple="dodge", shrink=.8)
    #     self.axes = fig.add_subplot(111)

    #     #colors and titles
    #     hist_colors = ['red', 'yellow', 'blue', 'green']
    #     list_titles = ['James One - Rest', 'Polar H10 - Rest', 'James One- SCWT', 'Polar H10 - SCWT']
      
    #     for i in range(4):
    #         sns.distplot(list_of_lists[i], ax=axes[i], color=hist_colors[i])
    #         axes[i].set_title(list_titles[i], fontsize=16)
    #         axes[i].set_xlabel('Interval size (ms)', fontsize=12)
    #         axes[i].set_ylabel('Density', fontsize=14)

    #     self.figure.tight_layout()
    #     self.canvas.draw()