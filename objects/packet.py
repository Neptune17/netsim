from utils import *

class Packet:

    def __init__(self,
                 destip,
                 srcip,
                 create_timestamp,
                 size):
        
        self.packet_id = Packet._get_next_packet()

        self.destip = destip
        self.srcip = srcip
        self.create_timestamp = create_timestamp
        self.size = size

        self.is_dropped = False
        self.ack = False
        self.finish_timestamp = float("inf")
        self.transport_offset = -1
        self.extra = {
            "Block_info" : None,
            "LOG_info" : None
        }

    def get_simplified_packet_info(self):
        return {
            "Packet_id" : self.packet_id,
            "Src_IP" : intip_to_strip(self.srcip),
            "Dest_IP" : intip_to_strip(self.destip),
            "Create_timestamp" : self.create_timestamp,
            "Finished_timestamp" : self.finish_timestamp,
            "Size" : self.size,
        }
    
    def get_full_packet_info(self):
        return {
            "Packet_id" : self.packet_id,
            "Src_IP" : intip_to_strip(self.srcip),
            "Dest_IP" : intip_to_strip(self.destip),
            "Create_timestamp" : self.create_timestamp,
            "Finished_timestamp" : self.finish_timestamp,
            "Size" : self.size,
            "Is_dropped" : self.is_dropped,
            "Ack" : self.ack,
            "Transport_offset" : self.transport_offset,
            "extra" : self.extra
        }

    def gen_retrans_packet(self, current_time):
        new_packet = Packet(self.destip, self.srcip, current_time, self.size)
        new_packet.transport_offset = self.transport_offset
        new_packet.extra = self.extra
        new_packet.ack = self.ack
        return new_packet

    def __str__(self):
        return str(self.get_simplified_packet_info())
    
    _packet_id = 1

    @classmethod
    def _get_next_packet(cls):
        result = cls._packet_id
        cls._packet_id += 1
        return result
    
    @classmethod
    def reset_packet_id(cls):
        Packet._packet_id = 1
    
    def __lt__(self,other):
      return self.packet_id < other.packet_id