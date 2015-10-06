#!/bin/bash

if [ "$@ " == " " ]; then
	echo "./quickstart <init | startup | shutdown | connect> [vm] [user]"
	exit
fi


if [ "$2" != "" ]; then
	vm=$2
else
	vm='bibivm'
fi

if [ "$3" != "" ]; then
	user=$3
else
	user='bibi'
fi

echo "VM name is $vm"
echo "VM user is $user"

if [ "$1" == "shutdown" ]; then VBoxManage controlvm $vm savestate; exit; fi 

if VBoxManage showvminfo $vm | grep 'name = ssh' > /dev/null
then
    echo "Already added ssh rule"
else
    echo "Adding ssh rule"
    VBoxManage modifyvm $vm --natpf1 "ssh,tcp,,3022,,22"
fi


if [ "$1" == "startup" ]; then
	echo "Starting the VM"
	VBoxManage startvm $vm --type headless
fi

if [ "$1" == "init" ]; then ssh -t $user@localhost -p 3022 'sudo "/root/install/doit.sh"'; fi

if [ "$1" == "connect" ]; then ssh $user@localhost -p 3022; fi

if [ "$1" == "init" ]; then
	echo "You can add the following to your .ssh/config:"
	echo "Host $vm"
	echo "  HostName localhost"
	echo "  User $user"
	echo "  Port 3022"
	echo
	echo "Then, use \`ssh $vm\` to connect"
fi
