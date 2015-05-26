# Press
*partitioning for humans*

# "Prime Time" release v0.4.0
## goals
    * Modular post image deployment operations
        - Network configuration
        - Chroot operations
    * Easy to extend plugin interfaces
        - Plugins can be downloaded and loaded at runtime
    * Seriously stable partitioning operations
    * Clean up structure/models/generators so they make more sense
    * Full "end user" configuration documentation

## TODO
    * standardize press system configuration (not user configuration)
        - Find logging, path, and other configurations in
            - /etc/press
            - ./.press
            - ~/.press
            - if a directory called plugins is found, it should be scanned for plugins
    * fsck options and mount options are hacks.
    * code duplication between Partition and LogicalVolume, create a base class
       and make it work.
    * Since we are using jinja in the post install, consider using it for genfstab.
    * Testing with lvm is a pain, build an LVM tear down process.
    * Define configuration requirements and check for them before running generators