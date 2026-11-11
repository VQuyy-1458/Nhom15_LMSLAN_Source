"""CSES tasks: short Vietnamese restatements, official samples and independent cases."""
import bisect
import itertools
from collections import Counter

TASKS={
1068:('Weird Algorithm','Đọc n (1 ≤ n ≤ 10^6). Khi n chẵn chia 2, khi lẻ thay bằng 3n+1. In toàn bộ dãy từ n đến 1, cách nhau bằng dấu cách.'),
1083:('Missing Number','Dòng đầu n (2 ≤ n ≤ 2·10^5), dòng sau có n−1 số khác nhau trong 1..n. In số còn thiếu.'),
1069:('Repetitions','Đọc chuỗi DNA không rỗng gồm A,C,G,T, dài tối đa 10^6. In độ dài đoạn liên tiếp có cùng một ký tự dài nhất.'),
1094:('Increasing Array','Đọc n rồi n số a[i] (1 ≤ n ≤ 2·10^5, 1 ≤ a[i] ≤ 10^9). Mỗi bước tăng một phần tử lên 1. In tổng số bước ít nhất để dãy không giảm.'),
1071:('Number Spiral','Đọc t (1..10^5), mỗi dòng y x (1..10^9). Xoắn ốc: 1 ở (1,1); hàng 2 bắt đầu 2,3; hàng 1 cột 2 là 4; tiếp 5 ở (1,3),6 ở (2,3),7 ở (3,3),8 ở (3,2),9 ở (3,1). In giá trị ở hàng y, cột x cho mỗi truy vấn.'),
1072:('Two Knights','Đọc n (1..10000). Với mỗi k từ 1 đến n, in số cách đặt hai quân mã trên bàn k×k sao cho không ăn nhau. Hai quân không phân biệt, không cùng ô.'),
1617:('Bit Strings','Đọc n (1..10^6). In số chuỗi nhị phân độ dài n modulo 1,000,000,007.'),
1618:('Trailing Zeros','Đọc n (1..10^9). In số chữ số 0 ở cuối biểu diễn thập phân của n!.'),
1754:('Coin Piles','Đọc t rồi t cặp a b (0..10^9). Mỗi lượt bỏ 2 đồng từ một chồng và 1 đồng chồng kia. Có thể làm cả hai về 0 không? In YES hoặc NO mỗi dòng.'),
2431:('Digit Queries','Chuỗi vô hạn nối 123456789101112… . Đọc q rồi q vị trí k (1 ≤ q ≤ 1000, 1 ≤ k ≤ 10^18), đánh số từ 1. In chữ số tại mỗi vị trí.'),
1621:('Distinct Numbers','Đọc n (1..2·10^5) rồi n số nguyên (1..10^9). In số giá trị khác nhau.'),
1084:('Apartments','Đọc n m k, n kích thước mong muốn và m kích thước căn hộ (n,m ≤ 2·10^5; k ≤ 10^9). Mỗi căn cấp tối đa một người, mỗi người một căn, sai lệch kích thước không quá k. In số người được cấp tối đa.'),
1090:('Ferris Wheel','Đọc n x rồi n trọng lượng (n ≤ 2·10^5; mỗi trọng lượng ≤ x ≤ 10^9). Mỗi cabin chở tối đa 2 người, tổng ≤ x. In số cabin tối thiểu.'),
1091:('Concert Tickets','Đọc n m, n giá vé, rồi m ngân sách (n,m ≤ 2·10^5; giá ≤ 10^9). Mỗi khách lần lượt mua vé chưa bán đắt nhất không vượt ngân sách. In giá vé hoặc -1 nếu không mua được.'),
1619:('Restaurant Customers','Đọc n (1..2·10^5), n cặp giờ đến/rời (1 ≤ đến < rời ≤ 10^9), các mốc giờ khác nhau. In số khách đông nhất đồng thời.'),
1629:('Movie Festival','Đọc n (1..2·10^5), n cặp bắt đầu/kết thúc (bắt đầu < kết thúc ≤ 10^9). Xem nhiều phim nhất, được xem phim tiếp theo ngay khi phim trước kết thúc. In số phim tối đa.'),
1074:('Stick Lengths','Đọc n (1..2·10^5) và n độ dài (1..10^9). Chi phí tăng/giảm 1 đơn vị là 1. In chi phí ít nhất để mọi thanh dài bằng nhau.'),
2183:('Missing Coin Sum','Đọc n (1..2·10^5) và n đồng có mệnh giá (1..10^9). Mỗi đồng dùng tối đa một lần. In số nguyên dương nhỏ nhất không thể tạo bằng tổng một tập con.'),
1141:('Playlist','Đọc n (1..2·10^5) và n mã bài hát (1..10^9). In độ dài đoạn liên tiếp dài nhất không chứa hai bài trùng mã.'),
1073:('Towers','Đọc n (1..2·10^5) và n khối theo thứ tự, kích thước 1..10^9. Đặt khối lên đỉnh tháp chỉ khi nhỏ hơn đỉnh hiện tại, hoặc mở tháp mới. Không đổi thứ tự. In số tháp ít nhất.')
}

