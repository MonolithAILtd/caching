# Caching
This document covers the process of Monolith's caching module. 

## General Mechanism 
The module hosts worker objects. When a worker object is initiated it instantly creates a directory with a unique id. This is where your temp files can be stored. Each worker has its own unique cache directory. If the python program crashes, comes to an end, or gets deleted in the program, the cach directory is instantly deleted. 

## Structure
The following structure defines the module:

```
├── README.md
├── __init__.py
├── cache
│   ├── __init__.py
├── errors.py
├── s3_worker.py
├── singleton.py
└── worker.py


```
The ```CacheManager``` is stored in the ```__init__.py```. This manages the interaction between the user and workers to ensure that no caches are hiding in the memory. Workers can be directly imported and used if you want but it's not recommended. 

## Use
The ```CacheManager``` only supports one worker, and cleans up everytime you start a new cache or session. The ```cache_path``` is a dynamic property to everytime it's called it will always reference the live current cache. As a result, it's hard to go wrong using the ```CacheManager```. Below is how to use ```CacheManager``` sessions with object being some random objest your working with:

```python
from caching import CacheManager

example = CacheManager()

with example:
	object.save(example.cache_path)
	object.load(example.cache_path)
	# do more logic here with loading and saving temp files 
```
Once you go out of the indent the cache is instantly cleaned up and ```example.cache_path) will return nothing. If you want to use your cache in your object or throughout your script use the following approach:

```python
from caching import CacheManager

example = CacheManager()

example.create_cache()

 # do your logic here

example.wipe_cache()
```
Again all caches get wiped if the program crashes or finishes, or if all memory pointers to the worker are gone. 

### Meta Data
Caches support meta data which is a stored in a json file. The meta data can be accessed by the ```meta``` property 
for the ```CacheManager``` object which returns a dictionary of what's stored in the ```meta.json``` file in the 
cache directory. Concurrency could be an issue if the meta is used a lot. Ideally, it shouldn't be. Redis caching 
should be used if you're reading and writing a lot in the local_cloud. The metadata in the cache should be used to 
insert metadata about the cache like a task_id associated with the cache. 

### lock
The cache can be locked. This can be achieved by firing the ```lock()``` function for the ```CacheManager``` object.
This stops the worker from wiping the cache at the end of it's life cycle. IT'S IMPORTANT THAT YOU HAVE A CLEAN UP 
MECHANISM IF YOU ENABLE THIS. PLEASE SPEAK TO MAXWELL WHEN IMPLEMENTING A LOCK.

## To Do
This module is small and simple, has scope, and can be used in places outside the server such as exploratory data science using notebooks:

- **multiple workers**: Right now this isn't needed and I feel and introducing it before it's needed with just add extra complexity. However, it is a possibility later on. A cache manager could manage a pool of workers. 
-  **open source**: This module is not going to make or break our company. Other people having it will not damage us in a business sense. There is potential gain from releasing this to an open source in terms of a bit on nice publicity and potentially other developers contributing and improving it. 
- **lock for S3**: Right now only local file locks for caching work. 
- **enable s3**: Some features for s3 are not supported 
- **functional tests for s3**: Functional tests that are connecting to s3 need to be done
