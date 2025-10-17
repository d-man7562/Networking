import socket
import os
import threading
import sys

HOST = '0.0.0.0'
if len(sys.argv) < 3:
    print("Usage: python httpserver.py <PORT> <DIRECTORY>")
    sys.exit(1)

PORT = int(sys.argv[1])
BASE_DIR = sys.argv[2]

if not os.path.isdir(BASE_DIR):
    print(f"Error: Directory '{BASE_DIR}' does not exist.")
    sys.exit(1)

print(f"Serving files from: {os.path.abspath(BASE_DIR)}")


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
    file_path = os.path.join(BASE_DIR, path.lstrip('/'))

    try:
        with open(file_path, 'rb') as f:
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
