from PyQt5.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QProgressBar, QWidget, QPushButton,\
    QMessageBox, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

import serial_comm as serial
import sys
import parameter as param
import numpy as np
from random import randint
import time
import db
import xls_prn
'''
To-do
1. Thread Flag
2. RANGE
3. STD
4. STD *2
'''


class Thread1(QThread):
    signal = pyqtSignal(float, float, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.par = parent
        self.par.flag = True
        self.vals = []

    def get_count(self):
        if self.par.phase < 4:
            self.par.phase += 1

    def run(self):
        self.get_count()
        self.vals = []
        ser = serial.Serial(param.com_port, self.bit_rate, timeout=1)
        for i in range(int(self.par.cycle.toPlainText())):
            if self.ser.readable():
            # if True:
                # res = randint(1, 10)
                res = int(ser.readline().decode(self.dec)[-3:]) / 10
                self.vals.append(res)
                self.par.label_probe.setText(f'  {self.par.phase}-{i+1}: {res}')
                # self.par.pgbar.setValue(i)
            ser.close()
        
        npval = np.array(self.vals)
        mean = round(np.mean(npval), 1)
        stddev = round(np.std(npval), 1)
        range_bool = ( npval.max() - npval.min() ) <= float(self.par.RANGE.toPlainText()) 
        std_bool = stddev <= float(self.par.STD.toPlainText())

        self.signal.emit(mean, stddev, range_bool and std_bool)

    def __del__(self):
        self.par.flag = False
        del self.vals


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.dec = param.dec
        self.bit_rate = param.bit_rate
        self.means = []
        self.serial = serial.Serial_COM(param.bit_rate, param.dec)

        self.w = 600
        self.h = 400
        self.margin = 30
        self.label_probe = None

        self.phase = 0
        self.is_passed = True
        self.flag = False
        self.DB = db.DB()
        self.PRN = xls_prn.Prn()


        self.initUI()

    def set_panel(self, mean, stddev, is_ok):
        self.res_panel[self.phase-1][0].setText(str(mean))
        self.res_panel[self.phase-1][1].setText(str(stddev))
        if is_ok:
            self.res_panel[self.phase-1][2].setText('OK')
        else:
            self.res_panel[self.phase-1][2].setText('NG')

        

    def start_probe(self):
        if self.flag:
            # QMessageBox.question(self, 'Message', f'[Error] 이미 실행중입니다.',
            #     QMessageBox.Yes, QMessageBox.NoButton)
            QMessageBox.question(self, 'Message', f'[Error] Alredy working.',
                QMessageBox.Yes, QMessageBox.NoButton)
            return
        if int(self.n_Axis.toPlainText()) > 4:
            QMessageBox.question(self, 'Message', f'[Error] n_Axis out of range (1~4)',
                QMessageBox.Yes, QMessageBox.NoButton)
            # QMessageBox.question(self, 'Message', f'[Error] 1~4 사이의 n_Axis 값을 입력하세요',
            #     QMessageBox.Yes, QMessageBox.NoButton)
            return
        if self.serial.toPlainText().strip() == '':
            # QMessageBox.question(self, 'Message', f'[Error] 시리얼 번호를 입력하세요.',
            #     QMessageBox.Yes, QMessageBox.NoButton)
            QMessageBox.question(self, 'Message', f'[Error] Missing serial number.',
                QMessageBox.Yes, QMessageBox.NoButton)
            return
        self.phase = 0
        self.x = Thread1(self)
        self.x.start()
        self.x.signal.connect(self.finished)

    def finished(self, mean, stddev, is_ok):
        QMessageBox.question(self, 'Message', f'Axis {self.phase}',
                QMessageBox.Yes, QMessageBox.NoButton)
        
        self.means.append(mean)
        self.is_passed = self.is_passed and is_ok

        if self.phase < int(self.n_Axis.toPlainText()):
            self.x.start()
            self.set_panel(mean, stddev, is_ok)
            
        else:
            serial = self.serial.toPlainText()
            oper = self.oper.currentText()
            RANGE = self.RANGE.toPlainText()
            STDDEV = self.STD.toPlainText()
            # self.DB.insert_result(serial, self.means, self.is_passed, oper, self)
            self.PRN.prn(self.code.currentText(), serial, self.means, RANGE, STDDEV)
            self.means = []

    def initOper(self):

        self.oper = QComboBox(self)
        self.oper.addItem('Oper1')
        self.oper.addItem('Oper2')

        self.code = QComboBox(self)
        self.code.addItem('Code1')
        self.code.addItem('Code2')

        self.serial = QTextEdit()
        self.serial.setFixedSize(int(self.w/2), 30)


        option_box = QVBoxLayout()
        option_box.addWidget(self.oper)
        option_box.addStretch(1)
        option_box.addWidget(self.code)
        option_box.addStretch(1)
        option_box.addWidget(self.serial)
        option_box.addStretch(1)
        
        tmp = QHBoxLayout()
        tmp.addLayout(option_box)

        vtmp = QVBoxLayout()

        self.RANGE = QTextEdit()
        self.RANGE.setText('4')
        self.RANGE.setFixedSize(70, 20)
        self.STD = QTextEdit()
        self.STD.setText('1')
        self.STD.setFixedSize(70, 20)

        self.cycle = QTextEdit()
        self.cycle.setText('100')
        self.cycle.setFixedSize(70, 20)
        self.n_Axis = QTextEdit()
        self.n_Axis.setText('4')
        self.n_Axis.setFixedSize(70, 20)

        btn_start = QPushButton('Start', self)
        btn_start.setFixedSize(int(self.w/2), int(self.h/3))
        btn_start.clicked.connect(self.start_probe)

        g_tmp = QGridLayout()
        g_tmp.addWidget(QLabel('RANGE'), 0,0)
        g_tmp.addWidget(self.RANGE, 0, 1)
        # g_tmp.addStretch(1)
        g_tmp.addWidget(QLabel('SIGMA'), 0,2)
        g_tmp.addWidget(self.STD, 0,3)

        g_tmp.addWidget(QLabel('n_Cycle'), 1,0)
        g_tmp.addWidget(self.cycle, 1,1)
        # g_tmp.addStretch(1)
        g_tmp.addWidget(QLabel('n_Axis'), 1,2)
        g_tmp.addWidget(self.n_Axis, 1,3)
        vtmp.addLayout(g_tmp)

        vtmp.addWidget(btn_start)
        tmp.addLayout(vtmp)        

        self.Frame.addLayout(tmp)

        # self.serial = Q

    def initSheet(self):
        grid = QGridLayout()
        grid.addWidget(QLabel('Axis'), 0,0)
        grid.addWidget(QLabel('Range'), 0,1)
        grid.addWidget(QLabel('Sigma'), 0,2)
        grid.addWidget(QLabel('Result'), 0,3)
        grid.addWidget(QLabel('Dir'), 0,4)
        grid.addWidget(QLabel('Y-'), 1,4)
        grid.addWidget(QLabel('X+'), 2,4)
        grid.addWidget(QLabel('Y+'), 3,4)
        grid.addWidget(QLabel('X-'), 4,4)

        grid.addWidget(QLabel('1'), 1,0)
        grid.addWidget(QLabel('2'), 2,0)
        grid.addWidget(QLabel('3'), 3,0)
        grid.addWidget(QLabel('4'), 4,0)
        grid.addWidget(QLabel('Mean'), 5,0)

        self.res_panel = []
        for row in range(1,4+1):
            tmp_arr = []
            for col in range(1,3+1):
                tmp_label = QLabel('.')
                tmp_arr.append(tmp_label)
                grid.addWidget(tmp_label, row, col)
            self.res_panel.append(tmp_arr)


        self.Frame.addLayout(grid)

    def initUI(self):
        self.setWindowTitle('Dahasys')
        self.setGeometry(30, 30, self.w, self.h)
        self.Frame = QVBoxLayout()

        self.initOper()
        self.label_probe = QLabel('  val', self)
        self.label_probe.setFont(QFont('Arial', 30))
        self.label_probe.setStyleSheet("background-color: #93E0C1;")

        # self.pgbar = QProgressBar(self)
        # self.pgbar.setFixedSize(self.w-self.margin, 30)
        self.Frame.addWidget(self.label_probe)
        # self.Frame.addWidget(self.pgbar)

        self.initSheet()

        self.status_bar = QLabel()
        self.status_bar.setStyleSheet("border: 1px solid black;")
        tmp = QHBoxLayout()
        tmp.addWidget(self.status_bar)
        self.Frame.addLayout(tmp)
        
        self.setLayout(self.Frame)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())