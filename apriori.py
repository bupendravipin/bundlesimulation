'''
Created on Jun 4, 2021

@author: 869259
'''
from flask.globals import request
'''
intent of code is to run Apriori algorithm basis user selection criteria
log file to keep track of saving results in db, post processing wrp, opion names
error status codes and msgs tracked in log file
result dataset shape tracked in log file
'''

# import libraries
import pandas as pd
import requests
import pyodbc
from mlxtend.frequent_patterns import apriori
from flask import jsonify
from logger import *
import time
import uuid

# generating unique id for saving in db
id = uuid.uuid4()
sql_query="select Sales_Doc_Number, Options, Option_Name from M2O_NPI2C.NPI2Cash_Sales_Order where Product_Code="
# input params
# productcode
# market
# freq
# DB connectivity
# create db connection
def db_connection(sql_driver,server_address,db_name,uid,pwd):
    conn=pyodbc.connect( 'DRIVER={'+sql_driver+'};'
                       'SERVER='+server_address+';'
                       'DATABASE='+db_name+';'
                       'UID='+uid+';'
                       'PWD='+pwd)
    return conn
# close db connection
def closeconnection(conn):
    conn.close()
def closecursor(crsr):
    crsr.close()

logger=logging_func()

def get_recommendation_test(request):
    params=request.get_json()
    productcode=params['Productcode']
    productcode=str(productcode)
    market=params['Market']
    freq=params['Frequency']
    return True
      
def get_recommendation(request):
    try:
        params=request.get_json()
        productcode=params['Productcode']
        productcode=str(productcode)
        market=params['Market']
        freq=params['Frequency']
#       below snippet runs in local 
        if medium!='db':
#             dxr_file_path='C:/Users/869259/Desktop/poc/others_data/DXR_Data_2019_20.xlsx'
            dxr_file_path='C:/Users/869259/Desktop/poc/others_data/ISPRI_Data/ISPRI_Sales_Data.xlsx'
            wrp_file_path='C:/Users/869259/Desktop/poc/others_data/ISPRI_Data/WRP - Apr 2021.xlsx'
