from os import getcwd

base = getcwd().replace('\\', '/') + '/'
xls_path = base + 'src/form.xlsx'
wr_path = base + 'src/new.xlsx'
img_path = base + 'src/logo.png'

bit_rate = 9600
dec = 'utf8'
com_port = 'COM1'