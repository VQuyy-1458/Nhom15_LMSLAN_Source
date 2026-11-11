"""Download public exercise specifications as reference data, never executable code."""
from pathlib import Path
import concurrent.futures as futures
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'backups/problem-sources-20261111'
JAVA=['leap','difference-of-squares','hamming','raindrops','reverse-string','pangram','isogram','resistor-color','triangle','complex-numbers','rational-numbers','bank-account','grade-school','clock','binary-search','luhn','isbn-verifier','rotational-cipher','scrabble-score','word-count']
PYTHON=['collatz-conjecture','armstrong-numbers','acronym','atbash-cipher','affine-cipher','binary-search-tree','diamond','etl','high-scores','matching-brackets','pascals-triangle','perfect-numbers','pig-latin','roman-numerals','sieve','sum-of-multiples','wordy','rna-transcription','nucleotide-count','proverb']
CPP=[1068,1083,1069,1094,1071,1072,1617,1618,1754,2431,1621,1084,1090,1091,1619,1629,1074,2183,1141,1073]

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'LAN-LMS-course-catalogue/1.0'})
    with urllib.request.urlopen(request,timeout=35) as response:return response.read()

def fetch(item):
    name,url=item;path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():path.write_bytes(get(url))
    return {'path':name,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for track,slugs in [('java',JAVA),('python',PYTHON)]:
        jobs.append((track+'/LICENSE','https://raw.githubusercontent.com/exercism/'+track+'/main/LICENSE'))
        for slug in slugs:
            prefix='exercises/practice/'+slug+'/'
            for name in ['.docs/instructions.md','.meta/config.json']:
                jobs.append((track+'/'+prefix+name,'https://raw.githubusercontent.com/exercism/'+track+'/main/'+prefix+name))
            jobs.extend([(f'spec/{slug}/description.md',f'https://raw.githubusercontent.com/exercism/problem-specifications/main/exercises/{slug}/description.md'),(f'spec/{slug}/canonical-data.json',f'https://raw.githubusercontent.com/exercism/problem-specifications/main/exercises/{slug}/canonical-data.json')])
    jobs.append(('spec/LICENSE','https://raw.githubusercontent.com/exercism/problem-specifications/main/LICENSE'))
    jobs.extend([(f'cses/{i}.html',f'https://cses.fi/problemset/task/{i}/') for i in CPP])
    results=[];failures=[]
    with futures.ThreadPoolExecutor(max_workers=6) as pool:
        tasks={pool.submit(fetch,item):item for item in dict(jobs).items()}
        for task in futures.as_completed(tasks):
            try:results.append(task.result())
            except Exception as error:failures.append({'item':tasks[task],'error':str(error)})
    for slug in JAVA:
        config=OUT/('java/exercises/practice/'+slug+'/.meta/config.json')
        if config.exists():
            for path in json.loads(config.read_bytes()).get('files',{}).get('solution',[]):
                rel='exercises/practice/'+slug+'/'+path
                try:results.append(fetch(('java/'+rel,'https://raw.githubusercontent.com/exercism/java/main/'+rel)))
                except Exception as error:failures.append({'item':rel,'error':str(error)})
    (OUT/'manifest.json').write_text(json.dumps({'files':results,'failures':failures},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Downloaded',len(results),'reference files; failures',len(failures))
    for failure in failures:print(failure)

if __name__=='__main__':main()
