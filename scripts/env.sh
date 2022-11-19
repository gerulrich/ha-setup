#!/bin/bash

#
# Generate an RSA ssh key pair with 4096 bits using the command
# $ ssh-keygen -t rsa -b 4096
#
# Copy public key in remote host 
# OpenWRT: System -> Administration -> SSH-Keys Tab.

ROUTER_IP="192.168.0.2"
KEY_FILE=~/id_rsa_tplink
OPEN_PORT_RULE_NAME='http odroid forward'
