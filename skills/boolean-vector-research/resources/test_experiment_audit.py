import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import experiment_audit as audit
import research_workflow as workflow

PROJECT=dict(construction=dict(kind='gold',params=dict(n=3,k=1,polynomial=11)),sbox=True)

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.run=self.base/'run';workflow.run(PROJECT,self.run)
    def tearDown(self):self.temp.cleanup()
    def rewrite(self,name,value):
        (self.run/name).write_bytes((json.dumps(value)+'\n').encode())
        m=json.loads((self.run/'manifest.json').read_text());m['files'][name]=hashlib.sha256((self.run/name).read_bytes()).hexdigest()
        (self.run/'manifest.json').write_text(json.dumps(m))
    def test_success_replay_and_stage_log(self):
        r=audit.verify(self.run,True);self.assertEqual(r['status'],'recomputed_match');self.assertTrue(r['runtime_fingerprints_match'])
        rows=[json.loads(x) for x in (self.run/'execution.jsonl').read_text().splitlines()]
        self.assertEqual([r['sequence'] for r in rows],list(range(1,len(rows)+1)))
        self.assertIn(('construction','completed'),[(r['stage'],r['status']) for r in rows]);self.assertEqual(rows[-1]['status'],'ready_to_finalize')
    def test_byte_tamper_detected(self):
        with (self.run/'summary.md').open('ab') as f:f.write(b'tampered')
        r=audit.verify(self.run,True);self.assertEqual(r['status'],'hash_mismatch');self.assertEqual(r['recomputation'],'skipped_due_to_hash_mismatch')
    def test_rehashed_wrong_metric_rejected_by_replay(self):
        a=json.loads((self.run/'analysis.json').read_text());a['nonlinearity']=999;self.rewrite('analysis.json',a)
        self.assertEqual(audit.verify(self.run)['status'],'hash_consistent')
        self.assertEqual(audit.verify(self.run,True)['status'],'content_mismatch')
        a['nonlinearity']=2.0;self.rewrite('analysis.json',a)
        self.assertEqual(audit.verify(self.run,True)['status'],'content_mismatch')
    def test_cross_file_input_mismatch_without_replay(self):
        a=json.loads((self.run/'analysis.json').read_text());a['input']['table'][0]=7;self.rewrite('analysis.json',a)
        self.assertEqual(audit.verify(self.run)['status'],'content_mismatch')
    def test_manifest_required_files_and_version(self):
        p=self.run/'manifest.json';m=json.loads(p.read_text());del m['files']['project.json'];p.write_text(json.dumps(m))
        with self.assertRaises(audit.AuditError):audit.verify(self.run)
        m['tool_version']='99.0';p.write_text(json.dumps(m))
        with self.assertRaises(audit.AuditError):audit.verify(self.run)
    def test_unsafe_manifest_paths(self):
        p=self.run/'manifest.json';original=json.loads(p.read_text())
        for name in ['../outside','C:\\secret','/tmp/secret','dir/file','dir\\file','manifest.json']:
            m=json.loads(json.dumps(original));m['files'][name]='0'*64;p.write_text(json.dumps(m))
            with self.assertRaises(audit.AuditError,msg=name):audit.verify(self.run)
    def test_missing_file_and_invalid_manifest(self):
        (self.run/'summary.md').unlink()
        with self.assertRaises(audit.AuditError):audit.verify(self.run)
        (self.run/'manifest.json').write_text('[')
        with self.assertRaises(audit.AuditError):audit.verify(self.run)
    def test_read_size_bounds(self):
        with patch.object(audit,'MAX_TOTAL_BYTES',1):
            with self.assertRaises(audit.AuditError):audit.verify(self.run)
        with self.assertRaises(audit.AuditError):audit.read_bounded(self.run/'analysis.json',1)
    def test_replay_budget_and_type(self):
        with self.assertRaises(audit.AuditError):audit.verify(self.run,True,1)
        with self.assertRaises(audit.AuditError):audit.verify(self.run,1)
        with self.assertRaises(audit.AuditError):audit.verify(self.run,False,True)
    def test_runtime_change_is_separate_from_mathematics(self):
        e=json.loads((self.run/'environment.json').read_text());e['runtime_sha256']['research_core.py']='0'*64;self.rewrite('environment.json',e)
        r=audit.verify(self.run,True);self.assertEqual(r['status'],'recomputed_match');self.assertFalse(r['runtime_fingerprints_match'])
    def test_legacy_020_compatible(self):
        p=self.run/'manifest.json';m=json.loads(p.read_text());m['tool_version']='0.2.0'
        for name in ['environment.json','execution.jsonl']:del m['files'][name];(self.run/name).unlink()
        p.write_text(json.dumps(m));self.assertEqual(audit.verify(self.run,True)['status'],'recomputed_match')
    def test_sbox_presence_mismatch(self):
        p=json.loads((self.run/'project.json').read_text());p['sbox']=False;self.rewrite('project.json',p)
        self.assertEqual(audit.verify(self.run)['status'],'content_mismatch')
    def test_cli_success_and_output_protection(self):
        cmd=[sys.executable,str(Path(audit.__file__).resolve()),'--directory',str(self.run),'--recompute']
        out=self.base/'audit.json';p=subprocess.run(cmd+['--out',str(out)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);original=out.read_bytes()
        self.assertEqual(subprocess.run(cmd+['--out',str(out)],capture_output=True).returncode,2);self.assertEqual(out.read_bytes(),original)
        self.assertEqual(subprocess.run(cmd+['--out',str(self.run/'new.json')],capture_output=True).returncode,2)
        self.assertFalse((self.run/'new.json').exists())
    def test_cli_tamper_returns_one(self):
        (self.run/'summary.md').write_text('tampered')
        r=subprocess.run([sys.executable,str(Path(audit.__file__).resolve()),'--directory',str(self.run)],capture_output=True,text=True)
        self.assertEqual(r.returncode,1);self.assertEqual(json.loads(r.stdout)['status'],'hash_mismatch')

    def rehash(self,name,data):
        (self.run/name).write_bytes(data)
        p=self.run/'manifest.json';m=json.loads(p.read_text());m['files'][name]=hashlib.sha256(data).hexdigest();p.write_text(json.dumps(m))

    def test_strict_json_duplicates_and_nonfinite(self):
        for text in [b'{"n":3,"n":4}',b'{"value":NaN}',b'{"value":Infinity}',b'{"value":-Infinity}',b'{"value":1e999}']:
            with self.assertRaises(audit.AuditError,msg=text):audit.decode(text,'test.json')

    def test_rehashed_log_truncated_and_wrong_stage(self):
        original=(self.run/'execution.jsonl').read_bytes();rows=[json.loads(x) for x in original.splitlines()]
        self.rehash('execution.jsonl',b'\n'.join(original.splitlines()[:-1])+b'\n')
        r=audit.verify(self.run,True);self.assertEqual(r['status'],'content_mismatch');self.assertEqual(r['recomputation'],'skipped_due_to_content_mismatch')
        rows[2]['stage']='fictional'
        self.rehash('execution.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in rows))
        self.assertTrue(any(x['issue']=='stage_protocol_mismatch' for x in audit.verify(self.run)['failures']))

    def test_log_sequence_and_elapsed(self):
        rows=[json.loads(x) for x in (self.run/'execution.jsonl').read_bytes().splitlines()]
        rows[0]['sequence']=True;rows[-1]['elapsed_seconds']=0
        self.rehash('execution.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in rows))
        issues={x['issue'] for x in audit.verify(self.run)['failures']}
        self.assertIn('invalid_sequence',issues);self.assertIn('elapsed_time_decreased',issues)

    def test_log_utc_required(self):
        rows=[json.loads(x) for x in (self.run/'execution.jsonl').read_bytes().splitlines()]
        rows[0]['time_utc']='2026-10-27T12:00:00'
        self.rehash('execution.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in rows))
        with self.assertRaises(audit.AuditError):audit.verify(self.run)
        rows[0]['time_utc']='2026-10-27T00:00:00Z';rows[0]['elapsed_seconds']=10**400
        self.rehash('execution.jsonl',b''.join((json.dumps(x)+'\n').encode() for x in rows))
        with self.assertRaises(audit.AuditError):audit.verify(self.run)

    def test_provenance_schema(self):
        env=json.loads((self.run/'environment.json').read_text())
        variants=[dict(env,platform=''),dict(env,runtime_sha256={'../x.py':'0'*64}),dict(env,runtime_sha256={'x.py':'bad'}),dict(env,tool_version='wrong'),dict(env,created_utc='not a date')]
        for v in variants:
            self.rewrite('environment.json',v)
            with self.assertRaises(audit.AuditError):audit.verify(self.run)

    def test_recompute_pointer_and_escaped_tokens(self):
        a=json.loads((self.run/'analysis.json').read_text());a['nonlinearity']=123;self.rewrite('analysis.json',a)
        f=next(f for f in audit.verify(self.run,True)['failures'] if f['file']=='analysis.json')
        self.assertEqual(f['witness']['pointer'],'/nonlinearity');self.assertEqual(f['witness']['expected'],'2')
        self.assertEqual(audit.first_difference({'a~/':[1]},{'a~/':[2]})['pointer'],'/a~0~1/0')

    def test_typed_input_mismatch_without_replay(self):
        a=json.loads((self.run/'analysis.json').read_text());a['input']['n']=3.0;self.rewrite('analysis.json',a)
        self.assertEqual(audit.verify(self.run)['status'],'content_mismatch')

    def test_sbox_skipped_protocol(self):
        p=self.base/'skip';workflow.run(dict(PROJECT,sbox=False),p)
        self.assertEqual(audit.verify(p,True)['status'],'recomputed_match')

if __name__=='__main__':unittest.main()
