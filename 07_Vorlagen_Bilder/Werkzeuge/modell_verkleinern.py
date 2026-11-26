#!/usr/bin/env python3
"""Verkleinert Meshy-GLB-Modelle fürs Handy.
Vertex-Clustering (UV-bewusst) auf eine Ziel-Dreieckszahl, Textur auf 1024 px JPEG.
Aufruf: shrink_glb.py eingabe.glb ausgabe.glb ziel_dreiecke [texturgroesse]
"""
import sys, json, struct, io
import numpy as np
from PIL import Image

def read_glb(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + jl])
    off = 20 + jl
    bl = struct.unpack('<I', b[off:off + 4])[0]
    bin_ = b[off + 8: off + 8 + bl]
    return j, bin_

CT = {5126: np.float32, 5125: np.uint32, 5123: np.uint16, 5121: np.uint8}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}

def acc(j, bin_, i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]
    start = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    dt = CT[a['componentType']]; n = NC[a['type']]
    stride = bv.get('byteStride', 0)
    if stride and stride != np.dtype(dt).itemsize * n:
        raw = np.frombuffer(bin_, np.uint8, count=stride * a['count'], offset=start).reshape(a['count'], stride)
        return raw[:, :np.dtype(dt).itemsize * n].copy().view(dt).reshape(a['count'], n)
    arr = np.frombuffer(bin_, dt, count=a['count'] * n, offset=start)
    return arr.reshape(a['count'], n) if n > 1 else arr

def load(path):
    j, bin_ = read_glb(path)
    P, U, I = [], [], []
    base = 0
    for node in j['nodes']:
        if 'mesh' not in node: continue
        M = np.array(node.get('matrix', [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]), dtype=np.float64).reshape(4, 4).T
        for p in j['meshes'][node['mesh']]['primitives']:
            pos = acc(j, bin_, p['attributes']['POSITION']).astype(np.float64)
            pos = (np.c_[pos, np.ones(len(pos))] @ M.T)[:, :3]
            uv = acc(j, bin_, p['attributes']['TEXCOORD_0']).astype(np.float64)
            idx = acc(j, bin_, p['indices']).astype(np.int64).reshape(-1, 3)
            P.append(pos); U.append(uv); I.append(idx + base); base += len(pos)
    tex = None
    mat = j['materials'][0]
    ti = mat.get('pbrMetallicRoughness', {}).get('baseColorTexture', {}).get('index')
    if ti is not None:
        im = j['images'][j['textures'][ti]['source']]
        bv = j['bufferViews'][im['bufferView']]
        o = bv.get('byteOffset', 0)
        tex = Image.open(io.BytesIO(bin_[o:o + bv['byteLength']])).convert('RGB')
    return np.vstack(P), np.vstack(U), np.vstack(I), tex

def cluster(pos, uv, idx, R, Q):
    mn = pos.min(0); ext = (pos.max(0) - mn).max()
    c = np.floor((pos - mn) / ext * R).astype(np.int64)
    q = np.floor(np.clip(uv, 0, 0.99999) * Q).astype(np.int64)
    key = ((c[:, 0] * (R + 1) + c[:, 1]) * (R + 1) + c[:, 2]) * (Q * Q) + q[:, 0] * Q + q[:, 1]
    uniq, inv = np.unique(key, return_inverse=True)
    n = len(uniq)
    cnt = np.bincount(inv, minlength=n).astype(np.float64)
    npos = np.stack([np.bincount(inv, pos[:, k], n) for k in range(3)], 1) / cnt[:, None]
    nuv = np.stack([np.bincount(inv, uv[:, k], n) for k in range(2)], 1) / cnt[:, None]
    t = inv[idx]
    ok = (t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])
    t = t[ok]
    s = np.sort(t, 1)
    _, first = np.unique(s, axis=0, return_index=True)
    t = t[np.sort(first)]
    used = np.unique(t)
    remap = -np.ones(n, np.int64); remap[used] = np.arange(len(used))
    return npos[used], nuv[used], remap[t]

