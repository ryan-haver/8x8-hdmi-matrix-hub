#!/bin/sh
# API evidence campaign against the packaged image: three hub environments, one after the other.
C=docs/validation/evidence/F-MTX-030/2026-10-03-wp-v2-backend-fixes/campaign.py
IMG="--image hdmi-matrix-hub:fix-backend-wp-v2-bugs --sim-image hdmi-matrix-hub-sim:fix-backend-wp-v2-bugs"
python $C $IMG --client api --select cec_telnet. --env OREI_USE_TELNET_CEC=true --out build/camp-api-telnet --record > build/camp-api-telnet.log 2>&1
echo "telnet group exit $?"
python $C $IMG --client api --select profile_state. --env OREI_USE_TELNET_CEC=false --env OREI_STATUS_CACHE_TTL=0 --out build/camp-api-ttl0 --record > build/camp-api-ttl0.log 2>&1
echo "ttl0 group exit $?"
python $C $IMG --client api --select "*" --exclude cec_telnet.,profile_state.,deploy. --env OREI_USE_TELNET_CEC=false --out build/camp-api-default --record > build/camp-api-default.log 2>&1
echo "default group exit $?"
