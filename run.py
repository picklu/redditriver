#!/usr/bin/env python3.6

import sys
from app.redditriver import *

if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit(f"Usage: {sys.argv[0]} [port]")
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 8080

    app = MyApplication(urls, globals())
    app.run(port=port)
