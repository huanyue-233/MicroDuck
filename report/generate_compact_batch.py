import base64,json,os,pathlib,urllib.request,time,concurrent.futures
root=pathlib.Path('report'); spec=json.loads((root/'deck_spec.json').read_text(encoding='utf-8'))
key=[x.split('=',1)[1].strip() for x in pathlib.Path.home().joinpath('.codex-ppt-skill/.env').read_text().splitlines() if x.startswith('OPENAI_API_KEY=')][0]
style='''Clean research-professional Chinese robotics presentation. White/light gray background, deep navy typography, teal and orange accents, subtle technical grid, rounded modules, crisp line icons, generous whitespace, projector-readable. Match the approved Slide 3 visual mood. 16:9 landscape. Render Chinese text exactly and legibly. No extra text, no logos, no watermark, no page number.'''
def gen(slide):
 n=slide['number']
 if n==3:return {'n':n,'status':'accepted'}
 prompt=style+'\n\nSlide title (exact): “'+slide['title']+'”.\nPurpose: '+slide['intent']+'.\nKey labels/content (use exact Chinese where provided):\n'+'\n'.join('• '+x for x in slide['key_points'])+'\n\nLayout: '+slide['layout']['composition']+'\nImportant constraint: '+slide['local_context']['caveat']+' Keep concise; do not invent facts.'
 payload={'model':'gpt-image-2.5','prompt':prompt,'size':'1536x1024','n':1}
 for attempt in range(3):
  try:
   req=urllib.request.Request('https://api.wokey.ai/v1/images/generations',data=json.dumps(payload,ensure_ascii=False).encode('utf-8'),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','Connection':'close'})
   with urllib.request.urlopen(req,timeout=240) as r: obj=json.loads(r.read())
   data=obj.get('data') or []
   if not data or not data[0].get('b64_json'): raise RuntimeError('no b64')
   out=root/'origin_image'/f'slide_{n:02d}.png'; out.parent.mkdir(exist_ok=True); out.write_bytes(base64.b64decode(data[0]['b64_json']))
   return {'n':n,'status':'ok','path':str(out),'bytes':out.stat().st_size}
  except Exception as e:
   if attempt==2:return {'n':n,'status':'error','error':type(e).__name__+': '+str(e)[:300]}
   time.sleep(5*(attempt+1))
slides=[s for s in spec['slides'] if s['number']!=3]
for start in range(0,len(slides),3):
 batch=slides[start:start+3]
 print('batch', [s['number'] for s in batch], flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
  for result in ex.map(gen,batch): print(json.dumps(result,ensure_ascii=False),flush=True)
