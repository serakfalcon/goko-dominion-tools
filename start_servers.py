#!/usr/bin/python

import sys
import logging
import os

import tornado.web
import tornado.ioloop
import tornado.httpserver

import gdt
from gdt.ratings.leaderboard_handler import LeaderboardHandler
from gdt.logsearch.logsearch_handler import SearchHandler
from gdt.kingviz.kingviz_handler import KingdomHandler
from gdt.automatch.communicator import AutomatchWSH
from gdt.blast.blast import BlastWSH


class SFH(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Access-Control-Allow-Origin", "*")


# Handle requests for log search, kingdom visualizer, and leaderboard.
class LogApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", SearchHandler),
            (r"/logsearch", SearchHandler),
            (r"/logsearch/", SearchHandler),
            (r"/kingdom", KingdomHandler),
            (r"/kingdom/", KingdomHandler),
            (r"/kingdomvisualize", KingdomHandler),
            (r"/kingdomvisualize/", KingdomHandler),
            (r"/leaderboard", LeaderboardHandler),
            (r"/leaderboard/", LeaderboardHandler),
            (r"/wshblast", BlastWSH),
            (r"/static/(.*)", SFH, {"path": "web/static"})
        ]
        tornado.web.Application.__init__(
            self, handlers
        )

class AutomatchApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/automatch", AutomatchWSH),
        ]
        tornado.web.Application.__init__(
            self, handlers
        )


if __name__ == '__main__':
    # Detailed logging for development
    #logging.basicConfig(level=logging.DEBUG)

    # Less detailed logging for production
    logging.basicConfig(level=logging.INFO)

    # Run logsearch+ on the requested port
    http_port = int(sys.argv[1])
    print('Starting log server on port %d' % http_port)
    ws_port = int(sys.argv[2])
    print('Starting automatch server on port %d' % ws_port)

    tornado.httpserver.HTTPServer(LogApplication()).listen(http_port)
    tornado.httpserver.HTTPServer(AutomatchApplication(), ssl_options={
                "certfile": os.path.join("/etc/ssl/certs/", "andrewiannaccone_com.crt"),
                "keyfile": os.path.join("/etc/ssl/private/", "key.pem"),
            }).listen(ws_port)

    tornado.ioloop.IOLoop.instance().start()