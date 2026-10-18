"""Run the browser state regressions without a DOM or a second filter engine."""
import shutil
import subprocess
import unittest

import engine
from server import boot


class WebTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is only needed for development tests")
    def test_template_and_saved_copy_lifetimes(self):
        result = subprocess.run([shutil.which("node"), "--test", "tool/test_workbench.cjs"],
                                cwd=engine.ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_server_exposes_same_six_templates(self):
        builds = boot()["config"]["builds"]
        self.assertEqual(len(builds), 6)
        self.assertEqual({b["id"] for b in builds if b["enabled"]},
                         {"flay-mana-lich", "skeleton-necromancer"})
        self.assertEqual(builds[-1]["id"], "heartseeker-shuriken-marksman")
        self.assertEqual(builds[-1]["name"], "追心手里剑")
        index = (engine.ROOT / "tool/web/index.html").read_text(encoding="utf-8")
        self.assertIn('<script src="workbench.js">', index)
        self.assertTrue((engine.ROOT / "tool/web/workbench.js").is_file())
