"""
Script for starting the simplest python-eve.
No auth.
"""
import sys
import logging
from eve import Eve
app = Eve()


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("Start Python-Eve...")
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()