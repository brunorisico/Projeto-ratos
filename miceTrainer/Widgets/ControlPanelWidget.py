"""
creation date: 12-4-2021 10:015
last modified: 13-09-2019 18:30

@author: Bruno Correia - brunorisico@gmail.com

Starting menu

Notes:
Only tested on Windows and will probably only work on windows unless the search funtion for the ports outputs other stuff that is not COMx

"""

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QScrollArea, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QSplitter, QGroupBox, QStyle, QGridLayout, QSizePolicy
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer,QDateTime

from pyqt_led import Led

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import matplotlib.pyplot as plt

class ControlPanelWidget(QWidget):
    """ 
    
    """
    def __init__(self, parent):
        super(ControlPanelWidget, self).__init__(parent)

        self.status_bar = parent.statusBar()

        #timer and trial
        self.timer_value_seconds = 0
        self.trials_value = 0
        self.current_trial_value = 1

        # ------------------------------- TOP LEFT ------------------------------------
        # group of buttons to control the experiment
        experiment_groupbox = QGroupBox("Experiment controls")

        # -------------------------- BUTTONS ----------------------------
        # start button
        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedHeight(50)
        self.start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self.start_button.clicked.connect(self.startTimer)

        # stop button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setFixedHeight(50)
        self.stop_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaStop')))
        self.stop_button.clicked.connect(self.endTimer)
        self.stop_button.setEnabled(False)

        # next trial button
        self.next_button = QPushButton('Next trial', self)
        self.next_button.setFixedHeight(50)
        self.next_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaSkipForward')))
        #self.next_button.clicked.connect(self.load_data)

        # -------------- TIMER ------------------------------
        timer_groupbox = QGroupBox("Timer")
        self.timer_label = QLabel('00:00:00')
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("QLabel {color: red; background-color: black;}")
        self.timer_label.setFont(QFont('Arial', 32))

        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)

        # timer groupbox layout
        timer_groupbox_layout = QVBoxLayout()
        timer_groupbox_layout.addWidget(self.timer_label)
        timer_groupbox.setLayout(timer_groupbox_layout)

        # -------------- TRIALS ------------------------------ 
        # trials groupbox
        trials_groupbox = QGroupBox("Number of trials")
        self.trials_label = QLabel('1 out of 1')
        self.trials_label.setAlignment(Qt.AlignCenter)
        self.trials_label.setStyleSheet("QLabel {color: goldenrod; background-color: black;}")
        self.trials_label.setFont(QFont('Arial', 32))

        # trials groupbox layout
        trials_groupbox_layout = QVBoxLayout()
        trials_groupbox_layout.addWidget(self.trials_label)
        trials_groupbox.setLayout(trials_groupbox_layout)

        # ------------------ LEDS ----------------------------
        # illustration purposes only
        self.house_led = Led(self, on_color=Led.white, shape=Led.capsule)
        self.left_led = Led(self, on_color=Led.green, shape=Led.capsule)
        self.right_led = Led(self, on_color=Led.red, shape=Led.capsule)

        #self.left_led.set_status(True)

        # layout
        experiment_control_layout = QGridLayout()
        experiment_control_layout.addWidget(self.start_button, 1, 0)
        experiment_control_layout.addWidget(self.stop_button, 1, 1)
        experiment_control_layout.addWidget(self.next_button, 1, 2)
        experiment_control_layout.addWidget(timer_groupbox, 2, 0, 1, 3)
        experiment_control_layout.addWidget(trials_groupbox, 3, 0, 1, 3)
        experiment_control_layout.addWidget(self.house_led, 4, 0)
        experiment_control_layout.addWidget(self.left_led, 4, 1)
        experiment_control_layout.addWidget(self.right_led, 4, 2)
        experiment_groupbox.setLayout(experiment_control_layout) 

        # ------------------------------- TOP RIGHT (HISTOGRAM) ------------------------------------
        self.histogram = HistogramWidget(self)
        
        # top split - left control buttons and timer - right the histogram
        self.left_right_splitter = QSplitter(Qt.Horizontal)
        self.left_right_splitter.addWidget(experiment_groupbox)
        self.left_right_splitter.addWidget(self.histogram)

        # ---------------------- TERMINAL -  BOTTOM ------------------------------
        self.terminal = TerminalWidget(self)

        # make the terminal "scrollable"
        terminal_scroll_area = QScrollArea()
        terminal_scroll_area.setWidget(self.terminal)
        terminal_scroll_area.setWidgetResizable(True)
        
        # top and bottom screen splitter
        self.top_bottom_splitter = QSplitter(Qt.Vertical)
        self.top_bottom_splitter.addWidget(self.left_right_splitter)
        self.top_bottom_splitter.addWidget(terminal_scroll_area)

        layout = QHBoxLayout(self)
        layout.addWidget(self.top_bottom_splitter)
        self.setLayout(layout)

    def setTimerTrial(self, timer, trial):
        self.timer_value_seconds = timer
        self.trials_value = trial
        
        time = QDateTime.fromTime_t(self.timer_value_seconds).toUTC().toString('hh:mm:ss')
        self.timer_label.setText(time)

        self.trials_label.setText("1 out of {}".format(self.trials_value))

    def showTime(self):
        if self.timer_value_seconds != 0:
            self.timer_value_seconds = self.timer_value_seconds - 1
            time = QDateTime.fromTime_t(self.timer_value_seconds).toUTC().toString('hh:mm:ss')
            self.timer_label.setText(time)
        else:
            self.endTimer()
            self.start_button.setEnabled(False)

    def startTimer(self):
        self.timer.start(1000)
        self.timer_label.setStyleSheet("QLabel {color: green; background-color: black;}")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def endTimer(self):
        self.timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)


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