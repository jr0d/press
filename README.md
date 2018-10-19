# Press
Image installer with custom partitioning

## Distro Support (baked in)

* RHEL/CentOS
    - 6
    - 7
* Ubuntu
    - 12.04 (LTS)
    - 14.04 (LTS)
    - 15.04
    - 16.04 (LTS)
    - 18.04 (LTS)
* Debian
    - 7 Wheezy
    - 8 Jessie
* Arch
* Gentoo

## Development
### Dependencies

* Linux 3.7+
* udisks
* gparted 3.0+

Python packages:

* python 2.7+, 3.3+
* requests
* pyyaml
* pyudev
* six

### Installation
    git clone git@github.com:jr0d/press.git
    cd press/
    git checkout -b 0.4.5 origin/0.4.5
    python setup.py develop

## User Configuration
Press is configured using a flexible key value data structure. The configuration can be presented in YAML, JSON, 
or serialized python dictionary object. The configuration tree is organized into the following top level keys:

* target: Explicit declaration of the post configuration module
* localization: language and timezone info
* image: image location, type, and checksum
* auth: Users, groups, and passwords
* bootloader: bootloader configuration and kernel commandline customization
* networking: Networking device interfaces and network configuration
* layout: Disk, partitioning, lvm, and file system configuration
* plugins: list of plugins to search for and activate

### Target
example:

    target: ubuntu_1404

This key tells press which post configuration code to use. The parameter will be optional in v0.5 and later where
targets will probe the image to determine what codes to run after the image has been deployed. For now (v0.4.x), it
is required.

Available targets:

    linux
    debian
    redhat
    enterprise_linux
    enterprise_linux_5
    enterprise_linux_6
    enterprise_linux_7
    ubuntu_1204
    ubuntu_1404
    ubuntu_1504
    arch
    gentoo

### Localization
example:
    
    localization:
        language: en_US.UTF-8
        timezone: US/Central

### Image
example:

    image:
        url: http://kickstart.rackspace.com/press/rax-dedicated-trusty-amd64-2015-04-21_16-33-21.tar.gz
        checksum:
            hash: acb5c18cb293fa1b1caa624d1336c2823b7e67fc
            method: sha1

- url: An http or https url or path to a file present on a local file system

- checksum: Optional field allowing for image verification
    - hash: hash used to verify the image after download
    - method: hash method (sha1, sha256, sha512, md5)

- keep: Optional, testing. Do not remove the image after downloading/copying


Press supports a variety of image formats and compression algorithms. For file based images 
(tar), files are extracted onto the installation target. For block based images (raw, qcow2, 
vmdk, raw), images are mounted and an rsync is performed onto the installation target.

### Bootloader
example:

    bootloader:
      target: first
      kernel_parameters:
        append:
          - biosdevname=0
          - net.ifnames=0
          - rdblacklist=bfa
          - nomodeset
        remove:
          - splash
          - quiet

- target: The disk reference to install the bootloader on. This can be a device node (/dev/sda),
 a device link (/dev/disk/by-label/ROOT), sysfs disk reference, or 'first' which references
 the first enumerated disk.
- kernel parameters: append or remove kernel command line options via bootloader configuration

At present, the bootloader press installs is dependent on the default bootloader used by the 
target distribution / operating system. 


It is common for images created for paravirtualized environments and containers 
(chroot/cgroups) to not include a bootloader or kernel images/modules. Thus, press does not
assume these packages will be present and will attempt to install any packages needed to boot
the device during post configuration.


EFI bootloader support will be added in v0.5 "Wishful Thinking"


### Networking
example:

    networking:
      hostname: 191676-www.kickstart.rackspace.com
      dns:
        search:
          - kickstart.rackspace.com
        nameservers:
          - 10.10.1.1
          - 10.10.1.2
      interfaces:
        -
          name: EXNET
          ref:
            type: dev # mac, pci, smbios, irq,
            value: eth0 # or eth0, 00:00:00:ff:ff:ff, em0, p4p1, 1
          missing_ok: True
        -
          name: SNET
          ref:
            type: dev
            value: eth1
          missing_ok: True
    
      networks:
      -
        interface: EXNET
        ip_address: 10.10.22.120
        netmask: 255.255.255.0
        gateway: 10.10.22.1
        routes:
          -
            cidr: 10.22.56.0/25
            gateway: 10.22.56.1
      -
        interface: SNET
        ip_address: 10.22.10.55
        netmask: 255.255.255.0
        routes:
          -
            cidr: 10.22.56.0/25
            gateway: 10.22.56.1
### Layout
example:
    
    use_fiber_channel: false
    loop_only: false
    partition_tables:
    -
      disk: first
      label: msdos
      partitions:
      -
        name: boot
        flags:
          - boot
        size: 500MiB
        mount_point: /boot
        file_system:
          type: ext4
          label: BOOT
      -
        name: pv0
        flags:
          - lvm
        size: 100%FREE
    
    volume_groups:
    -
      name: vglocal
      physical_volumes:
        - pv0
      pe_szie: 4MiB
      logical_volumes:
          -
            name: swap00
            size: 2GiB
            file_system:
              type: swap
              label: SWAP
          -
            name: tmp00
            size: 2GiB
            mount_point: /tmp
            file_system:
              type: ext4
              label: TMP
              superuser_reserve: 1%
              mount_options:
                - defaults
                - noexec
                - nosuid
                - nodev
          -
            name: root00
            size: 35%FREE
            mount_point: /
            file_system:
              type: ext4
              label: ROOT
              superuser_reserve: 1%
          -
            name: log00
            size: 10%FREE
            mount_point: /var/log
            file_system:
              type: ext4
              label: LOG
              superuser_reserve: 1%

### Repositories

example:

    repos:
      -
        name: Example Mirror
        mirror: http://mirror.rackspace.com/example/mirror/
        gpgkey: http://mirror.rackspace.com/example/mirror/GPGKEY

Debian targets may specify a path to a local key, RedHat targets require a URL.


## Invoking
### entry
### Logging
## Plugins
## Testing
### Vagrant
