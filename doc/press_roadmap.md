## Press Development Roadmap v0.4a ( release prototype codename: The Precious )


### Tag line(s):

1. Partitioning for humans
2. One installer to rule them all

### Objectives:

Create a highly configurable disk partition and logical volume interface for use during initial operating system deployment.

### Justification:

Allow for more accurate generation of partition tables and logical volumes per customer supplied configuration. Partitioning is highly visible and a huge pain point for customers who expect their build requirements to be met.

Greatly simplify OS Deployment process by providing a means to deploy any OS with one utility.

### Milestones:

* Parted interface (done)
    * Support for gpt and mbr
    * transparently handles disk alignment
* lvm interface (done)
* class model (75%)
* Configuration parsers
    * yaml configuration parser
    * json configuration parser
    * CORE configuration parser
* Images
    * tar ball image support
    * qcow2 image support (onMetal parity sans nova integration)
    * image creation process (iPXE kserver build farm?)
* 'post install' processes
    * user creation
    * network configuration
    * custom script definition
    * bootloader configuration
    * initramfs rebuild, hardware tweaks
* UEFI support

### Implied components:

* Tests
* Unified logging
* Documentation
    * Development
    * User
* Build scripts


### Timeline (tentative, not AGT approved (yet))

#### June 16th  – Prototype 001:
* deploy from static yaml configuration
* deploy Ubuntu tar ball image
* configure users, networking, launch a simple custom scripts

#### June 30th – Prototype 002:
* Dynamically generated yaml configuration from CORE
* Deploy from CentOS cloud image (qcow2)

#### July 14th – Prototype 003 (Final):
* Rackspace production image creation (OMSA/PSP/Comvault, etc)
   * Kitchen sink?
   * Post install process?
* Deploy + ADC integration (push hard)

#### July 30th – 0.4 RELEASE:
* Parity with existing hybrid offerings
* Finalize image creation and deployment strategy

#### v0.6 Features:
* UEFI Support
* Citrix XenServer
* ESXi Support

#### v0.8 Features:
* TBD


