from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import serial

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cycle = 100

    def start_probe(self):
        res = serial.get_mean_std(self.cycle)
        print(res)

    def initUI(self):
        self.setWindowTitle('Dahasys')
        self.setGeometry(30, 30, 1000, 800)
        
        btn_start = QPushButton('Start', self)
        btn_exit = QPushButton('Exit', self)
        
        btn_start.clicked.connect(self.start_probe())
        