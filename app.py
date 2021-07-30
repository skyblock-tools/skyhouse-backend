from flask import Flask

import pyximport
pyximport.install(build_dir="build", language_level=3)

import runtimeConfig

app = Flask(__name__)

runtimeConfig.app = app

# noinspection PyUnresolvedReferences
import cy.main

if __name__ == '__main__':
    app.run()
