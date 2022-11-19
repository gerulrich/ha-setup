#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

rule=$(ssh -i ${KEY_FILE} root@${ROUTER_IP} "uci show firewall | grep redirect | grep '""${OPEN_PORT_RULE_NAME}""'")
command=$(echo $rule | sed 's/\(.*\).name.*/\1.enabled=1/')
ssh -i ${KEY_FILE} root@${ROUTER_IP} "uci set ${command} && uci commit"