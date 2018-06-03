#!/usr/bin/env python3
"""
    batman.app
    ~~~~~~~~~~

    Web application for visualizing the health effects of bitter gourd and yam
    compounds, based on our results from text mining PubMed abstracts.

    This script is responsible for running the web application.

    Known bugs: none.

    :copyright: © 2018 by Jonathan Feenstra.
    :license: MIT, see LICENSE for more details.
"""

__version__ = '1.0'

from flask import (Flask, redirect, render_template, request, url_for)


# Initialize and configure Flask app
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')


# Instance relative configuration if applicable
try:
    app.config.from_pyfile('config.py')
except FileNotFoundError:
    pass


@app.route('/')
def index():
    """Render the 'home.html' template.

    :returns: rendered 'home.html' template.
    """
    return render_template('home.html')


@app.route('/about')
def about():
    """Render the 'about.html' template.

    :returns: rendered 'about.html' template.
    """
    return render_template('about.html')


@app.route('/network')
def network():
    """Render the 'network.html' template.

    :returns: rendered 'network.html' template.
    """
    return render_template('network.html')


@app.route('/help')
def help():
    """Render the 'help.html' template.

    :returns: rendered 'help.html' template.
    """
    return render_template('help.html')


@app.route('/contact')
def contact():
    """Render the 'contact.html' template.

    :returns: rendered 'contact.html' template.
    """
    return render_template('contact.html')


@app.route('/pacman')
def pacman():
    """Render the 'pacman.html' template.

    :returns: rendered 'pacman.html' template.
    """
    return render_template('pacman.html')


@app.errorhandler(404)
def page_not_found(e):
    """Render the '404.html' template.

    :returns: rendered '404.html' template.
    """
    return render_template('404.html'), 404


# Run the Flask app
if __name__ == '__main__':
    app.run()
