import time
import getpass
# time.sleep(2)
s = getpass.getpass("Enter your password:")

with open("s.txt", "w") as f:
	f.write(s)