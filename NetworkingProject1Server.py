import socket
import random
min = 1
max = 100
random_number = random.randint(min,max)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', 1236))
s.listen(5)

def wait_for_connection():
    while True:
        conn, addr = s.accept()
        conn.send(f'Hello from server! {str(random_number)}'.encode('utf-8'))
        break
    return conn, addr
conn, addr = wait_for_connection()
def response_for_guess(line):
    try:
        number = int(line)
    except ValueError:
        conn.send("invalid".encode('utf-8'))
        return True
    if not (1<= number<=100):
        conn.send(("invalid").encode('utf-8'))
        return True
    if number == random_number:
        return False
    if number <random_number:
        conn.send(("higher").encode('utf-8'))
        return True

    elif number > random_number:
        conn.send(("lower").encode('utf-8'))
        return True

buffer = b''
print("Connection Successful!")
while True:
    data = conn.recv(2048)
    buffer +=data
    while b'\n' in buffer:
        line, buffer = buffer.split(b'\n', 1)
        print(f"Received: {line}")
    line = data.decode('utf-8')
    print(f"received {line}")
    response = response_for_guess(line)

    if response == False:
        conn.send("Congrats, you guessed the correct number!".encode("utf-8"))
        random_number = random.randint(min,max)
        conn,addr = wait_for_connection()
        continue
    if response  == True:
        continue



