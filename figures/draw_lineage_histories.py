"""Counterexample: one observed resemblance relation, two candidate histories."""
from pathlib import Path
from visual_grammar import Diagram, BLUE, MUTED, PALE, GRID


def draw(output):
    d = Diagram(w=428, h=148)

    def apk(x, y, text):
        d.doc(x, y, fill=PALE)
        d.text(x, y-18, text, 10, BLUE, bold=True)

    d.title(26, 136, 'A', 'Directional derivation')
    apk(65, 102, 'APK A')
    apk(162, 102, 'APK B')
    d.arrow((77, 102), (150, 102), c=BLUE)
    d.text(113, 113, 'transforms', 9, MUTED)

    d.title(233, 136, 'B', 'Shared predecessor')
    d.doc(327, 111, fill='white')
    d.text(327, 93, 'Predecessor', 9, MUTED)
    apk(265, 75, 'APK A')
    apk(389, 75, 'APK B')
    d.arrow((315, 106), (265, 106), (265, 88), c=BLUE)
    d.arrow((339, 106), (389, 106), (389, 88), c=BLUE)

    d.line((112, 73), (112, 37), (172, 37), c=GRID, dash=True)
    d.line((327, 49), (327, 37), (256, 37), c=GRID, dash=True)
    d.rect(171, 27, 86, 20, PALE, GRID)
    d.text(214, 37, 'Same observations', 9.5, BLUE, bold=True)
    d.ax.set_ylim(20,148)
    d.fig.set_size_inches(428/72,128/72)
    d.finish(output)


if __name__ == '__main__':
    draw(Path(__file__).with_name('lineage-histories.pdf'))