CPP=r'''#include <bits/stdc++.h>
using namespace std; using ll=long long;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);const int task=__ID__;
 if(task==1068){ll n;cin>>n;cout<<n;while(n!=1){n=n%2?n*3+1:n/2;cout<<' '<<n;}}
 else if(task==1083){ll n,x,s;cin>>n;s=n*(n+1)/2;for(int i=1;i<n;i++){cin>>x;s-=x;}cout<<s;}
 else if(task==1069){string s;cin>>s;int best=1,cnt=0;char prev=0;for(char c:s){cnt=c==prev?cnt+1:1;best=max(best,cnt);prev=c;}cout<<best;}
 else if(task==1094){int n;cin>>n;ll prev=0,ans=0,x;while(n--){cin>>x;ans+=max(0LL,prev-x);prev=max(prev,x);}cout<<ans;}
 else if(task==1071){int t;cin>>t;while(t--){ll y,x;cin>>y>>x;cout<<(y>x?(y%2?(y-1)*(y-1)+x:y*y-x+1):(x%2?x*x-y+1:(x-1)*(x-1)+y))<<'\n';}}
 else if(task==1072){ll n;cin>>n;for(ll k=1;k<=n;k++)cout<<k*k*(k*k-1)/2-4*(k-1)*(k-2)<<'\n';}
 else if(task==1617){int n;cin>>n;ll v=1;while(n--)v=v*2%1000000007;cout<<v;}
 else if(task==1618){ll n,ans=0;cin>>n;while(n){n/=5;ans+=n;}cout<<ans;}
 else if(task==1754){int t;cin>>t;while(t--){ll a,b;cin>>a>>b;cout<<((a+b)%3==0&&max(a,b)<=2*min(a,b)?"YES":"NO")<<'\n';}}
 else if(task==2431){int q;cin>>q;while(q--){ll k;cin>>k;ll len=1,start=1,count=9;while(k>count*len){k-=count*len;len++;start*=10;count*=10;}ll number=start+(k-1)/len;cout<<to_string(number)[(k-1)%len]<<'\n';}}
 else if(task==1621){int n;cin>>n;set<ll>s;while(n--){ll x;cin>>x;s.insert(x);}cout<<s.size();}
 else if(task==1084){int n,m;ll k;cin>>n>>m>>k;vector<ll>a(n),b(m);for(auto&v:a)cin>>v;for(auto&v:b)cin>>v;sort(a.begin(),a.end());sort(b.begin(),b.end());int i=0,j=0,r=0;while(i<n&&j<m){if(b[j]<a[i]-k)j++;else if(b[j]>a[i]+k)i++;else{r++;i++;j++;}}cout<<r;}
 else if(task==1090){int n;ll x;cin>>n>>x;vector<ll>a(n);for(auto&v:a)cin>>v;sort(a.begin(),a.end());int l=0,r=n-1,ans=0;while(l<=r){if(a[l]+a[r]<=x)l++;r--;ans++;}cout<<ans;}
 else if(task==1091){int n,m;cin>>n>>m;multiset<ll>s;while(n--){ll x;cin>>x;s.insert(x);}while(m--){ll x;cin>>x;auto i=s.upper_bound(x);if(i==s.begin())cout<<-1<<'\n';else{--i;cout<<*i<<'\n';s.erase(i);}}}
 else if(task==1619){int n;cin>>n;vector<pair<ll,int>>e;while(n--){ll a,b;cin>>a>>b;e.push_back({a,1});e.push_back({b,-1});}sort(e.begin(),e.end());int sum=0,ans=0;for(auto p:e){sum+=p.second;ans=max(ans,sum);}cout<<ans;}
 else if(task==1629){int n;cin>>n;vector<pair<ll,ll>>e;while(n--){ll a,b;cin>>a>>b;e.push_back({b,a});}sort(e.begin(),e.end());ll end=0,ans=0;for(auto p:e)if(p.second>=end){ans++;end=p.first;}cout<<ans;}
 else if(task==1074){int n;cin>>n;vector<ll>a(n);for(auto&v:a)cin>>v;sort(a.begin(),a.end());ll ans=0;for(ll x:a)ans+=abs(x-a[n/2]);cout<<ans;}
 else if(task==2183){int n;cin>>n;vector<ll>a(n);for(auto&v:a)cin>>v;sort(a.begin(),a.end());ll reachable=0;for(ll x:a){if(x>reachable+1)break;reachable+=x;}cout<<reachable+1;}
 else if(task==1141){int n;cin>>n;map<ll,int>last;int left=0,best=0;for(int i=0;i<n;i++){ll x;cin>>x;if(last.count(x))left=max(left,last[x]+1);last[x]=i;best=max(best,i-left+1);}cout<<best;}
 else if(task==1073){int n;cin>>n;vector<ll>tops;while(n--){ll x;cin>>x;auto p=upper_bound(tops.begin(),tops.end(),x);if(p==tops.end())tops.push_back(x);else *p=x;}cout<<tops.size();}
 cout<<'\n';}
'''

