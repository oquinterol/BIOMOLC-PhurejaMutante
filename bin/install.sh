#!/bin/bash
# Fedora/RHEL/CentOS distro
 if [ -f /etc/redhat-release ]; then
    echo "FED"
# Debian/Ubuntu
elif [ -r /lib/lsb/init-functions ]; then
    echo "DEB"
fi
