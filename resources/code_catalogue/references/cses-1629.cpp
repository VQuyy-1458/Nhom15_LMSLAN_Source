#include <bits/stdc++.h>
using namespace std; using ll=long long;
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);const int task=1629;
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
