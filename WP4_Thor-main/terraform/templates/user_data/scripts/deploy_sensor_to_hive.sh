#!/bin/bash


echo waiting 300s for the hive to finish instalation
sleep 300

function fuCHECK_TERMINATE_COND () {

	if ! [[ $? -eq 0 ]] # if not eq to 0
	then
		# set unsuccessful condition
		TERMINATE=true
		TERMINATE_MSG="Couldn't set the deploy data."
	fi
}

function fuDEPLOY_SENSOR () {
echo
echo "###############################"
echo "# Deploying to T-Pot Hive ... #"
echo "###############################"
echo
sshpass -e ssh -4 -t -T -l "$MY_TPOT_USERNAME" -p 64295 "${MY_HIVE_IP}" << EOF
echo "$SSHPASS" | sudo -S bash -c 'useradd -m -s /sbin/nologin -G tpotlogs "$MY_HIVE_USERNAME";
mkdir -p /home/"$MY_HIVE_USERNAME"/.ssh;
echo "$MY_SENSOR_PUBLICKEY" >> /home/"$MY_HIVE_USERNAME"/.ssh/authorized_keys;
chmod 600 /home/"$MY_HIVE_USERNAME"/.ssh/authorized_keys;
chmod 755 /home/"$MY_HIVE_USERNAME"/.ssh;
chown "$MY_HIVE_USERNAME":"$MY_HIVE_USERNAME" -R /home/"$MY_HIVE_USERNAME"/.ssh'
EOF

echo
echo "###########################"
echo "# Done. Please reboot ... #"
echo "###########################"
echo

}

# Check Hive availability 
function fuCHECK_HIVE () {
echo
echo "############################################"
echo "# Checking for T-Pot Hive availability ... #"
echo "############################################"
echo
sshpass -e ssh -4 -t -l "$MY_TPOT_USERNAME" -p 64295 -f -N -L64305:127.0.0.1:64305 "${MY_HIVE_IP}" -o "StrictHostKeyChecking=no"
if [ $? -eq 0 ];
  then
    echo
    echo "#########################"
    echo "# T-Pot Hive available! #"
    echo "#########################"
    echo
    myHIVE_OK=$(curl -s http://127.0.0.1:64305)
    if [ "$myHIVE_OK" == "ok" ];
      then
	echo
        echo "##############################"
        echo "# T-Pot Hive tunnel test OK! #"
        echo "##############################"
        echo
        kill -9 $(pidof ssh)
      else
        echo
	echo "######################################################"
        echo "# T-Pot Hive tunnel test FAILED!                     #"
	echo "# Tunneled port tcp/64305 unreachable on T-Pot Hive. #"
	echo "# Aborting.                                          #"
        echo "######################################################"
        echo
        kill -9 $(pidof ssh)
	rm $MY_SENSOR_PUBLICKEYFILE
	rm $MY_SENSOR_PRIVATEKEYFILE
	rm $MY_LS_ENVCONFIGFILE
	return 1 # not successful
    fi;
  else
    echo
    echo "#################################################################"
    echo "# Something went wrong, most likely T-Pot Hive was unreachable! #"
    echo "# Aborting.                                                     #"
    echo "#################################################################"
    echo
    rm $MY_SENSOR_PUBLICKEYFILE
    rm $MY_SENSOR_PRIVATEKEYFILE
    rm $MY_LS_ENVCONFIGFILE
    return 1 # not successful
fi;
}

function fuSET_DEPLOY_DATA () {
echo
echo "setting the deploy data ..."
echo

MY_TPOT_USERNAME=${SSH_USER}
SSHPASS=${SSH_PASSWORD}

export SSHPASS

# MY_HIVE_IP should be set in terraform file

MY_HIVE_USERNAME="$(hostname)"
MY_TPOT_TYPE="SENSOR"
MY_LS_ENVCONFIGFILE="/data/elk/logstash/ls_environment"

MY_SENSOR_PUBLICKEYFILE="/data/elk/logstash/$MY_HIVE_USERNAME.pub"
MY_SENSOR_PRIVATEKEYFILE="/data/elk/logstash/$MY_HIVE_USERNAME"
if ! [ -s "$MY_SENSOR_PRIVATEKEYFILE" ] && ! [ -s "$MY_SENSOR_PUBLICKEYFILE" ];
  then
    echo
    echo "##############################"
    echo "# Generating ssh keyfile ... #"
    echo "##############################"
    echo
    mkdir -p /data/elk/logstash
    ssh-keygen -f "$MY_SENSOR_PRIVATEKEYFILE" -N "" -C "$MY_HIVE_USERNAME"
    MY_SENSOR_PUBLICKEY="$(cat "$MY_SENSOR_PUBLICKEYFILE")"
  else
    echo
    echo "#############################################"
    echo "# There is already a ssh keyfile. Aborting. #"
    echo "#############################################"
    echo
    return 1 # not successful
fi
echo
echo "###########################################################"
echo "# Writing config to /data/elk/logstash/ls_environment.    #"
echo "# If you make changes to this file, you need to reboot or #"
echo "# run /opt/tpot/bin/updateip.sh.                          #"
echo "###########################################################"
echo
tee $MY_LS_ENVCONFIGFILE << EOF
MY_TPOT_TYPE=$MY_TPOT_TYPE
MY_SENSOR_PRIVATEKEYFILE=$MY_SENSOR_PRIVATEKEYFILE
MY_HIVE_USERNAME=$MY_HIVE_USERNAME
MY_HIVE_IP=${MY_HIVE_IP}
EOF
}





# Deploy Pot to Hive
echo
echo "#################################"
echo "# Ship T-Pot Logs to T-Pot Hive #"
echo "#################################"
echo
echo "If you already have a T-Pot Hive installation running and"
echo "this T-Pot installation is running the type \"Pot\" the"
echo "script will automagically setup this T-Pot to ship and"
echo "prepare the Hive to receive logs from this T-Pot."
echo
echo
echo "###################################"
echo "# Deploy T-Pot Logs to T-Pot Hive #"
echo "###################################"
echo 
echo


fuSET_DEPLOY_DATA

fuCHECK_TERMINATE_COND



if ! [[ TERMINATE == true ]]
then
	fuCHECK_HIVE
	fuCHECK_TERMINATE_COND
else
	echo $TERMINATE_MSG
fi


if ! [[ TERMINATE == true ]]
then
	fuDEPLOY_SENSOR
	fuCHECK_TERMINATE_COND

	if [[ TERMINATE == true ]]
	then
		echo $TERMINATE_MSG
	fi
else
	echo $TERMINATE_MSG
fi



