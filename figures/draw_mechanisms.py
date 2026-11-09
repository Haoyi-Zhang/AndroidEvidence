"""Rebuild the paper's mechanism schematics at their intended physical size."""
from pathlib import Path
from diagram_core import Figure, BLUE, GRAY, INK, RED

def below(f,x,y,icon,label):
    """Keep multiline labels clear of the glyph at actual print scale."""
    f.icon(icon,x,y)
    f.t(x,y+f.units(19.5)[1],label)

def component_reach(f):
    for x,icon,label in [(52,'apk','Version\ncandidate'),(155,'diff','Affected code\nretained'),
                         (266,'branch','Reachable in\nthis setting'),(370,'run','Observed\nbehavior')]:
        below(f,x,30,icon,label)
    for a,b in [(69,139),(172,250),(283,354)]:
        f.route((a,30),(b,30),dash=True,color=GRAY)
    f.line((99,84),(140,84),dash=True,color=GRAY)
    f.t(149,84,'Each step needs its own evidence',align='left',color=GRAY)

def mismatch_binding(f):
    f.node(33,24,'cert','Build record',side='right')
    f.node(33,69,'apk','Binary scan',side='right')
    f.route((111,24),(154,24),(154,43),(177,43))
    f.route((111,69),(154,69),(154,51),(177,51))
    f.node(191,47,'compare','Same APK?',side='below')
    f.route((206,47),(240,47),(240,23),(263,23))
    f.route((240,47),(240,72),(263,72),color=RED,dash=True)
    f.node(278,23,'branch','Inspect disagreement',side='right')
    f.node(278,72,'reject','Do not combine claims',side='right',color=RED)
    f.t(254,12,'yes',align='right',color=GRAY)
    f.t(254,87,'no',align='right',color=RED)

FIGURES = [('component_reach', 420, 74), ('mismatch_binding', 420, 84)]

if __name__ == '__main__':
    for name,w,h in FIGURES:
        f=Figure(dict(media=(w,h),trim=(0,0,0,0),width=w))
        globals()[name](f)
        f.finish(Path(__file__).parent/(name.replace('_','-')+'.pdf'))
