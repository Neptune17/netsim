import random

from config.constant import *

from utils import *

class Router:

    def __init__(self, name, ip_list, queue_config, route_table, queue_sche_solution, max_rate):
        
        self.name = name

        self.out_links = []

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

        self.queue_sche_solution_cache_in = None
        self.queue_sche_solution_cache_out = None

    def get_next_event_time(self):

        min_port_available_time = None
        for port in range(len(self.port_available_time)):
            if min_port_available_time is None:
                min_port_available_time = self.out_links[port].get_next_available_time()
            else:
                min_port_available_time = min(min_port_available_time, self.out_links[port].get_next_available_time())

        return max(min_port_available_time, self.router_available_time)

    def add_link(self, link):
        self.out_links.append(link)
    
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

        packet = self.queues[port_id][self.queue_sche_solution_cache_out].pop()

        event_delay, send_delay, is_dropped = self.out_links[port_id].send_packet(packet, event_time)

        packet.is_dropped = is_dropped

        if packet.is_dropped:
            event_list.append((event_time + packetConfig.DROP_PUNISHMENDT, eventType.PACKET_EVENT, packet.srcip, packet))
        else:
            event_list.append((event_time + event_delay, eventType.PACKET_EVENT, self.out_links[port_id].dest_ip, packet))

        self.router_available_time = event_time + 1 / self.max_rate
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
            event_list.append((tartime, eventType.ROUTER_PRE_SEND_EVENT, self.send_packet))

        self.queue_sche_solution_cache_out = None

        return event_list

    def send_packet(self, event_time):
        
        event_list = []

        if self.in_queue_size_total() == 0:
            return event_list
        
        port_random_sort = list(range(len(self.queues)))
        random.shuffle(port_random_sort)

        for port in port_random_sort:
            if self.in_queue_size(port) != 0 and self.out_links[port].is_available(event_time):
                event_list.append((event_time, eventType.SOLUTION_ROUTER_SCHE_EVENT_OUT, self.queue_sche_solution.packet_out_queue, self, port))
                event_list.append((event_time, eventType.ROUTER_SEND_EVENT, self.send_packet_port, port))
                break

        return event_list

    def receive_packet(self, packet, port_ip, event_time):
        
        event_list = []

        if self.queue_sche_solution_cache_in is None:
            event_list.append((event_time, eventType.SOLUTION_ROUTER_SCHE_EVENT_IN, self.queue_sche_solution.packet_in_queue, self, packet))
            event_list.append((event_time, eventType.PACKET_EVENT, port_ip, packet))
        else:
            if self.in_queue_size_total() == 0 and self.lock_count == 0:
                self.lock_count += 1
                event_list.append((event_time, eventType.ROUTER_PRE_SEND_EVENT, self.send_packet))

            tarport = -1
            for tarsubnet in self.route_table:
                if strip_is_in_cidr(intip_to_strip(packet.destip), tarsubnet):
                    tarport = self.route_table[tarsubnet]
                    break

            assert(tarport != -1)

            if len(self.queues[tarport][self.queue_sche_solution_cache_in]) < self.queue_size[tarport][self.queue_sche_solution_cache_in]:
                self.queues[tarport][self.queue_sche_solution_cache_in].append(packet)
            else:
                packet.is_dropped = True
                event_list.append((event_time + packetConfig.DROP_PUNISHMENDT, eventType.PACKET_EVENT, packet.srcip, packet))
            
            self.queue_sche_solution_cache_in = None

        return event_list