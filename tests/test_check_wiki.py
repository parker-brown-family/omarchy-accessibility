"""Break a copy of the wiki one way at a time; the checker must fail each time. Run: python3 -m unittest -v"""
import shutil, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_wiki import check

SNAP = (ROOT / "snapshots").is_dir()


class Mutations(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for d in ("wiki", "docs", "snapshots"):
            if (ROOT / d).is_dir():
                shutil.copytree(ROOT / d, self.tmp / d)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def edit(self, path, old, new):
        p = self.tmp / path
        s = p.read_text()
        self.assertIn(old, s)
        p.write_text(s.replace(old, new, 1))

    def fails(self, part):
        self.assertTrue(any(part in e for e in check(self.tmp)[0]), check(self.tmp)[0])

    def test_clean(self):
        self.assertEqual(check(self.tmp)[0], [])

    @unittest.skipUnless(SNAP, "stored copies are not published")
    def test_altered_quote(self):
        self.edit("wiki/sources/savant-2024.md", "395 seconds", "305 seconds")
        self.fails("not in the stored copy")

    @unittest.skipUnless(SNAP, "stored copies are not published")
    def test_altered_copy(self):
        (self.tmp / "snapshots/savant-2024.txt").write_text("gone")
        self.fails("does not match its sha256")

    def test_missing_source(self):
        (self.tmp / "wiki/sources/qa-doc-2026.md").unlink()
        self.fails("no such source")

    def test_missing_finding(self):
        (self.tmp / "wiki/findings/pause-and-ask.md").unlink()
        self.fails("no such finding")

    def test_missing_measurement(self):
        shutil.rmtree(self.tmp / "docs")
        self.fails("no such source measure:")

    def test_superseded_by_nothing(self):
        self.edit("wiki/decisions/0002-mit.md", "status: approved", "status: superseded")
        self.fails("must agree")

    def test_unknown_read_level(self):
        self.edit("wiki/sources/savant-2024.md", "read: passages", "read: skimmed")
        self.fails("read must be one of")

    def test_no_copy_is_a_note_not_a_pass(self):
        (self.tmp / "snapshots/savant-2024.txt").unlink(missing_ok=True)
        self.assertTrue(any("UNCHECKED sources/savant-2024" in n for n in check(self.tmp)[1]))


if __name__ == "__main__":
    unittest.main()
