import serial
import serial.tools.list_ports
import socket
from threading import Thread
import struct
import queue
import time
import datetime
import os
import csv

data_csv_queue = queue.Queue()

class CsvWriter:
    def __init__(self):
        DATA_SIZE = 5
        self.data_structure = [
            {'name': 'time', 'index': 1 + DATA_SIZE*0, 'format': 'f'},  # 'i' represents 4-byte signed integer
            {'name': 'encoder 1 angle', 'index': 1 + DATA_SIZE*1, 'format': 'f'},  # 'f' represents 4-byte float
            {'name': 'encoder 2 angle ', 'index': 1 + DATA_SIZE*2, 'format': 'f'},  # 'H' represents 2-byte unsigned short
            {'name': 'phase a current', 'index': 1 + DATA_SIZE*3, 'format': 'f'},
            {'name': 'phase b current', 'index': 1 + DATA_SIZE*4, 'format': 'f'},
            {'name': 'phase c current', 'index': 1 + DATA_SIZE*5, 'format': 'f'},
            {'name': 'imu 1 temperature', 'index': 1 + DATA_SIZE*6, 'format': 'f'},
            {'name': 'imu 2 acc x', 'index': 1 + DATA_SIZE*7, 'format': 'f'},
            {'name': 'imu 2 acc y', 'index': 1 + DATA_SIZE*8, 'format': 'f'},
            {'name': 'imu 2 acc z', 'index': 1 + DATA_SIZE*9, 'format': 'f'},
            {'name': 'imu gy x', 'index': 1 + DATA_SIZE * 10, 'format': 'f'},
            {'name': 'imu gy y', 'index': 1 + DATA_SIZE * 11, 'format': 'f'},
            {'name': 'imu gy z', 'index': 1 + DATA_SIZE * 12, 'format': 'f'},
            {'name': 'imu1 q1', 'index': 1 + DATA_SIZE * 13, 'format': 'f'},
            {'name': 'imu1 q2', 'index': 1 + DATA_SIZE * 14, 'format': 'f'},
            {'name': 'imu1 q3', 'index': 1 + DATA_SIZE * 15, 'format': 'f'},
            {'name': 'imu1 q4', 'index': 1 + DATA_SIZE * 16, 'format': 'f'},
            {'name': 'cmd 1', 'index': 1 + DATA_SIZE * 17, 'format': 'f'},
            {'name': 'cmd 2', 'index': 1 + DATA_SIZE * 18, 'format': 'f'},
            {'name': 'imu1 gy bias x', 'index': 1 + DATA_SIZE * 19, 'format': 'f'},
            {'name': 'imu1 gy bias y', 'index': 1 + DATA_SIZE * 20, 'format': 'f'},
            {'name': 'imu1 gy bias z', 'index': 1 + DATA_SIZE * 21, 'format': 'f'},
            {'name': 'imu2 q1', 'index': 1 + DATA_SIZE * 22, 'format': 'f'},
            {'name': 'imu2 q2', 'index': 1 + DATA_SIZE * 23, 'format': 'f'},
            {'name': 'imu2 q3', 'index': 1 + DATA_SIZE * 24, 'format': 'f'},
            {'name': 'imu2 q4', 'index': 1 + DATA_SIZE * 25, 'format': 'f'},
            {'name': 'imu2 gy bias x', 'index': 1 + DATA_SIZE * 26, 'format': 'f'},
            {'name': 'imu2 gy bias y', 'index': 1 + DATA_SIZE * 27, 'format': 'f'},
            {'name': 'imu2 gy bias z', 'index': 1 + DATA_SIZE * 28, 'format': 'f'},
            {'name': 'imu2 gy x', 'index': 1 + DATA_SIZE * 29, 'format': 'f'},
            {'name': 'imu2 gy y', 'index': 1 + DATA_SIZE * 30, 'format': 'f'},
            {'name': 'imu2 gy z', 'index': 1 + DATA_SIZE * 31, 'format': 'f'},
            {'name': 'ref q1', 'index': 1 + DATA_SIZE * 32, 'format': 'f'},
            {'name': 'ref q2', 'index': 1 + DATA_SIZE * 33, 'format': 'f'},
            {'name': 'ref q3', 'index': 1 + DATA_SIZE * 34, 'format': 'f'},
            {'name': 'ref q4', 'index': 1 + DATA_SIZE * 35, 'format': 'f'},
            {'name': 'qe1', 'index': 1 + DATA_SIZE * 36, 'format': 'f'},
            {'name': 'qe2', 'index': 1 + DATA_SIZE * 37, 'format': 'f'},
            {'name': 'qe3', 'index': 1 + DATA_SIZE * 38, 'format': 'f'},
            {'name': 'qe4', 'index': 1 + DATA_SIZE * 39, 'format': 'f'},
            {'name': 'ref euler 1', 'index': 1 + DATA_SIZE * 40, 'format': 'f'},
            {'name': 'ref euler 2', 'index': 1 + DATA_SIZE * 41, 'format': 'f'},
            {'name': 'motor power 1', 'index': 1 + DATA_SIZE * 42, 'format': 'f'},
            {'name': 'motor power 1', 'index': 1 + DATA_SIZE * 43, 'format': 'f'},
            {'name': 'Kp', 'index': 1 + DATA_SIZE * 44, 'format': 'f'},
            {'name': 'Ki', 'index': 1 + DATA_SIZE * 45, 'format': 'f'},
            {'name': 'Kd', 'index': 1 + DATA_SIZE * 46, 'format': 'f'},
            {'name': 'p term', 'index': 1 + DATA_SIZE * 47, 'format': 'f'},
            {'name': 'i term', 'index': 1 + DATA_SIZE * 48, 'format': 'f'},
            {'name': 'd term', 'index': 1 + DATA_SIZE * 49, 'format': 'f'},
            {'name': 'error', 'index': 1 + DATA_SIZE * 50, 'format': 'f'},
            {'name': 'debug', 'index': 1 + DATA_SIZE * 51, 'format': 'f'},
            {'name': 'fft index1', 'index': 1 + DATA_SIZE * 52, 'format': 'H'},
            {'name': 'fft index2', 'index': 3 + DATA_SIZE * 52, 'format': 'H'},
            {'name': 'debug2', 'index': 1 + DATA_SIZE * 53, 'format': 'f'},
            {'name': 'start_flag', 'index': 1 + DATA_SIZE * 54, 'format': 'B'},
            {'name': 'excite axis', 'index': 2 + DATA_SIZE * 54, 'format': 'B'},
            {'name': 'sys id input', 'index': 1 + DATA_SIZE * 55, 'format': 'f'},
            {'name': 'sys id output', 'index': 1 + DATA_SIZE * 56, 'format': 'f'},
            {'name': 'sys id control output', 'index': 1 + DATA_SIZE * 57, 'format': 'f'},
            {'name': 'excite frequency', 'index': 1 + DATA_SIZE * 58, 'format': 'f'},
            {'name': 'gy x avg', 'index': 1 + DATA_SIZE * 59, 'format': 'f'},
            {'name': 'gy y avg', 'index': 1 + DATA_SIZE * 60, 'format': 'f'},
            {'name': 'gy z avg', 'index': 1 + DATA_SIZE * 61, 'format': 'f'},
            # Add more fields as needed
        ]
        pass

    def parse_bytearray(self, array):
        parsed_data = {}
        for field in self.data_structure:
            data_bytes = array[field['index']:field['index'] + struct.calcsize(field['format'])]
            parsed_data[field['name']] = struct.unpack(field['format'], data_bytes)[0]

        return parsed_data

    def save_csv(self):
        now = datetime.datetime.now()
        filename = now.strftime('%Y-%m-%d_%H-%M-%S.csv')

        foldername = 'uart_log'

        # Create the folder if it doesn't exist
        if not os.path.exists(foldername):
            os.makedirs(foldername)

        filepath = os.path.join(foldername, filename)

        with open(filepath, 'a', newline='') as csvfile:
            # Create a CSV writer object
            csvwriter = csv.DictWriter(csvfile, fieldnames=[field['name'] for field in self.data_structure])
            csvwriter.writeheader()
            pass

            while True:
                data = data_csv_queue.get()
                parsed_data = self.parse_bytearray(data)
                csvwriter.writerow(parsed_data)

                pass