#             wrp_file_path='C:/Users/869259/Desktop/poc/others_data/WRP - Apr 2021.xlsx'
            df_dxr_main=pd.read_excel(dxr_file_path,sheet_name=None)
            df_sales=df_dxr_main['Sheet1']
            logger.info('*************************** START IN LOCAL *********************************')
            logger.info('shape of df_sales {}'.format(df_sales.shape))
            df_wrp=pd.read_excel(wrp_file_path)
            #     to be removed
            df_sales['Quantity']=1
            df_sales[['Sales_Doc_Number','Options','Option_Name', 'Product_Code','Market']]=df_sales[['Sales_Doc_Number','Options','Option_Name','Product_Code','Market']].astype(str)
            df_sales=df_sales[df_sales['Product_Code']==productcode]
            if market!='':
                df_sales=df_sales[df_sales['Market']==market]
                logger.info('shape of df_sales with selected market  {}'.format(df_sales.shape))
            else:
                logger.info('Market provided as blank, so considering all markets; shape of df_sales with all markets for selected product  {}'.format(df_sales.shape))
            df_sales=df_sales[df_sales['Options']!=productcode]    
        else:
            logger.info('*************************** START IN DB *********************************')
            pass 
        # remove productcode from options
        #to be removed
    except Exception as e:
        msg='Debug in Input params; '
        msg=msg + str(e.__class__) + " " + str(e)
        logger.error(msg)
        return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR
    
    if medium=='db':
        # connect to db
        try:
            cnxn=db_connection(sql_driver,server_address,db_name,uid,pwd)
        except Exception as e:
            msg='Check medium, uid, pwd in pythonconfig.ini; Debug in db_connection method; '
            msg=msg + str(e.__class__) + " " + str(e)
            logger.error(msg)
            return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR
        # create sql query for salesorder data
        if market:
            salesorder_sql=sql_query+"'"+productcode+"'"+"and Market="+"'"+market+"'"
        else:
            salesorder_sql=sql_query+"'"+productcode+"'"
        try:
            # query to sales order data
            df_sales=pd.read_sql(salesorder_sql,cnxn)
            df_sales['Quantity']=1
            # remove productcode from options
            df_sales=df_sales[df_sales['Options']!=productcode]
            df_sales[['Sales_Doc_Number','Options','Option_Name']]=df_sales[['Sales_Doc_Number','Options','Option_Name']].astype(str)
            df_sales.shape
            # query to Item price table
            wrp_sql="select VARCOND,ZCTR from M2O_NPI2C.NPI2Cash_Item_Price"
            df_wrp=pd.read_sql(wrp_sql,cnxn)
            df_wrp.shape
        except Exception as e:
            msg=str(e.__class__) + " " + str(e)
            logger.error(msg)
            return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR
    else:
        pass
    # Run Apriori algorithm
    def run_apriori(df,support):
        try:
            b_plus = df.groupby(['Sales_Doc_Number', 'Options'])['Quantity'].sum().unstack().reset_index().fillna(0).set_index('Sales_Doc_Number')
            def encode_units(x):
                if x <= 0:
                    return 0
                if x >= 1:
                    return 1
            b_encode_plus = b_plus.applymap(encode_units)
            b_filter_plus = b_encode_plus[(b_encode_plus > 0).sum(axis=1)>=2]
            start_time=time.time()
            frequent_itemsets_plus = apriori(b_filter_plus, min_support=support, 
                                                 use_colnames=True).sort_values('support', ascending=False).reset_index(drop=True)
            end_time=time.time()
            apriori_time=end_time-start_time
            logger.info('Time taken to run Apriori {}'.format(apriori_time))
            frequent_itemsets_plus['Length'] = frequent_itemsets_plus['itemsets'].apply(lambda x: len(x))
            
            frequent_itemsets_plus['Options'] = [','.join(map(str, l)) for l in frequent_itemsets_plus['itemsets']]
            return frequent_itemsets_plus,requests.codes.ok
        except Exception as e:
            return e,requests.codes.INTERNAL_SERVER_ERROR
     
    df_apriori_result,status=run_apriori(df_sales,freq)
    if status!=requests.codes.ok:
        msg='Debug in run_apriori method; '
        msg=msg + str(df_apriori_result.__class__) + " " + str(df_apriori_result)
        logger.error(msg)
        return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR
         
    def map_wrp_options(df_sales,df_wrp,df_apriori_result):
        try:
            # map option and wrp
            # map option and option names
            items=df_wrp['VARCOND'].astype(str).to_list()
            price=df_wrp['ZCTR'].astype(str).to_list()
            options=df_sales['Options'].astype(str).to_list()
            option_names=df_sales['Option_Name'].astype(str).to_list()
            dict_option_names=dict(zip(options,option_names))
            dict_items_prices=dict(zip(items,price))
            # items without WRP info, assigning 0 
            items_without_wrp=list(set(options) - set(items))
            # len(items_without_wrp)
            items_without_wrp_dict=dict.fromkeys(items_without_wrp,0)
            dict_items_prices.update(items_without_wrp_dict)
            item_list=[]
            wrp_list=[]
            df_apriori_result['Option_Name']=''
            df_apriori_result['WRP']=''
            df_apriori_result['Total_WRP']=''
            df_apriori_result['Options']=df_apriori_result['Options'].astype(str)
            # assign option name to list of option codes
            for i in range(len(df_apriori_result['Options'])):
                item=df_apriori_result['Options'].iloc[i].split(',')
                item_list.append([dict_option_names[i] for i in item])
            df_apriori_result['options_names_list']=item_list
            for i in range(len(df_apriori_result['options_names_list'])):
                df_apriori_result['Option_Name'].iloc[i]=",".join(df_apriori_result['options_names_list'].iloc[i])
            # assign wrp to list of options
            for i in range(len(df_apriori_result['Options'])):
                item=df_apriori_result['Options'].iloc[i].split(',')
                wrp_list.append([dict_items_prices[i] for i in item])
            df_apriori_result['WRP_list']=wrp_list
            for i in range(len(df_apriori_result['WRP_list'])):
                df_apriori_result['WRP'].iloc[i]=",".join(df_apriori_result['WRP_list'].iloc[i])
            # sum of wrp
            for i in range(len(df_apriori_result['WRP'])):
                items = df_apriori_result['WRP'].iloc[i].split(',')
                items = [float(i) for i in items]
                df_apriori_result['Total_WRP'].iloc[i] = sum(items)
            return df_apriori_result,requests.codes.ok
        except Exception as e:
            return e,requests.codes.INTERNAL_SERVER_ERROR
    start_time=time.time()   
    df_final,status=map_wrp_options(df_sales,df_wrp,df_apriori_result)
    end_time=time.time()
    time_elapsed=end_time-start_time
    logger.info('Time taken for mapping WRP, option names, sum of WRP to Apriori result set {}'.format(time_elapsed))
    if status!=requests.codes.ok:
        msg='Debug in map_wrp_options method; '
        msg=msg + str(df_final.__class__) + " " + str(df_final)
        logger.error(msg)
        return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR
