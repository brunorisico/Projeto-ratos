"""
creation date: 12-4-2021 10:015
last modified: 13-09-2019 18:30

@author: Bruno Correia - brunorisico@gmail.com

Control panel
"""

from PyQt5.QtWidgets import QMainWindow, QTextEdit, QScrollArea, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QSplitter, QGroupBox, QStyle, QGridLayout, QSizePolicy
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer,QDateTime

from pyqt_led import Led

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import matplotlib.pyplot as plt

from Widgets.Threads.SerialThread import SerialThread

class ControlPanelWidget(QWidget):
    """ 
    
    """
    def __init__(self, parent):
        super(ControlPanelWidget, self).__init__(parent)

        #timer and trial
        self.timer_value_seconds = 0
        self.trials_value = 0
        self.current_trial_value = 0

        self.register_values = [0,0,0,0]

        self.serialThread = ""

        # ------------------------------- TOP LEFT ------------------------------------
        # group of buttons to control the experiment
        experiment_groupbox = QGroupBox("Experiment controls")

        # -------------------------- BUTTONS ----------------------------
        # start button
        self.start_button = QPushButton('Start', self)
        self.start_button.setFixedHeight(50)
        self.start_button.setIcon(self.style().standardIcon(getattr(QStyle, 'SP_MediaPlay')))
        self.start_button.clicked.connect(self.startTimer)

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
        leds_groupbox = QGroupBox("Leds")

        self.house_led_label = QLabel('House led')
        self.house_led_label.setAlignment(Qt.AlignCenter)
        self.house_led_label.setFont(QFont('Arial', 16))

        self.left_led_label = QLabel('Left led')
        self.left_led_label.setAlignment(Qt.AlignCenter)
        self.left_led_label.setFont(QFont('Arial', 16))

        self.right_led_label = QLabel('Right led')
        self.right_led_label.setAlignment(Qt.AlignCenter)
        self.right_led_label.setFont(QFont('Arial', 16))
        
        # illustration purposes only
        self.house_led = Led(self, on_color=Led.white, shape=Led.circle)
        self.house_led.setFixedSize(150, 150)
        self.left_led = Led(self, on_color=Led.green, shape=Led.circle)
        self.left_led.setFixedSize(150, 150)
        self.right_led = Led(self, on_color=Led.red, shape=Led.circle)
        self.right_led.setFixedSize(150, 150)

        leds_layout = QGridLayout()
        leds_layout.addWidget(self.house_led_label, 1, 0)
        leds_layout.addWidget(self.left_led_label, 1, 1)
        leds_layout.addWidget(self.right_led_label, 1, 2)

        leds_layout.addWidget(self.house_led, 2, 0)
        leds_layout.addWidget(self.left_led, 2, 1)
        leds_layout.addWidget(self.right_led, 2, 2)

        leds_groupbox.setLayout(leds_layout)

        # ----------------------- SENSORS ------------------------
        sensors_groupbox = QGroupBox("Sensors")

        self.feeder_sensor_label = QLabel('Feeder sensor')
        self.feeder_sensor_label.setAlignment(Qt.AlignCenter)
        self.feeder_sensor_label.setFont(QFont('Arial', 12))

        self.left_sensor_label = QLabel('Left sensor')
        self.left_sensor_label.setAlignment(Qt.AlignCenter)
        self.left_sensor_label.setFont(QFont('Arial', 12))

        self.right_sensor_label = QLabel('Right sensor')
        self.right_sensor_label.setAlignment(Qt.AlignCenter)
        self.right_sensor_label.setFont(QFont('Arial', 12))
        
        # illustration purposes only
        self.feeder_sensor = Led(self, on_color=Led.orange, shape=Led.rectangle)
        self.feeder_sensor.set_status(True)
        self.left_sensor = Led(self, on_color=Led.orange, shape=Led.rectangle)
        self.left_sensor.set_status(True)
        self.right_sensor = Led(self, on_color=Led.orange, shape=Led.rectangle)
        self.right_sensor.set_status(True)

        sensors_layout = QGridLayout()
        sensors_layout.addWidget(self.feeder_sensor_label, 1, 0)
        sensors_layout.addWidget(self.left_sensor_label, 1, 1)
        sensors_layout.addWidget(self.right_sensor_label, 1, 2)

        sensors_layout.addWidget(self.feeder_sensor, 2, 0)
        sensors_layout.addWidget(self.left_sensor, 2, 1)
        sensors_layout.addWidget(self.right_sensor, 2, 2)

        sensors_groupbox.setLayout(sensors_layout)

        # layout
        experiment_control_layout = QGridLayout()
        experiment_control_layout.addWidget(self.start_button, 1, 0, 1, 3)
        experiment_control_layout.addWidget(timer_groupbox, 2, 0, 1, 3)
        experiment_control_layout.addWidget(trials_groupbox, 3, 0, 1, 3)
        experiment_control_layout.addWidget(leds_groupbox, 4, 0, 1, 3)
        experiment_control_layout.addWidget(sensors_groupbox, 5, 0, 1, 3)
        experiment_groupbox.setLayout(experiment_control_layout) 

        # ------------------------------- TOP RIGHT (BarPlot) ------------------------------------
        self.barplot = BarPlotWidget(self)
        
        # top split - left control buttons and timer - right the barplot
        self.left_right_splitter = QSplitter(Qt.Horizontal)
        self.left_right_splitter.addWidget(experiment_groupbox)
        self.left_right_splitter.addWidget(self.barplot)
        self.left_right_splitter.setStretchFactor(1, 500)

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
 
    def showTime(self):
        print(self.timer_value_seconds)
        if self.timer_value_seconds != 0:
            self.timer_value_seconds = self.timer_value_seconds - 1
            time = QDateTime.fromTime_t(self.timer_value_seconds).toUTC().toString('hh:mm:ss')
            self.timer_label.setText(time)
        else:
            self.timer.stop()
            #self.start_button.setEnabled(False)

    def startTimer(self):
        self.serialThread.start_trial()
        #self.timer.start(1000)
        self.timer_label.setStyleSheet("QLabel {color: green; background-color: black;}")
        self.start_button.setEnabled(False)

    def setTimerTrialConnection(self, timer, trial, serial_connection):
        self.timer_value_seconds = timer
        self.trials_value = trial
        self.serial_connection = serial_connection

        def thread_control(value):
            print(value)
            # I hate to do chained if else but it is the only way I can do this in a short time
            # does not matter anyway since this is only for illustration purposes
            # the data is being recorded directly in the SerialThread for precision
            if value == 'DS':
                self.timer.start(1000)
                self.terminal.storeText("Delay started")
                self.terminal.displayText()

            elif value == 'FSF':
                self.timer.stop()
                self.start_button.setEnabled(True)
                self.terminal.storeText("Feeder sensor failed at trial {} out of {}".format(self.current_trial_value, self.trials_value))
                self.terminal.storeText("Arduino has been stoped and reset")
                self.terminal.displayText()


            # when the trial ends PRemature response - OmissionResponse - TimeResponse - preServeranceResponse
            elif value == 'PR' or value == 'OR' or value == 'TR' or value == 'SR':
                self.current_trial_value = self.current_trial_value + 1   
                if self.current_trial_value > self.trials_value:
                    self.timer.stop()
                    self.start_button.setEnabled(False)
                    print("IMPLEMENTAR FIM EXPERIENCIA")
                else:
                    self.trials_label.setText("{} out of {}".format(self.current_trial_value, self.trials_value))
                    if value == 'PR':
                        self.register_values[0] = self.register_values[0] + 1
                        response = "premature response"         
                    elif value == 'OR':
                        self.register_values[1] = self.register_values[1] + 1
                        response = "omission response" 
                    elif value == 'TR':
                        self.register_values[2] = self.register_values[2] + 1
                        response = "timed response" 
                    elif value == 'SR':
                        self.register_values[3] = self.register_values[3] + 1
                        response = "perseverant response" 

                    self.barplot.bar_plot(self.register_values)
                    new_line_after_trial = '\n' + '-----' * 10
                    self.terminal.storeText("Trial {} ended up with a {}{}".format(self.current_trial_value, response, new_line_after_trial))
                    self.terminal.displayText()

            # turn leds on and off in the GUI
            elif "ON" in value:
                light_status = "ON"
                if value == 'HL_ON':
                    self.house_led.set_status(True)
                    light_name = "House light"
                elif value == 'LL_ON':
                    self.left_led.set_status(True)
                    light_name = "Left light"
                elif value == 'RL_ON':
                    self.right_led.set_status(True)
                    light_name = "Right light"
                self.terminal.storeText("Trial {} out of {}. {} {}".format(self.current_trial_value, self.trials_value, light_name, light_status))
                self.terminal.displayText()

            elif "OFF" in value:
                light_status = "OFF"
                if value == 'HL_OFF':
                    self.house_led.set_status(False)
                    light_name = "House light"
                elif value == 'LL_OFF':
                    self.left_led.set_status(False)
                    light_name = "Left light"
                elif value == 'RL_OFF':
                    self.right_led.set_status(False)
                    light_name = "Right light"         
                self.terminal.storeText("Trial {} out of {}. {} {}".format(self.current_trial_value, self.trials_value, light_name, light_status))
                self.terminal.displayText()

                    
        # set trial and timer values
        time = QDateTime.fromTime_t(self.timer_value_seconds).toUTC().toString('hh:mm:ss')
        self.timer_label.setText(time)

        self.trials_label.setText("0 out of {}".format(self.trials_value))

        # start reading the serial connection
        self.serialThread = SerialThread(self, serial_connection)
        self.serialThread.signal.connect(thread_control)
        self.serialThread.start()

