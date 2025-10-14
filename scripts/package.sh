#!/bin/bash

set -euo pipefail

./mortician/ajt_common/package.sh \
	--package "Mortician" \
	--name "AJT Mortician" \
	--root "mortician" \
	"$@"
