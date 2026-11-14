#include <algorithm>
#include <array>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace std;
using A=array<int,5>;
bool dfs(vector<int>& masks,int i,A& d){if(i==(int)masks.size())return all_of(d.begin(),d.end(),[](int x){return x==0;});int m=masks[i];for(int j=0;j<5;j++)if((m>>j&1)&&d[j]){--d[j];if(dfs(masks,i+1,d))return true;++d[j];}return false;}
bool match(string s,A t){if(s.size()<5)return false;int sum=0;for(int j=0;j<5;j++){t[j]-=s[j]-'a';if(t[j]<0)return false;sum+=t[j];}if(sum!=(int)s.size()-5)return false;vector<int> masks;for(int j=5;j<(int)s.size();j++)masks.push_back(s[j]=='Z'?31:(s[j]-'A')<<1);sort(masks.begin(),masks.end(),[](int a,int b){return __builtin_popcount(a)<__builtin_popcount(b);});return dfs(masks,0,t);}
int main(int argc,char**argv){if(argc<12)return 2;A a,b;for(int i=0;i<5;i++){a[i]=stoi(argv[i+1]);b[i]=stoi(argv[i+6]);}for(int k=11;k<argc;k++){ifstream f(argv[k]);string l;int hits=0;while(getline(f,l)){auto c=l.find(':'),e=l.find(' ');if(c==string::npos||e==string::npos)continue;string x=l.substr(0,c),y=l.substr(c+1,e-c-1);if((match(x,a)&&match(y,b))||(match(x,b)&&match(y,a))){cout<<k-11<<' '<<l.substr(e+1)<<' '<<l.substr(0,e)<<'\n';if(++hits>=12 && !getenv("EXPLORER_ALL"))break;}}} }
