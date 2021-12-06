from utils import *
from config.constant import *

import numpy as np

from objects.packet import Packet

class abr_client:

    def __init__(self, 
                 config,
                 abr_request_size = 40,
                 buffer_max = 10,
                 srcip = strip_to_intip("192.168.0.2"),
                 destip = strip_to_intip("192.168.0.1")
                 ) -> None:
        self.config = config
        self.abr_request_size = abr_request_size
        self.srcip = srcip
        self.destip = destip
        self.buffer_max = buffer_max

        self.buffer_time = 0
        self.play_time = 0
        self.last_block_time = 0
        self.last_quality = 0
        self.last_block_id = -1

    def choose_stream_block(self, block_list, last_quality, buffer_time, play_time, download_rate):
        
        return 0

    def receive_packet(self, packet: Packet, event_time, force_update: bool):
        download_rate = 1000000
        if force_update:
            packet_list = []
            packet_list.append(Packet(destip = self.destip, srcip = self.srcip, create_timestamp = event_time, size = self.abr_request_size))
            
            if self.last_block_id == -1:
                next_quality = 0
                next_id = self.last_block_id + 1
                extra_abr_info = {
                    "time" : next_id,
                    "quality" : next_quality
                }
                extra_block_info = {
                    "Block_id" : -1,
                    "Block_offset" : -1,
                    "Block_TTL" : 10000,
                    "Block_create_time" : event_time,
                    "Block_priority" : 0
                }
                self.last_block_id += 1
                self.last_quality = next_quality
                
                packet_list[0].extra["ABR_info"] = extra_abr_info
                packet_list[0].extra["Block_info"] = extra_block_info
                event_list = [[event_time, eventType.LOG_ABR_EVENT], ["REQUEST", next_id, next_quality]]
                return packet_list, event_list
            
            else:
                elapsed_time = event_time - self.last_block_time
                if elapsed_time <= self.buffer_time - self.play_time:
                    self.play_time += elapsed_time
                else:
                    self.play_time = self.buffer_time

                event_list = []

                block_list = self.config["blocks"][self.last_block_id + 1]
                next_quality = self.choose_stream_block(block_list, self.last_quality, self.buffer_time, self.play_time, download_rate)
            
                packet_list = []
                packet_list.append(Packet(destip = self.destip, srcip = self.srcip, create_timestamp = event_time, size = self.abr_request_size))
                
                next_id = self.last_block_id + 1
                extra_abr_info = {
                    "time" : next_id,
                    "quality" : next_quality
                }
                extra_block_info = {
                    "Block_id" : -1,
                    "Block_offset" : -1,
                    "Block_TTL" : 10000,
                    "Block_create_time" : event_time,
                    "Block_priority" : 0
                }
                self.last_block_id += 1
                self.last_quality = next_quality
                self.last_block_time = event_time

                packet_list[0].extra["ABR_info"] = extra_abr_info
                packet_list[0].extra["Block_info"] = extra_block_info
                event_list.append([event_time, eventType.LOG_ABR_EVENT], ["REQUEST", next_id, next_quality])
                return packet_list, event_list
        
        if packet.extra["ABR_info"]["offset"] + 1 == packet.extra["ABR_info"]["total"]:
            
            elapsed_time = event_time - self.last_block_time
            if elapsed_time <= self.buffer_time - self.play_time:
                self.play_time += elapsed_time
            else:
                self.play_time = self.buffer_time

            self.buffer_time += self.config["video"]["block_time"]

            download_rate = packet.extra["ABR_info"]["total"] * 1480 / (event_time - self.last_block_time)

            event_list = []
            event_list.append(([event_time, eventType.LOG_ABR_EVENT], ["RECEIVE", self.last_block_id, self.last_quality]))

            if self.buffer_time - self.play_time < self.buffer_max:

                packet_list = []
                if self.last_block_id + 1 < self.config["video"]["block_cnt"]:
                    block_list = self.config["blocks"][self.last_block_id + 1]
                    next_quality = self.choose_stream_block(block_list, self.last_quality, self.buffer_time, self.play_time, download_rate)
                
                    packet_list.append(Packet(destip = self.destip, srcip = self.srcip, create_timestamp = event_time, size = self.abr_request_size))
                    
                    next_id = self.last_block_id + 1
                    extra_abr_info = {
                        "time" : next_id,
                        "quality" : next_quality
                    }
                    extra_block_info = {
                        "Block_id" : -1,
                        "Block_offset" : -1,
                        "Block_TTL" : 10000,
                        "Block_create_time" : event_time,
                        "Block_priority" : 0
                    }
                    
                    self.last_block_id += 1
                    self.last_quality = next_quality
                    self.last_block_time = event_time

                    packet_list[0].extra["ABR_info"] = extra_abr_info
                    packet_list[0].extra["Block_info"] = extra_block_info
                    event_list.append(([event_time, eventType.LOG_ABR_EVENT], ["REQUEST", next_id, next_quality]))
                return packet_list, event_list
            
            else:
                return [], event_list
        
        return [], []

class abr_sevrer:

    def __init__(self,
                 config,
                 bytes_per_packet = 1500,
                 bytes_per_header = 20,
                 ) -> None:
        self.config = config
        self.bytes_per_packet = bytes_per_packet
        self.bytes_per_header = bytes_per_header

    def receive_packet(self, packet: Packet, event_time):
        block_time = packet.extra["ABR_info"]["time"]
        block_quality = packet.extra["ABR_info"]["quality"]
        size = self.config["blocks"][block_time][block_quality]
        packet_list = []
        for offset in range(int(np.ceil(size / (self.bytes_per_packet - self.bytes_per_header)))):
            packet_list.append(Packet(destip = packet.srcip, srcip = packet.destip, create_timestamp = event_time, size = self.bytes_per_packet))
            
            extra_abr_info = {
                "time" : block_time,
                "quality" : block_quality,
                "offset" : offset,
                "total" : int(np.ceil(size / (self.bytes_per_packet - self.bytes_per_header))),
                "create_time" : event_time
            }
            extra_block_info = {
                "Block_id" : -1,
                "Block_offset" : -1,
                "Block_TTL" : 10000,
                "Block_create_time" : event_time,
                "Block_priority" : 0
            }
            packet_list[offset].extra["ABR_info"] = extra_abr_info
            packet_list[offset].extra["Block_info"] = extra_block_info

        return packet_list