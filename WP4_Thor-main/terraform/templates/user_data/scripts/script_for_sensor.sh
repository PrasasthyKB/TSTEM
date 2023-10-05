#! /bin/bash

#source ./common_script_for_hive_and_sensors.sh # puts us in tpotce/iso/installer/ dir


function prep_conf_for_SENSOR() {
	
	sed \
		--in-place \
	       	-e 's/STANDARD/HIVE_SENSOR/' \
		-e 's/webuser/${SSH_USER}/' \
		-e 's/w3b\$ecret/${SSH_PASSWORD}/' \
		${SSH_USER}.tpot.conf
}



prep_conf_for_SENSOR


sudo ./install.sh --type=auto --conf=${SSH_USER}.tpot.conf
