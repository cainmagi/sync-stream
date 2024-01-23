#!/bin/bash --login

# Make bashline configurations.
set -e
RESET='\033[0m'
COLOR='\033[1;32m'

function msg {
    echo -e "${COLOR}$(date): $1${RESET}"
}

function fail {
    msg "Error : $?"
    exit 1
}

function mcd {
    mkdir -p "$1" || fail
    cd "$1" || fail
}

function nvm_has {
    type "$1" > /dev/null 2>&1
}

TEST=false
TEST_SLOW=false
VERSION=false

# Pass options from command line
for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    if [[ $KEY != '--*' ]]
    then
        VALUE=$(echo $ARGUMENT | cut -f2 -d=)   
    fi
    case "$KEY" in
        --test)         TEST=true ;;
        --slow)         TEST_SLOW=true ;;
        --version)      VERSION=true ;;
        *)
    esac
done

# Check existence of conda
PYTHON="python3"
if nvm_has "conda"; then
	# PYTHON="conda run --live-stream -n base python3" || fail
    conda activate base || fail
else
    if nvm_has "mamba"; then
        # PYTHON="mamba run --live-stream -n base python3" || fail
        mamba activate base || fail
    else
        if nvm_has "micromamba"; then
            # PYTHON="micromamba run --live-stream -n base python3" || fail
            micromamba activate base || fail
        fi
    fi
fi

if $TEST
then
    if $TEST_SLOW
    then
        EXTRA_CMD="--slow"
    else
        EXTRA_CMD=""
    fi
    echo "${PYTHON} -m pytest ${EXTRA_CMD}"
    echo "${PYTHON} -m pytest ${EXTRA_CMD}" | bash
    exit 0
fi

if $VERSION
then
    echo "${PYTHON} -c \"from version import __version;print(__version__)\""
    echo "${PYTHON} -c \"from version import __version;print(__version__)\"" | bash
    exit 0
fi

exec bash
exit 0
