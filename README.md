# IOTraceCollector
A FUSE based file system wrapper to collect IO events

I use this to collect io access pattern from databases, K/V stores and (parallel) file systems. 

# Requirements
libfuse and fusepy

# Usage 

Tested with python2

    Terminal1$ ./io_trace.py -m mnt -b data 

    Terminal2$ mkdir mnt/hello
    Terminal2$ echo "Hello World!" > mnt/hello/world.txt

This results in two directories **data/trace** and **data/root** with: 

    more data/root/hello/world.txt 
    Hello World!

and

```more data/trace/20181019-131053.trace 
    
20181019-131053.774874:  GETATTR: path=/
20181019-131053.775285:  GETATTR: path=/.xdg-volume-info
20181019-131053.775397:   ACCESS: path=/; mode=4
20181019-131053.775475:  GETATTR: path=/autorun.inf
20181019-131053.775543:  GETATTR: path=/.Trash
20181019-131053.775635:  GETATTR: path=/AACS
20181019-131053.775730:  GETATTR: path=/BDSVM
20181019-131053.775800:  GETATTR: path=/BDMV
20181019-131053.776151:  READDIR: path=/
20181019-131053.776264:  GETATTR: path=/.Trash-1000
20181019-131053.776348:  GETATTR: path=/BDMV
20181019-131053.776404:  READDIR: path=/
20181019-131053.776515:  GETATTR: path=/BDMV
20181019-131053.776626:  READDIR: path=/
20181019-131053.776732:  READDIR: path=/
20181019-131053.776818:  READDIR: path=/
20181019-131053.776901:  READDIR: path=/
20181019-131053.776983:  READDIR: path=/
20181019-131053.777063:  READDIR: path=/
20181019-131053.777143:  READDIR: path=/
20181019-131053.777223:  READDIR: path=/
20181019-131053.777303:  READDIR: path=/
20181019-131053.777394:  READDIR: path=/
20181019-131053.777473:  READDIR: path=/
20181019-131053.777553:  READDIR: path=/
20181019-131053.777686:  READDIR: path=/
20181019-131053.777768:  READDIR: path=/
20181019-131053.777846:  READDIR: path=/
20181019-131053.777925:  READDIR: path=/
20181019-131053.778004:  READDIR: path=/
20181019-131053.778086:  READDIR: path=/
20181019-131053.778165:  READDIR: path=/
20181019-131053.778243:  READDIR: path=/
20181019-131053.779023:  READDIR: path=/
20181019-131053.779222:  GETATTR: path=/autorun.inf
20181019-131100.859571:  GETATTR: path=/hello
20181019-131100.859710:    MKDIR: path=/hello; mode=493
20181019-131100.859797:  GETATTR: path=/hello
20181019-131104.958900:  GETATTR: path=/hello
20181019-131104.959070:  GETATTR: path=/hello/world.txt
20181019-131104.959175:   CREATE: path=/hello/world.txt; mode=33188; fi=None
20181019-131104.959256:  GETATTR: path=/hello/world.txt
20181019-131104.959361:    FLUSH: path=/hello/world.txt
20181019-131104.961024:    WRITE: path=/hello/world.txt; offset=0; length_buf=13
20181019-131104.961096:    FLUSH: path=/hello/world.txt
20181019-131104.962715:  RELEASE: path=/hello/world.txt
```

The trace file can be written synchronously for debugging purposes or asynchronous, which is faster and less invasive. However, there is still some overhead due to the FUSE layer, the python interpreter and the trace writing. The timings might not reflect the real application behavior.  
