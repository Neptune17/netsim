import random

from config.constant import *

from utils import *

class Router:

    def __init__(self, name, ip_list, queue_config, route_table, queue_sche_solution, max_rate, log_path, label_solution = None):
        
        self.name = name

        self.out_links = [None for _ in range(len(ip_list))]

        self.ip_list = ip_list

        self.route_table = route_table
        for tarsubnet in self.route_table:
            for i in range(len(self.ip_list)):
                if intip_to_strip(self.ip_list[i]) == self.route_table[tarsubnet]:
                    self.route_table[tarsubnet] = i
                    break

        self.lock_time = -1.0
        self.lock_count = 0

        self.router_available_time = -1.0
        self.port_available_time = [ -1.0 for _ in range(len(self.ip_list))]

        self.max_rate = max_rate

        self.queue_size = []
        self.queues = []
        for i in range(len(ip_list)):
            self.queues.append([])
            for _ in range(len(queue_config)):
                self.queues[i].append([])
            self.queue_size.append(queue_config)

        self.queue_sche_solution = queue_sche_solution
        self.label_solution = label_solution

        self.queue_sche_solution_cache_in = None
        self.queue_sche_solution_cache_out = None
        self.label_solution_cache = None
        
        self.rr_port_index = 0

        self.log_path = log_path

    def log_queue_size(self, event_time):
        f = open(self.log_path + self.name + ".log", "a+")
        data = {}
        for i in range(len(self.ip_list)):
            data[intip_to_strip(self.ip_list[i])] = []
            for j in range(len(self.queues[i])):
                data[intip_to_strip(self.ip_list[i])].append(len(self.queues[i][j]))
        data["event_time"] = event_time
        print(data, file = f)
        f.close()

    def get_next_event_time(self):

        min_port_available_time = None
        for port in range(len(self.port_available_time)):
            if min_port_available_time is None:
                min_port_available_time = self.out_links[port].get_next_available_time()
            else:
                min_port_available_time = min(min_port_available_time, self.out_links[port].get_next_available_time())

        return max(min_port_available_time, self.router_available_time)

    def add_link(self, src_ip, link):
        for idx, port_ip in enumerate(self.ip_list):
            if port_ip == strip_to_intip(src_ip):
                self.out_links[idx] = link
                break
    
    def in_queue_size(self, port_id):
        size = 0
        for queue in self.queues[port_id]:
            size += len(queue)
        return size

    def in_queue_size_total(self):
        size = 0
        for port in range(len(self.queues)):
            size += self.in_queue_size(port)
        return size

    def send_packet_port(self, port_id, event_time):
        
        event_list = []

        assert(self.queue_sche_solution_cache_out is not None)

        packet = self.queues[port_id][self.queue_sche_solution_cache_out].pop(0)

        self.log_queue_size(event_time)
        
        # assert(self.out_links[port_id].is_available(event_time))

        event_delay, send_delay, dropped = self.out_links[port_id].send_packet(packet, event_time)

        if self.label_solution_cache is not None:
            packet.extra["routerlabel"] = self.label_solution_cache
            self.label_solution_cache = None

        packet.dropped = dropped

        if packet.dropped:
            event_list.append(([event_time + packetConfig.DROP_PUNISHMENDT, eventType.PACKET_EVENT], [packet.srcip, packet]))
        else:
            event_list.append(([event_time + event_delay, eventType.PACKET_EVENT], [self.out_links[port_id].dest_ip, packet]))

        self.router_available_time = event_time + packet.size / ((self.max_rate / 8.0) * 10**6)
        self.port_available_time[port_id] = event_time + send_delay

        self.lock_count -= 1
        self.lock_time = self.get_next_event_time()

        if self.in_queue_size_total() > 0:

            min_port_available_time = None
            for port in range(len(self.port_available_time)):
                if len(self.queues[port]) == 0:
                    continue
                if min_port_available_time is None:
                    min_port_available_time = self.out_links[port].get_next_available_time()
                else:
                    min_port_available_time = min(min_port_available_time, self.out_links[port].get_next_available_time())

            tartime = max(min_port_available_time, self.router_available_time)

            self.lock_count += 1
            event_list.append(([tartime, eventType.ROUTER_PRE_SEND_EVENT], [self.send_packet]))

        packet.add_log(event_time, self.name, intip_to_strip(self.ip_list[port_id]), "out", "")

        self.queue_sche_solution_cache_out = None

        return event_list

    def send_packet(self, event_time):
        
        event_list = []

        if self.in_queue_size_total() == 0:
            self.lock_count -= 1
            return event_list

        begin_index = self.rr_port_index
        while(True):
            if self.in_queue_size(self.rr_port_index) != 0 and self.out_links[self.rr_port_index].is_available(event_time):
                chosen_port_index = self.rr_port_index
                event_list.append(([event_time, eventType.SOLUTION_ROUTER_SCHE_EVENT_OUT], [self.queue_sche_solution.packet_out_queue, self, chosen_port_index]))
                if self.label_solution is not None:
                    event_list.append(([event_time, eventType.SOLUTION_ROUTER_LABEL_EVENT], [self.label_solution.router_out_label, self, chosen_port_index]))
                event_list.append(([event_time, eventType.ROUTER_SEND_EVENT], [self.send_packet_port, chosen_port_index]))
                self.rr_port_index += 1
                if self.rr_port_index == len(self.ip_list):
                    self.rr_port_index = 0
                break
            self.rr_port_index += 1
            if self.rr_port_index == len(self.ip_list):
                self.rr_port_index = 0
            if self.rr_port_index == begin_index:
                break
        if len(event_list) == 0:
            self.lock_count -= 1
        return event_list

    def receive_packet(self, packet, port_ip, event_time):
        
        event_list = []

        if self.queue_sche_solution_cache_in is None:
            event_list.append(([event_time, eventType.SOLUTION_ROUTER_SCHE_EVENT_IN], [self.queue_sche_solution.packet_in_queue, self, packet]))
            event_list.append(([event_time, eventType.PACKET_EVENT], [port_ip, packet]))
        else:
            if self.lock_count == 0:
                self.lock_count += 1
                tartime = max(self.get_next_event_time(), event_time)
                event_list.append(([tartime, eventType.ROUTER_PRE_SEND_EVENT], [self.send_packet]))

            tarport = -1
            for tarsubnet in self.route_table:
                if strip_is_in_cidr(intip_to_strip(packet.destip), tarsubnet):
                    tarport = self.route_table[tarsubnet]
                    break

            assert(tarport >= 0 and tarport < len(self.route_table))

            if len(self.queues[tarport][self.queue_sche_solution_cache_in]) < self.queue_size[tarport][self.queue_sche_solution_cache_in]:
                self.queues[tarport][self.queue_sche_solution_cache_in].append(packet)
                self.log_queue_size(event_time)
            else:
                packet.dropped = True
                event_list.append(([event_time + packetConfig.DROP_PUNISHMENDT, eventType.PACKET_EVENT], [packet.srcip, packet]))
            
            packet.add_log(event_time, self.name, intip_to_strip(port_ip), "in", "")

            self.queue_sche_solution_cache_in = None

        return event_list