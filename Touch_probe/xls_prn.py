import openpyxl
import os
import parameter as param

class Prn:
    def __init__(self):
        self.xls_path = param.xls_path
        self.wr_path = param.wr_path

    def prn(self, code: str, serial: int, cycle: int, Axis: list, mean: float, RANGE: float, is_passed: bool, oper: str):
        wb = openpyxl.load_workbook(self.xls_path)
        sheet = wb.active

        sheet['E4'] = str(code)
        sheet['H4'] = str(serial)
        sheet['A7'] = f'Cycle sequence: X+ X- Z+ Z- touch direction repeated {cycle}times'
        sheet['A9'] = f'R({cycle})={RANGE}Micron'
        sheet['A10'] = f'R({cycle})={RANGE}Micron'
        sheet['C9'] = Axis[0]
        sheet['E9'] = Axis[1]
        sheet['G9'] = Axis[2]
        sheet['I9'] = Axis[3]
        sheet['C10'] = mean
        if is_passed:
            sheet['D13'] = 'TEST OK'
        else:
            sheet['D13'] = 'TEST NG'
        sheet['H13'] = f'operator: {oper}'

        wb.save(self.wr_path)

        os.startfile(self.wr_path, 'print')


if __name__ == '__main__':
    prn = Prn()
    prn.prn(code='a', serial=123, cycle=100, Axis=[1,2,3,4], mean=3, RANGE=4, is_passed=True, oper="ML LEE")