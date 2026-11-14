#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;using U=uint64_t;
struct S{U k;int n,p,d;};
vector<S> sides; unordered_map<U,int> idx; unordered_map<string,vector<U>> memo;
const vector<U>& expand(string s){auto it=memo.find(s);if(it!=memo.end())return it->second;U x=0;for(int i=0;i<5;i++)x|=U(s[i]-'a')<<(4*i);vector<U> r{x};for(int i=5;i<(int)s.size();i++){vector<U> next;int m=s[i]=='Z'?15:s[i]-'A';for(U p:r){if(s[i]=='Z')next.push_back(p+1);for(int j=0;j<4;j++)if(m&(1<<j))next.push_back(p+(1ULL<<(4*(j+1))));}sort(next.begin(),next.end());next.erase(unique(next.begin(),next.end()),next.end());r=move(next);}return memo.emplace(s,move(r)).first->second;}
int main(int argc,char**argv){int base[4]={2,2,2,1};for(int p=0;p<=8;p++)for(int n=0;n<=10;n++)for(int b=0;b<=10;b++)for(int r=0;r<=10;r++)for(int q=0;q<=9;q++){int s[]={n,b,r,q};int k=p+n+b+r+q;if(k>15)continue;int pro=0,l=0;for(int i=0;i<4;i++){pro+=max(0,s[i]-base[i]);l+=max(0,base[i]-s[i]);}int d=15-k-l;if(d<0||p+pro+d!=8)continue;U key=p|(n<<4)|(b<<8)|(r<<12)|(q<<16);idx[key]=sides.size();sides.push_back({key,k+1,pro,d});}int L=sides.size();cerr<<"Sides "<<L<<endl;vector<unsigned char> state(size_t(L)*L);long upper[33]={},count[33]={},extra=0;for(int i=0;i<L;i++)for(int j=i;j<L;j++){auto a=sides[i],b=sides[j];int n=a.n+b.n,C=32-n;if(a.p<=C+b.d&&b.p<=C+a.d){state[size_t(i)*L+j]=1;upper[n]++;}}
 auto add=[&](U a,U b){auto ia=idx.find(a),ib=idx.find(b);if(ia==idx.end()||ib==idx.end()){extra++;return;}int i=ia->second,j=ib->second;if(i>j)swap(i,j);auto &v=state[size_t(i)*L+j];if(v==1){v=2;count[sides[i].n+sides[j].n]++;}else if(v==0)extra++;};

 long families=0;for(int k=1;k<argc;k++){ifstream f(argv[k]);if(!f){cerr<<"Missing "<<argv[k]<<endl;return 1;}string s;long row,ply;if(string(argv[k]).find(".keys")!=string::npos){U z;while(f>>z)add(z&((1ULL<<20)-1),z>>20);}else while(f>>s>>row>>ply){families++;auto x=s.find(':');const auto &a=expand(s.substr(0,x));const auto &b=expand(s.substr(x+1));for(auto j:a)for(auto z:b)add(j,z);}cerr<<argv[k]<<" families "<<families<<" extras "<<extra<<endl;}
 // Initial position is a certificate with zero moves.
 add(8|(2<<4)|(2<<8)|(2<<12)|(1<<16),8|(2<<4)|(2<<8)|(2<<12)|(1<<16));
 cout<<"N\tupper\tcovered\tmissing\n";long Utotal=0,Ctotal=0;for(int n=2;n<=32;n++){cout<<n<<'\t'<<upper[n]<<'\t'<<count[n]<<'\t'<<upper[n]-count[n]<<'\n';Utotal+=upper[n];Ctotal+=count[n];}cout<<"Total\t"<<Utotal<<'\t'<<Ctotal<<'\t'<<Utotal-Ctotal<<'\n'; if(const char* path=getenv("OUT_STATE")){ofstream f(path,ios::binary);f.write((char*)state.data(),state.size());}cerr<<"Extra "<<extra<<endl;return extra?2:0;}
