import unittest
from tools.audit_pinned_source_rights import source_imports
class TestPinnedAudit(unittest.TestCase):
    def test_nested_dynamic_import(self):
        b=b"import os\nfrom core_lite.inner import x\nfrom .local import y\n\ndef later():\n    import requests\n    import importlib\n    importlib.import_module('optional')\n"
        x=source_imports(b)
        self.assertEqual(x["modules"],["core_lite","importlib","os","requests"])
        self.assertEqual(x["dynamic"],[{"line":8,"call":"import_module"}])
    def test_unparseable(self):
        self.assertEqual(source_imports(b"def bad(:")["status"],"UNPARSEABLE")
if __name__=="__main__":unittest.main()
