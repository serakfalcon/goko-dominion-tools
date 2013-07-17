import hashlib
import sys
import os
import re
import time
import socket
import datetime
import copy
import pprint

import postgresql

from . import domgame
from . import constants


# Database connection object.
# TODO: Initialized on first use instead of on load
if socket.gethostname() == 'iron':
    _con = postgresql.open(user='ai', host='localhost', database='goko')
else:
    _con = postgresql.open(
        user='forum',
        host='gokologs.drunkensailor.org',
        database='goko',
        password='fds')


def prepare(conn, sql, d):
    """ Convenience method for creating parameterized statements for use with
        py-postgresql. Allows values to be referenced by name rather than by
        index.
    """
    params = []
    m = re.findall('{(.*?)}', sql)
    for k in set(m):
        params.append(d[k] if k in d else None)
        sql = re.sub('{%s}' % k, "$%d" % len(params), sql)
    return (conn.prepare(sql), params)


def search_game_results(search):
    return fetch_game_results(search_log_filenames(search))


def search_log_filenames(p):
    """ Fetch log filenames for matching games.
        - <p> is a dict of search parameters. Missing/None values ignored.
        Games are ordered from newest to oldest. If not None, <offset> skips
        results and <limit> restricts how many are returned."""

    # Don't modify the original <search> argument
    p = copy.deepcopy(p)

    # Cards in the supply list --> s1, s2, etc
    for i in range(0, 11):
        p['s%d' % i] = (p['supply'][i] if len(p['supply']) > i else None)

    # Cards in the not-in-supply list --> ns1, ns2, netc
    for i in range(0, 11):
        p['ns%d' % i] = (p['nonsupply'][i] if len(p['nonsupply']) > i 
                                           else None)

    # Solo games require a different query 
    if p['pcount'] == 1:
        sql = log_search_sql_solo(p)
    else:
        sql = log_search_sql(p)

    (ps, params) = prepare(_con, sql, p)
    out = [r[0] for r in ps(*params)]
    return out


def log_search_sql_solo(p):
    # Parameterized search statement.
    return """SELECT DISTINCT logfile
               FROM game g
               JOIN presult p1 USING(logfile)
         WHERE ({p1name}::varchar IS NULL
                OR {casesensitive} AND {p1name} = p1.pname
                OR NOT {casesensitive} AND lower({p1name}) = p1.pname_lower)
           AND ({bot}::boolean       IS NULL OR {bot} = g.bot)
           AND ({guest}::boolean     IS NULL OR {guest} = g.guest)
           AND ({shelters}::boolean  IS NULL OR {shelters} = g.shelters)
           AND ({colony}::boolean    IS NULL OR {colony} = g.colony)
           AND ({pcount}::smallint   IS NULL OR {pcount} = g.pcount)
           AND ({s0}::varchar        IS NULL OR g.supply ~* {s0})
           AND ({s1}::varchar        IS NULL OR g.supply ~* {s1})
           AND ({s2}::varchar        IS NULL OR g.supply ~* {s2})
           AND ({s3}::varchar        IS NULL OR g.supply ~* {s3})
           AND ({s4}::varchar        IS NULL OR g.supply ~* {s4})
           AND ({s5}::varchar        IS NULL OR g.supply ~* {s5})
           AND ({s6}::varchar        IS NULL OR g.supply ~* {s6})
           AND ({s7}::varchar        IS NULL OR g.supply ~* {s7})
           AND ({s8}::varchar        IS NULL OR g.supply ~* {s8})
           AND ({s9}::varchar        IS NULL OR g.supply ~* {s9})
           AND ({s10}::varchar       IS NULL OR g.supply ~* {s10})
           AND ({ns0}::varchar       IS NULL OR g.supply ~* {ns0})
           AND ({ns1}::varchar       IS NULL OR g.supply ~* {ns1})
           AND ({ns2}::varchar       IS NULL OR g.supply ~* {ns2})
           AND ({ns3}::varchar       IS NULL OR g.supply ~* {ns3})
           AND ({ns4}::varchar       IS NULL OR g.supply ~* {ns4})
           AND ({ns5}::varchar       IS NULL OR g.supply ~* {ns5})
           AND ({ns6}::varchar       IS NULL OR g.supply ~* {ns6})
           AND ({ns7}::varchar       IS NULL OR g.supply ~* {ns7})
           AND ({ns8}::varchar       IS NULL OR g.supply ~* {ns8})
           AND ({ns9}::varchar       IS NULL OR g.supply ~* {ns9})
           AND ({ns10}::varchar      IS NULL OR g.supply ~* {ns10})
           AND ({maxturns}::smallint IS NULL OR {maxturns} >= p1.turns)
           AND ({minturns}::smallint IS NULL OR {minturns} <= p1.turns)
           AND ({quit}::boolean      IS NULL OR {quit} = p1.quit)
           AND ({resign}::boolean    IS NULL OR {resign} = p1.resign)
           AND ({startdate}::date    IS NULL OR g.time > {startdate})
           AND ({enddate}::date      IS NULL OR g.time < {enddate})
           AND ({rating}::varchar    IS NULL OR {rating} = g.rating
                OR {rating} = 'pro+' AND g.rating IN ('pro', 'unknown'))
         LIMIT {limit}
        OFFSET {offset}"""


