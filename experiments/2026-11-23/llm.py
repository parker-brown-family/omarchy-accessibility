import json,time,urllib.request,statistics as st
tools=[{"type":"function","function":{"name":n,"description":d,"parameters":{"type":"object","properties":p,"required":list(p)}}} for n,d,p in [
("move_window","Move an app window to a workspace",{"app":{"type":"string"},"workspace":{"type":"integer"}}),
("focus_workspace","Switch to a workspace",{"workspace":{"type":"integer"}}),
("open_app","Open an application",{"app":{"type":"string"}}),
("press_control","Press the named control in the focused app",{"name":{"type":"string"}}),
("read","Read aloud the focused thing, window, or page",{"what":{"type":"string","enum":["focus","window","page","notifications"]}}),
("set_volume","Set volume percent",{"percent":{"type":"integer"}}),
("ask","Ask the person a clarifying question",{"question":{"type":"string"}})]]
cases=[("put my email on workspace three","move_window"),("go to workspace five","focus_workspace"),("open the browser","open_app"),("press save","press_control"),("what's on this page","read"),("where am I","read"),("turn it down to twenty percent","set_volume"),("read my notifications","read"),("click the send button","press_control"),("close it","ask"),("start libreoffice","open_app"),("delete that","ask")]
def go(t):
    b=json.dumps(dict(model="qwen3.5:9b",stream=False,think=False,keep_alive="2m",tools=tools,options=dict(temperature=0,num_ctx=4096),messages=[{"role":"system","content":"You control a desktop for a blind person. Call exactly one tool. If the target is ambiguous or destructive, call ask."},{"role":"user","content":t}])).encode()
    s=time.perf_counter();r=json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/chat",b,{"Content-Type":"application/json"}),timeout=120));return (time.perf_counter()-s)*1e3,r["message"].get("tool_calls"),r
print('load',round(go("hello")[0]))
L=[];ok=0
for t,w in cases:
    ms,tc,r=go(t);n=tc[0]["function"]["name"] if tc else None;L.append(ms);ok+=n==w;print(f"{ms:.0f} ms {t!r} -> {n} {tc[0]['function']['arguments'] if tc else r['message']['content'][:60]} {'' if n==w else 'WANT '+w}")
print('median',round(st.median(L)),'max',round(max(L)),'ok',ok,'/',len(cases))
