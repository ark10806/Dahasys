from PyQt5.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QProgressBar, QWidget, QPushButton,\
    QMessageBox, QVBoxLayout, QHBoxLayout, QTextEdit
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont

# import serial_comm as serial
import serial
import sys
import parameter as param
import numpy as np
from random import randint
import time
import db
import xls_prn
'''
To-do
1. Oper, Code 사용자화
2. Oper, Code, Serial Label
3. Database
'''


class Thread1(QThread):
    signal = pyqtSignal(float, float, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.par = parent
        self.vals = []
        self.dec = param.dec

    def get_count(self):
        if self.par.phase < 4:
            self.par.phase += 1

    def run(self):
        self.vals = []
        ser = None
        res = None
        raw = None
        try:
            ser = serial.Serial(param.com_port, param.bit_rate, timeout=1)
        except:
            self.par.status_bar.setText('Serial open failed')
            return
        
        self.get_count()
        n_cycle = int(self.par.cycle.toPlainText())
        i = 0
        while i < n_cycle:
        # for i in range(int(self.par.cycle.toPlainText())):
            try:
                if ser.readable():
                # if True:
                    raw = (ser.readline().decode(self.dec))[-4:]
                    print(raw)
                    # print(f'raw: {raw}, raw[:-3]: {raw[:-3]}, raw[:-3].isdigit(): {raw[:-3].isdigit()}')
                    if raw.strip().isdigit():
                        res = int(raw) / 10
                        self.vals.append(res)
                        self.par.label_probe.setText(f'  {self.par.phase}-{i+1}: {res}')
                        i += 1
                    else:
                        self.par.status_bar.setText(f'[{self.par.phase}-{i}]: Serial read failed')
                    # self.par.pgbar.setValue(i)
            except Exception as e:
                print(e)
                self.par.status_bar.setText(f'[{self.par.phase}-{i}]: Serial read failed')
        ser.close()
        
        npval = np.array(self.vals)
        mean = round(npval.max() - npval.min(), 2)
        stddev = round(np.std(npval), 1) * 2
        range_bool = ( npval.max() - npval.min() ) <= float(self.par.RANGE.toPlainText()) 
        std_bool = stddev <= float(self.par.STD.toPlainText())

        self.signal.emit(mean, stddev, range_bool and std_bool)

    def __del__(self):
        del self.vals


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.dec = param.dec
        self.bit_rate = param.bit_rate
        self.Axises = []
        # self.serial = serial.(param.bit_rate, param.dec)

        self.w = 600
        self.h = 400
        self.margin = 30
        self.label_probe = None

        self.phase = 0
        self.is_passed = True
        self.flag = False
        self.DB = db.DB(self)
        self.PRN = xls_prn.Prn(self)


        self.initUI()
        self.get_preset()

    def get_preset(self):
        ops, cds = self.DB.get_preset()
        for op in ops:
            self.oper.addItem(op)
        
        for cd in cds:
            self.code.addItem(cd)


    def set_panel(self, mean:float, stddev:float, is_ok:bool):
        self.res_panel[self.phase-1][0].setText(str(mean))
        self.res_panel[self.phase-1][1].setText(str(stddev))
        if is_ok:
            self.res_panel[self.phase-1][2].setText('OK')
        else:
            self.res_panel[self.phase-1][2].setText('NG')

        

    def start_probe(self):
        self.Axises = []
        magic = self.serial.toPlainText()
        if magic.find("!!") != -1:
            magic = magic.split("!!")
            if magic[0] == 'operator':
                self.DB.append_oper(magic[1])
            if magic[0] == 'code':
                self.DB.append_code(magic[1])
            self.show_msg('추가되었습니다. 프로그램을 재실행해주세요.')
            return
        if not self.DB.is_unique(magic):
            self.show_msg('중복된 시리얼 넘버입니다.')
            return
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

        for i in range(len(self.res_panel)):
            for j in range(len(self.res_panel[0])):
                self.res_panel[i][j].setText(',')
        self.phase = 0
        self.x = Thread1(self)
        self.x.start()
        self.flag = True
        self.x.signal.connect(self.finished)

    def show_msg(self, msg):
        QMessageBox.question(self, 'Message', msg,
                QMessageBox.Yes, QMessageBox.NoButton)

    def finished(self, mean, stddev, is_ok):
        self.set_panel(mean, stddev, is_ok)
        # QMessageBox.question(self, 'Message', f'Axis {self.phase}',
        #         QMessageBox.Yes, QMessageBox.NoButton)
        # if is_ok:
        #     QMessageBox.question(self, 'Message', f'Axis {self.phase}',
        #             QMessageBox.Yes, QMessageBox.NoButton)
        reply = QMessageBox.question(self, 'Message', f'Axis {self.phase}. retry?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.x.start()
            self.phase -= 1
            # self.set_panel('-', '-', False)

        else:
            self.Axises.append(mean)
            self.is_passed = self.is_passed and is_ok

            if self.phase < int(self.n_Axis.toPlainText()):
                self.x.start()
                
            else:
                self.res_panel[4][0].setText(str(round(np.mean(self.Axises), 3)))
                self.flag = False


    def handle_results(self):
        serial = self.serial.toPlainText()
        print(f'self.DB.is_unique(serial): {self.DB.is_unique(serial)}')
        print(f'len(self.Axises): {len(self.Axises)}')
        print(f'int(self.n_Axis.toPlainText()): {int(self.n_Axis.toPlainText())}')
        print(self.DB.is_unique(serial) and (len(self.Axises)==int(self.n_Axis.toPlainText())))
        if (self.DB.is_unique(serial) and (len(self.Axises)==int(self.n_Axis.toPlainText()))):
            print('Im in')
            # print(f'self.DB.is_unique(serial): {self.DB.is_unique(serial)}')
            # print(f'len(self.Axises): {len(self.Axises)}')
            # print(f'int(self.n_Axis.toPlainText()): {int(self.n_Axis.toPlainText())}')
            oper = self.oper.currentText()
            code = self.code.currentText()
            RANGE = self.RANGE.toPlainText()
            STDDEV = self.STD.toPlainText()
            self.DB.insert_result(serial, self.Axises, self.is_passed, oper, code, RANGE)
            self.PRN.prn(code, serial, self.cycle.toPlainText(), self.Axises, round(np.mean(self.Axises), 3),  RANGE, self.is_passed, oper)
        
        elif self.code.currentText() == 'PRINT':
        # elif not self.DB.is_unique(serial):
            vals = self.DB.get_past(serial)
            # self.PRN.prn()
            if vals:
                is_passed = bool(vals[5])
                axises = []
                for i in range(4):
                    axises.append(float(vals[i+1]))
                mean = np.mean(axises)
                self.PRN.prn(code=vals[8], serial=vals[0], cycle=vals[1], Axis=axises, mean=mean, RANGE=vals[9], is_passed=is_passed, oper=vals[7])
        
        else: 
            self.show_msg(f'[Error] 입력하신 serial {serial}은 유효하지 않은 값입니다..')
            self.status_bar.setText('serial 값을 존재하거나 중복되지 않는 값으로 조정 후 print 버튼을 누르면 결과를 출력합니다.')

    def initOper(self):

        self.oper = QComboBox(self)
        # self.oper.addItem('Oper1')
        # self.oper.addItem('Oper2')

        self.code = QComboBox(self)
        # self.code.addItem('Code1')
        # self.code.addItem('Code2')

        self.serial = QTextEdit()
        self.serial.setFixedSize(int(self.w/2), 30)


        option_box = QGridLayout()
        option_box.addWidget(QLabel('operator'), 0,0)
        option_box.addWidget(self.oper, 0,1)
        option_box.addWidget(QLabel('code'), 1,0)
        option_box.addWidget(self.code, 1,1)
        option_box.addWidget(QLabel('serial'), 2,0)
        option_box.addWidget(self.serial, 2,1)
        
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
        btn_start.setFixedSize(int(self.w/2), int(self.h/5))
        btn_start.clicked.connect(self.start_probe)

        g_tmp = QGridLayout()
        g_tmp.addWidget(QLabel('RANGE'), 0,0)
        g_tmp.addWidget(self.RANGE, 0, 1)
        # g_tmp.addStretch(1)
        g_tmp.addWidget(QLabel('2 SIGMA'), 0,2)
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
        for row in range(1,5+1):
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
        htmp = QHBoxLayout()
        self.label_probe = QLabel('  val', self)
        self.label_probe.setFixedSize(int(self.w/2), 35)
        self.label_probe.setFont(QFont('Arial', 30))
        self.label_probe.setStyleSheet("background-color: #93E0C1;")
        htmp.addStretch(3)
        htmp.addWidget(self.label_probe)
        htmp.addStretch(1)

        self.prnBtn = QPushButton('print', self)
        self.prnBtn.setFixedSize(int(self.w/2), int(self.h/5))
        self.prnBtn.clicked.connect(self.handle_results)
        htmp.addWidget(self.prnBtn)
        self.Frame.addLayout(htmp)
        # self.pgbar.setFixedSize(self.w-self.margin, 30)
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