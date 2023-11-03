import socket
import time



def send_float_array_udp(float_array):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    MESSAGE = float_array

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while(1):
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        time.sleep(1)


if __name__ == '__main__':
    array = list()
    array.append(123)
    data = bytes.fromhex('c0c0fff6d4e2c3ff00fcffc6ff00fcffc6000000000000000000000000000000ff42c58e41aa000060bbbb0000483cff00f0813fff93352b3fff9041f9beff9041f9bdff3c1b7d3fff5abdbdbbffdba3773affbe908bbe0000000000000000000000000a')
    # data = bytes.fromhex('C0C0FFFF')
    send_float_array_udp(data)