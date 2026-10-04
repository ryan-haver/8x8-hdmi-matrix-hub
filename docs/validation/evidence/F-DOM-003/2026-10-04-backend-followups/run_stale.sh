#!/bin/sh
# Re-record only the (scenario, client) pairs stale at the merge HEAD (build/stale-*.txt, from stale_list.py).
D=docs/validation/evidence/F-DOM-003/2026-10-04-backend-followups
IMG="--image hdmi-matrix-hub:fix-backend-followups-merge --sim-image hdmi-matrix-hub-sim:fix-backend-followups-merge"
python $D/campaign.py $IMG --client api --select "$(cat build/stale-api.txt)" --env OREI_USE_TELNET_CEC=false --out build/c3-api --record > build/c3-api.log 2>&1
echo "api $?"
python $D/campaign.py $IMG --client browser --select "$(cat build/stale-browser.txt)" --out build/c3-browser --record > build/c3-browser.log 2>&1
echo "browser $?"
grep -h "campaign\] [0-9]\|campaign\] done\|campaign\] fail" build/c3-api.log build/c3-browser.log
