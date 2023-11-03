from usb_main import CsvWriter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from collections import deque
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class GimbalPlot(CsvWriter):
    def __init__(self):
        deque_size = 200
        self.t_data = deque(maxlen=deque_size)
        self.parsed_data = None
        self.subplot_list = []  # List of dictionaries to hold line and data parameters
        self.figure, self.axes = plt.subplots(4, 1)  # Create a 4x1 grid of subplots
        plt.subplots_adjust(left=0.1, right=0.9, hspace=1.0)  # Adjust the spacing as needed

        titles = ['Subplot 1', 'Subplot 2', 'Subplot 3', 'Subplot 4']

        data_struct_1 = [
            {'data': deque(maxlen=deque_size), 'name': 'cam rate x', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate y', 'color': 'blue', 'twinx': True},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate z', 'color': 'black', 'twinx': False},
        ]

        data_struct_2 = [
            {'data': deque(maxlen=deque_size), 'name': 'cam rate x', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate y', 'color': 'blue', 'twinx': True},
        ]

        data_struct_3 = [
            {'data': deque(maxlen=deque_size), 'name': 'cam rate x', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate y', 'color': 'blue', 'twinx': True},
        ]

        data_struct_4 = [
            {'data': deque(maxlen=deque_size), 'name': 'cam rate x', 'color': 'red', 'twinx': False},
            {'data': deque(maxlen=deque_size), 'name': 'cam rate y', 'color': 'blue', 'twinx': True},
        ]

        data_list = [data_struct_1, data_struct_2, data_struct_3, data_struct_4]
        for i, ax in enumerate(self.axes.flat):
            ax.set_title(titles[i])
            line, = ax.plot([], [])
            self.subplot_list.append({'ax': ax, 'data': data_list[i]})

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        super().__init__()

    def fill_each_subplot(self, subplot):
        ax = subplot['ax']
        data_struct = subplot['data']
        legend_name = []

        for d in data_struct:
            line = d.get('line', None)  # Check if a line already exists for this data
            if line is None:
                line, = ax.plot([], [], label=d['name'], color=d['color'])  # Create a new line if it doesn't exist
                d['line'] = line

            d['data'].append(self.parsed_data[d['name']])
            line.set_data(self.t_data, d['data'])
            legend_name.append(d['name'])

        # ax.legend(loc='upper right')
        ax.relim()
        ax.autoscale()
        # t = self.t_data[-1]
        # if t > ax.get_xlim()[1]:
        #     ax.set_xlim(t - 10, t)

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
                plt.draw()  # Draw the updated plot
                plt.pause(0.001)

if __name__ == '__main__':
    s = GimbalPlot()
    s.plot_real_time()