import struct
import os


class GimbalStatusFormatter:
    def __init__(self):
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

    def make_c_format_list(self):
        folder_name = 'format'
        file_path = os.path.join(folder_name, 'c_format.txt')

        # Create the 'format' folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        with open(file_path, 'w') as file:
            c_type_map = {'B': 'uint8_t', 'H': 'uint16_t', 'f': 'float', 'd': 'double'}
            for item in self.data_structure:
                c_variable_name = item['c_var_name']
                c_data_type = c_type_map.get(item['format'])

                string = f'add_log_var(&{c_variable_name}, sizeof({c_data_type}));\n'
                file.write(string)
                pass

    def generate_txt_for_ros_msg(self):
        folder_name = 'format'
        file_path = os.path.join(folder_name, 'ros_format.txt')

        # Create the 'format' folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        # ROS built-in-types
        # https://docs.ros.org/en/foxy/Concepts/About-ROS-Interfaces.html
        ros_type_map = {'B': 'uint8', 'H': 'uint16', 'f': 'float32', 'd': 'float64'}

        with open(file_path, 'w') as file:
            file.write(f'EulerAngles gimbal_angle\n')
            for item in self.data_structure:
                c_variable_name = item['c_var_name']
                ros_data_type = ros_type_map.get(item['format'])
                ros_data_name = item['name'].replace(' ', '_')
                string = f'{ros_data_type} {ros_data_name}\n'
                file.write(string)




    def generate_txt_file(self):
        folder_name = 'format'
        file_path = os.path.join(folder_name, 'output.txt')

        # Create the 'format' folder if it doesn't exist
        os.makedirs(folder_name, exist_ok=True)

        with open(file_path, 'w') as file:
            file.write("asdf")
            # for item in self.data_structure:
            #     name = item['name']
            #     value = self.data_structure.get(name, 0)  # Replace 0 with a default value if data is missing
            #     file.write(f'{name}: {value}\n')

    def run(self):
        pass


if __name__ == '__main__':
    g = GimbalStatusFormatter()
    g.make_c_format_list()
    g.generate_txt_for_ros_msg()