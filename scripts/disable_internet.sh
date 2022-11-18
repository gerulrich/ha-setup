#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

ssh -i ${KEY_FILE} root@${ROUTER_IP} "iptables -I FORWARD -s $1 -j DROP"