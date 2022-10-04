#!/bin/sh 

# This shell script supplements the Multicluster configuration by allowing the Primary
# CVP Cluster to execute this script as a cron job. This script takes a backup of the
# Primary CVP Cluster and restores it over an SSH session on the secondary CVP cluster.

# IP Address of the Secondary Cluster's Primary CVP Node.
SECONDARY_CLUSTER=10.88.160.57

# Preparation prior to adding cron Job, generate an SSH key and copy to secondary cluster.
#
#   ssh-key-gen -t rsa -b 4096 <press enter until back to prompt>
#   ssh-copy-id -i ~/.ssh/id_rsa root@${SECONDARY_CLUSTER}
#

# BACKUP CVP
echo "#### BACKING UP CVP ON PRIMARY CLUSTER ####"
if cvpi backup cvp ; then
   printf "\n\n#### BACKUP "
else

fi
echo ""

# SYNC CVP BACKUP TO SECONDARY_CLUSTER
FILES=`ls -t /data/cvpbackup/cvp.20* | head -1`
FILES="$FILES $(ls -t /data/cvpbackup/cvp.eos* | head -1)"
echo "#### COPYING BACKUP TO SECONDARY CLUSTER ####"
for FILE in $FILES; do
  scp ${FILE} root@${SECONDARY_CLUSTER}:${FILE}
done
echo ""

echo "#### RESTORE ON SECONDARY CLUSTER ####"
ssh root@${SECONDARY_CLUSTER} "chown cvp:cvp /data/cvpbackup/* ; cvpi restore cvp ${FILES}"
echo "#### COMPLETE ####"