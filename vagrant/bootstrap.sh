#!/bin/bash

echo "Server = http://mirror.rackspace.com/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

pacman -Syy
pacman -S --noconfirm python2-pip
pip2 install virtualenv
if [ ! -d "env" ]; then
	mkdir env
fi
pushd env
if [ ! -f "press/bin/activate" ]; then
	virtualenv -p /usr/bin/python2 press
fi
. press/bin/activate

pip install ipython
popd
pushd /vagrant
python setup.py develop
losetup disk -f
popd

chown -R vagrant: env