class TerminalWidget(QTextEdit):
    def __init__(self, parent):
        super(TerminalWidget, self).__init__(parent)
        self.setReadOnly(True)

        self.text_storage = []

        # Qcolors
        #self.lightskyblue = QColor(35,206,250)
        #self.setTextColor(self.lightskyblue)

        self.setFontPointSize(10)

        self.storeText('Hello! To start the test press the start button!')
        self.displayText()
  
    def resetText(self):
        self.text_storage = []
        self.setPlainText(''.join(self.text_storage))

    def storeText(self, newEntry):
        timestamp=QDateTime.currentDateTime().toString('hh:mm:ss')
        newEntry = timestamp + ' --- ' + newEntry
        self.text_storage.insert(0, newEntry)

    def displayText(self):
        self.setPlainText('\n'.join(self.text_storage))


class BarPlotWidget(QWidget):
    def __init__(self, parent):
        super(BarPlotWidget, self).__init__(parent)
        plt.style.use('dark_background')

        self.figure = plt.figure(dpi=100)
        self.figure.tight_layout()
        self.canvas = FigureCanvas(self.figure)
        
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


    def bar_plot(self, data):
        # make sure figure is clear
        self.figure.clear()

        print(data)

        #sns.histplot(data=tips, x="day", hue="sex", multiple="dodge", shrink=.8)
        self.ax = self.figure.add_subplot(111)
        main_registers = ["Premature response", "Omission", "Timed reponse", "Perseverant response"]
        sns.barplot(x=main_registers, y=data, ax=self.ax, palette="Set1")

        self.canvas.draw()