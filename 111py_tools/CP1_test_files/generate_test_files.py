import os

Filesize = '1K', '5K', '25K', '100K', '1M','10M'

for filesize in Filesize:
    os.system(f'fallocate -x -l {filesize} {filesize}.txt')
