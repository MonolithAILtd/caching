# Monolith Caching

Using License Apache 2.0 

This module manages caching for directories. Using this package you are able to create tempory
directories, access meta data around the directory, and cache in AWS S3. The tempory directories 
are wiped once the program crashes or finishes unless the cache is locked. Caches can also be managed
across threads by configuring a Redis port.  



## Usage  
Caches are managed by a ```CacheManager``` which can be initialized by the following code:

```python
from monolithcaching import CacheManager

manager = CacheManager(local_cache_path="/path/to/local/directory/for/all/caches")
manager.create_cache()
```
This creates a local cache. If we wanted to point to an existing cache we would have set the 
```existing_cache``` parameter to the path of the cache with the following code:

```python
manager.create_cache(existing_cache="/path/to/existing/cache")

cache_path = manager.cache_path
```

### Connecting to S3 AWS
Connecting to S3 for caching can be done by the following code:

```python
manager = CacheManager(s3_cache_path="/path/to/local/directory/for/all/caches", s3=True)
```

### Connecting to Redis 
Connecting to Redis enables the cache manager to keep track of all caches and the amount of open cache 
processes pointing to each cache. This enables us to do safe caching over multiple threads, processes,
or servers (if you are caching in S3). If the cache is not locked, then when the count turns to zero,
the cache is wiped. We can connect to Redis by configuring the ```port``` and ```host``` parameters 
as seen in the following code:

```python
manager = CacheManager(local_cache_path="/path/to/local/directory/for/all/caches", port=6379, 
                       host="localhost")
```

### Locking Cache 
We can lock the cache, this is where the cache remains even if the program finishes or crashes. This 
can be done by the following code:

```python
manager.lock_cache()
manager.unlock_cache()
```

### Meta Data 
You can access meta data about the cache in the form of a dict with the following command:
```python
meta = manager.meta 
```
This contains the datetime of when the cache was made, and the ID of the cache. You can add meta 
data to the meta via the following command:

```python
manager.insert_meta(key="some key", value="some value")
```

```
pip install git+ssh://git@github.com/MonolithAILtd/caching.git@master#egg=caching
```

```
pip install git+https://github.com/MonolithAILtd/caching#egg=caching
```

# Contributing 
This repo is still fairly new so contributing will require some communication as we are currently working on supporting 
thread safe caching locally without the need for ```Redis```. You can contact with ideas and outline for a feature 
at ```maxwell@monolithai.com```.

Writing code is not the only way you can contribute. Merely using the module is a help, if you come across any issues 
feel free to raise them in the issues section of the Github page as this enables us to make the module more stable.
If there are any issues that you want to solve, your pull request has to have documentation, 100% unit test coverage 
and functional testing. 