def log_search_sql(p):
    # Parameterized search statement.
    return """SELECT DISTINCT logfile
               FROM game g
               JOIN presult p1 USING(logfile)
               JOIN presult p2 USING(logfile)
         WHERE (p1.pname != p2.pname)
           AND ({p1name}::varchar IS NULL
                OR {casesensitive} AND {p1name} = p1.pname
                OR NOT {casesensitive} AND lower({p1name}) = p1.pname_lower)
           AND ({p2name}::varchar IS NULL
                OR {casesensitive} AND {p2name} = p2.pname
                OR NOT {casesensitive} AND lower({p2name}) = p2.pname_lower)
           AND ({p1score}::float    IS NULL OR {p1score} = (p2.rank - p1.rank))
           AND ({bot}::boolean      IS NULL OR {bot} = g.bot)
           AND ({guest}::boolean    IS NULL OR {guest} = g.guest)
           AND ({shelters}::boolean IS NULL OR {shelters} = g.shelters)
           AND ({colony}::boolean   IS NULL OR {colony} = g.colony)
           AND ({pcount}::smallint  IS NULL OR {pcount} = g.pcount)
           AND ({s0}::varchar       IS NULL OR g.supply ~* {s0})
           AND ({s1}::varchar       IS NULL OR g.supply ~* {s1})
           AND ({s2}::varchar       IS NULL OR g.supply ~* {s2})
           AND ({s3}::varchar       IS NULL OR g.supply ~* {s3})
           AND ({s4}::varchar       IS NULL OR g.supply ~* {s4})
           AND ({s5}::varchar       IS NULL OR g.supply ~* {s5})
           AND ({s6}::varchar       IS NULL OR g.supply ~* {s6})
           AND ({s7}::varchar       IS NULL OR g.supply ~* {s7})
           AND ({s8}::varchar       IS NULL OR g.supply ~* {s8})
           AND ({s9}::varchar       IS NULL OR g.supply ~* {s9})
           AND ({s10}::varchar      IS NULL OR g.supply ~* {s10})
           AND ({ns0}::varchar       IS NULL OR g.supply !~* {ns0})
           AND ({ns1}::varchar       IS NULL OR g.supply !~* {ns1})
           AND ({ns2}::varchar       IS NULL OR g.supply !~* {ns2})
           AND ({ns3}::varchar       IS NULL OR g.supply !~* {ns3})
           AND ({ns4}::varchar       IS NULL OR g.supply !~* {ns4})
           AND ({ns5}::varchar       IS NULL OR g.supply !~* {ns5})
           AND ({ns6}::varchar       IS NULL OR g.supply !~* {ns6})
           AND ({ns7}::varchar       IS NULL OR g.supply !~* {ns7})
           AND ({ns8}::varchar       IS NULL OR g.supply !~* {ns8})
           AND ({ns9}::varchar       IS NULL OR g.supply !~* {ns9})
           AND ({ns10}::varchar      IS NULL OR g.supply !~* {ns10})
           AND ({maxturns}::smallint IS NULL
                OR {maxturns} >= GREATEST(p1.turns, p2.turns))
           AND ({minturns}::smallint IS NULL
                OR {minturns} <= GREATEST(p1.turns, p2.turns))
           AND ({quit}::boolean     IS NULL OR {quit} = (p1.quit OR p2.quit))
           AND ({resign}::boolean   IS NULL OR {resign} = (p1.resign OR p2.resign))
           AND ({rating}::varchar   IS NULL OR {rating} = g.rating
                OR {rating} = 'pro+' AND g.rating IN ('pro', 'unknown'))
           AND ({startdate}::date IS NULL OR g.time > {startdate})
           AND ({enddate}::date IS NULL OR g.time < {enddate})
         LIMIT {limit}
        OFFSET {offset}"""


