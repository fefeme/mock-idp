# coding: utf-8
from flask import Flask

__version__ = "0.3.1"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

import mockidp.saml.routes
import mockidp.routes
