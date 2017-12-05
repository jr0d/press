#!/bin/bash

yum install -y epel-release
yum update -y
yum install -y python-devel python-pip python-yaml
pip install jinja2 requests pyudev

echo "Creating loopback disk"
dd if=/dev/zero of=/loop_disk bs=1MiB count=512
dd if=/dev/zero of=/loop_disk2 bs=1MiB count=512
losetup -D
losetup /loop_disk -f
losetup /loop_disk2 -f