def cluster_color(pos, cols, idx, R):
    mn = pos.min(0); ext = (pos.max(0) - mn).max()
    c = np.floor((pos - mn) / ext * R).astype(np.int64)
    key = (c[:, 0] * (R + 1) + c[:, 1]) * (R + 1) + c[:, 2]
    uniq, inv = np.unique(key, return_inverse=True)
    n = len(uniq); cnt = np.bincount(inv, minlength=n).astype(np.float64)
    npos = np.stack([np.bincount(inv, pos[:, k], n) for k in range(3)], 1) / cnt[:, None]
    ncol = np.stack([np.bincount(inv, cols[:, k], n) for k in range(3)], 1) / cnt[:, None]
    t = inv[idx]
    ok = (t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2]); t = t[ok]
    s = np.sort(t, 1); _, first = np.unique(s, axis=0, return_index=True); t = t[np.sort(first)]
    used = np.unique(t); remap = -np.ones(n, np.int64); remap[used] = np.arange(len(used))
    return npos[used], ncol[used], remap[t]

def sample(tex, uv):
    a = np.asarray(tex.convert('RGB'), dtype=np.float64) / 255.0
    h, w = a.shape[:2]
    x = np.clip((uv[:, 0] % 1.0) * (w - 1), 0, w - 1).astype(np.int64)
    y = np.clip((uv[:, 1] % 1.0) * (h - 1), 0, h - 1).astype(np.int64)
    c = a[y, x]
    return c ** 2.2   # sRGB -> linear (glTF COLOR_0 ist linear)

def normals(pos, idx):
    v0, v1, v2 = pos[idx[:, 0]], pos[idx[:, 1]], pos[idx[:, 2]]
    fn = np.cross(v1 - v0, v2 - v0)
    nrm = np.zeros_like(pos)
    for k in range(3): np.add.at(nrm, idx[:, k], fn)
    l = np.linalg.norm(nrm, axis=1, keepdims=True); l[l == 0] = 1
    return nrm / l

