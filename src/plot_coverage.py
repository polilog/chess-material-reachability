#!/usr/bin/env python3
"""Regenerate publication SVG figures (optional dependency: matplotlib)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/coverage_breakdown.tsv').open() as f:
    rows=list(csv.DictReader(f,delimiter='\t'))
keys=['concrete','promotion_variants','templates','storage']
labels=['Concrete games','Promotion variants','Parameterized templates','Storage/deletion']
colors=['#25807B','#729BC6','#7753A8','#D79232']
values=[int(rows[-1][k]) for k in keys]; total=sum(values)
out=ROOT/'docs/figures';out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','figure.dpi':140})
fig,ax=plt.subplots(figsize=(9,3.5));bars=ax.barh(labels,values,color=colors,height=.58);ax.invert_yaxis();ax.set_xlim(0,max(values)*1.30);ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x/1e6:g}M'));ax.set_xlabel('Additional distinct material classes');ax.set_title('Coverage by proof method',loc='left',fontweight='bold',pad=12);ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True)
for bar,v in zip(bars,values):ax.text(v+max(values)*.025,bar.get_y()+bar.get_height()/2,f'{v:,}  ({v/total:.2%})',va='center',fontsize=10)
fig.tight_layout();fig.savefig(out/'coverage-by-method.svg',bbox_inches='tight');plt.close(fig)
n=[int(r['pieces']) for r in rows[:-1]];fig,ax=plt.subplots(figsize=(10,4.6));bottom=[0]*len(n)
for k,label,color in zip(keys,labels,colors):
    v=[int(r[k]) for r in rows[:-1]];ax.bar(n,v,bottom=bottom,label=label,color=color,width=.83);bottom=[a+b for a,b in zip(bottom,v)]
ax.set_title('Reachable material classes by total piece count',loc='left',fontweight='bold');ax.set_xlabel('Total pieces, including both kings');ax.set_ylabel('Distinct material classes');ax.set_xticks(list(range(2,33,2)));ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x/1e6:g}M'));ax.legend(ncol=2,loc='upper left',frameon=False);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);fig.tight_layout();fig.savefig(out/'coverage-by-size.svg',bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.3));names=['Main game records','Supplementary games','Parameterized templates','Storage/deletion'];counts=[309421,1113,66473,420];bars=ax.barh(names,counts,color=['#25807B','#5B9A95','#7753A8','#D79232'],height=.55);ax.invert_yaxis();ax.set_xscale('log');ax.set_xlim(100,1e6);ax.set_title('Stored certificate records (log scale)',loc='left',fontweight='bold');ax.set_xlabel('Records, not distinct material classes');ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
for bar,v in zip(bars,counts):ax.text(v*1.09,bar.get_y()+bar.get_height()/2,f'{v:,}',va='center')
fig.tight_layout();fig.savefig(out/'certificate-counts.svg',bbox_inches='tight');plt.close(fig)
