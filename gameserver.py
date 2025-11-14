import socket
import threading
import json
import random as rand
import time
import numpy as np
player = "&"
clock = 0
game_name = input("Enter game name:")
def leaderboard(clients,conn):
     with lock:
                # Build leaderboard: "username: score" per line
                    lines = [f"200 PLAYER {username}: {info['score']} {info['pos']}" for username, info in clients.items()]
                       
                    leaderboard = "\n".join(lines)

                    
                    conn.sendall((leaderboard + "\n").encode())
def timeclock():
    global clock
    while True:
        with lock:
            clock += 1  
            info_msg["201 INFO"]["clock"] = clock
            info_msg["201 INFO"]["num_players"] = len(clients)
        time.sleep(1)


def heartbeat(conn,us):
    try:
        data = conn.recv(1024)
        if not data:
            print(f"{us} disconnected")
            with lock:
                # old_x = clients[us]["pos"][0]
                # old_y = clients[us]["pos"][1]
                # map[old_y][old_x] = '.'
                del clients[us]
        
    except ConnectionResetError:
        print(f"{us} disconnected")
        with lock:
            # old_x = clients[us]["pos"][0]
            # old_y = clients[us]["pos"][1]
            # map[old_y][old_x] = '.'
            del clients[us]
            


def MAPU(map,x,y):
    message_lines = []
    for row_index, row in enumerate(map):
            # Convert row list to string
        row_str = ''.join(row)
        # Add extra info (row number) in front
        message_lines.append(f"203 MAP {row_index:02d}: {row_str}")
    message = '\n'.join(message_lines)
    broadcast("\n204 MAPU\n" + message + "\n")
    return None
map = ["................................................................................",
       "................................................................................",
        "................................................................................",
        "..................#....#...######..#.......#..#.....#..######..#....#..#######..",
        "..................#....#...#.......#.......#..##...##..#.......#....#.....#.....",
        "..................######...#####...#.......#..#.#.#.#..#####...######.....#.....",
        "..................#....#...#.......#.......#..#..#..#..#.......#....#.....#.....",
        "..................#....#...######..######..#..#.....#..######..#....#.....#.....",
        "................................................................................",
        "................................................................................",
        "................................................................................"]
map = [list(row) for row in map]
w = len(map[0])
h = len(map)
HOST = '0.0.0.0'
PORT = 8880
clients = {}
info_msg = {"201 INFO": { "game_name": game_name, "w" : w, "h" : h, "clock" : clock, "num_players": len(clients)}}
lock = threading.Lock()
def info(conn):
    global info_msg
    info_str = json.dumps(info_msg)

    conn.send((info_str + "\n").encode())
    return None
"""DICT: {username: conn, pos, score }

"""
def broadcast(message):
    """Send a message to all connected clients."""
    with lock:  # prevent concurrent modification
        for client_info in clients.values():  # iterate over each user's info dict
            try:
                client_socket = client_info["conn"]  # extract socket
                client_socket.sendall(f"{message}\n".encode())
          
            except Exception as e:
                print(f"400 Error sending to client: {e}")



def handle_client(conn,addr):
    us = None
    flag = False
    conn.sendall(f"206 Login with Username\n".encode())
    while True:
        username = conn.recv(1024).decode().split()
        if len(username) == 0:
            continue
        if username[0].lower() == "get":
            response = (
                    "HTTP/1.0 403 Forbidden\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: 67\r\n" 
                    "\r\n"
                    "This is not a webserver. Connection closed by foreign host.\n"
                )
            conn.sendall(response.encode())
            conn.close()
            break
        if username[0].lower() == "login":
                if len(username) == 1:
                    continue
                if username[1] in clients:
                    conn.sendall(f"500 Username Taken\n".encode())
                else:
                    us = username[1]
                    while True:
                        x,y = rand.randint(0, w-1), rand.randint(0, h-1)
                        if map[y][x] == "#": continue
                        break
                    clients[us] = {
                        "conn": conn,  # store the socket
                        "pos": [x,y],  # random legal position
                        "score": 0  # score
                        }  
                    # map[y][x] = player
                    MAPU(map,x,y)
                    broadcast(f"207 {us} logged in!\n")
                    flag = True
                    leaderboard(clients,conn)
                    break
        else:
            conn.sendall("401 Not logged in\n".encode())
            continue

    while flag:
        data= conn.recv(1024).decode().split()
        if not data:   continue    # True if data is empty
        match(data[0].upper()):
            case "MAP": 
                message_lines = []
                for row_index, row in enumerate(map):
                    row_str = ''.join(row)
                    message_lines.append(f"212 MAP {row_index:02d}: {row_str}")
                message = '\n'.join(message_lines)
                conn.sendall((message + "\n").encode())
            # case "INFO": conn.sendall(f"200 INFO <{game_name}>, <{w}>,<{h}>, <{clock}>, <{len(clients)}>".encode())
            case "INFO": info(clients[us]["conn"])
            case "PING": conn.sendall("PONG".encode())
            case "LEADERBOARD":
               leaderboard(clients,conn)
            case "MOVE":
                    if not data:   continue    # True if data is empty
                    
                    try:
                        x = int(data[1])
                        y = int(data[2])
                    except (IndexError, ValueError):
                        conn.sendall("402 Invalid MOVE request\n".encode())
                        continue
                    old_x = clients[us]["pos"][0]
                    old_y = clients[us]["pos"][1]
                    new_x = clients[us]["pos"][0] + x
                    new_y = clients[us]["pos"][1] + y
                    if new_x < 0 or new_x > w-1:
                        conn.sendall(f"403 Out of bounds\n".encode())
                        continue

                    if new_y < 0 or new_y > h-1:
                        conn.sendall(f"404 Out of bounds\n".encode())
                        continue

                    if map[new_y][new_x] == '#':
                        conn.sendall(f"405 Can't move onto this tile\n".encode())
                        continue
                    clients[us]["pos"][0] = new_x
                    clients[us]["pos"][1] = new_y
                    # map[old_y][old_x] = '.'
                    # map[new_y][new_x] = player
                    broadcast(f"208 MOVE {us} ({x,y})\n")
                    # MAPU(map,new_x,new_y)
    
            case "CHAT": 
                if len(data) > 1:
                    if len(data) > 2: 
                        if data[1] in clients:
                            new_us = data[1]
                            start_msg = f"210 PM {us}: "
                            message = ' '.join(data[2:])
                            clients[new_us]["conn"].sendall(f"{start_msg} {message}\n".encode())
                            clients[us]["conn"].sendall(f"{start_msg} {message}\n".encode())

                            continue
                    
                    message = ' '.join(data[1:])
                    message.join("\n")
                    broadcast(f"209 M {us.upper()}: {message}")
                    continue
                continue
            case "QUIT": 
                # old_x = clients[us]["pos"][0]
                # old_y = clients[us]["pos"][1]
                # map[old_y][old_x] = '.'
                del clients[us]
                conn.close()
                break
            case "GET":
                response = (
                    "HTTP/1.0 403 Forbidden\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: 67\r\n" 
                    "\r\n"
                    "This is not a webserver. Connection closed by foreign host.\n"
                )
                conn.sendall(response.encode())
                conn.close()
                break

            case default: conn.sendall(f"406 {data[0]} unreachable request\n".encode())


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server started on {HOST}:{PORT}")

    threading.Thread(target=timeclock,args=(),daemon=True).start()
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
if __name__ == "__main__":
    start_server()



