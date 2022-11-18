#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

ssh -i ${KEY_FILE} root@${ROUTER_IP} 'iptables -L FORWARD -v --line-numbers' | grep DROP
