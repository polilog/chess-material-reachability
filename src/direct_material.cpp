// Extract concrete material profiles from already verified witness streams.
// Reuses the legal move implementation; terminal-history checks are supplied
// by verify.py, which must be run before this descriptive statistics tool.
#define main verifier_original_main
#include "verify28.cpp"
#undef main
#include <unordered_set>

int main(int argc, char** argv) {
    if (argc < 3) { cerr << "Usage: direct_material OUTPUT.keys GAME...\n"; return 1; }
    unordered_set<uint64_t> seen;
    Board initial{};
    int back[] = {4,2,3,5,6,3,2,4};
    for (int i=0; i<8; ++i) {
        initial[i]=back[i]; initial[i+8]=1;
        initial[i+48]=-1; initial[i+56]=-back[i];
    }
    seen.insert(material(initial));
    for (int k=2; k<argc; ++k) {
        ifstream input(argv[k]);
        if (!input) return 2;
        string line, s; long records=0;
        while (getline(input,line)) {
            Board b=initial; int c=1,ep=-1;
            istringstream moves(line);
            while (moves >> s) {
                if (s.size()!=4 && s.size()!=5) return 3;
                for (int i : {0,2})
                    if (s[i]<'a'||s[i]>'h'||s[i+1]<'1'||s[i+1]>'8') return 3;
                int a=sq(s,0), z=sq(s,2), p=b[a], v=b[z];
                int pr=0;
                if (s.size()==5) {
                    auto pos=string("nbrq").find(s[4]);
                    if (pos==string::npos) return 3;
                    pr=int(pos)+2;
                }
                bool cap=v||(abs(p)==1&&a%8!=z%8);
                if (!move(b,a,z,c,pr,ep)) { cerr<<"Invalid move at "<<argv[k]<<":"<<records+1<<"\n"; return 4; }
                if (cap||pr) seen.insert(material(b));
                ep=abs(p)==1&&abs(a/8-z/8)==2?(a+z)/2:-1;
                c=-c;
            }
            ++records;
        }
        cerr<<argv[k]<<": "<<records<<" records, "<<seen.size()<<" cumulative profiles\n";
    }
    ofstream out(argv[1]);
    for (auto key:seen) out<<key<<'\n';
    return out ? 0 : 5;
}
