class QueueScheduler:

    def packet_out_queue(self, router, port_id):
        
        if len(router.queues[port_id][0]) != 0:
            router.queue_sche_solution_cache_out = 0
        else:
            router.queue_sche_solution_cache_out = 1

        return 
    
    def packet_in_queue(self, router, packet):
        
        if packet.ack:
            router.queue_sche_solution_cache_in = 0
        else:
            router.queue_sche_solution_cache_in = 1
        return