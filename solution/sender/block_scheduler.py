class BlockScheduler:

    def select_next_packet(self, sender, event_time):
        
        for i, block_queue in enumerate(sender.wait_for_select_packets):
            if len(block_queue) != 0:
                sender.sche_solution_cache = i
                return 
        
        return 