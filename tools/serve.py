#!/usr/bin/env python3
"""Local preview server that tells the browser not to cache, so edits show on every reload.

Usage:  python3 tools/serve.py PORT DIRECTORY
"""
import functools, http.server, sys


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


port, root = int(sys.argv[1]), sys.argv[2]
http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(NoCache, directory=root)).serve_forever()
