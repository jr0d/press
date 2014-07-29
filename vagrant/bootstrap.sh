#!/bin/bash

echo "Creating loopback disk"
dd if=/dev/zero of=/loop_disk bs=256MiB count=16
losetup -D
losetup /loop_disk -f
