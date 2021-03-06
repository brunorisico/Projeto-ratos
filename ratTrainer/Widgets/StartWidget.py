"""
creation date: 5-4-2021 20:00
last modified: 07-05-2021 16:15

@author: Bruno Correia - brunorisico@gmail.com

Starting menu

Notes:
Only tested on Windows and will probably only work on windows unless the search funtion for the ports outputs other stuff that is not COMx

"""

from PyQt5.QtWidgets import  QGridLayout, QWidget, QPushButton, QComboBox, QLabel, QLineEdit

import serial.tools.list_ports
import serial

class StartWidget(QWidget):
    """ 
    main interface display with start, settings and quit button
    """
    def __init__(self, parent):
        super(StartWidget, self).__init__(parent)

        self.main_window_reference = parent

        # variables
        self.available_com_ports_with_arduino = list()
        self.selected_com_port = ""

        # default values for trials and the timer (in seconds!) and VDS used
        self.number_of_trials = 100
        self.timer = 1800
        self.VDS = "Training"

        # interface layout
        self.menu_layout = QGridLayout()

        # search for com ports to look for the arduino
        self.search_COM_btn = QPushButton('Search', self)
        self.search_COM_btn.clicked.connect(self.search_COM_ports)

        # list the available ports on a combobox 
        self.comboBox_available_ports = QComboBox(self)
        self.comboBox_available_ports.activated[str].connect(self.new_com_selected)

        # VDS train or VDS proper
        self.comboBox_VDS_options = QComboBox(self)
        self.comboBox_VDS_options.addItem("VDS training session")
        self.comboBox_VDS_options.addItem("VDS test session")
        self.comboBox_VDS_options.activated[str].connect(self.vds_selected)

        # trials number
        self.trial_label = QLabel("<b>Number of trials</b>")
        self.trial_QLineEdit = QLineEdit()
        self.trial_QLineEdit.setText(str(self.number_of_trials))
        self.trial_QLineEdit.setReadOnly(True)

        # Timer
        self.timer_label = QLabel("<b>Timer (seconds)</b>")
        self.timer_QLineEdit = QLineEdit()
        self.timer_QLineEdit.setText(str(self.timer))
        self.timer_QLineEdit.setReadOnly(True)

        # connect button
        self.connect_btn = QPushButton('Connect', self)
        self.connect_btn.setFixedHeight(50)
        self.connect_btn.clicked.connect(self.connect_pressed)
        self.connect_btn.setEnabled(False)

        self.menu_layout.addWidget(self.search_COM_btn, 0, 0)
        self.menu_layout.addWidget(self.comboBox_available_ports, 0, 1)
        self.menu_layout.addWidget(self.comboBox_VDS_options, 1, 0, 1, 2)
        self.menu_layout.addWidget(self.trial_label, 2, 0)
        self.menu_layout.addWidget(self.trial_QLineEdit, 2, 1)
        self.menu_layout.addWidget(self.timer_label, 3, 0)
        self.menu_layout.addWidget(self.timer_QLineEdit, 3, 1)
        self.menu_layout.addWidget(self.connect_btn, 4, 0, 1, 2)

        self.setLayout(self.menu_layout)

        # search for ports everytime the program is started and update combobox
        self.search_COM_ports()


    def search_COM_ports(self):
        """
        search or the communications ports available
        and updates the combobox
        """
        self.comboBox_available_ports.clear()
        self.available_com_ports_with_arduino = list()

        all_available_com_ports = [list(x) for x in list(serial.tools.list_ports.comports())]

        for port_info in all_available_com_ports:
            if "Arduino" in port_info[1]:  #change to other string if Arduino is not being used
                self.available_com_ports_with_arduino.append(port_info)
                self.comboBox_available_ports.addItem(port_info[1])

        # sets the first door found as default
        try:
            self.selected_com_port = self.available_com_ports_with_arduino[0][0]
            self.connect_btn.setEnabled(True)
        except:
            self.connect_btn.setEnabled(False)


    def new_com_selected(self, order):   
        """
        called when a port is selected from the comboBox_available_ports
        """

        # we only need the COM port name...
        for port_info in self.available_com_ports_with_arduino:
            if order == port_info[1]:
                self.selected_com_port = port_info[0]

    def vds_selected(self, vds_selected):
        if vds_selected == "VDS training session":
            self.VDS = "Training"
            self.number_of_trials = 100
            self.timer = 1800
        elif vds_selected == "VDS test session":
            self.VDS = "Test"
            self.number_of_trials = 120
            self.timer = 3600
        self.trial_QLineEdit.setText(str(self.number_of_trials))
        self.timer_QLineEdit.setText(str(self.timer))

    def connect_pressed(self):
        """  
        Creates (or tries to) a serial connection to the Arduino and a Thread
        to listen to inputs from the Arduino

        This function will also change the widget to the experiment control panel
        """

        try:
            self.main_window_reference.set_status_bar_message("Trying to connect to Arduino using port {}".format(self.selected_com_port))
            serial_connection = serial.Serial(self.selected_com_port, 115200, timeout=0)

            self.main_window_reference.set_to_control_panel(int(self.timer_QLineEdit.text()), int(self.trial_QLineEdit.text()), serial_connection, self.VDS)

            self.main_window_reference.showMaximized()
            self.main_window_reference.set_status_bar_message("If you found any problem you can contact me using my personal email - brunorisico@gmail.com")

        except Exception as e:
            self.main_window_reference.set_status_bar_message(str(e).split(':')[0])

