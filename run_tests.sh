#!/bin/bash

set -x

coverage run $(which trial) txhttp
STATUS=$?

coverage html --include 'txhttp*'

exit $STATUS

