from PyQt5.QtCore import Qt, QThread, pyqtSignal

class SerialReaderThread(QThread):
    signal = pyqtSignal(int)

    def __init__(self, parent, dataStream):
        QThread.__init__(self)

        self.dataStream = dataStream
     
    def run(self): 
        while True:
            decodedStream = self.dataStream.readline().decode("utf-8").strip()
            
            #self.signal.emit(decodedStream)
            if decodedStream == '3':
                print(decodedStream)