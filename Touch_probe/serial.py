import serial
import parameter as param
import numpy as np

class Serial:
    def __init__(self, bit_rate, dec):
        self.dec = dec
        self.ser = serial.Serial(param.com_port, bit_rate, timeout=1)

    def get_mean_std(self, cycle):
        vals = []
        mean = 0
        std_dev = 0

        for i in range(cycle):
            if self.ser.readable():
                vals.append(int(self.ser.readline().decode(self.dec)[-3:]) / 10)
                if(param.VIS): print(f'{i}: {vals[-1]}')
        self.ser.close()

        mean = np.mean(vals)
        std_dev = np.std(vals)

        del vals

        return mean, std_dev