class GimbalUartParser(CsvWriter):
    def __init__(self):
        self.ser = None
        self.buf = bytearray()
        self.buffer = bytearray()
        super().__init__()

    # ref : https://github.com/pyserial/pyserial/issues/216
    def readline_new(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i + 1]
            self.buf = self.buf[i + 1:]
            return r
        while True:
            i = max(1, min(2048, self.ser.in_waiting))
            data = self.ser.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i + 1]
                self.buf[0:] = data[i + 1:]
                return r
            else:
                self.buf.extend(data)

    def send_float_array_udp(self, float_array):
        MESSAGE = float_array
        UDP_IP = "127.0.0.1"
        UDP_PORT = 5005
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        # print(float_array)

    def send_uart_sine_sweep(self):
        print("start excite")
        frequency = 0.5
        while frequency < 13.5:

            data = bytearray(struct.pack('<f', frequency))
            data.insert(0, 4)
            data.insert(0, 0xfe)
            data.insert(6, 0xff)
            self.ser.write(data)
            print(frequency)
            time.sleep((1.0/frequency)*5+1)
            frequency = frequency + 0.5


        frequency = 0.0

        data = bytearray(struct.pack('<f', frequency))
        data.insert(0, 4)
        data.insert(0, 0xfe)
        data.insert(6, 0xff)
        self.ser.write(data)
        print("end excite")
        pass

    def send_uart_step_input(self):
        data = bytearray()
        data.insert(0, 5)
        data.insert(0, 0xfe)
        data.insert(6, 0xff)
        print("step")
        pass

    def wait_for_input_send_uart(self):
        while 1:
            msg = input("command: ")

            try:
                val = float(msg[1:])
                data = bytearray(struct.pack('<f', val))
                if msg[0] == 'p':
                    data.insert(0, 1)
                elif msg[0] == 'i':
                    data.insert(0, 2)
                elif msg[0] == 'd':
                    data.insert(0, 3)
                else:
                    return
                data.insert(0, 0xfe)
                data.insert(6, 0xff)
                self.ser.write(data)

            except: #because converting to float fails
                if msg[0] == 'e':
                    self.send_uart_sine_sweep()
                elif msg[0] == 's':
                    self.send_uart_step_input()
                pass

        pass
    def read_serial_data(self):
        # data = self.ser.readline()
        data = self.readline_new()
        return data

    def search_com_ports(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(port.device)

        self.ser = serial.Serial(ports[-1].device, 921600, stopbits=serial.STOPBITS_TWO, parity= serial.PARITY_NONE)
        self.ser.flushInput()

    def read_serial_and_udp_send(self):
        while 1:
            data = self.read_serial_data()
            if len(data) == 300:
                self.send_float_array_udp(data)
                # print(data)
            else:
                # print("missed")
                pass
            self.ser.flushInput()

    def read_serial_by_byte(self):
        downsample = 0
        while 1:
            self.buffer += self.ser.read(self.ser.in_waiting)
            # if b'\n' in self.buffer:
            while b'\xc0\xc0' in self.buffer:
                temp = self.buffer.split(b'\xc0\xc0')
                self.buffer = temp[-1]
                temp = temp[0:-1]
                for data in temp:
                    # if len(data) == 298:
                    if len(data) == 348:
                        downsample = downsample + 1
                        if downsample % 10 == 0:
                            self.send_float_array_udp(b'\xc0\xc0'+data)
                        data_csv_queue.put(data)
                        # print(self.ser.in_waiting)
                        pass
                    else:
                        # print('missed')
                        pass
                pass

    def run(self):
        self.search_com_ports()
        # uartRx = Thread(target=self.read_serial_and_udp_send)
        uartRx = Thread(target=self.read_serial_by_byte)
        uartRx.start()

        csvSave = Thread(target=self.save_csv)
        csvSave.start()

        uartTx = Thread(target=self.wait_for_input_send_uart)
        uartTx.start()

        while True:
            # self.save_csv()
            # self.wait_for_input_send_uart()
            pass


if __name__ == '__main__':
    s = GimbalUartParser()
    s.run()




