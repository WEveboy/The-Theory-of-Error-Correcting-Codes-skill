import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import research_workflow as workflow


class WorkflowTests(unittest.TestCase):
    def test_gold_end_to_end_and_hashes(self):
        spec=dict(construction=dict(kind='gold',params=dict(n=3,k=1,polynomial=11)),advanced=True)
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run';m=workflow.run(spec,out)
            self.assertEqual(m['status'],'complete')
            for file,h in m['files'].items():self.assertEqual(hashlib.sha256((out/file).read_bytes()).hexdigest(),h)
            a=json.loads((out/'analysis.json').read_text());s=json.loads((out/'sbox.json').read_text())
            self.assertEqual(a['nonlinearity'],2);self.assertEqual(a['differential_uniformity'],2)
            self.assertEqual(s['bct']['boomerang_uniformity'],2)

    def test_trace_workflow_nonpermutation(self):
        spec=dict(construction=dict(kind='trace',params=dict(n=2,polynomial=7,terms=[dict(coefficient=1,exponent=1)])))
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run';workflow.run(spec,out)
            a=json.loads((out/'analysis.json').read_text());s=json.loads((out/'sbox.json').read_text())
            self.assertEqual(a['m'],1);self.assertTrue(a['balanced'])
            self.assertEqual(s['bct']['status'],'not_applicable')

    def test_existing_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'keep').write_text('unchanged')
            with self.assertRaises(ValueError):workflow.run({},p)
            self.assertEqual((p/'keep').read_text(),'unchanged')

    def test_invalid_input_no_experiment_created(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'run'
            with self.assertRaises(ValueError):workflow.run(dict(construction=dict(kind='gold',params=dict(n=4,k=2))),p)
            self.assertFalse(p.exists())
            with self.assertRaises(ValueError):workflow.run(dict(construction=dict(kind='table',params=dict(n=1,m=1,table=[0,1])),advanced=1),p)
            self.assertFalse(p.exists())

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);i=p/'spec.json';out=p/'run'
            i.write_text(json.dumps(dict(construction=dict(kind='quadratic-bent',params=dict(n=4)),sbox=False)))
            cmd=[sys.executable,str(Path(workflow.__file__).resolve()),'--input',str(i),'--out-dir',str(out)]
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
            self.assertFalse((out/'sbox.json').exists());self.assertTrue((out/'manifest.json').exists())
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertEqual(r.returncode,2)


if __name__=='__main__':unittest.main()
