import serial
from scipy import signal


class Device:
    def __init__(self, com, sample_rate=100, brate=115200):
        self.ser = serial.Serial(com, brate)
        self.sampe_rate = sample_rate
        self.h_b, self.h_a = signal.butter(8, 0.1, "highpass")
        self.data_valid = 0
        self.k = 0
        self.data_list_time = []
        self.range_list_time = list(range(self.sampe_rate))
        self.ir_list_data = []
        self.red_list_data = []
        self.bpm_list_data = []
        self.ir_list_data_filtered = []
        self.red_list_data_filtered = []
        self.data = {
            "temperatureC": 0,
            "red": 0,
            "ir": 0,
            "HR": 0,
            "SPO2": 0,
            "Time": 0,
            "Fin": 0,
        }

    def _culculate_spo2(self):
        if self.data_valid:
            ir_dc = min(self.ir_list_data)
            red_dc = min(self.red_list_data)
            ir_ac = max(self.ir_list_data) - ir_dc
            red_ac = max(self.red_list_data) - red_dc
            temp1 = ir_ac * red_dc
            if temp1 < 1:
                temp1 = 1
            R2 = (red_ac * ir_dc) / temp1
            SPO2 = -45.060 * R2 * R2 + 30.354 * R2 + 94.845
            if SPO2 > 100 or SPO2 < 0:
                SPO2 = 0
            return SPO2
        return 0

    def _culculate_HR(self):
        if self.data_valid:
            HR_num = signal.find_peaks(self.ir_list_data_filtered, distance=10)[0]
            time = self.data_list_time[-1] - self.data_list_time[0]
            HR = len(HR_num) / (time / 1000) * 60
            self.k = self.ir_list_data_filtered[-1]
            return HR
        return 0

    def get_data(self):
        if (
            len(self.ir_list_data_filtered) >= self.sampe_rate
            and len(self.red_list_data_filtered) >= self.sampe_rate
        ):
            self.data_valid = 1

        read_data = self.ser.readline().decode("utf-8")
        if "[DATA]" in read_data:
            data_list_str = read_data.split("]")[1].strip().split(",")
            self.data["temperatureC"] = float(data_list_str[0].split("=")[1])
            self.data["red"] = int(data_list_str[1].split("=")[1])
            self.data["ir"] = int(data_list_str[2].split("=")[1])
            self.data["Time"] = int(data_list_str[3].split("=")[1])

            if len(self.bpm_list_data) > 10:
                self.bpm_list_data.pop(0)
                self.data["HR"] = sum(self.bpm_list_data) / len(self.bpm_list_data)
            self.bpm_list_data.append(self._culculate_HR())

            if len(self.ir_list_data) > self.sampe_rate:
                self.ir_list_data.pop(0)
                data = signal.filtfilt(self.h_b, self.h_a, self.ir_list_data, axis=0)
                data = signal.detrend(
                    data,
                    axis=0,
                    type="linear",
                    bp=0,
                    overwrite_data=False,
                )
                self.ir_list_data_filtered = data
            self.ir_list_data.append(self.data["ir"])

            if len(self.red_list_data) > self.sampe_rate:
                self.red_list_data.pop(0)
                self.red_list_data_filtered = signal.detrend(
                    self.red_list_data,
                    axis=0,
                    type="linear",
                    bp=0,
                    overwrite_data=False,
                )
            self.red_list_data.append(self.data["red"])

            if len(self.data_list_time) > self.sampe_rate:
                self.data_list_time.pop(0)
            self.data_list_time.append(self.data["Time"])

            self.data["SPO2"] = self._culculate_spo2()
            if self.data["ir"] > 150000:
                self.data["Fin"] = 1
            else:
                self.data["Fin"] = 0
        return self.data


if __name__ == "__main__":
    max_divice = Device("COM11")
    while True:
        data = max_divice.get_data()
        print(max_divice.data)
