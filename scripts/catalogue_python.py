"""Independent complete Python reference programs for adapted Exercism tasks."""
SOLVER=r'''
import sys,json,re,math
SLUG=__SLUG__
def solve(p,i):
 s=SLUG
 if s=='collatz-conjecture':
  n=i['number'];r=0
  if n<=0:raise ValueError()
  while n!=1:n=n//2 if n%2==0 else n*3+1;r+=1
  return r
 if s=='armstrong-numbers':
  n=i['number'];return n==sum(int(c)**len(str(n)) for c in str(n))
 if s=='acronym':return ''.join(w[0] for w in re.sub(r"[^A-Za-z0-9' ]",' ',i['phrase']).split()).upper()
 if s in {'atbash-cipher','affine-cipher'}:
  text=re.sub('[^a-z0-9]','',i['phrase'].lower());a,b=(i.get('key') or {'a':1,'b':0}).values()
  if s=='affine-cipher' and math.gcd(a,26)!=1:raise ValueError()
  out=''
  for c in text:
   if c.isdigit():out+=c;continue
   x=ord(c)-97
   if s=='atbash-cipher':x=25-x
   elif p=='encode':x=(a*x+b)%26
   else:x=(pow(a,-1,26)*(x-b))%26
   out+=chr(97+x)
  return ' '.join(out[k:k+5] for k in range(0,len(out),5)) if p=='encode' else out
 if s=='binary-search-tree':
  tree=None
  def insert(t,v):
   if t is None:return {'data':v,'left':None,'right':None}
   side='left' if v<=t['data'] else 'right';t[side]=insert(t[side],v);return t
  for v in i['treeData']:tree=insert(tree,v)
  return tree if p=='data' else sorted(i['treeData'])
 if s=='diamond':
  n=ord(i['letter'])-65;rows=[]
  for k in range(n+1):
   row=[' ']*(2*n+1);row[n-k]=row[n+k]=chr(65+k);rows.append(''.join(row))
  return rows+rows[-2::-1]
 if s=='etl':return {c.lower():int(v) for v,letters in i['legacy'].items() for c in letters}
 if s=='high-scores':
  a=i['scores']
  if p in {'latest','latestAfterTopThree','latestAfterBest'}:return a[-1]
  if p=='personalBest':return max(a)
  if p=='personalTopThree':return sorted(a,reverse=True)[:3]
  return a
 if s=='matching-brackets':
  stack=[]
  for c in i['value']:
   if c in '([{':stack.append(c)
   elif c in ')]}':
    if not stack or stack.pop()!='([{'[')]}'.index(c)]:return False
  return not stack
 if s=='pascals-triangle':
  a=[]
  for n in range(i['count']):a.append([math.comb(n,k) for k in range(n+1)])
  return a
 if s=='perfect-numbers':
  n=i['number']
  if n<=0:raise ValueError()
  total=0
  for d in range(1,math.isqrt(n)+1):
   if n%d==0:
    if d<n:total+=d
    if n//d!=d and n//d<n:total+=n//d
  return 'perfect' if total==n else 'abundant' if total>n else 'deficient'
 if s=='pig-latin':
  def word(w):
   if w[0] in 'aeiou' or w.startswith(('xr','yt')):return w+'ay'
   k=0
   while k<len(w):
    if w[k] in 'aeiou' or (k>0 and w[k]=='y'):break
    if w[k:k+2]=='qu':k+=2;break
    k+=1
   return w[k:]+w[:k]+'ay'
  return ' '.join(word(w) for w in i['phrase'].split())
 if s=='roman-numerals':
  n=i['number'];out=''
  for v,t in [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]:
   q,n=divmod(n,v);out+=t*q
  return out
 if s=='sieve':
  n=i['limit'];a=[True]*(n+1)
  for p in range(2,math.isqrt(n)+1):
   if a[p]:
    for m in range(p*p,n+1,p):a[m]=False
  return [x for x in range(2,n+1) if a[x]]
 if s=='sum-of-multiples':return sum(n for n in range(1,i['limit']) if any(f and n%f==0 for f in i['factors']))
 if s=='wordy':
  q=i['question']
  if not q.startswith('What is ') or not q.endswith('?'):raise ValueError()
  parts=q[8:-1].replace('multiplied by','*').replace('divided by','/').replace('plus','+').replace('minus','-').split()
  if not parts or len(parts)%2==0:raise ValueError()
  value=int(parts[0])
  for k in range(1,len(parts),2):
   n=int(parts[k+1]);op=parts[k]
   if op=='+':value+=n
   elif op=='-':value-=n
   elif op=='*':value*=n
   elif op=='/':value=value//n
   else:raise ValueError()
  return value
 if s=='rna-transcription':return ''.join({'G':'C','C':'G','T':'A','A':'U'}[c] for c in i['dna'])
 if s=='nucleotide-count':
  if any(c not in 'ACGT' for c in i['strand']):raise ValueError()
  return {c:i['strand'].count(c) for c in 'ACGT'}
 if s=='proverb':
  words=i['strings']
  return [f'For want of a {a} the {b} was lost.' for a,b in zip(words,words[1:])]+([f'And all for the want of a {words[0]}.'] if words else [])
 raise ValueError('Unknown task')
try:
 request=json.load(sys.stdin);answer=solve(request['property'],request['input'])
except (ValueError,KeyError,ZeroDivisionError,IndexError):answer='ERROR'
print(json.dumps(answer,ensure_ascii=False,separators=(',',':')))
'''

