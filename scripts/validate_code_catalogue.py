"""Check every reference against the actual restricted Docker judge."""
import argparse
import concurrent.futures
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import code_runner

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',default='');parser.add_argument('--workers',type=int,default=3);args=parser.parse_args()
    folder=ROOT/'resources/code_catalogue';rows=json.loads((folder/'questions.json').read_text(encoding='utf8'))
    if args.only:rows=[r for r in rows if args.only in r['key']]
    def run(row):
        try:r=code_runner.judge((folder/row['reference']).read_bytes(),row['language'],row['programming']['problems'][0]);return {'key':row['key'],'result':r}
        except Exception as e:return {'key':row['key'],'error':str(e)}
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for r in pool.map(run,rows):
            results.append(r);print(r['key'],r.get('result',{}).get('verdict',r.get('error')),flush=True)
    report=ROOT/'backups'/('catalogue-validation'+('-'+args.only if args.only else '')+'.json');report.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    passed=sum(r.get('result',{}).get('verdict')=='AC' for r in results);print(f'Passed {passed}/{len(results)}',flush=True)
    return 0 if passed==len(results) else 1

if __name__=='__main__':raise SystemExit(main())
