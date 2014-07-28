#!/bin/bash

echo "Server = http://mirror.rackspace.com/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

pacman -Syy --noconfirm python2-pip python2-yaml
pushd /vagrant
python2 setup.py develop
losetup disk -f