DESCRIPTIONS={
'collatz-conjecture':'property steps, input {number:n}. Với n dương, lặp n/2 nếu chẵn, 3n+1 nếu lẻ đến 1; trả số bước. n ≤ 0 trả "ERROR".',
'armstrong-numbers':'property isArmstrongNumber, input {number:n}, n ≥ 0. Trả boolean: n có bằng tổng từng chữ số lũy thừa số chữ số của n không? Python cần xử lý số nguyên lớn.',
'acronym':'property abbreviate, input {phrase:string}. Lấy chữ cái đầu mỗi từ để viết tắt IN HOA; khoảng trắng, gạch nối và gạch dưới phân tách từ; dấu nháy trong từ không phân tách.',
'atbash-cipher':'property encode/decode, input {phrase:string}. Ánh xạ a↔z, b↔y,…; giữ chữ số, bỏ dấu câu và khoảng trắng, chuyển thường. Encode nhóm 5 ký tự cách nhau một dấu cách; decode không nhóm.',
'affine-cipher':'property encode/decode, input {phrase:string,key:{a:int,b:int}}. Chữ a-z mã 0..25, encode=(a*x+b)%26; decode dùng nghịch đảo modulo. Giữ chữ số, bỏ dấu câu, chuyển thường; encode nhóm 5. Nếu gcd(a,26) ≠ 1 trả "ERROR".',
'binary-search-tree':'property data/sortedData, input {treeData:[string,…]}. Chèn lần lượt vào BST theo thứ tự từ điển, giá trị ≤ nút đi trái. data trả cây {data,left,right}, nhánh rỗng null; sortedData trả mảng duyệt inorder.',
'diamond':'property rows, input {letter:"A".."Z"}. Trả mảng các dòng hình thoi chữ: A ở đỉnh và đáy, hàng giữa là letter; hai đường chéo tăng từ A. Giữ cả dấu cách đầu/cuối để mỗi dòng có chiều rộng 2*(letter-A)+1.',
'etl':'property transform, input {legacy:{"điểm":["CHỮ",…]}}. Đổi bảng nhóm chữ theo điểm thành object ánh xạ từng chữ thường sang điểm nguyên.',
'high-scores':'input {scores:[int,…]} không rỗng. property scores trả mảng gốc, latest trả phần tử cuối, personalBest trả lớn nhất, personalTopThree trả tối đa 3 điểm giảm dần có giữ trùng. latestAfterTopThree/latestAfterBest cũng phải trả điểm cuối gốc; scoresAfterTopThree/scoresAfterBest trả mảng gốc không bị thay đổi.',
'matching-brackets':'property isPaired, input {value:string}. Trả boolean ngoặc (),[],{} đóng mở đúng và lồng nhau đúng; bỏ qua ký tự khác.',
'pascals-triangle':'property rows, input {count:n}, n ≥ 0. Trả n dòng đầu tam giác Pascal dạng mảng 2 chiều, dòng 0 là [1]. count=0 trả [].',
'perfect-numbers':'property classify, input {number:n}. Tổng ước dương nhỏ hơn n bằng/lớn/nhỏ hơn n thì trả "perfect"/"abundant"/"deficient". n ≤ 0 trả "ERROR".',
'pig-latin':'property translate, input {phrase:string} gồm từ tiếng Anh chữ thường. Bắt đầu nguyên âm hoặc xr/yt thì thêm ay. Còn lại chuyển cụm phụ âm đầu ra sau rồi thêm ay; qu đi cùng, y sau ký tự đầu được xem là nguyên âm. Trả câu đã đổi.',
'roman-numerals':'property roman, input {number:n}, 1 ≤ n ≤ 3999. Trả số La Mã chuẩn với I,V,X,L,C,D,M và cặp trừ IV,IX,XL,XC,CD,CM.',
'sieve':'property primes, input {limit:n}, n ≥ 1. Dùng sàng Eratosthenes, trả mảng mọi số nguyên tố ≤ n tăng dần.',
'sum-of-multiples':'property sum, input {factors:[int,…],limit:n}, các số không âm. Tổng những số nguyên dương < n chia hết ít nhất một factor khác 0, mỗi số chỉ tính một lần.',
'wordy':'property answer, input {question:string}. Phân tích câu "What is …?" chứa số nguyên âm/dương và plus, minus, multiplied by, divided by; tính lần lượt từ trái sang phải (không ưu tiên nhân chia). Cú pháp sai hoặc phép toán không hỗ trợ trả "ERROR".',
'rna-transcription':'property toRna, input {dna:string}. Trả RNA với G→C, C→G, T→A, A→U; chuỗi rỗng hợp lệ.',
'nucleotide-count':'property nucleotideCounts, input {strand:string}. Trả object đếm A,C,G,T, luôn đủ 4 khóa. Có ký tự khác trả "ERROR".',
'proverb':'property recite, input {strings:[string,…]}. Mỗi cặp liền kề a,b tạo dòng "For want of a a the b was lost." (thay a,b bằng từ tương ứng). Cuối thêm "And all for the want of a FIRST.". Danh sách rỗng trả [].'
}
