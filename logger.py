import json
import random
from datetime import date, datetime
from threading import Thread
from time import sleep
import os
import copy


class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAl = 4


class Logger:
    """
    Класс журналирования. Быстрее logging'а
    """

    def __init__(self, lib="logs", min_print_level=LogLevel.DEBUG):
        if not os.path.exists(lib):
            os.mkdir(lib)
        if LogLevel.DEBUG <= min_print_level <= LogLevel.CRITICAl:
            self.print_level = min_print_level
        else:
            raise ValueError("Minimum print level set incorrectly")
        self.lines_to_write = []
        self.data_to_write = []
        now_time = datetime.now().strftime("%H%M%S%d%m%y")
        self.log_filename = f"{lib}/session_{now_time}.log"
        self.json_filename = f"{lib}/session_{now_time}.json"
        self._numerator = 0
        self.run = True
        self.thread_log_writer = Thread(target=self.log_writer)
        self.thread_log_writer.start()
        self.thread_json_writer = Thread(target=self.json_writer)
        self.thread_json_writer.start()

    @property
    def numerator(self):
        self._numerator += 1
        return self._numerator

    def log_writer(self):
        """
        Внимательный секретарь
        """
        with open(self.log_filename, "a", encoding="ascii") as file:
            while self.run or self.data_to_write:
                sleep(0.1)
                while self.lines_to_write:
                    file.write(self.lines_to_write[0])
                    del self.lines_to_write[0]
                    if not self.lines_to_write:
                        file.flush()
            file.close()

    def init_json(self):
        with open(self.json_filename, "w") as file:
            return json.dump([], file)

    def read_json(self):
        with open(self.json_filename, "r") as file:
            return json.load(file)

    def write_json(self, data):
        with open(self.json_filename, "w") as file:
            return json.dump(data, file, sort_keys=True, indent=2)

    def json_writer(self):
        self.write_json([])
        while self.run or self.data_to_write:
            sleep(0.1)
            while self.data_to_write:
                data: list = self.read_json()
                data.extend(self.data_to_write)
                self.data_to_write = []
                self.write_json(data)

    def to_log(self, level: int, case: str, info: str = "", **log_data):
        """

        :param level:
        :param case:
        :param info:
        """
        date_str = str(datetime.now())
        if 2 > len(case) > 7:
            raise ValueError("Reason name length must be 2-7 symbols")
        else:
            space_len = 8 - len(case) + 4
            line = date_str + "\t" + case
            for i in range(space_len):
                line += " "
            line += info
        self.lines_to_write.append(line + "\n")
        if level >= self.print_level:
            if level == 0:
                print("\033[37m {}".format(line))  # white
            elif level == 1:
                print("\033[34m {}".format(line))  # blue
            elif level == 2:
                print("\033[33m {}".format(line))  # yellow
            elif level == 3:
                print("\033[32m {}".format(line))  # green
            elif level == 4:
                print("\033[31m {}".format(line))  # red
            else:
                raise ValueError("Severity level incorrect")

        self.data_to_write.append(
            {"!id": self.numerator, "datetime": date_str, "level": level, "case": case, "data": log_data})

    def stop(self):
        self.run = False


if __name__ == '__main__':
    log = Logger()
    for _ in range(10000):
        start_t = datetime.now()
        log.to_log(1, "TEST", str(random.randint(100, 10000)), test1=random.randint(10, 1000),
                   test2=random.randint(10, 1000))
    log.stop()
