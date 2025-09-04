import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost',1236))
def send_guess():
    guess = (input("Enter a number between 1 and 100: ... "))
    return guess + '\n'

while True:
    data = s.recv(2048)
    line = data.decode('utf-8')
    print(line)
    if line == "Congrats, you guessed the correct number!":
        break
    guess = send_guess()
    s.send(str(guess).encode('utf-8'))
    

s.close()