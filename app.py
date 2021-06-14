'''
Created on May 25, 2021

@author: 869259
'''
'''
intent of code is for recommending frequently sold options for a selected product
input params:
productcode, market, frequency
if running in local - set medium param in pythonconfig.ini - medium=local
if running in webapp - set medium param in pythonconfig.ini - medium=db
set configurable params in pythonconfig.ini
output:
for success scenario - return status,id,productcode
for failure scenario - retuen status,msg

'''

from flask import Flask,request,jsonify
from apriori import get_recommendation

app=Flask(__name__)
app.config['JSON_SORT_KEYS']=False

@app.route('/testme')
def home():
    return 'success'

@app.route('/simulate',methods=['POST'])
def recommend():
    df_result=get_recommendation(request)
    return df_result
#     return(jsonify(df_result.to_json(orient='records')))
#     return recommendation(request)
if __name__=='__main__':
    app.run(debug=True)