def fetch_game_results(log_filenames):
    """ Fetch supply, VPs per player, etc. Return a GameResult object. """

    ps = _con.prepare("""SELECT * FROM game g WHERE logfile = ANY($1)""")
    games = {}
    for r in ps(log_filenames):
        g = domgame.GameResult.blank()
        for k in ['time', 'logfile', 'colony', 'shelters']:
            setattr(g, k, r[k])
        g.supply = []
        for s in r['supply'].split(','):
            if not(s.lower() in constants.CORE_CARDS):
                g.supply.append(s)
        g.supply = sorted(g.supply)
        games[g.logfile] = g

    # Fetch player-specific game results
    ps = _con.prepare("""SELECT * FROM presult p WHERE logfile = ANY($1)""")
    for r in ps(log_filenames):
        p = domgame.PlayerResult(r['pname'])
        for k in ['vps', 'turns', 'rank', 'quit', 'resign']:
            setattr(p, k, r[k])
        games[r['logfile']].presults[p.pname] = p

    return games.values()


def fetch_card_image_url(card):
    """ Retrieve third-party URL for a Dominion card image """
    return _con.prepare("""SELECT url FROM card_url WHERE
                        card=$1""")(card)[0][0]


def search_scores(search):
    logfiles = search_log_filenames(search)
    ps = _con.prepare(
        """SELECT logfile, p1.pname as p1name, p2.pname as p2name,
                  p2.rank - p1.rank as p1score
             FROM presult p1
             JOIN presult p2 USING(logfile)
            WHERE p1.pname < p2.pname
              AND logfile = ANY($1)""")
    return ps(logfiles)


def get_last_rated_game():
    return _con.query.first("""SELECT time, logfile FROM ts_rating
                                ORDER BY time desc LIMIT 1""")


def search_all_2p_scores(limit, time, logfile):
    ps = _con.prepare(
        """SELECT g.time, g.logfile, p1.pname as p1name, p2.pname as p2name,
                  p2.rank - p1.rank as p1score
             FROM game g
             JOIN presult p1 USING(logfile)
             JOIN presult p2 USING(logfile)
            WHERE p1.pname < p2.pname
              AND g.rating = 'pro'
              AND g.pcount = 2
              AND NOT g.guest
              AND ($2::timestamp IS NULL OR g.time>=$2)
              AND ($3::varchar IS NULL OR g.logfile!=$3)
            ORDER BY g.time ASC
            LIMIT $1""")
    return ps(limit, time, logfile)


def fetch_all_ratings():
    mu_sig = {}
    # TODO: Fix the Boodaloo problem more elegantly
    for (p,m,s) in _con.query("""SELECT pname, mu, sigma 
                                   FROM ts_rating
                                  WHERE pname != 'Boodaloo'"""):
        mu_sig[p] = {'mu': m, 'sigma': s}
    return mu_sig
        

def get_rating(pname):
    ps =  _con.prepare("""SELECT mu, sigma
                            FROM ts_rating
                           WHERE pname=$1
                           ORDER BY time DESC""")
    ms = ps.first(pname)
    if ms:
        return (float(ms[0]), float(ms[1]))
    else:
        return ms


def summarize_scores(pname, search):
    result_counts = {-1: 0, 0: 0, 1: 0}
    for r in search_scores(search):
        if pname == r['p1name']:
            result_counts[r['p1score']] += 1
        if pname == r['p2name']:
            result_counts[r['p1score']] += 1
    return result_counts


def get_bot_names():
    """Goko's lobby bots"""
    ps = _con.prepare('SELECT pname from bot')
    return [r[0] for r in ps()]


def is_bot(pname):
    """Check if given player is a lobby bot. Note that this"""
    for bot in get_bot_names():
        # Match names like 'Conqueror Bot III'
        if pname and pname.startswith(bot):
            return True
    return False


def get_advbot_names():
    """Oppponents in the Goko adventures quest"""
    return _con.prepare('SELECT pname from advbot')()


def fetch_supply_cards():
    """ All the cards in the game, lowercased """
    ps = _con.prepare("SELECT card FROM card_url")
    return [r[0].lower() for r in ps()]


def insert_card_url(card, url):
    """ Store third-party URL for a Dominion card image. """
    _con.prepare("""INSERT INTO card_url VALUES ($1, $2)""")(card, url)


