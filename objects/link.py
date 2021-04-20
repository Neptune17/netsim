import random

from utils import *

class Link:

    def __init__(self, dest_ip, trace_path):

        self.id = Link._get_next_id()

        self.dest_ip = dest_ip
        self.trace = self.analyze_trace_file(trace_path)
        self.current_trace_index = 0

        self.next_available_time = 0.0
    
    def get_next_available_time(self):
        return self.next_available_time

    def is_available(self, current_time):
        return self.next_available_time <= current_time

    def analyze_trace_file(self, trace_path):
        
        trace_list = []
        with open(trace_path, "r") as f:
            for line in f.readlines():
                trace_list.append(list(
                    map(lambda x: float(x), line.split(","))
                ))
                if len(trace_list[-1]) != 4:
                    raise ValueError("Trace file error!\nPlease check its format like : {0}".format(4))

        if len(trace_list) == 0:
            raise ValueError("Trace file error!\nThere is no data in the file!")
        
        if trace_list[0][0] != 0.0:
            raise ValueError("Trace file error!\nGive a startup trace line!(Time == 0.0)")

        return trace_list

    def get_link_status(self, current_time):

        while(True):
            if self.current_trace_index + 1 not in self.trace or self.trace[self.current_trace_index + 1][0] > current_time:
                bandwidth = self.trace[self.current_trace_index][1]
                delay = self.trace[self.current_trace_index][3]
                loss_rate = self.trace[self.current_trace_index][2]
                break
            self.current_trace_index += 1
        
        return bandwidth, delay, loss_rate

    def get_send_delay(self, size, current_time):

        bandwidth, delay, loss_rate = self.get_link_status(current_time)

        return size / (bandwidth * 10**6 / 8)

    def send_packet(self, packet, current_time):

        bandwidth, delay, loss_rate = self.get_link_status(current_time)

        dropped = random.random() < loss_rate

        send_delay = self.get_send_delay(packet.size, current_time)

        event_delay = send_delay + delay

        self.next_available_time = current_time + send_delay

        return event_delay, send_delay, dropped

    _next_id = 1

    @classmethod
    def _get_next_id(cls):
        result = Link._next_id
        Link._next_id += 1
        return result
    
    @classmethod
    def reset_link_id(cls):
        Link._next_id = 1