"""
 Implements a basic HTTP/1.0 Client from scratch

"""
import sys
import re
import traceback
from contextlib import contextmanager
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM

DEBUG = False

"""
Return a URL list from args
"""


def get_prog_args() -> list:
    argv_length = len(sys.argv)
    urls = [sys.argv[i] for i in range(1, argv_length)]
    return urls


"""
Returns the URL hostname and port
"""


def parse_url(url: str) -> tuple:
    if type(url) != str:
        raise TypeError("Argument is not a string")
    m = re.search(
        r'(?:https?://)?((?:\w+\.)?\w+(?:\.\w{2,4})?(?:\.\w{2,4})?)(:\d+)?(/[\w\-\._]*)',
        url
    )
    if m is None:
        raise TypeError("Invalid URL")
    hostname = m.group(1)
    port = int(m.group(2)[1:]) if m.group(2) else 80
    filepath = m.group(3)
    return hostname, port, filepath


"""
Returns a socket instance, with provided params.
"""


def create_socket(hostname: str, port: str):
    sckt = socket(AF_INET, SOCK_STREAM)
    host = gethostbyname(hostname)
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


"""
Builds a basic request header with given params
"""


def build_request_header(hostname: str, port: int, filepath: str):
    header = ''
    header += f'GET {filepath} HTTP/1.0\r\n'
    header += f'Host: {hostname}:{port}\r\n'
    header += 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0\r\n'
    header += 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n'
    header += '\r\n'
    return header


"""
Parses a HTTP response returning relevant content for project purposes
"""


def parse_response(res: str) -> tuple:
    parts = res.split('\r\n\r\n')
    header = parts[0]
    body = parts[1]
    first = header.split('\n', 1)[0]
    status = first.split()
    status_code = int(status[1])
    status_phrase = ' '.join(status[2:])
    ok = status_code < 400
    return ok, status_code, status_phrase, body


"""
Writes content string to a file with given filename
"""


def save_file(filename: str, content: str):
    with open(filename, 'w') as file:
        file.write(content)


if __name__ == '__main__':
    urls = get_prog_args()
    for url in urls:
        try:
            hostname, port, filepath = parse_url(url)
        except Exception as e:
            if DEBUG:
                print(traceback.format_exc())
            else:
                print('Invalid URL ', url)
                print(e)
            continue
        with open_socket(hostname, port) as client_socket:
            try:
                # Build and send request via TCP to server
                req = build_request_header(hostname, port, filepath)
                client_socket.send(bytes(req, "utf-8"))

                # Wait for response
                res = client_socket.recv(1024).decode()

                ok, status, phrase, body = parse_response(res)
                if ok:
                    # Save response body for sucessfull request
                    filename = filepath[1:] if filepath != '/' else 'index.html'
                    save_file(filename, res)
                else:
                    print(status, phrase)

            except KeyboardInterrupt:
                print('\nTerminating...')
                break
            except Exception as e:
                if DEBUG:
                    print(traceback.format_exc())
                else:
                    print('The following error occurred while processing request for ', url)
                    print(e)
                continue
