"""Untrusted byte-transition witnesses for SourceByteScanner.lean."""
import copy
from .source_scanner_v2 import initial,step,finish,lean_string


def certificate(data,chunk_chars=256):
    data.decode('utf-8',errors='strict')
    q=initial(); q['utf8']=0; pieces=[]; imports=[]
    for start in range(0,len(data),chunk_chars):
        part=data[start:start+chunk_chars]; es=[]
        for byte in part:
            if q['good']:
                q['utf8']=utf8_step(q['utf8'],byte)
                if q['utf8']==255: q['good']=False
            event=step(q,chr(byte))
            if event is not None:
                raw=event.encode('latin1')
                es.append(list(raw)); imports.append(raw.decode('utf-8',errors='strict'))
        pieces.append({'data':part,'after':copy.copy(q),'events':es})
    if not finish(q) or q['utf8']!=0: raise ValueError('source outside import-projection byte specification: '+repr(q))
    return pieces,imports


def bytes_literal(values):
    return '['+', '.join(str(v) for v in values)+']'


def control(q):
    b=lambda x:'true' if x else 'false'
    return '⟨'+', '.join([b(q['good']),'.'+q['mode'],str(q['word']),
       bytes_literal(map(ord,q['stack'])),b(q['header']),'.'+q['expect'],
       bytes_literal(map(ord,q['path'])),b(q['collect']),str(q['utf8'])])+'⟩'


def piece(p):
    events='['+', '.join(bytes_literal(xs) for xs in p['events'])+']'
    data=p['data']
    packed='0x'+format(int.from_bytes(data,'little'),'x')
    return f'⟨⟨{len(data)}, {packed}⟩, {control(p["after"])}, {events}⟩'


def utf8_step(state,b):
    if state==0:
        if b<128: return 0
        if 194<=b<=223: return 1
        if b==224: return 4
        if b==237: return 5
        if 225<=b<=236 or 238<=b<=239: return 2
        if b==240: return 6
        if b==244: return 7
        if 241<=b<=243: return 3
        return 255
    if state==4: return 1 if 160<=b<=191 else 255
    if state==5: return 1 if 128<=b<=159 else 255
    if state==6: return 2 if 144<=b<=191 else 255
    if state==7: return 2 if 128<=b<=143 else 255
    return state-1 if 1<=state<=3 and 128<=b<=191 else 255