def inserts(games):
    """ Insert GameResult objects into the database. """

    # Aggregate data for each game into arrays. Don't actually insert into the
    # database yet
    rows = {'game': [], 'pres': [], 'gain': [], 'ret': []}
    for g in games:

        # Copy values from GameResult object.
        gd = {}
        for k in ['time', 'logfile', 'supply', 'colony', 'shelters', 'pcount',
                  'plist', 'bot', 'guest', 'rating', 'adventure']:
            gd[k] = getattr(g, k, None)
        gd['supply'] = ', '.join(g.supply)
        gd['plist'] = ', '.join(list(g.presults.keys()))
        gd['pcount'] = len(g.presults)
        rows['game'].append(gd.getKeys() + gd.values())

        # Copy values from PlayerResult object.
        for pname in g.presults:
            pd = {}
            for k in ['pname', 'vps', 'turns', 'rank', 'quit', 'order',
                      'resign', 'logfile', 'pcount', 'pname_lower']:
                pd[k] = getattr(ret, k, None)
            p = g.presults[pname]
            pd = dict(pres_keys, [getattr(p, k, None) for k in pres_keys])
            pd['pcount'] = len(g.presults)
            pd['pname_lower'] = pname.lower()
            pd['logfile'] = g.logfile
            rows['pres'].append(pd.getKeys() + pd.values())

        # Copy values from GainRet object.
        for gain in g.gains:
            gaind = {}
            for k in ['logfile', 'cname', 'cpile', 'pname', 'turn']:
                gaind[k] = getattr(ret, k, None)
            gaind['logfile'] = g.logfile
            rows['gain'].append(gaind.getKeys() + gaind.values())

        # Copy values from GainRet object.
        for ret in g.rets:
            retd = {}
            for k in ['logfile', 'cname', 'cpile', 'pname', 'turn']:
                retd[k] = getattr(ret, k, None)
            retd['logfile'] = g.logfile
            rows['ret'].append(retd.getKeys() + retd.values())

    # Insert game data
    _con.prepare("""INSERT INTO game ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                    VALUES ($12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22)""")\
        .load_rows(game_arr)

    # Insert player data
    _con.prepare("""INSERT INTO pres ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                    VALUES ($11,$12,$13,$14,$15,$16,$17,$18,$19,$20)""")\
        .load_rows(pres_arr)

    # Insert card gained data
    _con.prepare("""INSERT INTO gain ($1,$2,$3,$4,$5)
                    VALUES ($6,$7,$8,$9,$10)""").load_rows(gain_arr)

    # Insert card returned data
    _con.prepare("""INSERT INTO ret ($1,$2,$3,$4,$5)
                    VALUES ($6,$7,$8,$9,$10)""").load_rows(ret_arr)


def insert_ratings(rating_history):
    h_rows = []
    r_rows = {}

    for r in rating_history:
        # Store last rating for each player
        r_rows[r['pname']] = (r['time'], r['logfile'], r['pname'],
                              r['new_rating'].mu, r['new_rating'].sigma)

        # Store rating history entry
        h_rows.append((r['time'], r['logfile'], r['pname'],
                       r['old_rating'].mu, r['old_rating'].sigma,
                       r['old_opp_rating'].mu, r['old_opp_rating'].sigma,
                       r['new_rating'].mu, r['new_rating'].sigma))

    # Insert or update rating
    ps = _con.prepare("""UPDATE ts_rating
                            SET time=$1, logfile=$2, mu=$4, sigma=$5
                          WHERE pname=$3""").load_rows(r_rows.values())
    for pname in r_rows:
        r = r_rows[pname]

        ps = _con.prepare("SELECT 1 FROM ts_rating WHERE pname=$1")
        if not ps(pname):
            try:
                ps = _con.prepare("""INSERT INTO ts_rating
                                        (time, logfile, pname, mu, sigma)
                                 VALUES ($1,$2,$3,$4,$5)""")(*r)
            except:
                print(r)
                raise

    # Insert rating histories
    ps = _con.prepare("""INSERT INTO ts_rating_history
                                (time, logfile, pname, old_mu, old_sigma,
                                 old_opp_mu, old_opp_sigma, new_mu, new_sigma)
                         VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""")
    ps.load_rows(h_rows)


def insert_leaderboard(rating_tuples):
    ps = _con.prepare("""INSERT INTO rating VALUES ($1, $2, $3, $4)""")
    ps.load_rows(rating_tuples)
