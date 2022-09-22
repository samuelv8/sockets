import sys
from contextlib import contextmanager
from socket import socket, AF_INET, SOCK_STREAM
from urllib import response

"""
Returns a socket instance, with provided params.
"""


def create_socket(host: str, port: str):
    sckt = socket(AF_INET, SOCK_STREAM)
    sckt.connect((host, port))
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


if __name__ == '__main__':
    urls = []
    content = ''
    urls = get_prog_args()
    for url in urls:
        try:
            server_host, server_port = parse_url(url)
        except:
            print('Invalid URL: ', url)
            continue
        with open_socket(server_host, server_port) as client_socket:
            try:
                # send the user's line over the TCP connection
                client_socket.send(bytes(content, "utf-8"))
                res = client_socket.recv(1024).decode()
                status, body = parse_response(res)
                if status == 'ok':
                    save_file(res)
                else:
                    print(status)


            except KeyboardInterrupt:
                print('\nTerminating...')
                break
            except Exception as e:
                print(e)
                continue
