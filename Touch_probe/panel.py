from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
import serial_comm as serial
import sys
import parameter as param
import numpy as np

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.dec = param.dec
        self.bit_rate = param.bit_rate
        self.val = []
        self.cycle = 100
        self.serial = serial.Serial_COM(param.bit_rate, param.dec)

        self.w = 1000
        self.h = 800
        self.margin = 30
        self.label_probe = None


        self.initUI()

    def start_probe(self):
        ser = serial.Serial(param.com_port, self.bit_rate, timeout=1)
        for i in range(self.cycle):
            if self.ser.readable():
                res = int(ser.readline().decode(self.dec)[-3:]) / 10
                self.vals.append(res)
                self.label_probe.setText(f'{i+1} {res}')
                if(param.VIS): print(f'{i}: {self.vals[-1]}')
        ser.close()


    def initUI(self):
        self.setWindowTitle('Dahasys')
        self.setGeometry(30, 30, self.w, self.h)
        
        btn_start = QPushButton('Start', self)
        btn_start.setGeometry(self.margin, self.margin, 100, 100)

        self.label_probe = QLabel('value', self)

        btn_exit = QPushButton('Exit', self)
        btn_exit.setGeometry(self.w - 130, self.margin, 100, 100)

        
        
        btn_start.clicked.connect(self.start_probe)
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())