#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

ssh -i ${KEY_FILE} root@${ROUTER_IP} "/sbin/wifi down radio0 && sleep 20 && /sbin/wifi up radio0"
