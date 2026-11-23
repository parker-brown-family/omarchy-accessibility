import gi,time,json,statistics as st
gi.require_version('Atspi','2.0'); gi.require_version('Gio','2.0')
from gi.repository import Atspi,Gio,GLib
Atspi.init(); d=Atspi.get_desktop(0)
addr=Gio.bus_get_sync(Gio.BusType.SESSION).call_sync('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress',None,None,0,-1).unpack()[0]
con=Gio.DBusConnection.new_for_address_sync(addr,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
def call(bus,path,iface,m,args=None):
    return con.call_sync(bus,path,iface,m,args,None,0,20000,None).unpack()
kids=call('org.a11y.atspi.Registry','/org/a11y/atspi/accessible/root','org.a11y.atspi.Accessible','GetChildren')[0]
for bus,path in kids:
    try:
        name=call(bus,path,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',('org.a11y.atspi.Accessible','Name')))[0]
    except Exception as e: name='?'
    rt=[]
    for _ in range(100):
        t=time.perf_counter()
        try: call(bus,path,'org.freedesktop.DBus.Properties','Get',GLib.Variant('(ss)',('org.a11y.atspi.Accessible','Name')))
        except Exception: pass
        rt.append((time.perf_counter()-t)*1e3)
    out=dict(app=name,roundtrip_ms=round(st.median(rt),2))
    try:
        t=time.perf_counter(); items=call(bus,'/org/a11y/atspi/cache','org.a11y.atspi.Cache','GetItems')[0]; out['cache_ms']=round((time.perf_counter()-t)*1e3,1); out['cache_items']=len(items)
    except Exception as e: out['cache_err']=str(e)[:90]
    print(json.dumps(out))
