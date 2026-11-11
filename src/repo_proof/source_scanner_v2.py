"""Untrusted certificate generator for the independent Lean source automaton.

No generated state/event is accepted without kernel checking its transition.
"""
import copy


def initial():
    return dict(good=True,mode='normal',word=0,stack='',header=True,
                expect='idle',path='',collect=False)


def word(c):
    return 'a'<=c<='z' or 'A'<=c<='Z' or '0'<=c<='9' or c=='_'


def canonical(p):
    return (bool(p) and all(s not in ('','.','..') for s in p.split('/'))
            and ':' not in p.split('/')[0]
            and all(ord(c)>=32 and ord(c)!=127 and c not in '\\"' for c in p))


PREFIXES={}
for keyword,ids in [('import',[1,2,3,4,5,6]),('interface',[1,7,8,9,10,11,12,13,14]),
                    ('struct',[15,16,17,18,19,20]),('union',[21,22,23,24,25]),
                    ('enum',[26,27,28,29]),('const',[30,31,32,33,34]),
                    ('feature',[35,36,37,38,39,40,41])]:
    for length,code in enumerate(ids,1): PREFIXES[keyword[:length]]=code
PREFIX_TEXT={code:text for text,code in PREFIXES.items()}


def flush(q):
    code=q['word']
    q.update(mode='normal',word=0)
    if code==6:
        if q['header'] and not q['stack'] and q['expect']=='idle': q['expect']='path'
        else: q['good']=False
    elif q['expect']!='idle': q['good']=False
    elif not q['stack'] and code in (20,25,14,29,34,41):
        q['header']=False


def normal(q,c):
    if not q['good']: return None
    if word(c): q.update(mode='word',word=PREFIXES.get(c,0))
    elif c in ' \t\r\n': pass
    elif c=='/': q['mode']='slash'
    elif c=='"':
        if q['expect']=='semi': q['good']=False
        else: q.update(mode='quoted',collect=q['expect']=='path',path='')
    elif c==';':
        if q['expect']=='semi':
            p=q['path'][::-1]; q.update(expect='idle',path='',collect=False); return p
        elif q['expect']=='path': q['good']=False
    elif q['expect']!='idle': q['good']=False
    elif c in '([{': q['stack']=c+q['stack']
    elif c in ')]}':
        if q['stack'] and q['stack'][0]=={')':'(',']':'[','}':'{'}[c]: q['stack']=q['stack'][1:]
        else: q['good']=False
    elif c in '-+?=><,|&.@': pass
    else: q['good']=False
    return None


def step(q,c):
    if not q['good']: return None
    m=q['mode']
    if m=='normal': return normal(q,c)
    if m=='word':
        if word(c):
            if q['word']: q['word']=PREFIXES.get(PREFIX_TEXT[q['word']]+c,0)
        else: flush(q); return normal(q,c)
    elif m=='slash':
        if c=='/': q['mode']='line'
        elif c=='*': q['mode']='block'
        else: q['good']=False
    elif m=='line':
        if c=='\n': q['mode']='normal'
    elif m=='block':
        if c=='*': q['mode']='star'
    elif m=='star':
        if c=='/': q['mode']='normal'
        elif c!='*': q['mode']='block'
    elif m=='quoted':
        if c=='\n': q['good']=False
        elif c=='\\':
            if q['collect']: q['good']=False
            else: q['mode']='escaped'
        elif c=='"':
            if q['collect']:
                if canonical(q['path'][::-1]): q.update(mode='normal',expect='semi')
                else: q['good']=False
            else: q['mode']='normal'
        elif q['collect']: q['path']=c+q['path']
    elif m=='escaped':
        if word(c) or c in '.~!=&^-\\?\'"': q['mode']='quoted'
        else: q['good']=False
    return None


def finish(q):
    q=copy.copy(q)
    if q['mode']=='word': flush(q)
    elif q['mode']=='line': q['mode']='normal'
    return q['good'] and q['mode']=='normal' and not q['stack'] and q['expect']=='idle'


def certificate(data,chunk_chars=256):
    text=data.decode('utf-8',errors='strict')
    q=initial(); pieces=[]; imports=[]
    for start in range(0,len(text),chunk_chars):
        part=text[start:start+chunk_chars]; es=[]
        for c in part:
            event=step(q,c)
            if event is not None: es.append(event)
        pieces.append({'text':part,'after':copy.copy(q),'events':es})
        imports+=es
    if not finish(q): raise ValueError('source outside import-projection specification: '+repr(q))
    return pieces,imports


def lean_string(s):
    import json
    if any(ord(c)<32 and c not in '\r\n\t' for c in s):
        raise ValueError('unsupported control character in Lean literal encoder')
    return json.dumps(s,ensure_ascii=False)


def lean_control(q):
    boolean=lambda x:'true' if x else 'false'
    def chars(s):
        return '['+', '.join("'"+({'\\':'\\\\',"'":"\\'"}.get(c,c))+"'" for c in s)+']'
    return ('⟨'+', '.join([boolean(q['good']),'.'+q['mode'],str(q['word']),
            chars(q['stack']),boolean(q['header']),'.'+q['expect'],
            chars(q['path']),boolean(q['collect'])])+'⟩')
