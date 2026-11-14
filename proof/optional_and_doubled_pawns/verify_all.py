from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for d in ('promotion_deletion','optional_master','doubled_pair'):
    print('\n===',d,'===',flush=True)
    subprocess.run([sys.executable,str(root/d/'verify.py')],cwd=root/d,check=True)
print('\n=== Counting and reduction ===',flush=True)
subprocess.run([sys.executable,str(root/'count_and_reduction.py')],check=True)
