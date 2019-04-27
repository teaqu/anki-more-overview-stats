"""
Author: C9HDN <https://github.com/C9HDN>
https://ankiweb.net/shared/info/2116130837
"""

# pylint: disable=import-error
from anki.utils import ids2str
from aqt.overview import Overview

def table(self):
    """Returns html table with more statistics than before."""
    sched = self.mw.col.sched
    deck = self.mw.col.decks.current()
    dconf = self.mw.col.decks.confForDid(deck.get('id'))

    # Get default counts
    # 0 = new, 1 = learn, 2 = review
    counts = list(sched.counts())
    finished = not sum(counts)

    # No need to show stats if we have finished collection today
    if finished:
        mssg = sched.finishedMsg()
        return '<div style="white-space: pre-wrap;">%s</div>' % mssg
    
    dueTomorrow = [
        min(dconf.get('new').get('perDay'), _count_cards(deck, sched, 'new')), 
        sched.col.db.scalar("""
            select count() from cards where did in %s and queue in (2,3)
            and due = ?""" % sched._deckLimit(), sched.today+1)
    ]
    buried = _count_cards(deck, sched, 'buried')
    suspended = _count_cards(deck, sched, 'suspended')

    # If count is more than 1000, just show 1000+
    # todo: replace 1000 with sched.reportLimit?
    for i, count in enumerate(counts):
        if count >= 1000:
	        counts[i] = "1000+"

    # pylint: disable=undefined-variable
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
    </table>
    </td><td align=center>
    %s</td></tr></table>''' % (
        _("Due today"), counts[0], counts[1], counts[2],
        _("Due tomorrow"), dueTomorrow[0], dueTomorrow[1],
        _("Buried"), buried,
        _("Suspended"), suspended, 
        self.mw.button("study", _("Study Now"), id="study")) 

def _count_cards(deck, sched, queue):
    "Returns count of cards given queue"
    queues = {'review': 2, 'new': 0, 'suspended': -1, 'buried': -2}.get(queue)
    return  sched.col.db.scalar("""
    select count() from cards where id in (
        select id from cards where did = %s and queue = ? limit ?
    )""" % deck.get('id'), queues,  sched.reportLimit)

# Overide table method
Overview._table = table
