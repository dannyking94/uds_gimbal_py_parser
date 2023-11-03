import serial
import serial.tools.list_ports
import struct
import datetime
import os
import csv

class GimbalUartParser:
    def __init__(self):
        self.ser = None
        self.cnt = list()
        self.input = list()
        self.output = list()

    def search_com_ports(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(port.device)

        self.ser = serial.Serial(ports[-1].device, 57600, stopbits=serial.STOPBITS_TWO, parity= serial.PARITY_NONE)
        self.ser.flushInput()

    def read_serial(self):
        data = self.ser.read(size=16001)

        # Search for correct reading
        # readline cannot be read because newline is 10 and it confuses with cnt at 10.
        while data[-1] != 0xff:
            self.ser.flushInput()
            data = self.ser.read(size=16001)

        # Parse Data array
        i = 0
        while i < len(data)-10:
            count_byte = data[i:i+2]
            count = struct.unpack('<H', count_byte)[0]
            input_byte = data[i+2:i+6]
            input = struct.unpack('<f', input_byte)[0]
            output_byte = data[i+6:i+10]
            output = struct.unpack('<f', output_byte)[0]
            # output = output*3.14159/180 #deg/s to rad/s
            i = i+10

            self.cnt.append(count)
            self.input.append(input)
            self.output.append(output)

        self.save_as_csv()

    def save_as_csv(self):
        now = datetime.datetime.now()
        filename = now.strftime('%Y-%m-%d_%H-%M-%S.csv')

        foldername = 'sysid_data'

        # Create the folder if it doesn't exist
        if not os.path.exists(foldername):
            os.makedirs(foldername)

        filepath = os.path.join(foldername, filename)

        with open(filepath, 'w', newline='') as csvfile:
            # Create a CSV writer object
            writer = csv.writer(csvfile)

            writer.writerow(['count', 'input', 'output'])
            # Write each float in the list as a separate row
            for i in range(len(self.input)):
                writer.writerow([self.cnt[i], self.input[i], self.output[i]])

        pass

    def run(self):
        self.search_com_ports()
        self.ser.write(0xaa)
        self.read_serial()



if __name__ == '__main__':
    s = GimbalUartParser()
    s.run()


