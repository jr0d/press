$ python test.py 
124G
133143986176
15G
139G
<Size> : 149250113536b
139G
142336M
root [ ext4, 130G ]
Making test Layout:

Adding partion using add_partition_percent('percent_example', 'ext4', 56)
Success!
Adding partition using add_partition_fill('left_over', 'ext4')
Sucess!
256G / 256G
(0, 'boot')
(1, 'tmp')
(2, 'root')
(3, 'opt')
(4, 'percent_example')
(5, 'left_over')
Partition Table (gpt):
Disk Size: 274877906944 (256G)
[boot]  ext3    500M
[tmp]   ext3    2G
[root]  ext4    130G
[opt]   ext4    100G
[percent_example]   ext4    13G
[left_over] ext4    10G
            remaining: 256G / 256G

