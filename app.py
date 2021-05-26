'''
Created on May 26, 2021

@author: 869259
'''
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/home')
def home():
    return 'Hello World'

if __name__ == '__main__':
    app.run(debug=True)
