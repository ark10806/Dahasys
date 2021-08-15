import openpyxl
import os
import parameter as param

class Prn:
    def __init__(self, hi):
        self.xls_path = param.xls_path
        self.wr_path = param.wr_path
        self.hi = hi

    def prn(self, code: str, serial: int, cycle: int, Axis: list, mean: float, RANGE: float, is_passed: bool, oper: str):
        try:
            wb = openpyxl.load_workbook(self.xls_path)
            sheet = wb.active
            img = openpyxl.drawing.image.Image(param.img_path)
            # img.resize((int(img.size[0]/2), int(img.size[1]/2)))
            sheet.add_image(img, 'A1')


            sheet['E4'] = str(code)
            sheet['H4'] = str(serial)
            sheet['A7'] = f'Cycle sequence: X+ X- Z+ Z- touch direction repeated {cycle}times'
            sheet['A9'] = f'R({cycle})={RANGE}Micron'
            sheet['A10'] = f'R({cycle})={RANGE}Micron'
            length_vac = 4 - len(Axis)
            for i in range(length_vac):
                Axis.append(' ')
            
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
        
        except:
            self.hi.show_msg(f'엑셀 파일을 닫고 다시 시도해 주세요.')




if __name__ == '__main__':
    prn = Prn()
    prn.prn(code='a', serial=123, cycle=100, Axis=[1,2,3,4], mean=3, RANGE=4, is_passed=True, oper="ML LEE")