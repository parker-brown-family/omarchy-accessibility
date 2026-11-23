"""Print LibreOffice Writer's visible, named, pressable controls as JSON."""
import gi, json
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
Atspi.init(); d = Atspi.get_desktop(0); out = []
for i in range(d.get_child_count()):
    a = d.get_child_at_index(i)
    if not a or a.get_name() != "soffice": continue
    c = a.get_child_at_index(0).get_collection_iface()
    r = Atspi.MatchRule.new(Atspi.StateSet.new([Atspi.StateType.SHOWING]), Atspi.CollectionMatchType.ALL, {}, Atspi.CollectionMatchType.ALL, [], Atspi.CollectionMatchType.ANY, [], Atspi.CollectionMatchType.ALL, False)
    out = [(x.get_role_name(), x.get_name()) for x in c.get_matches(r, Atspi.CollectionSortOrder.CANONICAL, 0, True) if x.get_name() and x.get_action_iface()]
print("NAMES " + json.dumps(out))
