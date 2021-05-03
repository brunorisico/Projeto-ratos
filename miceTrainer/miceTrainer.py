"""
creation date: 1-4-2021 6:00
last modified: 12-04-2021 10:15

@author: Bruno Correia - brunorisico@gmail.com

Parent program window - QMainWindow
Other components (Widgets) are initiated here

"""

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QIcon
 
from Widgets.StartWidget import StartWidget
from Widgets.ControlPanelWidget import ControlPanelWidget

# from modules.widget import StroopTestWidget
# mport ast


class Mice(QMainWindow):
    """Main window of the program
    """
    def __init__(self):
        super().__init__()

        self.control_panel_widget = ControlPanelWidget(self)

        self.setCentralWidget(StartWidget(self))
        self.set_status_bar_message("")

    def set_status_bar_message(self, message):
        self.statusBar().showMessage(message)

    def set_to_control_panel(self, timer, trials, serial_connection):
        self.setCentralWidget(self.control_panel_widget)
        self.control_panel_widget.setTimerTrialConnection(timer, trials, serial_connection)


    # def closeEvent(self, event):
    #     msgBox = QMessageBox()
    #     msgBox.setWindowTitle("Quit the program")
    #     msgBox.setText("Are you sure?")
    #     msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #     msgBox.setDefaultButton(QMessageBox.Yes)
    #     if msgBox.exec_() == QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setStyle('Fusion')

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    main_window = Mice()
    #main_window.showMaximized()
    main_window.setMinimumSize(400, 200)
    main_window.setWindowIcon(QIcon('rat_icon.png')) # "Icon made by Pixel perfect from www.flaticon.com"
    main_window.setWindowTitle("Rat Trainer")
    main_window.show()

    sys.exit(app.exec_())
