import socket
import os
import threading

HOST = '0.0.0.0'
PORT = 8000

MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.jpeg': 'image/jpeg'
}

def get_content_type(filename):
    ext = os.path.splitext(filename)[1].lower()
    return MIME_TYPES.get(ext, 'application/octet-stream')

def serve_file(path):
    
    if path == '/':
        path = '/index.html'
    try:
        with open(path.lstrip('/'), 'rb') as f:
            content = f.read()
            content_type = get_content_type(path)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(content)}\r\n"
                f"\r\n"
            ).encode() + content
    except FileNotFoundError:
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 13\r\n"
            "\r\n"
            "404 Not Found"
        ).encode()
    return response

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        request = conn.recv(1024).decode()
        print("Request:\n", request)

        try:
            path = request.split(' ')[1]
        except IndexError:
            conn.close()
            return

        response = serve_file(path)
        conn.sendall(response)
    finally:
        conn.close()

# Set up socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print(f"Serving HTTP on {HOST}:{PORT}...")

while True:
    conn, addr = s.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.daemon = True  # So threads don't prevent program exit
    thread.start()
