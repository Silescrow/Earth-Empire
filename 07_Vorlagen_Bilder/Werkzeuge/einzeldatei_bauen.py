# Baut aus dem Spiel-Ordner eine einzige HTML-Datei mit allem eingebaut
import base64, re, sys, os, json
src, out = sys.argv[1], sys.argv[2]
rd = lambda f: open(os.path.join(src,f),'rb').read()
b64 = lambda f: base64.b64encode(rd(f)).decode()
h = open(os.path.join(src,'index.html'),encoding='utf8').read()
for img in ['laden.jpg','menue.jpg']:
    uri='data:image/jpeg;base64,'+b64(img)
    h=h.replace('url('+img+')','url('+uri+')').replace("loadImg('"+img+"')","loadImg('"+uri+"')")
import glob
for f in sorted(glob.glob(os.path.join(src,'ui','*.jpg'))):
    rel='ui/'+os.path.basename(f); h=h.replace('url('+rel+')','url(data:image/jpeg;base64,'+base64.b64encode(open(f,'rb').read()).decode()+')')
icon='data:image/png;base64,'+b64('icon-192.png')
h=h.replace('href="icon-192.png"','href="'+icon+'"').replace('<link rel="manifest" href="manifest.webmanifest">\n','')
g=open(os.path.join(src,'game.js'),encoding='utf8').read()
mf=re.search(r"const MODEL_FILES = (\{.*?\});",g).group(1)
files=dict(re.findall(r"(\w+):'(models/[^']+)'",mf))
low=re.findall(r"'(\w+)'", re.search(r"const MODEL_LOW = new Set\(\[(.*?)\]\)",g).group(1))
models={k:'data:model/gltf-binary;base64,'+b64(f) for k,f in files.items()}
for k in low:
    lf=files[k].replace('models/','models/niedrig/')
    if os.path.exists(os.path.join(src,lf)): models[k+'_low']='data:model/gltf-binary;base64,'+b64(lf)
pre = ('<script>window.EE_MENU_MUSIC="data:audio/mpeg;base64,'+b64('musik_menue.mp3')+'";window.EE_GAME_MUSIC="data:audio/mpeg;base64,'+b64('musik_spiel.mp3')+'";</script>\n'
       '<script>window.EE_WORLD="data:image/png;base64,'+b64('weltkarte.png')+'";</script>\n'
       '<script>window.EE_MODELS='+json.dumps(models)+';</script>\n')
def inline(name):
    global h
    m=re.search(r'<script src="'+re.escape(name)+r'(\?v=[\d.]+)?"></script>', h); assert m, name
    code=open(os.path.join(src,name),encoding='utf8').read().replace('</script>','<\\/script>')
    h=h[:m.start()]+('' if name!='audio.js' else pre)+'<script>'+code+'</script>'+h[m.end():]
for n in re.findall(r'<script src="([a-z0-9_.]+\.js)(?:\?v=[\d.]+)?"></script>', h): inline(n)
open(out,'w',encoding='utf8').write(h)
print(out, len(h)//1000000, 'MB', len(models),'Modelle')
