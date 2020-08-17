# Cache Simulator

A simple command-line simulation for computer cache memory without implementing the main memory.<br>
So as you may expect we do not have real data, we just only deal with memory addresses.<br>

**The first two lines of the input must be in the given format**

```
<block size> - <architecture> - <associativity> - <write policy> - <write_miss policy>
<cache size> - <second cache size(if necessary)>
```
\<block size>: Should be in power of 2<br>
\<architecture>: 0 for Von_Neumann (unified I-D cache) - 1 for Harvard (split I-D cache)<br>
\<associativity>: Should be in power of 2<br>
\<write policy>: (wt = Write_Through) - (wb = Write_Back)<br>
\<write_miss policy>: (wa = Write_Allocate) - (nw = No_Write_Allocate(Write Around))<br>
\<cache size>: Should be in power of 2<br>

**After the first two lines, we have our requests with this format**

```
<request type> <memory address>
```

Allowed request types are seperated by 0, 1 and 2: <br>
```
0 : Data load
1 : Data store
2 : Instruction load(in harvard architecture)
```
## Sample input
``` 
16 - 1 - 1 - wb - wa
128 - 128
0 00000 data read miss (compulsory)
2 10000 instruction miss (compulsory, replaces 00000 if assoc=1 & unified)
2 20000 instruction miss (compulsory, replaces 00000 if assoc=2 & unified)
2 30000 instruction miss (compulsory, replaces 00000 if assoc=2 & unified)
2 40000 instruction miss (compulsory, replaces 00000 if assoc=4 & unified)
0 00000 data read miss (miss if assoc=1 & unified)
2 10001 instruction miss (miss if assoc=1 & unified)
```
## Sample output
```
***CACHE SETTINGS***
Split I- D-cache
I-cache size: 128
D-cache size: 128
Associativity: 1
Block size: 16
Write policy: WRITE BACK
Allocation policy: WRITE ALLOCATE

***CACHE STATISTICS***
INSTRUCTIONS
accesses: 5
misses: 5
miss rate: 1.0000 (hit rate 0.0000)
replace: 4
DATA
accesses: 2
misses: 1
miss rate: 0.5000 (hit rate 0.5000)
replace: 0
TRAFFIC (in words)
demand fetch: 24
copies back: 0
```