#!/bin/sh
# Copy cloud.cfg to a location that is visible from within the VM
mkdir tmp
cp ../avira/deploy/cloudinit\ configs\cloud.cfg tmp
vagrant up
vagrant halt
vagrant destroy -f
rm -rf tmp
