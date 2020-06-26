import datetime

file_name = str(datetime.datetime.now()) + ".png"

file_name = file_name.replace(" ", "-")
file_name = file_name.replace(".", "-")
file_name = file_name.replace(":", "-")

# file_name = file_name 

print(file_name)