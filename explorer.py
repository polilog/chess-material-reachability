#!/usr/bin/env python3
"""Local Chess Material Explorer. Run from the compact proof repository."""
import argparse, json, sys, subprocess, threading, webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'explorer'))
from engine import Explorer
from verify import sha

def main():
    if not __debug__:raise SystemExit("Do not use python -O: the checkers require assertions.")
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--replay',type=Path,default=ROOT/'replay');p.add_argument('--port',type=int,default=8765);p.add_argument('--no-browser',action='store_true');p.add_argument('--query',nargs=2,metavar=('WHITE','BLACK'),help='comma-separated P,N,B,R,Q counts');a=p.parse_args()
    replay=a.replay.resolve()
    if not (replay/'summary.tsv').is_file():
        if replay.exists():p.error(f'{replay} exists but is not a completed replay. Choose a new --replay path.')
        print('First run: reconstructing and verifying the certificate index. This is a one-time operation.',file=sys.stderr,flush=True)
        subprocess.run([sys.executable,str(ROOT/'verify.py'),'--work',str(replay)],cwd=ROOT,check=True,stdout=sys.stderr if a.query else None)
    if (replay/'summary.tsv').read_bytes() != (ROOT/'results/expected.tsv').read_bytes():
        p.error('Replay summary is incomplete or inconsistent. Run a fresh verification.')
    marker=replay/'VERIFIED.json'
    if marker.is_file():
        m=json.loads(marker.read_text())
        if m.get('manifest_sha256')!=sha(ROOT/'data/manifest.json') or m.get('summary_sha256')!=sha(replay/'summary.tsv'):
            p.error('Replay provenance mismatch. Choose a fresh --replay directory.')
    else:
        print('Legacy replay: no completion marker; use a fresh replay for verified provenance.',file=sys.stderr)
    explorer=Explorer(replay);lock=threading.Lock()
    if a.query:
        try:q=[tuple(map(int,s.split(','))) for s in a.query]
        except ValueError:p.error('Each query must contain five comma-separated integers in P,N,B,R,Q order.')
        if any(len(t)!=5 or any(x<0 or x>15 for x in t) for t in q):p.error('Each query must contain five counts between 0 and 15.')
        r=explorer.find(*q)
        if r['status']=='ok':print(r['pgn'])
        else:print(json.dumps(r,indent=2),file=sys.stderr);sys.exit(1)
        return
    class Handler(BaseHTTPRequestHandler):
        def send_body(self,status,body,ctype):
            self.send_response(status);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path.split('?')[0] in ('/','/index.html'):self.send_body(200,(ROOT/'explorer/index.html').read_bytes(),'text/html; charset=utf-8')
            else:self.send_body(404,b'Not found','text/plain')
        def do_POST(self):
            if self.path!='/api/find':self.send_body(404,b'Not found','text/plain');return
            try:
                n=int(self.headers.get('Content-Length','0'));assert 0<n<4096
                body=json.loads(self.rfile.read(n));a,b=body['white'],body['black']
                assert all(isinstance(s,list) and len(s)==5 and all(type(x) is int and 0<=x<=15 for x in s) for s in (a,b))
                with lock:r=explorer.find(a,b)
                self.send_body(200,json.dumps(r).encode(),'application/json')
            except (ValueError,KeyError,AssertionError) as e:self.send_body(400,json.dumps({'status':'error','reason':f'Invalid request or lookup error: {e}'}).encode(),'application/json')
            except Exception as e:self.send_body(500,json.dumps({'status':'error','reason':f'Lookup failed: {e}'}).encode(),'application/json')
    http=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);url=f'http://127.0.0.1:{a.port}/';print('Chess Material Explorer: '+url+'\nPress Ctrl+C to stop.',flush=True)
    if not a.no_browser:webbrowser.open(url)
    try:http.serve_forever()
    except KeyboardInterrupt:pass
    finally:http.server_close()
if __name__=='__main__':main()
