import serial
import parameter as param
import numpy as np

class Serial_COM:
    def __init__(self, bit_rate, dec):
        self.dec = dec
        self.bit_rate = bit_rate
        self.val = []
        # self.ser = serial.Serial(param.com_port, bit_rate, timeout=1)
        # self.ser = serial.Serial(param.com_port, bit_rate, timeout=1)

    def get_mean_std(self, cycle, label):
        ser = serial.Serial(param.com_port, self.bit_rate, timeout=1)
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
        ser.close()

        return mean, std_dev