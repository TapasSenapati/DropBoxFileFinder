import os
import sys

from flask import Flask

app = Flask(__name__)


if __name__ == "__main__":
    # Run the flask app
    try:
        # Start the flask app
        app.run()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

from dropbox_finder import routes