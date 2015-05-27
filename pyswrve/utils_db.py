# -*- coding: utf-8 -*-

import re, psycopg2

### --- PostgreSQL --- ###
def fix_cust_props_psql(fname):
    ''' Fix custom_properties csv file for loading to PostgreSQL '''
    
    with open(fname) as f:
        data = f.read()
    
    data = re.sub('\\\,', '.', data)  # iPhone7,2 => iPhone7.2
    data = re.sub(',\r,', ',,', data)  # fix rows splitted in the middle
    data = re.sub(',\",', ',0,', data)  # fix " on level's pos
    
    with open(fname, 'w') as f:
        f.write(data)
        
def psql_upload(db, user, pswd, tname, fpath):
    ''' Load data from csv file to PostgreSQL database '''
    
    # Connect to DB
    con = psycopg2.connect(user=user, database=db, password=pswd)
    
    cmd = 'COPY %s FROM \'%s\' \
WITH(FORMAT CSV, DELIMITER \',\',HEADER, NULL \'\N\');' % (tname, fpath)

    with con:
        cur = con.cursor()
        cur.execute(cmd)
        
    if con:
        con.close()