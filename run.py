#!/usr/bin/env python2
import sys
from app import *

if __name__ == "__main__":
    if len(sys.argv) > 2:
        sys.exit("Usage: %s [port]" %sys.argv[0])
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 8080
    
    app = MyApplication(urls, globals())
    app.run(port=port)