#!/bin/bash

# cat ${HOME}/.ssh/config:
#
#       # work account
#       Host github.com
#           HostName github.com
#           User git
#           IdentityFile ~/.ssh/id_rsa_work
#       # personal account
#       Host github.com-personal
#           HostName github.com
#           User git
#           IdentityFile ~/.ssh/id_rsa_personal
#
# Test ssh-keys:
# ssh -T git@github.com
#
# ssh -T git@github.com-personal


USERNAME=
NAME=
EMAIL=
GPG_KEY=

PROJECT="$1"
git clone git@github.com-${USERNAME}:${USERNAME}/$PROJECT.git
cd $PROJECT
git config user.name "${NAME}"
git config user.email "${EMAIL}"
git config --global user.signingkey "${GPG_KEY}"