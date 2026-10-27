"""Optional author workflow: stage a complete Bundle from source + frozen resources."""
import argparse,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--cangjie',required=True,type=Path);a=p.parse_args()
    bundle=ROOT/'build/capabilities';shutil.copytree(ROOT/'source',bundle,dirs_exist_ok=True)
    shutil.copytree(ROOT/'skills/boolean-vector-research/resources',bundle/'resources',dirs_exist_ok=True)
    subprocess.run([sys.executable,str(a.cangjie/'scripts/cangjie.py'),'compile','--bundle',str(bundle),'--out',str(ROOT/'build/recompiled-skill'),'--output','single'],check=True)
if __name__=='__main__':main()
