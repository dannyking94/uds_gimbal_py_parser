import serial
import serial.tools.list_ports
import socket
from threading import Thread, Event
import struct
import queue
import time
import datetime
import os
import csv
import curses
from curses import wrapper
import traceback
from math import pi

data_csv_queue = queue.Queue() #used for csv write
data_ui_queue = queue.Queue()

class CsvWriter:
    def __init__(self):
        DATA_SIZE = 5
        self.data_structure = [
            {'name': 'message type', 'format': 'B', 'c_var_name': 'g_log.message_type'},
            {'name': 'time', 'format': 'f', 'c_var_name': 'g_log_time'},
            {'name': 'cam imu ready', 'format': 'B', 'c_var_name': 'g_imu.camera.gyro_ready'},
            {'name': 'cam bias error', 'format': 'f', 'c_var_name': 'g_imu.camera.gyro_bias_error'},
            {'name': 'cam imu err', 'format': 'f', 'c_var_name': 'g_imu.camera.fusion_error'},
            {'name': 'beta', 'format': 'f', 'c_var_name': 'g_imu.camera.madgwick_beta'},
            {'name': 'kf gy bias x', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_gy_bias[0]'},
            {'name': 'kf gy bias y', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_gy_bias[1]'},
            {'name': 'kf gy bias z', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_gy_bias[2]'},
            {'name': 'kf bias px', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_bias_P[0]'},
            {'name': 'kf bias py', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_bias_P[1]'},
            {'name': 'kf bias pz', 'format': 'f', 'c_var_name': 'g_imu.camera.kf_bias_P[2]'},
            {'name': 'pitch', 'format': 'f', 'c_var_name': 'g_imu.camera.euler[0]'},
            {'name': 'roll', 'format': 'f', 'c_var_name': 'g_imu.camera.euler[1]'},
            {'name': 'cam rate x', 'format': 'f', 'c_var_name': 'g_imu.camera.gy[0]'},
            {'name': 'cam rate y', 'format': 'f', 'c_var_name': 'g_imu.camera.gy[1]'},
            {'name': 'cam rate z', 'format': 'f', 'c_var_name': 'g_imu.camera.gy[2]'},
            {'name': 'cam acc x', 'format': 'f', 'c_var_name': 'g_imu.camera.acc[0]'},
            {'name': 'cam acc y', 'format': 'f', 'c_var_name': 'g_imu.camera.acc[1]'},
            {'name': 'cam acc z', 'format': 'f', 'c_var_name': 'g_imu.camera.acc[2]'},
            {'name': 'b imu ready', 'format': 'B', 'c_var_name': 'g_imu.board.gyro_ready'},
            {'name': 'b bias error', 'format': 'f', 'c_var_name': 'g_imu.board.gyro_bias_error'},
            {'name': 'b imu err', 'format': 'f', 'c_var_name': 'g_imu.board.fusion_error'},
            {'name': 'b pitch', 'format': 'f', 'c_var_name': 'g_imu.board.euler[0]'},
            {'name': 'b roll', 'format': 'f', 'c_var_name': 'g_imu.board.euler[1]'},
            {'name': 'b acc x', 'format': 'f', 'c_var_name': 'g_imu.board.acc[0]'},
            {'name': 'b acc y', 'format': 'f', 'c_var_name': 'g_imu.board.acc[1]'},
            {'name': 'b acc z', 'format': 'f', 'c_var_name': 'g_imu.board.acc[2]'},
            {'name': 'b rate x', 'format': 'f', 'c_var_name': 'g_imu.board.gy[0]'},
            {'name': 'b rate y', 'format': 'f', 'c_var_name': 'g_imu.board.gy[1]'},
            {'name': 'b rate z', 'format': 'f', 'c_var_name': 'g_imu.board.gy[2]'},
            {'name': 'b beta', 'format': 'f', 'c_var_name': 'g_imu.board.madgwick_beta'},
            {'name': 'b gy bias x', 'format': 'f', 'c_var_name': 'g_gy_bias_var[3].bias'},
            {'name': 'b gy bias y', 'format': 'f', 'c_var_name': 'g_gy_bias_var[4].bias'},
            {'name': 'b gy bias z', 'format': 'f', 'c_var_name': 'g_gy_bias_var[5].bias'},
            {'name': 'b kf gy bias x', 'format': 'f', 'c_var_name': 'g_imu.board.kf_gy_bias[0]'},
            {'name': 'b kf gy bias y', 'format': 'f', 'c_var_name': 'g_imu.board.kf_gy_bias[1]'},
            {'name': 'b kf gy bias z', 'format': 'f', 'c_var_name': 'g_imu.board.kf_gy_bias[2]'},
            {'name': 'b kf bias px', 'format': 'f', 'c_var_name': 'g_imu.board.kf_bias_P[0]'},
            {'name': 'b kf bias py', 'format': 'f', 'c_var_name': 'g_imu.board.kf_bias_P[1]'},
            {'name': 'b kf bias pz', 'format': 'f', 'c_var_name': 'g_imu.board.kf_bias_P[2]'},
            {'name': 'pitch error', 'format': 'f', 'c_var_name': 'g_pid_var[PITCH].error'},
            {'name': 'pitch p', 'format': 'f', 'c_var_name': 'g_pid_var[PITCH].pidterm[0]'},
            {'name': 'pitch i', 'format': 'f', 'c_var_name': 'g_pid_var[PITCH].pidterm[1]'},
            {'name': 'pitch d', 'format': 'f', 'c_var_name': 'g_pid_var[PITCH].pidterm[2]'},
            {'name': 'pitch ref', 'format': 'f', 'c_var_name': 'g_pid_var[PITCH].ref'},
            {'name': 'pitch svpwm', 'format': 'd', 'c_var_name': 'drv_var[PITCH].svpwm_angle'},
            {'name': 'roll error', 'format': 'f', 'c_var_name': 'g_pid_var[ROLL].error'},
            {'name': 'roll p', 'format': 'f', 'c_var_name': 'g_pid_var[ROLL].pidterm[0]'},
            {'name': 'roll i', 'format': 'f', 'c_var_name': 'g_pid_var[ROLL].pidterm[1]'},
            {'name': 'roll d', 'format': 'f', 'c_var_name': 'g_pid_var[ROLL].pidterm[2]'},
            {'name': 'roll ref', 'format': 'f', 'c_var_name': 'g_pid_var[ROLL].ref'},
            {'name': 'roll svpwm', 'format': 'f', 'c_var_name': 'drv_var[ROLL].svpwm_angle'},
            {'name': 'sbgc count', 'format': 'H', 'c_var_name': 'g_sbgc_var.cycle_time'},
            {'name': 'sbgc euler 1', 'format': 'f', 'c_var_name': 'g_sbgc_var.euler[0]'},
            {'name': 'sbgc euler 2', 'format': 'f', 'c_var_name': 'g_sbgc_var.euler[1]'},
            {'name': 'sbgc euler 3', 'format': 'f', 'c_var_name': 'g_sbgc_var.euler[2]'},
            {'name': 'encoder', 'format': 'H', 'c_var_name': 'g_sbgc_var.encoder'},
        ]
        self.flash_structure = [
            {'name': 'dcm_type', 'format': 'B'},
            {'name': 'motor_on', 'format': 'B'},
            {'name': 'pitch reverse', 'format': 'B'},
            {'name': 'roll reverse', 'format': 'B'},
            {'name': 'fusion lv', 'format': 'B'},
            {'name': 'bias method', 'format': 'B'},
            {'name': 'reserved 6', 'format': 'B'},
            {'name': 'reserved 7', 'format': 'B'},
            {'name': 'dcmP', 'format': 'f'},
            {'name': 'dcmR', 'format': 'f'},
            {'name': 'dcmY', 'format': 'f'},
            {'name': 'd11', 'format': 'f'},
            {'name': 'd12', 'format': 'f'},
            {'name': 'd13', 'format': 'f'},
            {'name': 'd21', 'format': 'f'},
            {'name': 'd22', 'format': 'f'},
            {'name': 'd23', 'format': 'f'},
            {'name': 'd31', 'format': 'f'},
            {'name': 'd32', 'format': 'f'},
            {'name': 'd33', 'format': 'f'},
            {'name': 'pitch Kp', 'format': 'f'},
            {'name': 'pitch Ki', 'format': 'f'},
            {'name': 'pitch Kd', 'format': 'f'},
            {'name': 'roll Kp', 'format': 'f'},
            {'name': 'roll Ki', 'format': 'f'},
            {'name': 'roll Kd', 'format': 'f'},
            {'name': 'offset_p', 'format': 'f'},
            {'name': 'offset_r', 'format': 'f'},
            {'name': 'command', 'format': 'f'},
            {'name': 'bias x', 'format': 'f'},
            {'name': 'bias y', 'format': 'f'},
            {'name': 'bias z', 'format': 'f'},
        ]
        pass

    def parse_bytearray(self, array):
        parsed_data = {}
        start_index = 1
        for field in self.data_structure:
            if array[start_index-1] != 0xff:
                raise ValueError("Parsing error. Check Data type of " +"!!!!" + field['name'] +"!!!!!!!!!")
            data_bytes = array[start_index:start_index + struct.calcsize(field['format'])]
            parsed_data[field['name']] = struct.unpack(field['format'], data_bytes)[0]
            start_index += struct.calcsize(field['format']) + 1
        return parsed_data

    def parse_flash_bytearray(self, array):
        parsed_data = {}
        start_index = 2
        for field in self.flash_structure:
            data_bytes = array[start_index:start_index + struct.calcsize(field['format'])]
            parsed_data[field['name']] = struct.unpack(field['format'], data_bytes)[0]
            start_index += struct.calcsize(field['format'])
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

            # while True:
            while not self.stop_flag.is_set():
                # following try-except is for stop_flag to work
                # without timeout the process is stuck at data_csv_queue.get() line and never checks stop_flag
                try:
                    data = data_csv_queue.get(timeout=1)
                    if data[1] == 0: #0 for real time log
                        parsed_data = self.parse_bytearray(data)
                        csvwriter.writerow(parsed_data)
                    else:
                        continue
                except:
                    traceback.print_exc()
                    pass


class GimbalUartParser(CsvWriter):
    def __init__(self):
        self.ser = None
        self.step_t = time.time()
        self.buf = bytearray()
        self.buffer = bytearray()
        self.stop_flag = Event()
        self.buf_size = 350
        self.step_on = 0
        self.command_list = [
            {'command': 'flash read', 'key': 0xf0, 'function': self.f_change_param},
            {'command': 'flash default', 'key': 0xf1, 'function': self.f_change_param},
            {'command': 'flash erase', 'key': 0xf2, 'function': self.f_change_param},
            {'command': 'pitch Kp', 'key': 0xa0, 'function': self.f_change_param},
            {'command': 'pitch Ki', 'key': 0xa1, 'function': self.f_change_param},
            {'command': 'pitch Kd', 'key': 0xa2, 'function': self.f_change_param},
            {'command': 'roll Kp', 'key': 0xa3, 'function': self.f_change_param},
            {'command': 'roll Ki', 'key': 0xa4, 'function': self.f_change_param},
            {'command': 'roll Kd', 'key': 0xa5, 'function': self.f_change_param},
            {'command': 'command', 'key': 0xa6, 'function': self.f_change_param},
            {'command': 'control', 'key': 0xa7, 'function': self.f_change_param},
            {'command': 'offset_p', 'key': 0xa8, 'function': self.f_change_param},
            {'command': 'offset_r', 'key': 0xa9, 'function': self.f_change_param},
            {'command': 'pitch dir', 'key': 0xaa, 'function': self.f_change_param},
            {'command': 'roll dir', 'key': 0xab, 'function': self.f_change_param},
            {'command': 'bias write', 'key': 0xac, 'function': self.f_change_param},
            {'command': 'bias method', 'key': 0xad, 'function': self.f_change_param},
            {'command': 'bias x', 'key': 0xc0, 'function': self.f_change_param},
            {'command': 'bias y', 'key': 0xc1, 'function': self.f_change_param},
            {'command': 'bias z', 'key': 0xc2, 'function': self.f_change_param},
            {'command': 'fusion lv', 'key': 0xae, 'function': self.f_change_param},
            {'command': 'dcm_type', 'key': 0xb0, 'function': self.f_change_param},
            {'command': 'd11', 'key': 0xb1, 'function': self.f_change_param},
            {'command': 'd12', 'key': 0xb2, 'function': self.f_change_param},
            {'command': 'd13', 'key': 0xb3, 'function': self.f_change_param},
            {'command': 'd21', 'key': 0xb4, 'function': self.f_change_param},
            {'command': 'd22', 'key': 0xb5, 'function': self.f_change_param},
            {'command': 'd23', 'key': 0xb6, 'function': self.f_change_param},
            {'command': 'd31', 'key': 0xb7, 'function': self.f_change_param},
            {'command': 'd32', 'key': 0xb8, 'function': self.f_change_param},
            {'command': 'd33', 'key': 0xb9, 'function': self.f_change_param},
            {'command': 'dcmP', 'key': 0xba, 'function': self.f_change_param},
            {'command': 'dcmR', 'key': 0xbb, 'function': self.f_change_param},
            {'command': 'dcmY', 'key': 0xbc, 'function': self.f_change_param},
            {'command': 'step pitch', 'key': 0xe0, 'function': self.f_change_param},
            {'command': 'step roll', 'key': 0xe1, 'function': self.f_change_param},
            {'command': 'sine pitch', 'key': 0xe2, 'function': self.f_change_param},
        ]
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

    def f_change_param(self, key, data):
        data.insert(0, key)
        data.insert(0, 0xfe)
        data.insert(6, 0xff)
        self.ser.write(data)
        pass

    def f_step(self):
        self.step_on = 1 - self.step_on
        pass

    def parse_input_command(self, msg):
        command = None
        output = []

        for command_dict in self.command_list:
            if command_dict['command'] in msg:
                command = command_dict['command']
                val = msg.replace(command, '', 1).strip().split()
                if len(val) == 1:
                    val = val[0]
                else:
                    val = 0
                break

        if command == None:
            return ['', '']

        output.append(command)
        output.append(val)

        return output

    def wait_for_input_send_uart(self):
        while 1:
            msg = input("command: ")

            split = self.parse_input_command(msg)

            # split = msg.split()
            for field in self.command_list:
                if field['command'] == split[0]:
                    function = field['function']
                    try:
                        data = bytearray(struct.pack('<f', float(split[1])))
                    except:
                        data = bytearray(struct.pack('<f', 0))
                    if function == self.f_change_param:
                        function(field['key'], data)
                    else:
                        function()
        pass

    def read_serial_data(self):
        # data = self.ser.readline()
        data = self.readline_new()
        return data

    def search_com_ports(self):
        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            print(port.device + " - " + port.description)
            if port.description[0:35] == 'STMicroelectronics Virtual COM Port':
                print("Connected to " + port.device)
                self.ser = serial.Serial(port.device, 128000, stopbits=serial.STOPBITS_TWO,
                                         parity=serial.PARITY_NONE)
                self.ser.flushInput()
                return 1
        print("Can not find device")
        exit()

    def read_serial_by_byte(self):
        downsample = 0
        # while 1:
        while not self.stop_flag.is_set():
            self.buffer += self.ser.read(self.ser.in_waiting)
            # if b'\n' in self.buffer:
            while b'\xc0\xc0' in self.buffer:
                temp = self.buffer.split(b'\xc0\xc0')
                self.buffer = temp[-1]
                temp = temp[0:-1]
                for data in temp:
                    if len(data) == self.buf_size-2:
                        downsample = downsample + 1
                        self.send_float_array_udp(data)
                        # if downsample % 1 == 0:
                        #     self.send_float_array_udp(data)
                            # self.send_float_array_udp(b'\xc0\xc0'+data)
                        data_csv_queue.put(data)
                        data_ui_queue.put(data)
                        if data[1] == 1:
                            self.parse_flash_bytearray(data)
                            pass
                        # print(self.ser.in_waiting)
                        pass
                    else:
                        # print('missed')
                        pass
                pass

    def stop(self):
        self.stop_flag.set()

    def step_loop(self):
        angle = 10*3.14159/180.0
        sign = -1
        while not self.stop_flag.is_set():
            if self.step_on:
                if (time.time() - self.step_t) > 1:
                    self.step_t = time.time()
                    sign = sign * -1
                    data = bytearray(struct.pack('<f', sign*angle))
                    data.insert(0, 0xe0) #e0 - pitch, e1 - roll
                    data.insert(0, 0xfe)
                    data.insert(6, 0xff)
                    self.ser.write(data)


    def run(self):
        self.search_com_ports()
        # uartRx = Thread(target=self.read_serial_and_udp_send)
        uartRx = Thread(target=self.read_serial_by_byte)
        uartRx.start()

        csvSave = Thread(target=self.save_csv)
        csvSave.start()

        step = Thread(target=self.step_loop)
        step.start()

        try:
            while True:
                self.wait_for_input_send_uart()
                pass
        except KeyboardInterrupt:
            print("Stop")
            self.stop()
            uartRx.join()
            csvSave.join()
        except:
            traceback.print_exc()
            self.stop()
            uartRx.join()
            csvSave.join()


class GimbalUI(GimbalUartParser):
    def __init__(self):
        super().__init__()
        self.ui_data = None
        self.flash_data = None
        #keys below for display only
        self.flash_data_keys = [
            'pitch Kp', 'pitch Ki', 'pitch Kd', 'roll Kp', 'roll Ki', 'roll Kd',
            'offset_p', 'offset_r', 'command', 'fusion lv', 'bias method',
            'bias x', 'bias y', 'bias z'
        ] #only float type works here
        self.rt_data_keys = [
            'time', 'cam imu ready', 'cam bias error', 'cam imu err', 'kf gy bias x', 'kf gy bias y', 'kf gy bias z',
            'kf bias px', 'kf bias py', 'kf bias pz',
            'pitch', 'roll', 'cam rate x', 'cam rate y', 'cam rate z', 'cam acc x', 'cam acc y', 'cam acc z',
            'pitch svpwm', 'pitch ref']
        self.sbgc_data_keys = ['sbgc count', 'sbgc euler 1', 'sbgc euler 2', 'sbgc euler 3', 'encoder']
        self.rt_data2_keys = [
            'b imu ready', 'b bias error', 'b pitch', 'b roll', 'b beta',
            'b kf gy bias x', 'b kf gy bias y', 'b kf gy bias z',
            'b kf bias px', 'b kf bias py', 'b kf bias pz'
        ]
        self.ui_command = ""

    def param_loop(self, win):
        win.clear()
        # self.ui_data['time']
        y_pos = 0
        for key in self.flash_data_keys:
            value = self.flash_data.get(key, 'N/A')
            if not isinstance(value, float):
                win.addstr(y_pos, 0, "{:10}: {}".format(key, value))
                # win.addstr(y_pos, 0, "!!Wrong key: {}".format(key))
                y_pos += 1
                continue
            win.addstr(y_pos, 0, "{:10}: {:.2f}".format(key, value))
            y_pos += 1

        #bias estimation


        #Control mode
        msg = self.motor_mode_parse(win)
        win.addstr(y_pos, 0, "control   : " + msg)
        y_pos += 1

        #Polarity
        msg = self.polarity_read(win, 'pitch reverse')
        win.addstr(y_pos, 0, "pitch dir : " + msg)
        y_pos += 1
        msg = self.polarity_read(win, 'roll reverse')
        win.addstr(y_pos, 0, "roll dir  : " + msg)
        y_pos += 1

        #dcm type
        self.dcm_mode_parse(win, y_pos)
        win.refresh()
        pass

    def bias_fusion_param(self, win, y_pos):
        key = 'fusion lv'
        val = self.flash_data.get(key, 'N/A')
        if val == 1:
            msg = "PITCH(1)"
        elif val == 2:
            msg = "ROLL(2)"
        elif motor_val == 3:
            msg = "BOTH(3)"
        elif motor_val == 0:
            msg = "OFF(0)"
        else:
            msg = "ERR"
        return msg


    def dcm_mode_parse(self, win, y_pos):
        key = 'dcm_type'
        val = self.flash_data.get(key, 'N/A')

        if val == 0:
            dcm_keys = ['dcmP', 'dcmR', 'dcmY']
            win.addstr(y_pos, 0, "dcm_type  : Euler(0)")
            y_pos += 1
            for key in dcm_keys:
                val = self.flash_data.get(key, 'N/A')
                win.addstr(y_pos, 0, "{}  : {:.8f}".format(key, val))
                y_pos += 1

        elif val == 1:
            dcm_keys = ['d11', 'd12', 'd13', 'd21', 'd22', 'd23', 'd31', 'd32', 'd33']

            win.addstr(y_pos, 0, "dcm_type  : Custom(1)")
            y_pos += 1
            for key in dcm_keys:
                val = self.flash_data.get(key, 'N/A')
                win.addstr(y_pos, 0, "{}  : {:.8f}".format(key, val))
                y_pos += 1


    def polarity_read(self, win, key):
        val = self.flash_data.get(key, 'N/A')
        if val == 1:
            msg = "reverse(1)"
        elif val == 0:
            msg = "nominal(0)"
        else:
            msg = "ERR"
        return msg
        pass

    def motor_mode_parse(self, win):
        key = 'motor_on'
        motor_val = self.flash_data.get(key, 'N/A')
        if motor_val == 1:
            msg = "PITCH(1)"
        elif motor_val == 2:
            msg = "ROLL(2)"
        elif motor_val == 3:
            msg = "BOTH(3)"
        elif motor_val == 0:
            msg = "OFF(0)"
        else:
            msg = "ERR"
        return msg

    def unit_change(self, key, value):
        if key == 'pitch':
            return value*180/pi
        elif key == 'roll':
            return value*180/pi
        elif key == 'b pitch':
            return value*180/pi
        elif key == 'b roll':
            return value*180/pi
        # elif key == 'cam imu err':
        #     return value
        # elif key == 'b beta':
        #     return value*1000
        else:
            return value

    def rt_data_loop(self, win):
        win.clear()
        # self.ui_data['time']
        y_pos = 0
        for key in self.rt_data_keys:
            value = self.ui_data.get(key, 'N/A')
            if not isinstance(value, (float, int)):
                win.addstr(y_pos, 0, "!!Wrong key: {}".format(key))
                y_pos += 1
                continue
            value = self.unit_change(key, value)
            win.addstr(y_pos, 0, "{:12}: {:.3f}".format(key, value))
            y_pos += 1
        win.refresh()
        pass

    def rt_data2_loop(self, win):
        win.clear()
        # self.ui_data['time']
        y_pos = 0
        for key in self.rt_data2_keys:
            value = self.ui_data.get(key, 'N/A')
            if not isinstance(value, (float, int)):
                win.addstr(y_pos, 0, "!!!!Wrong key: {}".format(key))
                y_pos += 1
                continue
            value = self.unit_change(key, value)
            win.addstr(y_pos, 0, "{:12}: {:.3f}".format(key, value))
            y_pos += 1
        win.refresh()

        pass

    def sbgc_data_loop(self, win):
        win.clear()
        y_pos = 0
        for key in self.sbgc_data_keys:
            value = self.ui_data.get(key, 'N/A')
            win.addstr(y_pos, 0, "{:12}: {:.3f}".format(key, value))
            y_pos += 1
        win.refresh()
        pass

    def command_loop(self, win):
        win.clear()
        win.addstr(0, 0, "Enter a command: " + self.ui_command)
        win.nodelay(True)
        try:
            user_input = win.getkey()  # Capture user input
            # self.ui_command = user_input.decode('utf-8')  # Update the command
            if user_input == "\n":
                self.command_parse_and_send()
                pass
            elif user_input == "\x7f" or user_input == "\b":
                # Handle backspace: Remove the last character from self.ui_command
                if len(self.ui_command) > 0:
                    self.ui_command = self.ui_command[:-1]
            else:
                self.ui_command += user_input

            win.refresh()
        except:
            pass

    def command_parse_and_send(self):
        split = self.parse_input_command(self.ui_command)

        for field in self.command_list:
            if field['command'] == split[0]:
                function = field['function']
                try:
                    data = bytearray(struct.pack('<f', float(split[1])))
                except:
                    data = bytearray(struct.pack('<f', 0))
                if function == self.f_change_param:
                    function(field['key'], data)
                else:
                    pass

                self.ui_command = "sent!"
                return

        self.ui_command = ""


    def ui_loop(self, stdscr):
        param_win = curses.newwin(27, 30, 1, 1)
        rt_data_win = curses.newwin(24, 25, 1, 31)
        rt_data2_win = curses.newwin(24, 25, 1, 60)
        command_win = curses.newwin(2, 80, 28, 1)
        sbgc_win = curses.newwin(10, 25, 1, 91)
        try:
            while True:
                # self.ui_data = self.parse_bytearray(data_ui_queue.get_nowait())
                data = data_ui_queue.get(timeout=1)
                if data[1] == 0: #0 for real time log
                    self.ui_data = self.parse_bytearray(data)
                    self.rt_data_loop(rt_data_win)
                    self.rt_data2_loop(rt_data2_win)
                    self.sbgc_data_loop(sbgc_win)
                if data[1] == 1: #1 for real time log
                    self.flash_data = self.parse_flash_bytearray(data)
                    self.param_loop(param_win)

                self.command_loop(command_win)

                pass
        except KeyboardInterrupt:
            self.stop()
            print("ended3")
        except:
            traceback.print_exc()
            self.stop()
        self.stop()
        pass

    def run(self):
        self.search_com_ports()
        # uartRx = Thread(target=self.read_serial_and_udp_send)
        usbRx = Thread(target=self.read_serial_by_byte)
        usbRx.start()

        csvSave = Thread(target=self.save_csv)
        csvSave.start()

        try:
            wrapper(self.ui_loop)
        except KeyboardInterrupt:
            self.stop()
            usbRx.join()
            csvSave.join()
        except:
            traceback.print_exc()
            self.stop()
            usbRx.join()
            csvSave.join()

        self.stop()
        pass


if __name__ == '__main__':
    # s = GimbalUartParser()
    s = GimbalUI()
    s.run()




