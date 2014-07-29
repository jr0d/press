#!/bin/bash

ENVDIR='/root/env'
ENVNAME='press'

echo "Server = http://mirror.rackspace.com/archlinux/\$repo/os/\$arch" > /etc/pacman.d/mirrorlist

pacman -Syy
pacman -S --noconfirm python2-pip
pip2 install virtualenv
if [ ! -d "$ENVDIR" ]; then
	mkdir "$ENVDIR"
fi
pushd "$ENVDIR"

if [ ! -f "$ENVDIR/$ENVNAME/bin/activate" ]; then
	virtualenv -p /usr/bin/python2 press
fi

. "$ENVDIR/$ENVNAME/bin/activate"

pip install ipython
popd
pushd /vagrant
python setup.py develop
losetup disk -f
popd

