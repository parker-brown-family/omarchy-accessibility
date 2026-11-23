import gi,time,sys,json
gi.require_version('Atspi','2.0')
from gi.repository import Atspi
Atspi.init()
ACT={'button','push button','toggle button','check box','radio button','menu item','link','entry','text','combo box','list item','page tab','slider','table cell','icon','menu','switch','spin button'}
d=Atspi.get_desktop(0)
def walk(o,acc,depth=0):
    if o is None or depth>60 or len(acc)>20000: return
    try:
        acc.append((o.get_role_name(),o.get_name()))
        for i in range(o.get_child_count()): walk(o.get_child_at_index(i),acc,depth+1)
    except Exception as e: acc.append(('ERR',str(e)[:40]))
for i in range(d.get_child_count()):
    a=d.get_child_at_index(i)
    if a is None: continue
    ts=[]
    for _ in range(3):
        Atspi.Accessible.clear_cache(a) if hasattr(a,'clear_cache') else None
        acc=[];t=time.perf_counter();walk(a,acc);ts.append((time.perf_counter()-t)*1e3)
    act=[x for x in acc if x[0] in ACT]
    named=[x for x in act if x[1]]
    print(json.dumps(dict(app=a.get_name(),tk=a.get_toolkit_name(),nodes=len(acc),interactive=len(act),named=len(named),ms=[round(x,1) for x in ts],chars=sum(len(r)+len(n or '') for r,n in act))))
