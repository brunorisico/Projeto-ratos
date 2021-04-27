from PyQt5.QtCore import Qt, QThread, pyqtSignal

from openpyxl import Workbook
from datetime import datetime

class SerialThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, parent, arduino_connection):
        QThread.__init__(self)


        self.spreadsheet = Workbook()
        self.pre_trial_sheet = self.spreadsheet.create_sheet("Pre-trial")
        
        headers = ["Code", "Timestamp", "Delta start timestamp"]
        self.pre_trial_sheet.append(headers)
        
        self.start_signal = False
        self.arduino_started_timestamp = 0

        self.arduino_connection = arduino_connection
        self.buffer = ''
        self.expected_strings = ['HL_ON','HL_OFF', 
                                 'LL_ON', 'LL_OFF', 
                                 'RL_ON', 'RL_OFF',
                                 'PR', 'OR', 'TR', 'SR',
                                 'ITIS', 'DS', 'MO',
                                 'FSA', 'FSR', 'FSF', 'LSA',
                                 'LSR', 'RSA', 'RSR', 
                                 'SA', 'TO', 'RTS', 'FTS', 'TE']

        self.trial = 1

    def run(self):
        while True:
            if self.start_signal:
                while self.arduino_connection.readline().decode("utf-8").strip() != "SA":
                    print('Trying to start Arduino')
                    self.arduino_connection.write(bytes("start", 'utf-8'))
                    self.start_signal = False
                
                self.arduino_started_timestamp = datetime.now()
                self.write_to_spreadsheet(0, "SA", self.arduino_started_timestamp)
                self.signal.emit("SA")
            else:
                decodedStream = self.arduino_connection.readline().decode("utf-8").strip()
                if decodedStream != '':
                    # need to create a buffer to avoid getting just partial strings
                    self.buffer = self.buffer + decodedStream

                    if self.buffer in self.expected_strings:
                        print(self.buffer)
                        #self.signal.emit(self.buffer)
                        self.buffer = ""

    def start_trial(self):
        self.start_signal = True

    def write_to_spreadsheet(self, sheet_number, code, timestamp):
        print(self.spreadsheet.sheetnames)

        #working_sheet = self.spreadsheet.get_sheet_by_name([])
        

        #working_sheet.append([code, timestamp, timestamp - self.arduino_started_timestamp])

        #self.spreadsheet.save(filename="olalalal.xlsx")