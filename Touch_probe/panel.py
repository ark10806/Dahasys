from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import serial_comm as serial
import sys
import parameter as param

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cycle = 100
        self.serial = serial.Serial_COM(param.bit_rate, param.dec)
        self.initUI()

    def start_probe(self):
        res = self.serial.get_mean_std(self.cycle)
        print(res)

    def initUI(self):
        self.setWindowTitle('Dahasys')
        self.setGeometry(30, 30, 1000, 800)
        
        btn_start = QPushButton('Start', self)
        btn_exit = QPushButton('Exit', self)
        
        btn_start.clicked.connect(self.start_probe())
        
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())