def write_glb_col(path, pos, nrm, col, idx):
    pos = pos.astype(np.float32); nrm = nrm.astype(np.float32); col = col.astype(np.float32)
    big = len(pos) > 65535
    ib = idx.astype(np.uint32 if big else np.uint16).tobytes()
    pad = lambda x: x + b'\0' * ((4 - len(x) % 4) % 4)
    chunks = []; views = []; off = 0
    def add(data, target=None):
        nonlocal off
        data = pad(data); v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
        if target: v['target'] = target
        views.append(v); chunks.append(data); off += len(data); return len(views) - 1
    vi = add(ib, 34963); vp = add(pos.tobytes(), 34962); vn = add(nrm.tobytes(), 34962); vc = add(col.tobytes(), 34962)
    j = {'asset': {'version': '2.0', 'generator': 'EarthEmpire shrink'},
         'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
         'meshes': [{'primitives': [{'attributes': {'POSITION': 1, 'NORMAL': 2, 'COLOR_0': 3}, 'indices': 0, 'material': 0}]}],
         'materials': [{'pbrMetallicRoughness': {'baseColorFactor': [1, 1, 1, 1], 'metallicFactor': 0, 'roughnessFactor': 1}, 'doubleSided': True}],
         'accessors': [
            {'bufferView': vi, 'componentType': 5125 if big else 5123, 'count': int(idx.size), 'type': 'SCALAR'},
            {'bufferView': vp, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3', 'min': pos.min(0).tolist(), 'max': pos.max(0).tolist()},
            {'bufferView': vn, 'componentType': 5126, 'count': len(nrm), 'type': 'VEC3'},
            {'bufferView': vc, 'componentType': 5126, 'count': len(col), 'type': 'VEC3'}],
         'bufferViews': views, 'buffers': [{'byteLength': off}]}
    js = json.dumps(j, separators=(',', ':')).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    binb = b''.join(chunks)
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<I', len(js)) + b'JSON' + js)
        f.write(struct.pack('<I', len(binb)) + b'BIN\0' + binb)

def write_glb(path, pos, nrm, uv, idx, tex, texsize):
    pos = pos.astype(np.float32); nrm = nrm.astype(np.float32); uv = uv.astype(np.float32)
    big = len(pos) > 65535
    ib = idx.astype(np.uint32 if big else np.uint16).tobytes()
    pad = lambda x: x + b'\0' * ((4 - len(x) % 4) % 4)
    chunks = []; views = []; off = 0
    def add(data, target=None):
        nonlocal off
        data = pad(data); v = {'buffer': 0, 'byteOffset': off, 'byteLength': len(data)}
        if target: v['target'] = target
        views.append(v); chunks.append(data); off += len(data); return len(views) - 1
    vi = add(ib, 34963); vp = add(pos.tobytes(), 34962); vn = add(nrm.tobytes(), 34962); vu = add(uv.tobytes(), 34962)
    t = tex.copy(); t.thumbnail((texsize, texsize), Image.LANCZOS)
    buf = io.BytesIO(); t.save(buf, 'JPEG', quality=84, optimize=True)
    vimg = add(buf.getvalue())
    j = {'asset': {'version': '2.0', 'generator': 'EarthEmpire shrink'},
         'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
         'meshes': [{'primitives': [{'attributes': {'POSITION': 1, 'NORMAL': 2, 'TEXCOORD_0': 3}, 'indices': 0, 'material': 0}]}],
         'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}, 'metallicFactor': 0, 'roughnessFactor': 1}, 'doubleSided': True}],
         'textures': [{'source': 0, 'sampler': 0}], 'samplers': [{'magFilter': 9729, 'minFilter': 9987}],
         'images': [{'bufferView': vimg, 'mimeType': 'image/jpeg'}],
         'accessors': [
            {'bufferView': vi, 'componentType': 5125 if big else 5123, 'count': int(idx.size), 'type': 'SCALAR'},
            {'bufferView': vp, 'componentType': 5126, 'count': len(pos), 'type': 'VEC3', 'min': pos.min(0).tolist(), 'max': pos.max(0).tolist()},
            {'bufferView': vn, 'componentType': 5126, 'count': len(nrm), 'type': 'VEC3'},
            {'bufferView': vu, 'componentType': 5126, 'count': len(uv), 'type': 'VEC2'}],
         'bufferViews': views, 'buffers': [{'byteLength': off}]}
    js = pad(json.dumps(j, separators=(',', ':')).encode()).replace(b'\0', b' ')
    if len(js) % 4: js += b' ' * (4 - len(js) % 4)
    binb = b''.join(chunks)
    total = 12 + 8 + len(js) + 8 + len(binb)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<I', len(js)) + b'JSON' + js)
        f.write(struct.pack('<I', len(binb)) + b'BIN\0' + binb)

def main():
    src, dst, target = sys.argv[1], sys.argv[2], int(sys.argv[3])
    texsize = int(sys.argv[4]) if len(sys.argv) > 4 else 1024
    pos, uv, idx, tex = load(src)
    if len(sys.argv) > 5 and sys.argv[5] == 'farbe':
        cols = sample(tex, uv)
        lo, hi = 8, 600; best = None
        for _ in range(14):
            R = (lo + hi) // 2
            r = cluster_color(pos, cols, idx, R)
            if len(r[2]) > target: hi = R - 1
            else: best = r; lo = R + 1
            if hi < lo: break
        p2, c2, i2 = best
        write_glb_col(dst, p2, normals(p2, i2), c2, i2)
        print(f'{src.split("/")[-1][:50]}: {len(idx)} -> {len(i2)} Dreiecke (Farben)'); return
    if len(idx) <= target:
        p2, u2, i2 = pos, uv, idx
    else:
        lo, hi = 8, 400; best = None
        for _ in range(12):
            R = (lo + hi) // 2
            p2, u2, i2 = cluster(pos, uv, idx, R, 16)
            if len(i2) > target: hi = R - 1
            else: best = (p2, u2, i2); lo = R + 1
            if hi < lo: break
        p2, u2, i2 = best if best else cluster(pos, uv, idx, 8, 16)
    write_glb(dst, p2, normals(p2, i2), u2, i2, tex, texsize)
    print(f'{src.split("/")[-1][:50]}: {len(idx)} -> {len(i2)} Dreiecke')

if __name__ == '__main__':
    main()
