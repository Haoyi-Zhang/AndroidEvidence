"""Claim taxonomy, worked evidence graphs, and coded survey coverage."""
from matplotlib.patches import Rectangle
from visual_grammar import *


def taxonomy(out):
    d=Diagram(h=184)
    d.title(10,172,'','Android lineage claims')
    d.line((11,151),(35,151),(35,35),c=MUTED)
    entries=[
      (136,'Artifact comparison',BLUE,('L0 Identity','L1 Composition','L2 Resemblance')),
      (87,'Production history',TEAL,('L3 Derivation','L4 Process provenance')),
      (38,'Policy and behavior',PURPLE,('L5 Authorization','L6 Behavioral assurance')),
    ]
    for y,title,c,leaves in entries:
        d.line((35,y),(64,y),c=c,lw=1.25)
        d.dot(66,y,3,c,'white')
        d.text(76,y,title,9.5,c,'left',True)
        d.line((175,y),(217,y),c=c)
        lo=y-11*(len(leaves)-1);hi=y+11*(len(leaves)-1)
        d.line((217,lo),(217,hi),c=c)
        for i,s in enumerate(leaves):
            yy=hi-i*22
            d.line((217,yy),(241,yy),c=c)
            d.dot(244,yy,2.5,c)
            d.text(255,yy,s,9.3,INK,'left')
    d.text(255,7,'Branches group topics, not implications.',8.6,MUTED,'left')
    d.finish(out)


def worked(out):
    d=Diagram(h=160)
    d.rect(12,10,176,88,PALE)
    d.rect(240,10,176,88,GREEN)
    d.doc(95,128,BLUE)
    d.doc(333,128,TEAL,GREEN)
    d.text(95,147,'Package A',10,BLUE,bold=True)
    d.text(333,147,'Package B',10,TEAL,bold=True)
    d.line((105,129),(322,129),c=MUTED,dash=True)
    for x in (206,214,222):
        d.rect(x-2.5,126.5,5,5,'white',MUTED,.65)
    d.text(214,141,'Shared library · similar features',9,INK)
    d.text(214,116,'Direction not established',8.9,RED,bold=True)
    d.arrow((95,117),(95,100),c=BLUE)
    d.arrow((333,117),(333,100),c=TEAL)
    for x,c,items in [(95,BLUE,[(85,'Attested build','L4'),(43,'Delegated release','L5')]),
                      (333,TEAL,[(85,'Observed endpoint','L6')])]:
        for y,label,claim in items:
            d.dot(x,y,3,c)
            d.text(x-10,y,label,8.9,INK,'right')
            d.arrow((x+4,y),(x+20,y),c=c)
            d.token(x+31,y,claim,c)
    d.line((95,80),(95,48),c=BLUE)
    d.text(126,22,'Scoped to A',9.2,BLUE,bold=True)
    d.text(364,62,'Scoped to B',9.2,TEAL,bold=True)
    d.finish(out)


def lifecycle(out):
    d=Diagram(h=158)
    xs=[45,111,178,245,312,379]
    steps=['Source','Resolve','Build','Approve','Distribute','Execute']
    evidence=['Repository\nhistory','Resolver log\nand SBOM','Attestation\nand rebuild',
              'Delegation\nand signature','Transparency\nand freshness','Static or\ndynamic check']
    for i,(x,step,ev) in enumerate(zip(xs,steps,evidence),1):
        c=BLUE if i<4 else TEAL
        d.token(x,103,str(i),c,PALE if i<4 else GREEN)
        d.text(x,127,step,9.5,c,bold=True)
        d.line((x,93),(x,62),c=c,dash=True)
        d.doc(x,49,c,PALE if i<4 else GREEN)
        d.text(x,24,ev,8.8,INK)
    for a,b in zip(xs,xs[1:]):d.arrow((a+10,103),(b-10,103),c=MUTED)
    d.text(8,148,'Release path',9.0,MUTED,'left',True)
    d.finish(out)


def assurance(out):
    d=Diagram(h=162)
    d.title(10,150,'A','Authorized production')
    d.title(10,67,'B','Behavioral property')
    d.line((11,80),(194,80),c=GRID)
    for x,y,lab,c in [(47,114,'Materials',BLUE),(139,114,'Build and role',BLUE),
                      (47,32,'Property Q',TEAL),(139,32,'Analysis model',TEAL)]:
        d.doc(x,y,c,PALE if c==BLUE else GREEN)
        d.text(x,y-20,lab,8.8,c,bold=True)
    d.arrow((58,114),(126,114),c=BLUE)
    d.arrow((58,32),(126,32),c=TEAL)
    d.arrow((150,114),(209,114),(209,86),(239,86),c=BLUE)
    d.arrow((150,32),(209,32),(209,73),(239,73),c=TEAL)
    d.doc(251,80,PURPLE,PALE)
    d.text(251,105,'Same APK',9.5,PURPLE,bold=True)
    d.arrow((264,80),(304,80),c=PURPLE)
    d.check(315,80)
    d.text(325,80,'Joint claim',9.5,TEAL,'left',True)
    d.text(279,129,'Component comparison',8.8,MUTED,'left')
    d.line((320,120),(320,115),(278,115),(278,96),(260,91),c=MUTED,dash=True)
    d.text(317,106,'cross-check only',8.4,MUTED,'left')
    d.finish(out)


def coverage(counts,fields,out):
    d=Diagram(h=169)
    keys=[('1','Direct',BLUE,BLUE,None),('P','Partial','#b1c4ce',TEAL,None),
          ('0','Scoped absence','#e9edf0','#86939d',None),('?','Unresolved','white',OCHRE,'///')]
    for (k,label,c,e,h),x in zip(keys,[116,183,251,347]):
        d.rect(x,151,8,8,c,e,.55,hatch=h)
        d.text(x+12,155,label,9.5,INK,'left')
    x0=118;step=11.7
    for i,(row,(_,label)) in enumerate(zip(counts,fields)):
        y=134-i*17
        d.text(x0-9,y+4,label,9.5,INK,'right')
        j=0
        for k,_,c,e,h in keys:
            count=row[k]
            if count:
                d.rect(x0+j*step,y,step*count-.6,9,c,e,.55,hatch=h)
                if k!='?':
                    d.text(x0+(j+count/2)*step,y+4.5,str(count),9.45,'#ffffff' if k=='1' else INK)
                j+=count
        assert j==21
        d.text(377,y+4,f"{row['?']} unresolved",9.5,INK,'left')
    d.line((x0,21),(x0+21*step,21),c=MUTED)
    for i in (0,7,14,21):
        d.line((x0+i*step,18),(x0+i*step,21),c=MUTED,lw=.6)
        d.text(x0+i*step,11,str(i),9.5)
    d.finish(out)
