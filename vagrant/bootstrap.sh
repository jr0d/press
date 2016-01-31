#!/bin/bash

pip2 install jinja2
echo "Creating loopback disk"
dd if=/dev/zero of=/loop_disk bs=1MiB count=512
dd if=/dev/zero of=/loop_disk2 bs=1MiB count=512
losetup -D
losetup /loop_disk -f
losetup /loop_disk2 -f

