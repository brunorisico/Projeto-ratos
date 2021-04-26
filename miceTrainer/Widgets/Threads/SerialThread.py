from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time

class SerialThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, parent, arduino_connection):
        QThread.__init__(self)

        self.start_signal = False

        self.arduino_connection = arduino_connection
        self.buffer = ''
        self.expected_strings = ['HL_ON','HL_OFF', 
                                 'LL_ON', 'LL_OFF', 
                                 'RL_ON', 'RL_OFF',
                                 'PR', 'OR', 'TR', 'SR',
                                 'ITIS', 'DS', 'MO',
                                 'FSA', 'FSR', 'FSF' 'LSA',
                                 'LSR', 'RSA', 'RSR', 
                                 'SA', 'TO', 'RTS', 'FTS']

        self.trial = 1

    def run(self):
        while True:
            if self.start_signal:
                while self.arduino_connection.readline().decode("utf-8").strip() != "SA":
                    print('Trying to start Arduino')
                    self.arduino_connection.write(bytes("start", 'utf-8'))
                    self.start_signal = False
                self.signal.emit("SA")
            else:
                decodedStream = self.arduino_connection.readline().decode("utf-8").strip()
                if decodedStream != '':
                    # need to create a buffer to avoid getting just partial strings
                    self.buffer = self.buffer + decodedStream

                    if self.buffer in self.expected_strings:
                        self.signal.emit(self.buffer)
                        self.buffer = ""

    def start_trial(self):
        self.start_signal = True
        
                   