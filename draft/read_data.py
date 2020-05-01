import wfdb
import matplotlib.pyplot as plt
 
# 读取本地的100号记录，从0到25000，通道0
record = wfdb.rdrecord('MIT-BIH/105', sampfrom=0, sampto=25000, physical=False, channels=[0, ])

ventricular_signal = record.d_signal[:1000].reshape(1000)
# ventricular_signal = ventricular_signal[:,1]
print(ventricular_signal.shape)