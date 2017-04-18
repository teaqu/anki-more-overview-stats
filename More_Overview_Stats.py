# Author: C9HDN

# Get Overview class
from aqt.overview import Overview

# Replace _table method
def table(self):
    # Get card data from the database
    totalNew = self.mw.col.db.first("""
    select
    sum(case when queue=0 then 1 else 0 end) -- new
    from cards where did in %s""" % self.mw.col.sched._deckLimit())
    
    total = self.mw.col.db.first("""
    select count(id) from cards
    where did in %s """ % self.mw.col.sched._deckLimit())

    totalReview = self.mw.col.db.scalar("""
    select count() from cards where did in %s and queue > 0
    and due < ?""" % self.mw.col.sched._deckLimit(), self.mw.col.sched.today+1)

    suspended = self.mw.col.db.scalar("""
    select count() from cards where did in %s and queue < 0
    """ % self.mw.col.sched._deckLimit())

    unseen = self.mw.col.db.scalar("""
    select count() from cards where did in %s and queue = 0
    """ % self.mw.col.sched._deckLimit())

    # Get counts from database
    counts = list(self.mw.col.sched.counts())
    finished = not sum(counts)
    
    # If count is more than 1000, just show 1000+
    for n in range(len(counts)):
        if counts[n] == 1000:
            counts[n] = "1000+"
    but = self.mw.button

    # No need to show stats if we have finished collection today
    if finished:
        mssg = self.mw.col.sched.finishedMsg()
        return '<div style="white-space: pre-wrap;">%s</div>' % mssg
    else:
        # Setup counts
        new = counts[0], '#00a'
        learn = counts[1], '#a00'
        review = counts[2], '#0a0'
        
        # Change order depending on how new cards are added
        newCardSpread = self.mw.col.conf['newSpread']
        if newCardSpread == 1:
            counts = learn[1], learn[0], review[1], review[0], new[1], new[0]
        else:
            counts = new[1], new[0], learn[1], learn[0], review[1], review[0]

        # Setup variables to insert into the table
        variables = (_("Due today"),) + counts + (
            _("Total reviews"), totalReview,
            _("Total new cards"), totalNew[0],
            _("Total cards"), total[0],
            _("Suspended cards"), suspended,
            _("Unseen cards"), unseen,
            but("study", _("Study Now"), id="study")
        )
        
        # Show table
        return '''
        <table width=300 cellpadding=5>
        <tr><td align=left valign=top>
        <table cellspacing=5>
            <tr>
                <td>%s:</td>
                <td><b>
                    <font color=%s>%s</font>
                    <font color=%s>%s</font>
                    <font color=%s>%s</font>
                </b></td>
            </tr>
            <tr><td>%s:</td><td align=right>%s</td></tr>
            <tr><td>%s:</td><td align=right>%s</td>
            <tr><td>%s:</td><td align=right>%s</td>
            <tr><td>%s:</td><td align=right>%s</td>
            <tr><td>%s:</td><td align=right>%s</font></td></tr>
        </table>
        </td><td align=center>
        %s</td></tr></table>
        ''' % variables
Overview._table = table
