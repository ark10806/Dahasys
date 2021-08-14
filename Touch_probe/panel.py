from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import serial_comm as serial
import sys
import parameter as param

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cycle = 100
        self.serial = serial.Serial_COM(param.bit_rate, param.dec)
        self.w = 1000
        self.h = 800
        self.margin = 30


        self.initUI()

    def start_probe(self):
        res = self.serial.get_mean_std(self.cycle)
        print(res)

    def initUI(self):
        self.setWindowTitle('Dahasys')
        self.setGeometry(30, 30, self.w, self.h)
        
        btn_start = QPushButton('Start', self)
        btn_start.setGeometry(self.margin, self.margin, 100, 100)
        btn_exit = QPushButton('Exit', self)
        btn_exit.setGeometry(self.w - 130, self.margin, 100, 100)
        
        #btn_start.clicked.connect(self.start_probe())
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())