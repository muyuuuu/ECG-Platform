import wfdb

record = wfdb.rdheader("/home/lanling/github/ECG-Platform//MIT-BIH/mit-bih-database/203")
print(record.comments)