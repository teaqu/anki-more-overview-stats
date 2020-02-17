"""
Author: calumks <https://github.com/calumks>
https://ankiweb.net/shared/info/2116130837
"""

# pylint: disable=import-error
# pylint: disable=undefined-variable
# queue types: 0=new/cram, 1=lrn, 2=rev, 3=day lrn, -1=suspended, -2=buried
from anki.utils import ids2str
from aqt.overview import Overview
from aqt.qt import *
from anki import version
from anki.lang import _

def table(self):
    """Returns html table with more statistics than before."""
    sched = self.mw.col.sched
    deck = self.mw.col.decks.current()
    dconf = self.mw.col.decks.confForDid(deck.get('id'))
    but = self.mw.button

    # Get default counts
    # 0 = new, 1 = learn, 2 = review
    counts = list(sched.counts())
    finished = not sum(counts)
    counts = _limit(counts)
    
    totals = [
        #new 
        sched.col.db.scalar("""
            select count() from (select id from cards where did = %s 
            and queue = 0)""" % deck.get('id')),
        # learn
        sched.col.db.scalar("""
            select count() from (select id from cards where did = %s 
            and queue in (1,3))""" % deck.get('id')),
        # review
        sched.col.db.scalar("""
            select count() from (select id from cards where did = %s 
            and queue = 2)""" % deck.get('id')),
         # suspended
        sched.col.db.scalar("""
            select count() from (select id from cards where did = %s 
            and queue = -1)""" % deck.get('id')),
        # buried
        sched.col.db.scalar("""
            select count() from (select id from cards where did = %s 
            and queue = -2)""" % deck.get('id')),
    ]

    if (dconf.get('new')):
        dueTomorrow = _limit([
            # new
            min(dconf.get('new').get('perDay'), totals[0]),
            # review
            sched.col.db.scalar("""
                select count() from cards where did = %s and queue in (2,3)
                and due = ?""" % deck.get('id'), sched.today + 1)
        ])

    html = ''

    # Style if less than 2.1.20
    if (int(version.replace('.', '')) < 2120):
        html += '''
            <style>
                .new-count {color: #00a}
                .learn-count {color: #C35617}
                .review-count {color: #0a0}
            </style>'''

    # No need to show due if we have finished collection today
    if finished:
        mssg = sched.finishedMsg()
        html +=  '''
            <div style="white-space: pre-wrap;">%s</div>
            <table cellspacing=5>''' % mssg
    else:
        html +='''
            <table cellpadding=5>
            <tr><td align=center valign=top nowrap="nowrap">
            <table cellspacing=5>
            <tr><td nowrap="nowrap">%s:</td><td align=right>
                <span title="new" class="new-count">%s</span>
                <span title="learn" class="learn-count">%s</span>
                <span title="review" class="review-count">%s</span>
            </td></tr>''' % (_("Due today"), counts[0], counts[1], counts[2]) 
        
    if (dconf.get('new')):
        html += '''
            <tr><td nowrap="nowrap">%s:</td><td align=right>
                <span title="new" class="new-count">%s</span>
                <span title="learn" class="learn-count">%s</span>
            </td></tr>''' % (_("Due tomorrow"), dueTomorrow[0], 
            dueTomorrow[1])
    
    html += '''
        <tr>
            <td nowrap="nowrap">%s:</td>
            <td align=right nowrap="nowrap">
                <span title="new" class="new-count">%s</span>
                <span title="learn" class="learn-count">%s</span>
                <span title="review" class="review-count">%s</span>
                <span title="buried" style="color:#ffa500">%s</span>
                <span title="suspended" style="color:#adb300">%s</span>
            </td>
        </tr>
    </table>''' % (_("Total Cards"), totals[0], totals[1], totals[2], totals[4], 
    totals[3])

    if not finished:
        html += '''</td>
            <td align=center nowrap="nowrap">%s</td>
        </tr></table>''' % (but("study", _("Study Now"), id="study"))
    
    return html

# If count is more than 1000, just show 1000+
# todo: replace 1000 with sched.reportLimit?
def _limit(counts):
    for i, count in enumerate(counts):
        if count >= 1000:
	        counts[i] = "1000+"
    return counts

# Overide table method
Overview._table = table
