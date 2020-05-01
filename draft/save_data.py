import pandas as pd
import wfdb
import matplotlib.pyplot as plt

# 读取本地的100号记录，从0到25000，通道0
record = wfdb.rdrecord('MIT-BIH/105', sampfrom=0, sampto=1000, physical=False)

data = record.d_signal
# record.d_signal.shape
channels = data.shape[1]
columns = ["channel_" + str(i) for i in range(channels)]

df = pd.DataFrame(data, columns=columns)
df.to_csv("test.csv")