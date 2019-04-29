"""
Author: calumks <https://github.com/calumks>
https://ankiweb.net/shared/info/2116130837
"""

# pylint: disable=import-error
# pylint: disable=undefined-variable
# queue types: 0=new/cram, 1=lrn, 2=rev, 3=day lrn, -1=suspended, -2=buried
from anki.utils import ids2str
from aqt.overview import Overview

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
        # lern
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

    # No need to show due if we have finished collection today
    if finished:
        mssg = sched.finishedMsg()
        html +=  '''
            <div style="white-space: pre-wrap;">%s</div>
            <table cellspacing=5>''' % mssg
    else:
        html +='''
            <table width=400 cellpadding=5>
            <tr><td align=center valign=top>
            <table cellspacing=5>
            <tr><td>%s:</td><td align=right>
                <font title="new" color=#00a>%s</font>
                <font title="lern" color=#C35617>%s</font>
                <font title="review" color=#0a0>%s</font>
            </td></tr>''' % (_("Due today"), counts[0], counts[1], counts[2]) 
        
    if (dconf.get('new')):
        html += '''
            <tr><td>%s:</td><td align=right>
                <font title="new" color=#00a>%s</font>
                <font title="review" color=#0a0>%s</font>
            </td></tr>''' % (_("Due tomorrow"), dueTomorrow[0], 
            dueTomorrow[1])
    
    html += '''
        <tr><td>%s:</td><td align=right>
            <font title="new" color=#00a>%s</font>
            <font title="lern" color=#C35617>%s</font>
            <font title="review" color=#0a0>%s</font>
            <font title="buried" color=#ffa500>%s</font>
            <font title="suspended" color=#adb300>%s</font>
        </td></tr>
    </table>''' % (_("Total Cards"), totals[0], totals[1], totals[2], totals[3], 
    totals[4])

    if not finished:
        html += '</td><td align=center>%s</td></tr></table>' % (
           but("study", _("Study Now"), id="study"))
    
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
