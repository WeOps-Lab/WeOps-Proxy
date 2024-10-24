#!/bin/sh
set -e
green_echo () {
    echo -e "\033[32m${1}\033[0m"
}

yellow_echo () {
    echo -e "\033[33m${1}\033[0m"
}

green_echo "CONSUL_ADDR: ${CONSUL_ADDR}"
green_echo "IPMI_RUNTIME: ${IPMI_RUNTIME}"
green_echo "ZONE: ${ZONE:-default}"
green_echo "REMOTE_URL: ${REMOTE_URL}"

yellow_echo "Render supervisord.conf"
consul-template -consul-addr=${CONSUL_ADDR} -config templates/supervisord.hcl -once

yellow_echo "Start Proxy...."
supervisord -c config/supervisord.conf --nodaemon