#         return jsonify({'Error': msg + "%s" %str(df_final)}),requests.codes.INTERNAL_SERVER_ERROR
#         return jsonify({'Error': msg + "%s" %str(df_apriori_result)}),requests.codes.INTERNAL_SERVER_ERROR
    logger.info('shape of Apriori result set {}'.format(df_final.shape))
    df_final.rename({'support':'Support'},axis=1,inplace=True)
    df_final=df_final[['Options','Option_Name','Total_WRP','Support','Length']]
    df_final['ID']=id
    df_final['Product_Code']=int(productcode)
#     df_final=df_final[['ID','Product Code','Options','Option Name','Total_WRP','Support','Length']]
    out={'status':'success in local','ID':id,'Product_Code':productcode}
    if medium!='db':
        logger.info('*************************** END IN LOCAL *********************************')
#         return jsonify(out),requests.codes.ok
        df_final=df_final[['ID','Product_Code','Options','Option_Name','Total_WRP','Support','Length']].astype(str)
        return jsonify(df_final.to_json(orient='records'))
        
    else:    
    # save to results to DB
        try:
            cursor=cnxn.cursor()
            start_time=time.time()
            logger.info('Apriori results saving to DB START TIME  {}'.format(start_time))
            logger.info('shape of Apriori result set {}'.format(df_final.shape))
            for index,row in df_final.iterrows():
                cursor.execute('INSERT INTO M2O_NPI2C.NPI2Cash_Results([ID],[Product_Code],[Options],[Option_Name],[Total_WRP],[Support],[Length]) values (?,?,?,?,?,?,?)', 
                                row['ID'], 
                                row['Product_Code'],
                                row['Options'], 
                                row['Option_Name'],
                                row['Total_WRP'],
                                row['Support'],
                                row['Length'])
                cnxn.commit()
            closecursor(cursor)
            closeconnection(cnxn)
            end_time=time.time()
            logger.info('Apriori results saved to DB END TIME  {}'.format(end_time))
            time_elapsed_db=end_time-start_time
            logger.info('Apriori results saved to DB END TIME  {}'.format(time_elapsed_db))
            out={'status':'success in db','ID':id,'Product Code':productcode}
            logger.info('*************************** END IN DB *********************************')
            df_final=df_final[['ID','Product_Code','Options','Option_Name','Total_WRP','Support','Length']].astype(str)
            return jsonify(df_final.to_json(orient='records'))
#             return jsonify(out),requests.codes.ok
    #         return {'status':200, 'msg':'saved to db'}
        except Exception as e:
            msg='Debug in save results db; '
            msg=msg + str(df_final.__class__) + " " + str(df_final)
            logger.error(msg)
            return jsonify({'status':'fail','message': msg}), requests.codes.INTERNAL_SERVER_ERROR