def expected(task,text):
    if task==1069:return max(len(list(g)) for _,g in itertools.groupby(text.strip()))
    a=list(map(int,text.split()));n=a[0];v=a[1:]
    if task==1068:
        r=[n]
        while n!=1:n=n//2 if n%2==0 else 3*n+1;r.append(n)
        return ' '.join(map(str,r))
    if task==1083:return next(x for x in range(1,n+1) if x not in set(v))
    if task==1094:
        total=0
        for j in range(1,n):total+=max(0,v[j-1]-v[j]);v[j]=max(v[j-1],v[j])
        return total
    if task==1071:
        result=[]
        for y,x in zip(v[::2],v[1::2]):
            z=max(y,x);corner=z*z-z+1;result.append(corner+(y-x)*(1 if z%2==0 else -1))
        return '\n'.join(map(str,result))
    if task==1072:return '\n'.join(str((k*k)*(k*k-1)//2-4*(k-1)*(k-2)) for k in range(1,n+1))
    if task==1617:return pow(2,n,1000000007)
    if task==1618:
        total=0;d=5
        while d<=n:total+=n//d;d*=5
        return total
    if task==1754:return '\n'.join('YES' if (x+y)%3==0 and max(x,y)<=2*min(x,y) else 'NO' for x,y in zip(v[::2],v[1::2]))
    if task==2431:
        result=[]
        for pos in v:
            length=1;start=1
            while pos>9*start*length:pos-=9*start*length;length+=1;start*=10
            result.append(str(start+(pos-1)//length)[(pos-1)%length])
        return '\n'.join(result)
    if task==1621:return len(set(v))
    if task==1084:
        m,k=v[:2];wanted=sorted(v[2:2+n]);flats=sorted(v[2+n:]);r=0
        for w in wanted:
            j=bisect.bisect_left(flats,w-k)
            if j<len(flats) and flats[j]<=w+k:flats.pop(j);r+=1
        return r
    if task==1090:
        x=v[0];weights=sorted(v[1:]);r=0
        while weights:
            heavy=weights.pop();r+=1
            if weights and weights[0]+heavy<=x:weights.pop(0)
        return r
    if task==1091:
        m=v[0];tickets=sorted(v[1:1+n]);result=[]
        for budget in v[1+n:]:
            idx=bisect.bisect_right(tickets,budget)-1;result.append(tickets.pop(idx) if idx>=0 else -1)
        return '\n'.join(map(str,result))
    if task in {1619,1629}:
        events=list(zip(v[::2],v[1::2]))
        if task==1619:return max(sum(x<=t<y for x,y in events) for t in v)
        # independent exhaustive interval scheduling for our small supplemental tests
        best=0
        for mask in range(1<<n):
            chosen=sorted(events[k] for k in range(n) if mask>>k&1)
            if all(chosen[k-1][1]<=chosen[k][0] for k in range(1,len(chosen))):best=max(best,len(chosen))
        return best
    if task==1074:return min(sum(abs(x-t) for x in v) for t in v)
    if task==2183:
        sums={0}
        for x in v:sums|={s+x for s in list(sums)}
        return next(x for x in range(1,sum(v)+2) if x not in sums)
    if task==1141:return max(j-i for i in range(n) for j in range(i+1,n+1) if len(set(v[i:j]))==j-i)
    if task==1073:
        # minimal number of strictly decreasing subsequences = longest nondecreasing subsequence
        dp=[]
        for j,x in enumerate(v):dp.append(1+max([dp[k] for k in range(j) if v[k]<=x] or [0]))
        return max(dp)
    raise ValueError(task)

def cases(task):
    if task==1068:return [str(n)+'\n' for n in [1,2,3,7,27,1000000]]
    if task==1083:return ['2\n1\n','2\n2\n','5\n5 4 3 2\n','6\n1 2 3 4 5\n','8\n8 2 4 1 7 3 6\n']
    if task==1069:return [s+'\n' for s in ['A','AAAAAA','ACGT','AACCCCCGGGGTT','TGGTGGG','T'*1000]]
    if task==1094:return [str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a in [[1],[1,2,3],[5,4,3,2,1],[7,7,7],[1000000000,1,1,1],[3,2,5,1,7]]]
    if task==1071:return ['5\n1 1\n1 2\n2 1\n3 2\n2 3\n','4\n1000000000 1\n1 1000000000\n999999999 999999999\n1000000000 1000000000\n']
    if task in {1072,1617,1618}:return [str(n)+'\n' for n in ({1072:[1,2,3,8,20],1617:[1,2,10,100,1000000],1618:[1,4,5,25,125,1000000000]}[task])]
    if task==1754:return ['8\n0 0\n1 2\n2 1\n1 1\n0 3\n1000000000 1000000000\n3 6\n6 15\n','3\n2 2\n9 9\n999999999 999999999\n']
    if task==2431:return ['10\n1\n9\n10\n11\n189\n190\n191\n192\n1000000000000000000\n999999999999999999\n']
    arrays=[[1],[2,2,2],[1,2,3,4,5],[5,4,3,2,1],[1,3,2,1,2,4],[1000000000,1,1000000000]]
    if task in {1621,1074,2183,1141,1073}:return [str(len(a))+'\n'+' '.join(map(str,a))+'\n' for a in (arrays if task!=2183 else [[1],[2],[1,1,3],[1,2,2,7],[1,1,1,1],[2,3,5]])]
    if task==1084:return ['1 1 0\n1\n1\n','2 2 0\n1 2\n3 4\n','3 2 1\n4 5 6\n3 5\n','4 3 5\n60 45 80 60\n30 60 75\n']
    if task==1090:return ['1 10\n10\n','4 10\n5 5 5 5\n','5 9\n9 1 8 2 7\n','6 10\n6 6 6 6 6 6\n']
    if task==1091:return ['1 2\n5\n4 5\n','3 4\n5 5 5\n5 5 5 5\n','5 6\n1 2 3 4 5\n6 3 3 1 10 2\n']
    if task in {1619,1629}:return ['1\n1 2\n','3\n1 2\n3 4\n5 6\n','4\n1 8\n2 7\n3 6\n4 5\n','5\n1 3\n2 4\n3 7\n5 6\n8 9\n']
    raise ValueError(task)
