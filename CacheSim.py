from math import log2
''' Linked-list data structure to sava the cache sets '''
class LinkedList :
    def __init__(self, head=None) :
        self.head = head
        self.tail = head      
    def add_node(self, node) :
        if self.head is None and self.tail is None :
            self.head = node
            self.tail = node
        else :    
            self.tail.next = node
            self.tail = node    
    def node_to_tail(self, data) : 
        curr = self.head
        prev = None
        while curr.data != data :
            prev = curr
            curr = curr.next
        if curr == self.head and curr.next is not None : self.head = curr.next
        elif curr == self.tail : return
        else : prev.next = curr.next
        self.tail.next = curr
        self.tail = curr
        self.tail.next = None 
''' Each node of the linked-list refers to a cache-line '''          
class Node :
    def __init__(self, data) :
        self.data = data
        self.next = None
class Cache :
    def __init__(self, cache_size, block_size, associativity, write_policy, write_miss_policy) :
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_policy = write_policy
        self.write_miss_policy = write_miss_policy
        self.cache_sets = []   
        for i in range(cache_size // (associativity * block_size)) :
            self.cache_sets.append(LinkedList())
            for j in range(associativity) : self.cache_sets[i].add_node(Node(CacheLine(block_size)))
        self.off_set_len = int(log2(self.block_size))
        self.index_len = int(log2(len(self.cache_sets)))         
    def in_cache(self, binary_memory_address) :
        cache_block = 0
        index_start = 32 - self.off_set_len - self.index_len
        index_end = 32 - self.off_set_len
        if self.associativity != (self.cache_size // self.block_size) : cache_block = int(binary_memory_address[index_start:index_end], 2) % len(self.cache_sets)  
        cache_set = self.cache_sets[cache_block]
        curr = cache_set.head
        while curr is not None :
            if curr.data.tag == binary_memory_address[0:index_start] : return True, cache_set, curr
            curr = curr.next
        return False, cache_set, None    
    def load(self, d_i, binary_memory_address) :
        global fetch, copies_back, data_replaces, instruction_replaces
        hit, cache_set, cache_block = self.in_cache(binary_memory_address)
        if hit :
            cache_set.node_to_tail(cache_block.data)
            return 1
        fetch +=  self.block_size // 4
        if cache_set.head.data.dirty : 
            copies_back += self.block_size // 4 
            cache_set.head.data.dirty = False
        if cache_set.head.data.tag != '' :
            if d_i : instruction_replaces += 1
            else : data_replaces += 1         
        index_start = 32 - self.off_set_len - self.index_len                   
        cache_set.head.data.tag = binary_memory_address[0:index_start]
        cache_set.node_to_tail(cache_set.head.data)
        return 0
    def write(self, d_i, binary_memory_address) :
        global copies_back
        hit, cache_set, cache_block = self.in_cache(binary_memory_address)
        if self.write_policy == 'wb' and self.write_miss_policy == 'wa' :
            if hit : 
                cache_block.data.dirty = True
                return 1       
            self.load(d_i, binary_memory_address)
            cache_set.tail.data.dirty = True
        if self.write_policy == 'wb' and self.write_miss_policy == 'nw' :
            if hit :
                cache_block.data.dirty = True
                return 1
            copies_back += 1   
        if self.write_policy == 'wt' and self.write_miss_policy == 'wa' :
            copies_back += 1
            if hit : return 1
            self.load(d_i, binary_memory_address)
        if self.write_policy == 'wt' and self.write_miss_policy == 'nw' :
            copies_back += 1
            if hit : return 1
        return 0            
class CacheLine :
    def __init__(self, size) :
        self.size = size
        self.dirty = False
        self.tag = ''
instruction_hits, data_hits, fetch, data_accesses, instruction_accesses, data_replaces, instruction_replaces, copies_back = 0, 0, 0, 0, 0, 0, 0, 0     
instruction_cache_size, data_cache_size, cache_size = 0, 0, 0
cache, instruction_cache, data_cache = None, None, None
block_size, unified_seperated, associativity, write_policy, write_miss_policy = input().split(' - ')
if int(unified_seperated) : instruction_cache_size, data_cache_size = map(int, input().split(' - '))
else : cache_size = int(input())  
if int(unified_seperated) :
    instruction_cache = Cache(instruction_cache_size, int(block_size), int(associativity), write_policy, write_miss_policy)
    data_cache = Cache(data_cache_size, int(block_size), int(associativity), write_policy, write_miss_policy)
else : cache = Cache(cache_size, int(block_size), int(associativity), write_policy, write_miss_policy) 
while True :
    line = input().split()
    if not len(line) : break
    binary_memory_address = '{:0=32}'.format(int(bin(int(line[1], 16))[2:]))
    if line[0] is '0' : 
        if int(unified_seperated) : data_hits += data_cache.load(0, binary_memory_address)
        else : data_hits += cache.load(0, binary_memory_address)
        data_accesses += 1
    elif line[0] is '1' : 
        if int(unified_seperated) : data_hits += data_cache.write(0, binary_memory_address) 
        else : data_hits += cache.write(0, binary_memory_address)
        data_accesses += 1
    elif line[0] is '2' :  
        if int(unified_seperated) : instruction_hits += instruction_cache.load(1, binary_memory_address) 
        else : instruction_hits += cache.load(1, binary_memory_address)
        instruction_accesses += 1
if int(unified_seperated) : cache = data_cache
''' Cleaning dirty blocks '''
for cache_set in cache.cache_sets :
    curr = cache_set.head
    while curr is not None :
        if curr.data.dirty : copies_back += int(block_size) // 4
        curr = curr.next    
print('***CACHE SETTINGS***')
print('Unified I- D-cache' if not int(unified_seperated) else 'Split I- D-cache')
print('Size: ' + str(cache_size) if not int(unified_seperated) else ('I-cache size: ' + str(instruction_cache_size) + '\n' + 'D-cache size: ' + str(data_cache_size)))  
print('Associativity: ' + str(associativity))
print('Block size: ' + str(block_size))
print('Write policy: ' + ('WRITE BACK' if write_policy == 'wb' else 'WRITE THROUGH'))
print('Allocation policy: ' + ('WRITE ALLOCATE\n' if write_miss_policy == 'wa' else 'WRITE NO ALLOCATE\n'))
print('***CACHE STATISTICS***')
print('INSTRUCTIONS')
print('accesses: ' + str(instruction_accesses))
print('misses: ' + str(instruction_accesses - instruction_hits))
print('miss rate: ' + ('{:.4f}'.format((instruction_accesses - instruction_hits) / instruction_accesses) if instruction_accesses else '0.0000') + ' (hit rate ' + ('{:.4f}'.format(instruction_hits / instruction_accesses) if instruction_accesses else '0.0000') + ')')
print('replace: ' + str(instruction_replaces))
print('DATA')
print('accesses: ' + str(data_accesses))
print('misses: ' + str(data_accesses - data_hits))
print('miss rate: ' + ('{:.4f}'.format((data_accesses - data_hits) / data_accesses) if data_accesses else '0.0000') + ' (hit rate ' + ('{:.4f}'.format(data_hits / data_accesses) if data_accesses else '0.0000') + ')')
print('replace: ' + str(data_replaces))
print('TRAFFIC (in words)')
print('demand fetch: ' + str(fetch))
print('copies back: ' + str(copies_back))