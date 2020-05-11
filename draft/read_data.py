import wfdb

record = wfdb.rdheader("/home/lanling/github/ECG-Platform//MIT-BIH/mit-bih-database/103")
print(record.comments)