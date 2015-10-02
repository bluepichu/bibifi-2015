#!/bin/bash

vm='bibivm'
user='bibi'

echo "Assuming VM name to be $vm"
echo "Assuming VM user to be $user"

if VBoxManage showvminfo $vm | grep 'name = ssh' > /dev/null
then
    echo "Already added ssh rule"
else
    echo "Adding ssh rule"
    VBoxManage modifyvm $vm --natpf1 "ssh,tcp,,3022,,22"
fi

echo "Starting the VM"
VBoxManage startvm $vm --type headless

echo "SSH into vm"
ssh -t $user@localhost -p 3022 'sudo "/root/install/doit.sh"'

echo "You can add the following to your .ssh/config:"
echo "Host bibivm"
echo "  HostName localhost"
echo "  User bibi"
echo "  Port 3022"
echo
echo "Then, use `ssh bibivm` to connect"
