#!/usr/bin/env python3
"""
    batman.app
    ~~~~~~~~~~

    Web application for visualizing the health effects of bitter gourd and yam
    compounds, based on our results from text mining PubMed articles.

    :copyright: © 2018 by Jonathan Feenstra.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '0.1'

from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """Render the 'home.html' template."""
    return render_template('home.html')

@app.route('/about')
def about():
    """Render the 'about.html' template."""
    return render_template('about.html')

@app.route('/search')
def search():
    """Render the 'search.html' template."""
    return render_template('search.html')

@app.route('/help')
def help():
    """Render the 'help.html' template."""
    return render_template('help.html')

@app.route('/contact')
def contact():
    """Render the 'contact.html' template."""
    return render_template('contact.html')

@app.route('/pacman')
def pacman():
    """Render the 'pacman.html' template."""
    return render_template('pacman.html')

@app.route('/shutdown')
def shutdown_server():
    """Shut down the hosted server."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return 'server shutdown'

if __name__ == '__main__':
    app.run(debug=True)
