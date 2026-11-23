"""The loop's promises, on stand-in controls. Run: python3 -m unittest discover -s tests"""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "loop"))
try:
    import oa
except (ImportError, ValueError) as e:
    raise unittest.SkipTest(f"needs AT-SPI: {e}")


class Control:
    def __init__(self, name, role="toggle button", on=False, usable=True, works=True, accepts=True, vanishes=False):
        self.__dict__.update(locals()); self.pressed = 0; self.there = True

    def get_name(self): return self.name
    def get_role_name(self): return self.role
    def clear_cache_single(self): pass
    def get_action_iface(self): return self
    def get_state_set(self): return self

    def do_action(self, _):
        self.pressed += 1
        if not self.accepts: return False
        if self.works: self.on = not self.on
        if self.vanishes: self.there = False
        return True

    def contains(self, s):
        return {oa.S.CHECKED: self.on, oa.S.PRESSED: False, oa.S.CHECKABLE: False, oa.S.SENSITIVE: self.usable,
                oa.S.ENABLED: self.usable, oa.S.SHOWING: self.there}[s]


class Press(unittest.TestCase):
    def setUp(self): oa.SETTLE = 0.05

    def test_says_the_new_state(self):
        c = Control("Bold")
        self.assertEqual((oa.press(c), oa.press(c)), ("Bold is on.", "Bold is off."))

    def test_does_not_claim_a_change_that_did_not_happen(self):
        self.assertEqual(oa.press(Control("Bold", works=False)), "Pressed Bold. It is still off.")

    def test_greyed_out_is_never_pressed(self):
        c = Control("Redo", usable=False)
        self.assertIn("Nothing was pressed", oa.press(c)); self.assertEqual(c.pressed, 0)

    def test_refusal_is_reported(self):
        self.assertIn("refused", oa.press(Control("Bold", accepts=False)))

    def test_plain_button_says_it_cannot_tell(self):
        self.assertEqual(oa.press(Control("Print", role="push button")), "Pressed Print. I could not tell what changed.")

    def test_a_control_that_leaves(self):
        self.assertIn("gone from the screen", oa.press(Control("Close", role="push button", vanishes=True)))


class Choose(unittest.TestCase):
    names = ["Bold", "End", "Paragraph Style", "Paragraph style", "Undo"]

    def test_exact(self): self.assertEqual(oa.pick("bold", self.names), ("press", [0]))
    def test_two_of_a_name_asks(self): self.assertEqual(oa.pick("paragraph style", self.names), ("ask", [2, 3]))
    def test_near_asks(self): self.assertEqual(oa.pick("undoe", self.names)[0], "ask")
    def test_absent(self): self.assertEqual(oa.pick("archive", self.names), ("none", []))
    def test_no_controls(self): self.assertEqual(oa.pick("bold", []), ("none", []))

    def test_words(self):
        self.assertEqual(oa.parse("Press the Bold button."), ("press", "bold"))
        self.assertEqual(oa.parse("Where am I?"), ("where", ""))
        self.assertEqual(oa.parse("delete everything")[0], "unknown")


if __name__ == "__main__":
    unittest.main()
