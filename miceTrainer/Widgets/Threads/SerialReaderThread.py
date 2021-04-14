from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time

class SerialReaderThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, parent, dataStream):
        QThread.__init__(self)

        self.dataStream = dataStream
        self.buffer = ''
        self.expected_strings = ['PR', 'OR', 'TR', 'SR', 'HL_ON', 'LL_ON', 'RL_ON', 'HL_OFF', 'LL_OFF', 'RL_OFF', 'start']

    def run(self): 
        while True:
            # need to create a buffer to avoid getting just partial strings
            decodedStream = self.dataStream.readline().decode("utf-8").strip()
            if decodedStream != '':
                self.buffer = self.buffer + decodedStream

                if self.buffer in self.expected_strings:
                    self.signal.emit(self.buffer)
                    #print(self.buffer)
                    self.buffer = ""
                   