#!/bin/bash

# Install dependencies for the Docker Image.

# Make bashline configurations.
set -e
RESET='\033[0m'
COLOR='\033[1;32m'
COLOR_WARN='\033[1;33m'
COLOR_ERR='\033[1;31m'

function msg {
  echo -e "${COLOR}$(date): $1${RESET}"
}

function msg_warn {
  echo -e "${COLOR_WARN}$(date): $1${RESET}"
}

function msg_err {
  echo -e "${COLOR_ERR}$(date): $1${RESET}"
}

function fail {
  msg_err "Error : $?"
  exit 1
}

function mcd {
  mkdir -p "$1" || fail
  cd "$1" || fail
}

function nvm_has {
    type "$1" > /dev/null 2>&1
}

INSTALL_MODE=$1
PYTHON="python3"

# Check existence of python3
EXTRA_PY=""
if ! nvm_has ${PYTHON}; then
	if [ "x${CONDA}" = "x" ]; then
    	msg_warn "Need to have python installed in the image. If not provided, will try to install python with apt."
    	EXTRA_PY="python3-dev python3-pip"
	fi
fi

# Required packages
apt-get -y update || fail && apt-get -y install \
    apt-utils apt-transport-https curl wget \
    gnupg2 lsb-release ${EXTRA_PY} || fail

if ! nvm_has "lsb_release"; then
    msg_err "lsb_release does not exist. This should not happen. Please contact the author for technical supports."
    exit 1
fi

# Check the OS version
NAME_OS=$(lsb_release -is)

if [ "x${NAME_OS}" = "xUbuntu" ] || [ "x${NAME_OS}" = "xDebian" ]; then
	msg "Pass the OS check. Current OS: ${NAME_OS}."
else
	msg_err "The base image is an unknown OS, this dockerfile does not support it: ${NAME_OS}."
fi

if [ "x${INSTALL_MODE}" = "xdev" ]; then
	apt-get -y upgrade || fail
	apt-get -y update -qq || fail && apt-get -y install git-core || fail
	msg "Successfully install developer's dependencies."
fi

apt-get -y update || fail && apt-get -y upgrade || fail && apt-get -y dist-upgrade || fail && apt-get -y autoremove || fail && apt-get -y autoclean || fail


if [ "x${INSTALL_MODE}" = "xdev" ]; then
    ${PYTHON} -m pip install --compile --no-cache-dir .[file,host,test,dev]
else
    if [ "x${INSTALL_MODE}" = "xtest" ]; then
        ${PYTHON} -m pip install --compile --no-cache-dir .[file,host,test]
    else
        if [ "x${INSTALL_MODE}" = "xminimal" ]; then
            ${PYTHON} -m pip install --compile --no-cache-dir .
        else
            ${PYTHON} -m pip install --compile --no-cache-dir .[file,host]
        fi
    fi
fi

msg "Successfully install the python dependencies."
