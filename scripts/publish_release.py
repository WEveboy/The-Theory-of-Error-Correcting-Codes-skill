"""Publish prepared assets using the repository's ephemeral Actions token."""
import hashlib,json,os,time,urllib.error,urllib.parse,urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    repo=os.environ['GITHUB_REPOSITORY'];commit=os.environ['GITHUB_SHA'];token=os.environ['GITHUB_TOKEN'];tag='edition-v1.0.0'
    if repo!='WEveboy/The-Theory-of-Error-Correcting-Codes-skill':raise RuntimeError('unexpected publication repository')
    def api(path,method='GET',data=None,binary=False):
        url=path if path.startswith('https://') else 'https://api.github.com'+path
        headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'BooleanVectorResearch-Release','X-GitHub-Api-Version':'2022-11-28'}
        if data is not None:
            headers['Content-Type']='application/octet-stream' if binary else 'application/json'
            data=data if binary else json.dumps(data).encode()
        with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers,method=method),timeout=90) as r:return json.load(r)
    releases=api('/repos/'+repo+'/releases')
    if any(r['tag_name']==tag for r in releases):raise RuntimeError('first edition already exists; inspect rather than overwrite')
    release=api('/repos/'+repo+'/releases','POST',dict(tag_name=tag,target_commitish=commit,name='第一版 V1 · Boolean Vector Research Skills',draft=False,prerelease=False,body='公开版本1.0.0，冻结开发基线0.2.2。Codex与DeepSeek Harness安装版共享16张能力卡及8个数学/审计程序。两份19页TeX/PDF教程均从安装仓颉开始。安装包、源码ZIP与SHA256SUMS见下方；正文和维护流程见仓库README。测试与打包由本次CI完成，宿主付费模型会话不包含在契约测试中。'))
    assets=[]
    for path in sorted((ROOT/'dist').iterdir()):
        if not path.is_file():continue
        if path.suffix not in ('.zip','.tgz','.pdf') and path.name!='SHA256SUMS.txt':continue
        data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
        item=api(release['upload_url'].split('{')[0]+'?name='+urllib.parse.quote(path.name),'POST',data,True)
        if item.get('digest') and item['digest']!='sha256:'+digest:raise RuntimeError('GitHub asset digest mismatch: '+path.name)
        verified=False
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(item['browser_download_url'],headers={'User-Agent':'BooleanVectorResearch-Verify'}),timeout=90) as r:
                    actual=hashlib.sha256(r.read()).hexdigest()
                if actual!=digest:raise RuntimeError('downloaded asset hash mismatch: '+path.name)
                verified=True;break
            except urllib.error.HTTPError:
                if attempt==3:raise
                time.sleep(2)
        assert verified
        assets.append(dict(name=path.name,sha256=digest,bytes=len(data),url=item['browser_download_url']))
    result=dict(status='published_and_download_verified',commit=commit,tag=tag,release_url=release['html_url'],assets=assets)
    (ROOT/'build/remote-release-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
