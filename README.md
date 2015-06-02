# Press
Image installer with custom partitioning

# 'Prime Time' release 0.4.0
## Distro Support (baked in)

* RHEL/CentOS
    - 6
    - 7
* Ubuntu
    - 12.04 (LTS)
    - 14.04 (LTS)
    - 15.04
* Debian
    - 7 Wheezy
    - 8 Jessis
* Arch
* Gentoo

## Development
### Dependencies

* Linux 3.7+
* udisks
* gparted 3.0+

Python packages:

* python 2.7 (3.0 is not supported at present)
* requests
* pyyaml
* pyudev

### Installation
    git clone git@github.rackspace.com:OSDeployment/press.git
    cd press/
    git checkout -b v0.3 origin/v0.3
    python setup.py develop

## Testing
### Vagrant