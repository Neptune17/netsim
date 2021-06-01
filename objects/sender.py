from config.constant import *

from objects.packet import Packet

from utils import *

class Sender:

    def __init__(self, name, ip, cc_solution, sche_solution, label_solution = None):

        self.name = name
        self.ip = ip
        
        self.out_links = []
        
        self.wait_for_select_packets = []
        self.wait_for_push_packets = []

        self.current_transport_seq = 0
        self.wait_for_ack_num = 0

        self.cc_solution = cc_solution
        self.sche_solution = sche_solution
        self.label_solution = label_solution

        self.cc_solution_cache = None
        self.sche_solution_cache = None
        self.packet_label_cache = None

        self.lock_time = -1.0
        self.lock_count = 0

    def add_link(self, src_ip, link):
        self.out_links.append(link)

    def generate_send_events(self, event_time):
        
        event_list = []

        if self.lock_count != 0:
            return event_list
        
        tar_time = event_time
        if self.lock_time > event_time:
            tar_time = self.lock_time

        if len(self.wait_for_push_packets) + self.wait_for_select_size() == 0:
            return event_list

        if len(self.wait_for_push_packets) == 0:
            event_list.append(([tar_time, eventType.SOLUTION_SENDER_SCHE_EVENT], [self.sche_solution.select_next_packet, self]))
        event_list.append(([tar_time, eventType.SOLUTION_SENDER_CC_EVENT_SEND], [self.cc_solution.send_event, self]))
        event_list.append(([tar_time, eventType.SENDER_EVENT], [self.send_packet]))

        self.lock_time = tar_time
        self.lock_count += 1

        return event_list

    def wait_for_select_size(self):
        size = 0
        for block_queue in self.wait_for_select_packets:
            size += len(block_queue)
        return size

    def add_block(self, block, event_time):

        flag_push_events = False

        if len(self.wait_for_push_packets) + self.wait_for_select_size() == 0:
            flag_push_events = True

        self.wait_for_select_packets.append(block.generate_packets())
        
        if flag_push_events:
            return self.generate_send_events(event_time)

        return []

    def send_packet(self, event_time):
        
        event_list = []

        if self.sche_solution_cache == -233:
            return event_list

        assert(self.cc_solution_cache is not None)
        assert(self.sche_solution_cache is not None or len(self.wait_for_push_packets) != 0)

        if "CWND" in self.cc_solution_cache:
            if self.wait_for_ack_num >= self.cc_solution_cache["CWND"]:
                event_list = []
                
                self.cc_solution_cache = None
                self.sche_solution_cache = None

                self.lock_count -= 1

                return event_list

        if len(self.wait_for_push_packets) != 0:
            packet = self.wait_for_push_packets.pop(0)
        else:
            packet = self.wait_for_select_packets[self.sche_solution_cache].pop(0)

        if packet.transport_offset == -1:
            packet.transport_offset = self.current_transport_seq
            self.current_transport_seq += 1

        if self.packet_label_cache is not None:
            packet.extra["label"] = self.packet_label_cache

        event_delay, send_delay, dropped = self.out_links[0].send_packet(packet, event_time)

        packet.dropped = dropped

        if packet.dropped:
            event_list.append(([event_time + packetConfig.DROP_PUNISHMENDT, eventType.PACKET_EVENT], [packet.srcip, packet]))
        else:
            event_list.append(([event_time + event_delay, eventType.PACKET_EVENT], [self.out_links[0].dest_ip, packet]))

        actual_delay = send_delay
        if "PADDING_RATE" in self.cc_solution_cache:
            actual_delay = max(packet.size / ((self.cc_solution_cache["PADDING_RATE"] / 8) * 10**6 ), send_delay)

        self.lock_count -= 1
        self.lock_time = event_time + actual_delay

        if len(self.wait_for_push_packets) + self.wait_for_select_size() != 0:
            event_list.extend(self.generate_send_events(event_time + actual_delay))

        packet.add_log(event_time, self.name, intip_to_strip(self.ip), "out", "")

        self.wait_for_ack_num += 1

        self.cc_solution_cache = None
        self.sche_solution_cache = None

        return event_list

    def receive_packet(self, packet, port_ip, event_time):

        event_list = []

        if packet.dropped:
            event_list.append(([event_time, eventType.SOLUTION_SENDER_CC_EVENT_DROP], [self.cc_solution.drop_event]))
            retrans_packet = packet.gen_retrans_packet(event_time)
            if len(self.wait_for_push_packets) + self.wait_for_select_size() == 0:
                event_list.extend(self.generate_send_events(event_time))
            self.wait_for_push_packets.append(retrans_packet)
        
        else:
            if packet.ack:
                packet.finish_timestamp = event_time
                data = {}
                data["inflight"] = self.wait_for_ack_num
                data["rtt"] = packet.extra['LOG_info'][-1][0] - packet.extra['LOG_info'][0][0] + packet.extra["delay"]
                if 'relabel' in packet.extra:
                    data["delivered"] = packet.extra['relabel']
                if 'rerouterlabel' in packet.extra:
                    data["ECN"] = packet.extra['rerouterlabel']
                event_list.append(([event_time, eventType.SOLUTION_SENDER_CC_EVENT_ACK], [self.cc_solution.ack_event, data]))
            else:
                packet.finish_timestamp = event_time

                ack_packet = Packet(packet.srcip, packet.destip, event_time, packetConfig.BYTES_PER_HEADER)
                ack_packet.ack = True
                ack_packet.transport_offset = packet.transport_offset
                ack_packet.extra["delay"] = packet.extra['LOG_info'][-1][0] - packet.extra['LOG_info'][0][0]
                if 'label' in packet.extra:
                    ack_packet.extra["relabel"] = packet.extra["label"]
                if 'routerlabel' in packet.extra:
                    ack_packet.extra["rerouterlabel"] = packet.extra["routerlabel"]
                push_event_flag = False
                if len(self.wait_for_push_packets) + self.wait_for_select_size() == 0:
                    push_event_flag = True
                self.wait_for_push_packets.append(ack_packet)

                if push_event_flag:
                    event_list.extend(self.generate_send_events(event_time))
                
                event_list.append(([event_time, eventType.BLOCK_EVENT_ACK], [packet]))

        packet.add_log(event_time, self.name, intip_to_strip(port_ip), "in", "")

        self.wait_for_ack_num -= 1
        event_list.extend(self.generate_send_events(event_time))

        event_list.append(([event_time, eventType.LOG_PACKET_EVENT], [packet]))

        return event_list