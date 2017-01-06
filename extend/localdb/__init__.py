
# localdb base config

config = {
    'database': {
        'path': '/data/localdb_tax/',  # path should be exist,the root dir for localdb
        'tables': ['node_info', 'block', 'block_header', 'block_records', 'vote', 'vote_header'],  # the localdb dirs
        'block_size': None,  # block size (in bytes)
        'write_buffer_size': 512 << 20,  # (int) – size of the write buffer (in bytes) 512MB
        'max_file_size': 512 << 20,  # (int) – size of the single ldb file(in bytes) 1M~1G
        'max_open_files': None,  # (int) – maximum number of files to keep open
        'lru_cache_size': None,  # lru_cache_size (int) – size of the LRU cache (in bytes)
        'compression': 'snappy',  # whether to use Snappy compression (enabled by default)

    },
    'encoding': 'utf-8',  # the encoding for bytes
}
