# "Forgetful Tyrannosaurus" release v0.4.5
* Hooks
* Repository manager plugin
* authorized_keys support
* ntp server and system time configuration

# "Prime Time" release v0.4.9
* SSD detection
    - Changes to file system mount options (discard)
    - SSD "Overprovisioning" https://www.thomas-krenn.com/en/wiki/SSD_Over-provisioning_using_hdparm
* EFI bootloader support
* Disto Support
    - RHEL 6/7
    - Debian 7/8
    - Ubuntu 12.04, 14.04, 15.04
    - Gentoo
    - Arch
* kexec booting
* Clean up configuration disk references
    - remove 'any'
    - allow reference by index
        - index:0
        - index:1...index:n
* Easy to extend plugin interfaces
    - Plugins can be downloaded and loaded at runtime
* Seriously stable partitioning operations
* Clean up structure/models/generators so they make more sense
* Full "end user" configuration documentation
* Tests
* Post Target discovery, import, and registration
    - Find a better name for this, they are the things that run OS specific post actions

# "Wishful Thinking" release v0.5.0
* Move disk scanning and bare metal operation to disk object
    - MockDisk() for testing
* Probe functions in post configuration targets, allowing the user to omit a target
declaration
* cloud-init support
* Raw and QCOW2 image support
* Pull images from docker hub
* Glance support
* Distro Support
    - SLES
    - Oracle EL
    - CORE OS
    - Docker Box image
* OS Support (Pending discovery)
    - Citrix XenServer
    - ESX
    - FreeBSD/OpenBSD
    - Microsoft Windows

# "Elminster" release v1.0
* Redesign object structure
    - Class interfaces, ie... IPartitionContainer, when implemented, the class can hold a Partition object, or something along those lines
