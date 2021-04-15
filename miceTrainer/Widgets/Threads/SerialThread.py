from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time

class SerialThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, parent, arduino_connection):
        QThread.__init__(self)

        self.start_signal = False

        self.arduino_connection = arduino_connection
        self.buffer = ''
        self.expected_strings = ['PR', 'OR', 'TR', 'SR', 'HL_ON', 'LL_ON', 'RL_ON', 'HL_OFF', 'LL_OFF', 'RL_OFF', 'start', 'MO', 'ITIS', 'DS']

    def run(self): 
        while True:
            # need to create a buffer to avoid getting just partial strings
            if self.start_signal:
                while self.arduino_connection.readline().decode("utf-8").strip() != "start":
                    print('Acorda Arduino!!!!!')
                    self.arduino_connection.write(bytes("start", 'utf-8'))
                    self.start_signal = False
                self.signal.emit("ITIS")
            else:
                decodedStream = self.arduino_connection.readline().decode("utf-8").strip()
                if decodedStream != '':
                    self.buffer = self.buffer + decodedStream

                    if self.buffer in self.expected_strings:
                        self.signal.emit(self.buffer)
                        #print(self.buffer)
                        self.buffer = ""

    def start_trial(self):
        self.start_signal = True
        
                   