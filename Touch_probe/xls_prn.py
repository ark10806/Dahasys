import openpyxl
import os
import parameter as param

class Prn:
    def __init__(self):
        self.xls_path = param.xls_path

    def prn(self, code: str, serial: int, Axis: list, RANGE: float, STDDEV: float):
        wb = openpyxl.load_workbook(self.xls_path)
        sheet = wb.active

        sheet['A1'] = str(code)
        sheet['A2'] = str(serial)
        sheet['A3'] = str(Axis[0])
        sheet['A4'] = str(Axis[1])
        sheet['A5'] = str(Axis[2])
        sheet['A6'] = str(Axis[3])

        wb.save(self.xls_path)

        os.startfile(self.xls_path, 'print')


if __name__ == '__main__':
    prn = Prn()
    prn.prn(code='a', serial=123, Axis=[1,2,3,4], RANGE=1, STDDEV=2)