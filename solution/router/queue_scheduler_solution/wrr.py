from numpy.lib.function_base import angle
from solution.router.queue_scheduler import QueueScheduler

class WRR(QueueScheduler):

    def __init__(self):
        super().__init__()
        self.rr_index = 0
        self.rr_label = {
            0: 3,
            1: 1,
            2: 3,
            3: 2,
            4: 3,
            5: 2
        }
        self.rr_max = 6

    def packet_out_queue(self, router, port_id):
        
        router.queue_sche_solution_cache_out = None

        if len(router.queues[port_id][0]) != 0:
            router.queue_sche_solution_cache_out = 0
            return 
        while(True):
            if len(router.queues[port_id][self.rr_label[self.rr_index]]) != 0:
                router.queue_sche_solution_cache_out = self.rr_label[self.rr_index]
            self.rr_index += 1
            if self.rr_index == self.rr_max:
                self.rr_index = 0
            if router.queue_sche_solution_cache_out is not None:
                break

        return 
    
    def packet_in_queue(self, router, packet):
        
        if packet.ack:
            router.queue_sche_solution_cache_in = 0
        else:
            router.queue_sche_solution_cache_in = packet.extra["Block_info"]["Block_priority"]
        return