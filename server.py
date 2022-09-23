"""
 Implements a basic HTTP/1.0 Server from scratch

"""

import sys
from contextlib import contextmanager
from threading import Thread
from socket import socket, \
    AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

# Socket default params
DEFAULT_SERVER_HOST = 'localhost'
DEFAULT_SERVER_PORT = 3000
DEFAULT_SERVER_DIR = 'docs'

"""
Returns host, port and dir based on input arguments. If not provided, returns
default ones.
"""


def get_prog_args():
    argv_length = len(sys.argv)
    if argv_length < 2:
        return DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT, DEFAULT_SERVER_DIR
    if argv_length < 3:
        return sys.argv[1], DEFAULT_SERVER_PORT, DEFAULT_SERVER_DIR
    if argv_length < 4:
        return sys.argv[1], sys.argv[2], DEFAULT_SERVER_DIR
    return sys.argv[1], sys.argv[2], sys.argv[3]


"""
Returns a socket instance, with provided params.
"""


def create_socket(host: str, port: str):
    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sckt.bind((host, int(port)))
    sckt.listen(1)
    print(f'Socket listening on port {port} ...')
    return sckt


"""
Context manager for opening and closing a server socket.
"""


@contextmanager
def open_socket(host: str, port: str):
    sckt = create_socket(host, port)
    try:
        yield sckt
    finally:
        sckt.close()


"""
Returns content from a given file and a status (404 if file not found or
something else).
"""


def get_file_content(dir, filename):
    if filename == '/':
        filename = '/index.html'
    try:
        fin = open(dir + filename)
        content = fin.read()
        fin.close()
        status = 200
    except FileNotFoundError:
        fin = open('docs/not-found.html')
        content = fin.read()
        fin.close()
        status = 404

    return content, status


def get_client_request(conn: socket):
    return conn.recv(1024).decode()


def send_http_response(conn: socket, res: str):
    return conn.sendall(res.encode())


"""
Main flow to process a client request, and return response, given a socket 
connection.
"""


def process_request(conn: socket, addr):
    try:
        request = get_client_request(conn)
        print(request)

        headers = request.split('\n')
        filename = headers[0].split()[1]
        content, status = get_file_content(server_dir, filename)

        if status == 200:
            response = 'HTTP/1.0 200 OK\r\n\r\n' + content
        elif status == 404:
            response = 'HTTP/1.0 404 Not Found\r\n\r\n' + content
        else:
            response = 'HTTP/1.0 400 Bad Request\r\n\r\n'
    except:
        response = 'HTTP/1.0 400 Bad Request\r\n\r\n'
    finally:
        send_http_response(conn, response)
        conn.close()


if __name__ == '__main__':
    server_host, server_port, server_dir = get_prog_args()
    with open_socket(server_host, server_port) as server_socket:
        try:
            while True:
                # Wait for client connections
                client_connection, client_address = server_socket.accept()
                # Send it to a new thread to process
                t = Thread(target=process_request,
                           args=(client_connection, client_address))
                t.start()
        except KeyboardInterrupt:
            print('\nTerminating...')
