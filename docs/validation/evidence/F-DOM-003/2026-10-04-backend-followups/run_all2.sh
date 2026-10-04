#!/bin/sh
# Full evidence refresh for fix-backend-followups against the packaged image (uc: source hub).
D=docs/validation/evidence/F-DOM-003/2026-10-04-backend-followups
IMG="--image hdmi-matrix-hub:fix-backend-followups --sim-image hdmi-matrix-hub-sim:fix-backend-followups"
python $D/campaign.py $IMG --client api --select cec_telnet. --env OREI_USE_TELNET_CEC=true --out build/c2-api-telnet --record > build/c2-api-telnet.log 2>&1
echo "telnet $?"
python $D/campaign.py $IMG --client api --select profile_state. --env OREI_USE_TELNET_CEC=false --env OREI_STATUS_CACHE_TTL=0 --out build/c2-api-ttl0 --record > build/c2-api-ttl0.log 2>&1
echo "ttl0 $?"
python $D/campaign.py $IMG --client api --select "*" --exclude cec_telnet.,profile_state.,deploy. --env OREI_USE_TELNET_CEC=false --out build/c2-api-default --record > build/c2-api-default.log 2>&1
echo "default $?"
python $D/campaign.py $IMG --client browser --select "*" --out build/c2-browser --record > build/c2-browser.log 2>&1
echo "browser $?"
python $D/campaign.py $IMG --client ha --select "*" --out build/c2-ha --record > build/c2-ha.log 2>&1
echo "ha $?"
python $D/vrun.py run --client uc --out build/c2-uc --record > build/c2-uc.log 2>&1
echo "uc $?"
grep -h "campaign\] done\|campaign\] fail\|campaign\] blocked\|validate\] done\|validate\] FAIL" build/c2-*.log
