#!/bin/bash
# Jared Rodriguez
# 2009

VERSION='0.2_beta'
if [ -e /tmp/lock ]
then
	echo wtf!
	/bin/bash -l
fi

touch /tmp/lock

ntpdate 10.6.3.55
clear

echo 'Rackspace Deployment System' $VERSION
echo
echo 'Installing Gentoo 10.1 x86_64...'
sleep 5

device=`dmsetup table | head -1 | awk '{print $1}' | sed -e 's/\([h|s]da\)[0-9]:/\1/g'`

if [ $device == 'No' ]; then
  device='sda'
fi

parted="parted --script /dev/${device}"
echo
echo Removing previous image...
for i in `parted --script /dev/${device} print | awk '{print $1}' | egrep  '^[0-9]$'`
 do 
   echo removing partition $i
   $parted rm $i
done

echo
echo Unmapping disks...
for part in `dmsetup table | awk -F ':' '{print $1}'`
 do
   echo removing partion $part
   dmsetup remove $part
 done

sleep 5

$parted mklabel gpt
$parted mkpart primary 1 512
$parted mkpart primary 512 2560
$parted mkpart primary 2560 3584
$parted mkpart primary 3584 15872

$parted print
clear
echo Attempting to make file systems. 
sleep 5

mkfs.ext4 -L BOOT /dev/${device}1
if [ $? -ne '0' ]; then
 echo 'bad things'
 read things
fi
mkswap -L SWAP /dev/${device}2
mkfs.ext4 -L TEMP /dev/${device}3
mkfs.ext4 -L ROOT /dev/${device}4

mkdir /mnt/gentoo
mount /dev/${device}4 /mnt/gentoo
mkdir /mnt/gentoo/boot
mkdir /mnt/gentoo/dev
mknod /mnt/gentoo/dev/null c 1 3
mknod /mnt/gentoo/dev/console c 5 1
mkdir /mnt/gentoo/tmp
mkdir /mnt/gentoo/proc

mount -o bind /dev/ /mnt/gentoo/dev
mount -t proc none /mnt/gentoo/proc
mount /dev/${device}1 /mnt/gentoo/boot
mount /dev/${device}3 /mnt/gentoo/tmp

wget http://10.6.3.55/rh/gallantfx/bar-1.4-src.tar.bz2 -O /tmp/bar.tar.bz2
cd /tmp
tar xjf bar.tar.bz2
mv bar-1.4/bar .

wget http://10.6.3.55/gentoo/gentoo-10.1.x86_64.tar.bz2 -O /mnt/gentoo/gentoo-10.1.x86_64.tar.bz2

clear
echo Extracting Image. Please wait.
/tmp/bar -n /mnt/gentoo/gentoo-10.1.x86_64.tar.bz2 | tar xjpf - -C /mnt/gentoo

chmod 1777 /mnt/gentoo/tmp
#rm /mnt/gentoo/root/kickstart/gentoo_post.py
#wget http://10.6.3.55/rh/jared/gentoo_post.py -O /mnt/gentoo/root/kickstart/gentoo_post.py


## pass date to the chroot to avoid time shifts
DATE=`date`
echo attempting to set hwclock
hwclock --set --date "${DATE}"
chroot /mnt/gentoo /root/post.sh "${DATE}" ${device}

rm /mnt/gentoo/gentoo-10.1.x86_64.tar.bz2

umount /mnt/gentoo/dev
umount /mnt/gentoo/proc
umount /mnt/gentoo/tmp
umount /mnt/gentoo/boot
umount /mnt/gentoo

clear
echo -e '\n\nImage deployment complete.'
echo Rebooting.
reboot


