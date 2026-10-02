import asyncio,json,time,urllib.request
from tools.validate.runner import Runner
class ReadyRunner(Runner):
 def _ready(self):
  deadline=time.monotonic()+40
  while time.monotonic()<deadline:
   try:
    with urllib.request.urlopen(self.base_url+'/api/health',timeout=2) as response:
     matrix=json.load(response)['data']['matrix']
    if matrix['connected'] and matrix['telnet_connected']: return
   except Exception: pass
   time.sleep(.1)
  raise RuntimeError('Matrix HTTP/Telnet readiness timed out')
 def _start_system(self):
  super()._start_system();self._ready()
 def _restart_hub(self):
  # Owned source hubs restart. Externally managed packaged hubs reconnect;
  # wait for both transports before the next scenario in either case.
  super()._restart_hub();self._ready()
 def _environment(self,client):
  environment=super()._environment(client)
  if hasattr(self,'configured_cec_transport'):
   environment['hub']['env']['OREI_USE_TELNET_CEC']=self.configured_cec_transport
   environment['hub']['env']['OREI_STATUS_CACHE_TTL']='0'
  return environment