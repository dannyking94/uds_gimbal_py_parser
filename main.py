import serial
import serial.tools.list_ports
import socket
from threading import Thread


class GimbalUartParser:
    def __init__(self):
        self.ser = None

    def send_float_array_udp(self, float_array):
        MESSAGE = float_array
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        # print(float_array)

    def read_udp(self):
        # Receive data
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.2', 9991))
        sock.setblocking(True)
        while(1):
            try:
                data, addr = sock.recvfrom(512)
                self.ser.write(data)
                print(data)
            except socket.error:
                # print("error")
                pass

    def read_serial_data(self):
        data = self.ser.readline()
        return data

    def search_com_ports(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(port.device)

        self.ser = serial.Serial(ports[-1].device, 57600, stopbits=serial.STOPBITS_TWO, parity= serial.PARITY_NONE)
        self.ser.flushInput()

    def read_serial_and_udp_send(self):
        data = self.read_serial_data()
        if len(data) == 300:
            self.send_float_array_udp(data)
            # print(data)
        self.ser.flushInput()

    def run(self):
        self.search_com_ports()
        udpRx = Thread(target=self.read_udp)
        udpRx.start()
        while True:
            self.read_serial_and_udp_send()
            pass


if __name__ == '__main__':
    s = GimbalUartParser()
    s.run()


