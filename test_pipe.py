import subprocess

passwd = input("Enter password: ")

s = subprocess.Popen(["python", "test_input.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
s.stdout.readline()
s.stdin.write(f"{passwd}\n".encode())
s.stdout.readline()
