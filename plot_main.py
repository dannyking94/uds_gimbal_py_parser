from usb_main import CsvWriter
import matplotlib.pyplot as plt
from collections import deque
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005


class GimbalPlot(CsvWriter):
    def __init__(self):
        super().__init__()
        deque_size = 200
        self.t_data = deque(maxlen=deque_size)
        self.parsed_data = None
        self.subplot_list = []  # List of dictionaries to hold line and data parameters
        self.figure, self.axes = plt.subplots(4, 1, sharex=True)
        plt.subplots_adjust(left=0.1, right=0.9, hspace=1.0)

        titles = ['Euler', 'Pitch PID', 'Roll PID', 'Subplot 4']

        data_struct_1 = [
            {'data': deque(maxlen=deque_size), 'name': 'pitch', 'color': 'red', 'twinx': False, 'scale': 180/3.14},
            {'data': deque(maxlen=deque_size), 'name': 'roll', 'color': 'blue', 'twinx': True, 'scale': 180/3.14},
        ]

        data_struct_2 = [
            {'data': deque(maxlen=deque_size), 'name': 'pitch p', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'pitch d', 'color': 'blue', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'pitch i', 'color': 'black', 'twinx': True},
        ]

        data_struct_3 = [
            {'data': deque(maxlen=deque_size), 'name': 'roll p', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'roll d', 'color': 'blue', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'roll i', 'color': 'black', 'twinx': True},
        ]

        data_struct_4 = [
            {'data': deque(maxlen=deque_size), 'name': 'cam rate x', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate y', 'color': 'blue', 'twinx': False},
        ]

        data_list = [data_struct_1, data_struct_2, data_struct_3, data_struct_4]
        for i, ax in enumerate(self.axes.flat):
            ax.set_title(titles[i])
            self.subplot_list.append({'ax': ax, 'data': data_list[i]})

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))

    def fill_each_subplot(self, subplot):
        ax = subplot['ax']
        data_struct = subplot['data']

        for d in data_struct:
            line = d.get('line', None)
            if line is None:
                if d['twinx']:
                    ax2 = ax.twinx()
                    line = ax2.plot([], [], label=d['name'], color=d['color'])[0]
                else:
                    line, = ax.plot([], [], label=d['name'], color=d['color'])
                d['line'] = line

            scale = d.get('scale', None)
            if scale is None:
                scale = 1
                d['scale'] = 1

            d['data'].append(self.parsed_data[d['name']]*d['scale'])
            line.set_data(self.t_data, d['data'])
            if d['twinx']:
                ax2 = line.axes
                ax2.relim()
                ax2.autoscale()

        ax.relim()
        ax.autoscale()

    def plot_real_time(self):
        downSample = 0
        while True:
            data, addr = self.sock.recvfrom(1024)
            if data[1] == 0:  # 0 for real-time log
                self.parsed_data = self.parse_bytearray(data)

            t = self.parsed_data['time']

            self.t_data.append(t)

            for subplot in self.subplot_list:
                self.fill_each_subplot(subplot)

            downSample = downSample + 1
            if downSample % 6 == 0:
                plt.draw()
                plt.pause(0.001)

if __name__ == '__main__':
    s = GimbalPlot()
    s.plot_real_time()