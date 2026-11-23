import gi,time,json,statistics as st
gi.require_version('Atspi','2.0')
from gi.repository import Atspi
Atspi.init(); d=Atspi.get_desktop(0)
for i in range(d.get_child_count()):
    a=d.get_child_at_index(i)
    if a is None or a.get_child_count()==0: continue
    f=a.get_child_at_index(0); c=f.get_collection_iface() if f else None
    if c is None: print('COLL',a.get_name(),'no Collection'); continue
    res=[]
    for _ in range(7):
        ss=Atspi.StateSet.new([Atspi.StateType.SHOWING])
        r=Atspi.MatchRule.new(ss,Atspi.CollectionMatchType.ALL,{},Atspi.CollectionMatchType.ALL,[],Atspi.CollectionMatchType.ANY,[],Atspi.CollectionMatchType.ALL,False)
        t=time.perf_counter(); m=c.get_matches(r,Atspi.CollectionSortOrder.CANONICAL,0,True); t1=time.perf_counter()
        for x in m: x.clear_cache_single() if hasattr(x,'clear_cache_single') else None
        n=[(x.get_role_name(),x.get_name()) for x in m]; t2=time.perf_counter(); res.append(((t1-t)*1e3,(t2-t)*1e3))
    print('COLL',a.get_name(),'frame',repr(f.get_name())[:60],'matches',len(m),'refs_ms',[round(x[0],1) for x in res],'with_names_ms',[round(x[1],1) for x in res])
# act: LibreOffice Bold toggle via action, wait for state
def find(o,pred,depth=0):
    if o is None or depth>40: return None
    try:
        if pred(o): return o
        for i in range(o.get_child_count()):
            r=find(o.get_child_at_index(i),pred,depth+1)
            if r: return r
    except Exception: return None
for i in range(d.get_child_count()):
    a=d.get_child_at_index(i)
    if a and a.get_name()=='soffice':
        b=find(a,lambda o:o.get_name()=='Bold' and 'button' in o.get_role_name() and o.get_action_iface())
        print('ACT found',b and b.get_role_name())
        if b:
            L=[]
            for _ in range(10):
                before=b.get_state_set().contains(Atspi.StateType.CHECKED) or b.get_state_set().contains(Atspi.StateType.PRESSED)
                t=time.perf_counter(); b.get_action_iface().do_action(0)
                while time.perf_counter()-t<2:
                    b.clear_cache_single() if hasattr(b,'clear_cache_single') else b.clear_cache()
                    s=b.get_state_set(); now=s.contains(Atspi.StateType.CHECKED) or s.contains(Atspi.StateType.PRESSED)
                    if now!=before: break
                L.append(round((time.perf_counter()-t)*1e3,1)); time.sleep(.2)
            print('ACT ms',L)
