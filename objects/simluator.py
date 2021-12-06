import heapq
import random
import pandas as pd
from objects.app_abr import abr_client, abr_sevrer

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
        self.cur_log_index = -1
        self.log_counter = 0

        self.random_queue_index_maxlen = 2000
        self.random_queue_index_pool = [i for i in range(self.random_queue_index_maxlen)]
        self.random_queue_index_index = 0

        random.shuffle(self.random_queue_index_pool)

        os.mkdir(self.log_path + "router_log/")
        os.mkdir(self.log_path + "sender_log/")
        os.mkdir(self.log_path + "abr_log/")

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
                label_solution = None if (len(node_config) == 7) else node_config[7]

                ip_list = []
                for strip in strip_list:
                    ip_list.append(strip_to_intip(strip))

                router = Router(name = name, ip_list = ip_list, queue_config = queue_config, route_table = route_table, queue_sche_solution = queue_sche_solution, max_rate = max_rate, log_path = self.log_path + "router_log/", label_solution = label_solution)
                self.routers.append(router)
                for ip in ip_list:
                    self.ip_map[ip] = router
        
        for edge_config in config_dict["edges"]:
            src_ip = edge_config[0]
            dest_ip = edge_config[1]
            trace_path = edge_config[2]
            link = Link(dest_ip = strip_to_intip(dest_ip), trace_path = trace_path)
            self.links.append(link)
            self.ip_map[strip_to_intip(src_ip)].add_link(src_ip, link)
        
        for sender in self.senders:
            print(sender.name, "Sender")
            print("out links:")
            print("if0:", intip_to_strip(sender.ip), "->", intip_to_strip(sender.out_links[0].dest_ip))
            print()

        for router in self.routers:
            print(router.name, "Router")
            print("out links:")
            for idx, link in enumerate(router.out_links):
                print("if" + str(idx) + ":", intip_to_strip(router.ip_list[idx]), "->", intip_to_strip(router.out_links[idx].dest_ip))
            print("route table:")
            for subnet in router.route_table:
                print(subnet, "->", intip_to_strip(router.ip_list[router.route_table[subnet]]))
            print()

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
                heapq.heappush(self.event_queue, [create_timestamp, eventType.BLOCK_EVENT_CREATE, self.get_random_index(), self.ip_map[strip_to_intip(src_ip)].add_block, block.block_id])

        if "abr" in config_dict:
            for abr_config in config_dict["abr"]:
                src_ip = abr_config[0]
                dest_ip = abr_config[1]
                abr_trace = abr_config[2]

                data = open(abr_trace).readlines()
                quality_cnt = int(data[0].split(' , ')[0])
                block_cnt = int(data[0].split(' , ')[1])
                block_time = int(data[0].split(' , ')[2])

                config_abr = {}
                config_abr["video"] = {}
                config_abr["video"]["block_time"] = block_time
                config_abr["video"]["block_cnt"] = block_cnt
                config_abr["video"]["quality_cnt"] = quality_cnt
                config_abr["blocks"] = [[0 for __ in range(quality_cnt)] for _ in range(block_cnt)]

                for i in range(block_cnt):
                    for j in range(quality_cnt):
                        config_abr["blocks"][i][j] = int(data[i * 2 + j + 1])
                
                self.ip_map[strip_to_intip(src_ip)].abr_solution = abr_client(
                    config_abr,
                    abr_request_size = 40,
                    buffer_max = 10,
                    srcip = strip_to_intip(src_ip),
                    destip = strip_to_intip(dest_ip))
                self.ip_map[strip_to_intip(dest_ip)].abr_solution = abr_sevrer(
                    config_abr,
                    bytes_per_packet = 1500,
                    bytes_per_header = 20)
                heapq.heappush(self.event_queue, [0, eventType.ABR_FORCE_UPDATE, self.get_random_index(), self.ip_map[strip_to_intip(src_ip)].abr_force_update])

    def get_random_index(self):
        self.random_queue_index_index += 1
        if self.random_queue_index_index == self.random_queue_index_maxlen:
            self.random_queue_index_index = 0
        return self.random_queue_index_pool[self.random_queue_index_index]

    def log_packet(self, packet):
        if self.cur_log_index < 0:
            self.cur_log_index = 1
            os.mkdir(self.log_path + "packet_log/")
            os.mknod(self.log_path + "packet_log/" + "packet-" + str(self.cur_log_index) + ".log")
        elif self.log_counter % logConfig.MAX_LINE_PER_FILE == 0:
            self.cur_log_index += 1
            os.mknod(self.log_path + "packet_log/" + "packet-" + str(self.cur_log_index) + ".log")
        
        f = open(self.log_path + "packet_log/" + "packet-" + str(self.cur_log_index) + ".log", "a+")
        print(packet.get_full_packet_info(), file = f)
        f.close()

        self.log_counter += 1

    def log_ABR(self, type, id, quality, event_time):
        f = open(self.log_path + "abr_log/" + "abr.log", "a+")
        print(event_time, type, id, quality, file = f)
        f.close()

    def run(self, time = float("inf")):

        if time != float("inf"):
            heapq.heappush(self.event_queue, (self.current_time + time, eventType.STOP_CHECKER))

        while(True):

            if len(self.event_queue) == 0:
                break

            event = heapq.heappop(self.event_queue)
            # print(event)

            event_time = event[0]
            event_type = event[1]

            print(event_time, eventType.DEBUG_STR[event_type])

            if event_type == eventType.STOP_CHECKER:
                # To check if time is up
                # event details:
                #   event_time
                #   STOP_CHECKER
                break
            if event_type == eventType.BLOCK_EVENT_CREATE:
                # To create transmission
                # event details:
                #   event_time
                #   BLOCK_EVENT_CREATE
                #   random_index 
                #   Block target Src Sender's add_block func
                #   Block id
                event_list = event[3](self.block_map[event[4]], event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
            if event_type == eventType.SENDER_EVENT:
                # To send a packet in a sender(CC and packet selection should be done before this)
                # event details:
                #   event_time
                #   SENDER_EVENT
                #   random_index 
                #   Sender's send_packet func
                event_list = event[3](event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
            if event_type == eventType.SOLUTION_SENDER_SCHE_EVENT:
                # To call packet selection algorithm before send a packet in a sender
                # event details:
                #   event_time
                #   SOLUTION_SENDER_SCHE_EVENT
                #   random_index 
                #   Target Sender's block selection algorithm's select_next_packet func
                #   Target Sender
                event[3](event[4], event_time)
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_SEND:
                # To call CC algorithm before send a packet in a sender
                # event details:
                #   event_time
                #   SOLUTION_SENDER_CC_EVENT_SEND
                #   random_index 
                #   Target Sender's CC algorithm's send_event func
                #   Target Sender
                event[3](event[4])
            if event_type == eventType.SOLUTION_ROUTER_SCHE_EVENT_IN:
                # To call queue manage algorithm on router to choose which queue should the packet in (receive)
                # event details:
                #   event_time
                #   SOLUTION_ROUTER_SCHE_EVENT_IN
                #   random_index 
                #   Target Router's queue manage algorithm's packet_in_queue func
                #   Target Router
                #   Target packet
                event[3](event[4], event[5])
            if event_type == eventType.SOLUTION_ROUTER_SCHE_EVENT_OUT:
                # To call queue manage algorithm on router to choose which queue should the packet out (send)
                # event details:
                #   event_time
                #   SOLUTION_ROUTER_SCHE_EVENT_OUT
                #   random_index 
                #   Target Router
                #   Target Port index
                event[3](event[4], event[5])
            if event_type == eventType.PACKET_EVENT:
                # Packet transferred to a Router or a Sender
                # event details:
                #   event_time
                #   PACKET_EVENT
                #   random_index 
                #   Target ip
                #   Target packet
                event_list = self.ip_map[event[3]].receive_packet(event[4], event[3], event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
            if event_type == eventType.ROUTER_PRE_SEND_EVENT:
                # To start a packet send event in a router(rr choose interface of router)
                # event details:
                #   event_time
                #   ROUTER_PRE_SEND_EVENT
                #   random_index 
                #   Target router's send_packet func
                event_list = event[3](event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
            if event_type == eventType.ROUTER_SEND_EVENT:
                # To send a packet in certain interface of a router(queue selection should be done before this)
                # event details:
                #   event_time
                #   ROUTER_SEND_EVENT
                #   random_index 
                #   Target router's send_packet_port func
                #   Target interface index on target router
                event_list = event[3](event[4], event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
            if event_type == eventType.BLOCK_EVENT_ACK:
                # To update transmission status when a packet of it is acked
                # event details:
                #   event_time
                #   BLOCK_EVENT_ACK
                #   random_index 
                #   acked packet
                if event[3].extra["Block_info"]["Block_id"] != -1:
                    self.block_map[event[3].extra["Block_info"]["Block_id"]].update_block_status_ack(event[3])
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_ACK:
                # To update Sender's CC algorithm when packet ack event is detected
                # event details:
                #   event_time
                #   SOLUTION_SENDER_CC_EVENT_ACK
                #   random_index 
                #   Target Sender's CC algorithm's ack_event func
                #   extra data for CC algorithm
                event[3](event_time, event[4])
            if event_type == eventType.SOLUTION_SENDER_CC_EVENT_DROP:
                # To update Sender's CC algorithm when packet lost event is detected
                # event details:
                #   event_time
                #   SOLUTION_SENDER_CC_EVENT_DROP
                #   random_index 
                #   Target Sender's CC algorithm's drop_event func
                event[3](event_time)
            if event_type == eventType.LOG_PACKET_EVENT:
                # To log packet when it arrives dest
                # event details:
                #   event_time
                #   LOG_PACKET_EVENT
                #   random_index 
                #   Target Packet
                self.log_packet(event[3])
            if event_type == eventType.SOLUTION_ROUTER_LABEL_EVENT:
                # To add packet label when it leaves router
                # event details:
                #   event_time
                #   SOLUTION_ROUTER_LABEL_EVENT
                #   random_index 
                #   Target Router
                #   Port id
                event[3](event[4], event[5])
            if event_type == eventType.LOG_ABR_EVENT:
                self.log_ABR(event[3],event[4], event[5], event_time)
            if event_type == eventType.ABR_FORCE_UPDATE:
                event_list = event[3](event_time)
                for (event_info, event_func) in event_list:
                    assembled_event = []
                    assembled_event.extend(event_info)
                    assembled_event.extend([self.get_random_index()])
                    assembled_event.extend(event_func)
                    heapq.heappush(self.event_queue, assembled_event)
        return 