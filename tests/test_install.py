import importlib.util,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'scripts/install_codex.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)

class InstallTests(unittest.TestCase):
    def test_fresh_install_and_hash_verification(self):
        with tempfile.TemporaryDirectory() as d:
            r=installer.install(Path(d));self.assertEqual(r['public_version'],'1.0.0');self.assertTrue((Path(r['target'])/'resources/research_core.py').exists())
    def test_existing_preserved_and_backed_up_on_explicit_replace(self):
        with tempfile.TemporaryDirectory() as d:
            installer.install(Path(d));p=Path(d)/installer.NAME/'user-note.txt';p.write_text('keep')
            with self.assertRaises(ValueError):installer.install(Path(d))
            self.assertEqual(p.read_text(),'keep')
            r=installer.install(Path(d),True);self.assertEqual((Path(r['backup'])/'user-note.txt').read_text(),'keep')
    def test_source_corruption_prevents_install(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d)/'fake';fake.mkdir();(fake/'EDITION.json').write_text('{"files":{"missing.py":"'+'0'*64+'"}}')
            with patch.object(installer,'source_directory',return_value=fake):
                with self.assertRaises(OSError):installer.install(Path(d)/'target')
            self.assertFalse((Path(d)/'target').exists())

if __name__=='__main__':unittest.main()
