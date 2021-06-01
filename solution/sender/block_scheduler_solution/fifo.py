from solution.sender.block_scheduler import BlockScheduler

class FIFO(BlockScheduler):

    def select_next_packet(self, sender, event_time):
        
        for i, block_queue in enumerate(sender.wait_for_select_packets):
            if len(block_queue) != 0:
                if block_queue[0].extra["Block_info"]["Block_TTL"] + block_queue[0].extra["Block_info"]["Block_create_time"] < event_time:
                    sender.wait_for_select_packets.pop(i)
                    continue
                sender.sche_solution_cache = i
                return 
        
        if sender.sche_solution_cache == None:
            sender.sche_solution_cache = -233

        return 