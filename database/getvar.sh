#!/bin/bash

set -euo pipefail
shopt -s inherit_errexit

export \
	DEBIAN_FRONTEND="noninteractive" \
	DEBIAN_PRIORITY="critical" \
	NEEDRESTART_SUSPEND="1"

. /var/lib/vultr/common.sh


metadata_variable_list=(
	"pmadbpass"
	"pmadbuser"
	"pmamodalpass"
	"wpadminpass"
	"wpadminuser"
	"xhprofpass"
	"xhprofuser"
)


for var in "${metadata_variable_list[@]}"; do
	get_var "${var}"
    echo "${!var}"    
done





