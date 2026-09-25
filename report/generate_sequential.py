import base64,json,os,pathlib,urllib.request,time
root=pathlib.Path('report'); spec=json.loads((root/'deck_spec.json').read_text(encoding='utf-8')); key=[x.split('=',1)[1].strip() for x in pathlib.Path.home().joinpath('.codex-ppt-skill/.env').read_text().splitlines() if x.startswith('OPENAI_API_KEY=')][0]
style='Clean research-professional Chinese robotics academic slide matching approved sample: white/light gray background, deep navy typography, teal and orange accents, subtle technical grid, crisp line icons, generous whitespace, projector-readable, 16:9. Exact Chinese text, no extra text, no logos, no watermark, no page number.'
nums=[int(x) for x in os.environ['SLIDES'].split(',')]
for n in nums:
 s=next(x for x in spec['slides'] if x['number']==n)
 prompt=style+'\nTitle exact: “'+s['title']+'”.\nPurpose: '+s['intent']+'.\nShow these exact labels/content:\n'+'\n'.join('• '+x for x in s['key_points'])+'\nLayout: '+s['layout']['composition']+'\nConstraint: '+s['local_context']['caveat']+' Do not invent facts.'
 payload={'model':'gpt-image-2.5','prompt':prompt,'size':'1280x720','n':1}
 out=root/'origin_image'/f'slide_{n:02d}.png'
 for a in range(3):
  try:
   req=urllib.request.Request('https://api.wokey.ai/v1/images/generations',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Connection':'close'})
   with urllib.request.urlopen(req,timeout=180) as r: obj=json.loads(r.read())
   out.write_bytes(base64.b64decode(obj['data'][0]['b64_json'])); print('OK',n,out.stat().st_size,flush=True); break
  except Exception as e:
   print('ERR',n,a+1,type(e).__name__,str(e)[:100],flush=True)
   if a<2: time.sleep(5)
 else: print('FAILED',n,flush=True)
