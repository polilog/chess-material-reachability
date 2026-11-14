#include <array>
#include <string>
#include <vector>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <fstream>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <cstdint>
using namespace std;
using Board=array<int,64>;
int sign(int a){return (a>0)-(a<0);} bool inside(int x,int y){return x>=0&&x<8&&y>=0&&y<8;}
int at(const Board& b,int x,int y){return inside(x,y)?b[y*8+x]:0;}
int king(const Board&b,int c){for(int i=0;i<64;i++)if(b[i]==6*c)return i;return -1;}
bool attack(const Board& b,int z,int c){int x=z%8,y=z/8;for(int a=0;a<64;a++){int p=b[a]*c;if(p<=0)continue;int u=a%8,v=a/8,dx=x-u,dy=y-v,X=abs(dx),Y=abs(dy);if(p==1){if(X==1&&dy==c)return true;continue;}if(p==2){if(X*Y==2)return true;continue;}if(p==6){if(max(X,Y)==1)return true;continue;}bool line=dx==0||dy==0,diag=X==Y;if(!(dx||dy)||!((p==3&&diag)||(p==4&&line)||(p==5&&(line||diag))))continue;int sx=sign(dx),sy=sign(dy);u+=sx;v+=sy;while(u!=x||v!=y){if(at(b,u,v))break;u+=sx;v+=sy;}if(u==x&&v==y)return true;}return false;}
bool move(Board& b,int a,int z,int c,int pr,int ep){if(a<0||a>=64||z<0||z>=64||a==z)return false;int p=b[a]*c,v=b[z]*c;if(p<=0||v>0||v==-6)return false;int dx=z%8-a%8,dy=z/8-a/8,X=abs(dx),Y=abs(dy),taken=-1;if(p==1){if(!dx){if(v||!(dy==c||(dy==2*c&&a/8==(c==1?1:6)&&!b[a+8*c])))return false;}else{if(X!=1||dy!=c)return false;if(!v){if(z!=ep||b[z-8*c]!=-c)return false;taken=z-8*c;}}if((z/8==0||z/8==7)!=(pr!=0)|| (pr&&(pr<2||pr>5)))return false;}else{if(pr)return false;if(p==2){if(X*Y!=2)return false;}else if(p==6){if(max(X,Y)!=1)return false;}else{bool line=dx==0||dy==0,diag=X==Y;if(!((p==3&&diag)||(p==4&&line)||(p==5&&(line||diag))))return false;int step=sign(dx)+8*sign(dy);for(int i=a+step;i!=z;i+=step)if(b[i])return false;}}Board t=b;t[a]=0;t[z]=pr?pr*c:p*c;if(taken>=0)t[taken]=0;if(attack(t,king(t,c),-c))return false;b=t;return true;}
uint64_t material(const Board& b){uint64_t w=0,v=0;for(int p:b)if(p&&abs(p)<6){if(p>0)w+=1ULL<<(4*(p-1));else v+=1ULL<<(4*(-p-1));}return min(w,v)|(max(w,v)<<20);}
string sig(const Board&b,int c){string s;for(int p:b)s+=char(p+6);s+=char(c+1);return s;}
int num(const Board&b){int n=0;for(int p:b)n+=(p!=0);return n;}
int sq(const string&s,int i){return s[i]-'a'+8*(s[i+1]-'1');}
bool validate(const string& l,set<uint64_t>& result,bool dead){Board b{};int base[]={4,2,3,5,6,3,2,4};for(int i=0;i<8;i++){b[i]=base[i];b[i+8]=1;b[i+48]=-1;b[i+56]=-base[i];}int c=1,ep=-1,quiet=0,n=32;unordered_map<string,int> reps;istringstream f(l);string s;set<uint64_t> local;while(f>>s){if(s.size()!=4&&s.size()!=5)return false;for(int i:{0,2})if(s[i]<'a'||s[i]>'h'||s[i+1]<'1'||s[i+1]>'8')return false;if(++reps[sig(b,c)]>=5||quiet>=150)return false;int a=sq(s,0),z=sq(s,2),pr=s.size()==5?string("  nbrq").find(s[4]):0;if(pr<0||pr>5)return false;int p=b[a],v=b[z];bool cap=v||(abs(p)==1&&a%8!=z%8);if(!move(b,a,z,c,pr,ep))return false;if(cap)n--;quiet=(cap||abs(p)==1)?0:quiet+1;ep=abs(p)==1&&abs(a/8-z/8)==2?(a+z)/2:-1;c=-c;if(cap||pr)local.insert(material(b));}if(dead){auto k=material(b);if(k!=0&&k!=(16ULL<<20)&&k!=(256ULL<<20))return false;result.insert(local.begin(),local.end());return true;}if(!attack(b,king(b,c),-c))return false;for(int a=0;a<64;a++)if(b[a]*c>0)for(int z=0;z<64;z++){if(abs(b[a])==1&&(z/8==0||z/8==7)){for(int pr=2;pr<=5;pr++){Board t=b;if(move(t,a,z,c,pr,ep))return false;}}else{Board t=b;if(move(t,a,z,c,0,ep))return false;}}result.insert(local.begin(),local.end());return true;}


int main(int argc,char**argv){unordered_set<uint64_t> seen;int valid=0,invalid=0;for(int i=1;i<argc;i++){ifstream f(argv[i]);if(!f)return 2;string s;int row=0;while(getline(f,s)){row++;set<uint64_t> keys;if(!validate(s,keys,i==2)){invalid++;cerr<<"invalid "<<i<<" "<<row<<endl;continue;}valid++;seen.insert(keys.begin(),keys.end());}}cout<<"valid "<<valid<<" invalid "<<invalid<<endl;for(auto k:seen){int n=2;for(int i=0;i<10;i++)n+=(k>>(4*i))&15;if(n<=7)cout<<k<<endl;}return invalid?1:0;}
