import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "tools/vm"))
from spoken import spoken


def line(sec, us, body): return f"[Tue Nov 24 05:04:{sec} 2026 : {us}] speechd:     {body}\n"


def sent(sec, us, text): return line(sec, us, f"Command sent to output module: |{text}| (0)")


def ended(sec, code): return line(sec, 1, f"Event from output module while speaking: |{code} X\n{code} X\n|")


def message(sec, us, text): return sent(sec, us, "SET\n") + sent(sec, us, "rate=0\n.\n") + sent(sec, us, "SPEAK\n") + sent(sec, us, text) + sent(sec, us, "\n.\n")


class Spoken(unittest.TestCase):
    def test_only_words_are_kept_not_the_protocol(self):
        self.assertEqual([x[2] for x in spoken(message(52, 5, "Hello"))], ["Hello"])

    def test_the_time_is_that_lines_own_with_short_microseconds_padded(self):
        self.assertEqual(spoken("[stray : 9] x\n" + message(53, 19863, "Hi"))[0][0], "05:04:53.019")

    def test_marks_and_entities_are_undone(self):
        self.assertEqual(spoken(message(52, 1, '<speak>A.<mark name="b"/> B &amp; &lt;c&gt;</speak>'))[0][2], "A. B & <c>")

    def test_words_over_two_lines_are_one_message(self):
        self.assertEqual(spoken(message(52, 1, "one\ntwo"))[0][2], "one two")

    def test_finished_cut_off_and_unknown_are_three_answers(self):
        log = message(52, 1, "a") + ended(52, 702) + message(53, 1, "b") + ended(53, 703) + message(54, 1, "c")
        self.assertEqual([x[1] for x in spoken(log)], ["finished", "cut off", None])

    def test_a_single_character_counts(self):
        self.assertEqual(spoken(sent(52, 1, "CHAR\n") + sent(52, 1, "x"))[0][2], "x")

    def test_empty_log(self): self.assertEqual(spoken(""), [])
