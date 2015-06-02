# "Prime Time" release v0.4.0
* SSD detection
    - Changes to file system mount options (discard)
* EFI bootloader support
* Disto Support
    - RHEL 6/7
    - Debian 7/8
    - Ubuntu 12.04 - 15.04
    - Gentoo
    - Arch
    - SLES
    - Oracle EL
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

# "Wishful Thinking" release v0.5.0
* Move disk scanning and bare metal operation to disk object
    - MockDisk() for testing
* Probe functions in post configuration targets, allowing the user to omit a target
declaration