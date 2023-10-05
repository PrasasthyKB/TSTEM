#! /bin/bash

#source ./common_script_for_hive_and_sensors.sh # puts us in tpotce/iso/installer/ dir


function prep_conf_for_HIVE() {
	
	sed \
		--in-place \
	       	-e 's/STANDARD/HIVE/' \
		-e 's/webuser/${SSH_USER}/' \
		-e 's/w3b\$ecret/${SSH_PASSWORD}/' \
		${SSH_USER}.tpot.conf
}


# creates a sudo user to be used by sensors to deploy themselvs into the hive
function create_user_for_deployment() {
	#password="S3cur3"
	pass=$(perl -e 'print crypt($ARGV[0], "pass_salt")' ${SSH_PASSWORD})
	sudo useradd -m -p "$pass" ${SSH_USER}
	sudo usermod -aG sudo ${SSH_USER}
}


function enable_ssh_pass_authentication () {
	cd /etc/ssh
	sudo sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' sshd_config
	sudo systemctl restart ssh.service
}




create_user_for_deployment


prep_conf_for_HIVE


sudo ./install.sh --type=auto --conf=${SSH_USER}.tpot.conf


enable_ssh_pass_authentication
