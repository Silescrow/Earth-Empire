import json, sys
from PIL import Image, ImageDraw, ImageFilter
W,H=1440,720; SS=4; LAT0,LAT1=90,-90
big=Image.new('L',(W*SS,H*SS),0); d=ImageDraw.Draw(big)
def px(lon,lat): return ((lon+180)/360*W*SS, (LAT0-lat)/(LAT0-LAT1)*H*SS)
def polys(g):
  if g['type']=='Polygon': yield g['coordinates']
  elif g['type']=='MultiPolygon': yield from g['coordinates']
land=json.load(open('/tmp/ne/geojson/ne_50m_land.geojson'))
for f in land['features']:
  for p in polys(f['geometry']):
    d.polygon([px(*c[:2]) for c in p[0]], fill=255)
    for h in p[1:]: d.polygon([px(*c[:2]) for c in h], fill=0)
# kleine Inseln: mindestens ~1,2 Pixel groß, damit sie spielbar sind
mi=json.load(open('/tmp/ne/geojson/ne_10m_minor_islands.geojson'))
r=1.2*SS/2+1.5
for f in mi['features']:
  for p in polys(f['geometry']):
    pts=[px(*c[:2]) for c in p[0]]
    d.polygon(pts, fill=255)
    xs=[a for a,b in pts]; ys=[b for a,b in pts]; cx=sum(xs)/len(xs); cy=sum(ys)/len(ys)
    if max(xs)-min(xs)<2*r and max(ys)-min(ys)<2*r: d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=255)
# Nordpol: Packeis auf dem Nordpolarmeer (ab etwa 80° Nord, Rand wellig)
import math
pts=[]
for i in range(0,361):
    lon=-180+i; lat=80.5+1.6*math.sin(math.radians(lon*3))+0.9*math.sin(math.radians(lon*7+40))
    pts.append(px(lon,lat))
pts+= [px(180,90),px(-180,90)]
d.polygon(pts, fill=255)
# Südpol: Antarktis ganz bis zum Rand füllen
d.rectangle([0,px(0,-85)[1],W*SS,H*SS], fill=255)
im=big.resize((W,H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))
im.save(sys.argv[1])
