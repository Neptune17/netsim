import numpy as np

from utils import *

from objects.packet import Packet

class Block:

    def __init__(self,
                 destip = strip_to_intip("192.168.0.2"),
                 srcip = strip_to_intip("192.168.0.1"),
                 size = 200000,
                 priority = 0,
                 time_to_live = 0.2,
                 create_timestamp = 0.0,
                 bytes_per_packet = 1500,
                 bytes_per_header = 20):

        self.block_id = Block.get_next_block_id()
        
        self.destip = destip
        self.srcip = srcip
        self.priority = priority
        self.size = size
        self.time_to_live = time_to_live
        self.create_timestamp = create_timestamp
        self.bytes_per_packet = bytes_per_packet
        self.bytes_per_header = bytes_per_header

        self.finish_timestamp = float("inf")
        self.total_pkt_nums = int(np.ceil(size / (bytes_per_packet - bytes_per_header)))
        self.acked_pkt_nums = 0
        self.acked_time_list = [(0, -1.0) for i in range(self.total_pkt_nums)]

    def generate_packets(self):
        packet_list = []
        for offset in range(self.total_pkt_nums):
            packet_list.append(Packet(destip = self.destip, srcip = self.srcip, create_timestamp = self.create_timestamp, size = self.bytes_per_packet))
            
            extra_block_info = {
                "Block_id" : self.block_id,
                "Block_offset" : offset,
                "Block_TTL" : self.time_to_live,
                "Block_create_time" : self.create_timestamp
            }
            
            packet_list[offset].extra["Block_info"] = extra_block_info

        return packet_list

    def update_block_status_ack(self, ack_packet):

        in_block_offset = ack_packet.extra["Block_info"]["Block_offset"]
        finish_timestamp = ack_packet.finish_timestamp
        packet_id = ack_packet.packet_id

        if self.acked_time_list[in_block_offset] == (0, -1.0):
            self.acked_time_list[in_block_offset] = (packet_id, finish_timestamp)
            self.acked_pkt_nums += 1
            if self.acked_pkt_nums == self.total_pkt_nums:
                self.finish_timestamp = finish_timestamp
            return True

        return False

    def is_miss_ddl(self):
        return self.finish_timestamp - self.create_timestamp > self.time_to_live

    def __str__(self):
        return str(self.get_simplified_block_info())

    def get_full_block_info(self):
        return {
            "Block_id" : self.block_id,
            "Src_IP" : intip_to_strip(self.srcip),
            "Dest_IP" : intip_to_strip(self.destip),
            "Create_timestamp" : self.create_timestamp,
            "Finished_timestamp" : self.finish_timestamp,
            "Priority" : self.priority,
            "Size" : self.size,
            "Time_to_live" : self.time_to_live,
            "DDL_missed" : self.is_miss_ddl(),
            "Total_pkt_nums" : self.total_pkt_nums,
            "Acked_pkt_nums" : self.acked_pkt_nums,
            "Acked_pkt_list" : self.acked_time_list
        }
    
    def get_simplified_block_info(self):
        return {
            "Block_id" : self.block_id,
            "Src_IP" : intip_to_strip(self.srcip),
            "Dest_IP" : intip_to_strip(self.destip),
            "Create_timestamp" : self.create_timestamp,
            "Finished_timestamp" : self.finish_timestamp,
            "Priority" : self.priority,
            "Size" : self.size,
            "Time_to_live" : self.time_to_live,
            "DDL_missed" : self.is_miss_ddl()
        }

    _block_id = 1

    @classmethod
    def get_next_block_id(cls):
        ret = cls._block_id
        cls._block_id += 1
        return ret

    @classmethod
    def reset_block_id(cls):
        cls._block_id = 1