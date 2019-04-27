"""
Author: C9HDN <https://github.com/C9HDN>
https://ankiweb.net/shared/info/2116130837
"""

from anki.utils import ids2str
from aqt.overview import Overview

def table(self):
    """ Returns html table with more statistics than before. """
    shed = self.mw.col.sched

    # Get default counts
    # 0 = new, 1 = learn, 2 = review
    counts = list(shed.counts())
    finished = not sum(counts)

    # No need to show stats if we have finished collection today
    if finished:
        mssg = shed.finishedMsg()
        return '<div style="white-space: pre-wrap;">%s</div>' % mssg

    # Add more counts
    counts.append(count_cards(shed, 'new') - counts[0])
    counts.append(count_cards(shed, 'review') - counts[2])
    counts.append(sum(counts))
    counts.append(count_cards(shed, 'buried'))
    counts.append(count_cards(shed, 'suspended'))

    # If count is more than 1000, just show 1000+
    # todo: replace 1000 with sched.reportLimit?
    for i, count in enumerate(counts):
        if count >= 1000:
	        counts[i] = "1000+"

    return '''
    <table width=300 cellpadding=5>
    <tr><td align=center valign=top>
    <table cellspacing=5>
    <tr><td>%s:</td><td align=right>
        <font color=#00a>%s</font>
        <font color=#C35617>%s</font>
        <font color=#0a0>%s</font>
    </td></tr>
    <tr><td>%s:</td><td align=right>
        <font color=#00a>%s</font>
        <font color=#0a0>%s</font>
    </td></tr>
    <tr><td>%s:</td><td align=right>%s</td></tr>
    <tr><td>%s:</td><td align=right>%s</td></tr>
    <tr><td>%s:</td><td align=right>%s</td></tr>
    </table>
    </td><td align=center>
    %s</td></tr></table>''' % (
        _("Due today"), counts[0], counts[1], counts[2],
        _("Due later"), counts[3], counts[4],
        _("Total"), counts[5],
        _("Buried"), counts[6],
        _("Suspended"), counts[7],
        self.mw.button("study", _("Study Now"), id="study"))

def count_cards(sched, queue):
    "Returns count of cards given queue"
    queues = {'review': 2, 'new': 0, 'suspended': -1, 'buried': -2}
    return sched.col.db.scalar("""select count() from cards where id in (
        select id from cards where did in %s and queue = ? limit ?
    )""" % ids2str(sched.col.decks.active()), queues.get(queue), sched.reportLimit)

# Overide table method
Overview._table = table
