import wfdb
 
# 读取本地的100号记录，从0到25000，通道0
record = wfdb.rdann('/home/lanling/github/ECG-Platform/MIT-BIH/mit-bih-database/105', "atr", sampfrom=0, sampto=20000)
# 统计次数
for index in record.symbol:
    print(index)

# 如何读取性别和年龄 ?
# record = wfdb.rdheader('/home/lanling/github/ECG-Platform/MIT-BIH/mit-bih-database/103')
# print(record.__dict__)