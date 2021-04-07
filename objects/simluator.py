import heapq
import pandas as pd

from objects.sender import Sender
from objects.link import Link
from objects.block import Block
from objects.router import Router

from config.constant import *

from utils import *

class Simluator:
    
    def __init__(self,
                 config_dict,
                 log_path):
        
        self.current_time = 0.0
        self.event_queue = []

        self.senders = []
        self.routers = []
        self.links = []
        self.blocks = []

        self.ip_map = {}
        self.block_map = {}

        self.log_path = log_path

        for node_config in config_dict["nodes"]:
            node_type = node_config[0]
            if node_type == objectType.SENDER:
                name = node_config[1]
                strip = node_config[2]
                scheduler_solution = node_config[3]
                cc_solution = node_config[4]
                sender = Sender(name = name, ip = strip_to_intip(strip), cc_solution = cc_solution, sche_solution = scheduler_solution)
                self.senders.append(sender)
                self.ip_map[strip_to_intip(strip)] = sender
            if node_type == objectType.ROUTER:
                name = node_config[1]
                strip_list = node_config[2]
                queue_config = node_config[3]
                route_table = node_config[4]
                queue_sche_solution = node_config[5]
                max_rate = node_config[6]

                ip_list = []
                for strip in strip_list:
                    ip_list.append(strip_to_intip(strip))

                router = Router(name = name, ip_list = ip_list, queue_config = queue_config, route_table = route_table, queue_sche_solution = queue_sche_solution, max_rate = max_rate)
                self.routers.append(router)
                for ip in ip_list:
                    self.ip_map[ip] = router
        
        for edge_config in config_dict["edges"]:
            src_ip = edge_config[0]
            dest_ip = edge_config[1]
            trace_path = edge_config[2]
            link = Link(dest_ip = strip_to_intip(dest_ip), trace_path = trace_path)
            self.links.append(link)
            self.ip_map[strip_to_intip(src_ip)].add_link(link)
        
        for ip in self.ip_map:
            print(intip_to_strip(ip), self.ip_map[ip])

        for block_config in config_dict["blocks"]:
            src_ip = block_config[0]
            dest_ip = block_config[1]
            trace_path = block_config[2]

            df_data = pd.read_csv(trace_path, header=None)
            shape = df_data.shape
            if shape[1] == 4:
                df_data.columns = ["time", "size", "priority", "time_to_live"]

            for i in range(shape[0]):
                create_timestamp = df_data["time"][i]
                size = df_data["size"][i]
                priority = df_data["priority"][i]
                time_to_live = df_data["time_to_live"][i]

                block = Block(destip = strip_to_intip(dest_ip),
                              srcip = strip_to_intip(src_ip),
                              size = size,
                              priority = priority,
                              time_to_live = time_to_live,
                              create_timestamp = create_timestamp,
                              bytes_per_packet = packetConfig.BYTES_PER_PACKET,
                              bytes_per_header = packetConfig.BYTES_PER_HEADER)
                self.blocks.append(block)
                self.block_map[block.block_id] = block
                heapq.heappush(self.event_queue, (create_timestamp, eventType.BLOCK_EVENT_CREATE, self.ip_map[strip_to_intip(src_ip)].add_block, block.block_id))

    def run(self, time = float("inf")):

        if time != float("inf"):
            heapq.heappush(self.event_queue, (self.current_time + time, eventType.STOP_CHECKER))

        while(True):

            if len(self.event_queue) == 0:
                break

            event = heapq.heappop(self.event_queue)

            event_time = event[0]
            event_type = event[1]

            print(event_time, eventType.DEBUG_STR[event_type])

            if event_type == eventType.STOP_CHECKER:
                break
            if event_type == eventType.BLOCK_EVENT_CREATE:
                event_list = event[2](self.block_map[event[3]], event_time)
                for event in event_list:
                    heapq.heappush(self.event_queue, event)
            if event_type == eventType.SENDER_EVENT:
                event_list = event[2](event_time)
                for event in event_list:
                    heapq.heappush(self.event_queue, event)
            if event_type == eventType.SOLUTION_SENDER_SCHE_EVENT:
                event[2](event[3])
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_SEND:
                event[2](event[3])
            if event_type == eventType.SOLUTION_ROUTER_SCHE_EVENT_IN:
                event[2](event[3], event[4])
            if event_type == eventType.SOLUTION_ROUTER_SCHE_EVENT_OUT:
                event[2](event[3], event[4])
            if event_type == eventType.PACKET_EVENT:
                event_list = self.ip_map[event[2]].receive_packet(event[3], event[2], event_time)
                f = open(self.log_path + "packet_log/packet-0.log", "a+")
                print(event[3].get_full_packet_info(), file = f)
                f.close()
                for event in event_list:
                    heapq.heappush(self.event_queue, event)
            if event_type == eventType.ROUTER_PRE_SEND_EVENT:
                event_list = event[2](event_time)
                for event in event_list:
                    heapq.heappush(self.event_queue, event)
            if event_type == eventType.ROUTER_SEND_EVENT:
                event_list = event[2](event[3], event_time)
                for event in event_list:
                    heapq.heappush(self.event_queue, event)
            if event_type == eventType.BLOCK_EVENT_ACK:
                self.block_map[event[2].extra["Block_info"]["Block_id"]].update_block_status_ack(event[2])
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_ACK:
                event[2]()
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_DROP:
                event[2]()
        return 