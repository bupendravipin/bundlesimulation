'''
Created on May 31, 2021

@author: 869259
'''

from flask import Flask, request, jsonify
import pandas as pd
from logger import *
app = Flask(__name__)

logger=logging_func()

@app.route('/')
def home():
    logger.info('In home endpoint')
    return 'Hello World'

@app.route('/simulate')
def recommend():
    logger.info('In simulate endpoint')
    df=pd.DataFrame([1,2,3],columns=['A'])
#     url = 'https://raw.githubusercontent.com/bupendravipin/bundlesimulation/master/712034.xlsx'
#     df = pd.read_excel(url, index_col=0)
    return(jsonify(df.to_json(orient='records')))

# return(jsonify(df_result.to_json(orient='records')))

if __name__ == '__main__':
    app.run(debug=True)

