"""
Author: calumks <https://github.com/calumks>
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
    counts = _limit(counts)
    
    dueTomorrow = _limit([
        min(dconf.get('new').get('perDay'), _count_cards(deck, sched, 'new')), 
        sched.col.db.scalar("""
            select count() from cards where did in %s and queue in (2,3)
            and due = ?""" % sched._deckLimit(), sched.today+1)
    ])
    
    totals = _limit([
        _count_cards(deck, sched, 'new'),
        _count_cards(deck, sched, 'lern'),
        _count_cards(deck, sched, 'review'),
        _count_cards(deck, sched, 'buried'),
        _count_cards(deck, sched, 'suspended')
    ])

    # No need to show stats if we have finished collection today
    if finished:
        mssg = sched.finishedMsg()
        # pylint: disable=undefined-variable
        return '''
        <div style="white-space: pre-wrap;">%s</div>
        <table cellspacing=5>
            <tr><td>%s:</td><td align=right>
                <font title="new" color=#00a>%s</font>
                <font title="review" color=#0a0>%s</font>
            </td></tr>
            <tr><td>%s:</td><td align=right>
                <font title="new" color=#00a>%s</font>
                <font title="lern" color=#C35617>%s</font>
                <font title="review" color=#0a0>%s</font>
                <font title="buried" color=#ffa500>%s</font>
                <font title="suspended" color=#adb300>%s</font>
            </td></tr>
        </table>
        ''' % (
            mssg, _("Due tomorrow"), dueTomorrow[0], dueTomorrow[1],
            _("Total"), totals[0], totals[1], totals[2], totals[3], totals[4])

    # pylint: disable=undefined-variable
    return '''
    <table width=300 cellpadding=5>
    <tr><td align=center valign=top>
    <table cellspacing=5>
    <tr><td>%s:</td><td align=right>
        <font title="new" color=#00a>%s</font>
        <font title="lern" color=#C35617>%s</font>
        <font title="review" color=#0a0>%s</font>
    </td></tr>
    <tr><td>%s:</td><td align=right>
        <font title="new" color=#00a>%s</font>
        <font title="review" color=#0a0>%s</font>
    </td></tr>
    <tr><td>%s:</td><td align=right>
        <font title="new" color=#00a>%s</font>
        <font title="lern" color=#C35617>%s</font>
        <font title="review" color=#0a0>%s</font>
        <font title="buried" color=#ffa500>%s</font>
        <font title="suspended" color=#adb300>%s</font>
    </td></tr>
    </table>
    </td><td align=center>
    %s</td></tr></table>''' % (
        _("Due today"), counts[0], counts[1], counts[2],
        _("Due tomorrow"), dueTomorrow[0], dueTomorrow[1],
        _("Total"), totals[0], totals[1], totals[2], totals[3], totals[4],
        self.mw.button("study", _("Study Now"), id="study")) 

def _count_cards(deck, sched, queue):
    "Returns count of cards given queue"
    queues = {'review': 2, 'lern': 1, 'new': 0, 'suspended': -1, 'buried': -2}
    return  sched.col.db.scalar("""
    select count() from cards where id in (
        select id from cards where did = %s and queue = ? limit ?
    )""" % deck.get('id'), queues.get(queue), sched.reportLimit)

# If count is more than 1000, just show 1000+
# todo: replace 1000 with sched.reportLimit?
def _limit(counts):
    for i, count in enumerate(counts):
        if count >= 1000:
	        counts[i] = "1000+"
    return counts

# Overide table method
Overview._table = table
