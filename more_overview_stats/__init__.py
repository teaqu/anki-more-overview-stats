import os

from aqt.overview import Overview
from aqt.webview import AnkiWebView
from aqt.qt import *
from aqt import gui_hooks, mw
from anki.lang import _
from anki.utils import ids2str


def table(self):
    """Returns html table with more statistics than before."""

    # queue types: 0=new/cram, 1=lrn, 2=rev, 3=day lrn, -1=suspended, -2=buried
    sched = mw.col.sched
    deck = mw.col.decks.current()
    dconf = mw.col.decks.config_dict_for_deck_id(deck.get('id'))
    but = mw.button
    ids = ids2str(mw.col.decks.deck_and_child_ids(deck.get('id')))

    # Total Cards
    totals = [
        # new
        sched.col.db.scalar("""
            select count() from (select id from cards where did in %s 
            and queue = 0)""" % ids),
        # learn
        sched.col.db.scalar("""
            select count() from (select id from cards where did in %s 
            and queue in (1,3))""" % ids),
        # review
        sched.col.db.scalar("""
            select count() from (select id from cards where did in %s 
            and queue = 2)""" % ids),
        # suspended
        sched.col.db.scalar("""
            select count() from (select id from cards where did in %s 
            and queue = -1)""" % ids),
        # buried
        sched.col.db.scalar("""
            select count() from (select id from cards where did in %s 
            and queue in (-2,-3))""" % ids),
    ]

    # Due today
    counts = list(sched.counts())
    finished = not sum(counts)

    # Due tomorrow
    # (not necessary in some instances such as a custom study session)
    if dconf.get('new'):
        c = sched.col.decks.config_dict_for_deck_id(deck.get('id'))

        due_tomorrow = [
            # new
            min(dconf.get('new').get('perDay'), totals[0] - counts[0]),
            # review
            sched.col.db.scalar("""
                select count() from cards where id in (select id from cards where did in %s and queue = 2
                and due = ? limit %d)""" % (ids, c["rev"]["perDay"]), sched.today + 1)
        ]

    # Start table, due today
    html = '''
        <table cellpadding=5 id=overview>
        <tr><td align=center valign=top nowrap="nowrap">
        <table cellspacing=5>
        <tr><td nowrap="nowrap">%s:</td><td align=right>
            <span title="new" class="new-count">%s</span>
            <span title="learn" class="learn-count">%s</span>
            <span title="review" class="review-count">%s</span>
        </td></tr>''' % ("Due today", counts[0], counts[1], counts[2])

    # due tomorrow
    if dconf.get('new'):
        html += '''
            <tr><td nowrap="nowrap">%s:</td><td align=right>
                <span title="new" class="new-count">%s</span>
                <span title="review" class="review-count">%s</span>
            </td></tr>''' % ("Due tomorrow", due_tomorrow[0], due_tomorrow[1])

    # Total cards
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
    </table>''' % ("Total Cards", totals[0], totals[1], totals[2], totals[4],
                   totals[3])

    # Show study now button
    if not finished:
        html += '''</td>
            <td align=center nowrap="nowrap">%s</td>
        </tr></table>''' % (but("study", _("Study Now"), id="study", extra=" autofocus"))

    return html

# inject overview into congrats webview
def webview_will_set_content(web_content, context):
    if type(context).__name__ == "OverviewBottomBar" and context.overview.mw.col.sched._is_finished():
        styles = """
            <style>
                #overview {margin: 0 auto;display: table}
                .new-count {color: #00a}
                .learn-count {color: #C35617}
                .review-count {color: #0a0}
                table {}
            </style>
        """
        web_content.body = styles + table(Overview) + web_content.body

# Add addon to Anki
Overview._table = table
gui_hooks.webview_will_set_content.append(webview_will_set_content)