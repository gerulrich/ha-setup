#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

disabled=$($DIR/firewall_list.sh | grep $1 | wc -l)

if [ $disabled -gt 0 ]; then
    ssh -i ${KEY_FILE} root@${ROUTER_IP} "iptables -D FORWARD -s $1 -j DROP"
fi