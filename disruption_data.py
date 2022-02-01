from docx import Document
import pandas as pd
import os
from database import getConn
import itertools
import numpy as np

directory = "./static/assets/configuration/RM Central/"


def store_data(doc_sub_id, station_list, table0, table1, table2, table3):
    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to CHATBOT")

    for i in range(doc_sub_id):
        cur.execute('INSERT INTO StationDisruptionPlan (id, station_name, doc_owner) VALUES (%s, %s, %s)', [i + 1, station_list[i], table0[i]])
        conn.commit()
    conn.close()

    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to CHATBOT")

    
    for i, val in enumerate(table1):
        for k in val:
            if((k[0] != '' or k[1] != '' or k[2] !='')):
                if(k[0] != 'N/A' or k[1] != 'N/A' or k[2] != 'N/A'):
                    if(k[0] != None or k[1] != None or k[2] != None):
                        cur.execute('INSERT INTO OtherStationSupport VALUES (%s, %s, %s, %s)', [i + 1, k[0], k[1], k[2]])
                        conn.commit()
    conn.close()

    
    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to CHATBOT")   

    for i, val in enumerate(table3):
        for k in val:
            if(k[0] != '' or k[1] != '' ):
                if(k[0] != 'N/A' or k[1] != 'N/A'):
                    if(k[0] != None or k[1] != None):
                        cur.execute('INSERT INTO StationTips VALUES (%s, %s, %s)', [i + 1, k[0], k[1]])
                        conn.commit()

    conn.close()


    conn = getConn()
    cur = conn.cursor()
    cur.execute("SET SEARCH_PATH to CHATBOT") 

    for i, val in enumerate(table2):
        for j in val:
            a = []
            b = []
            c = []
            d = []
            for x, k in enumerate(j):
                if x == 0:
                    a.append(k)
                elif x == 1:
                    b.append(k)
                elif x == 2:
                    c.append(k)
                elif x == 3:
                    d.append(k)

            cur.execute('INSERT INTO AltTransportInfo VALUES (%s, %s, %s, %s)', [i+1, b[0], 0, a])
            cur.execute('INSERT INTO AltTransportInfo VALUES (%s, %s, %s, %s)', [i+1, b[0], 1, c])
            cur.execute('INSERT INTO AltTransportInfo VALUES (%s, %s, %s, %s)', [i+1, b[0], 2, d])
            conn.commit()

    conn.close()




def document_extracter(Dname):
    document = Document(Dname)
    data = []
    ext_table0 = []  
    table0 = []  
    table1 = []  
    table2 = []  
    table3 = []  
    table4 = [] 
    table5 = []  
    table6 = []  
    for j in range(0, 10):
        try:
            table = document.tables[j]
        except:
            continue

        keys = None
        for i, row in enumerate(table.rows):
            text = (cell.text for cell in row.cells)
            if i == 0:
                keys = tuple(text)
                continue

            row_data = tuple(text)
            if j == 0:
                table0.append(row_data)
            if j == 1:
                table1.append(row_data)
            if j == 2:
                table2.append(row_data)
            if j == 3:
                table3.append(row_data)
            if j == 6:
                table6.append(row_data)
 
    return (table0, table2, table3, table6)




station_list = []
doc_sub_id=59
document_owner_list=[]
StationDisruptionPlan_list=[]
OtherStationSupport_list=[]
AltTransportInfo_list=[]
StationTips_list=[]
for filename in os.listdir(directory):   
    f = os.path.join(directory, filename)
   
    if os.path.isfile(f):
        
        value=document_extracter(f)
        
        for i in value[0]:
            document_owner=i[1]
        document_owner_list.append(document_owner)
        
       
        OtherStationSupport_list.append(value[1])
        
        
        AltTransportInfo_list.append(value[2])
        
        
        StationTips_list.append(value[3])
        
    
        try:
            star_index = f.index("Station Disruption Plan -")
        except:
            star_index = f.index("Station Disruption Plan ")
         
        try:
            end_index=f.index("Issue 1 - ")
        except Exception :
            try:
                end_index=f.index(" Issue 2 - ")
            except Exception:
                try:
                    end_index=f.index(" Issue - ")
                except Exception :
                    try:
                        end_index=f.index(" Issue 1a - ")
                    except Exception :
                        try:
                            end_index=f.index(" Issue  2 - ")
                        except Exception:
                            try:
                                end_index=f.index(" Issue 2 ")
                            except Exception:
                                try:
                                    end_index=f.index(" Issue 2-")
                                except Exception:
                                    try:
                                        end_index=f.index(" Issue 3 - ")
                                    except Exception:
                                        print("end index excep")
                
                
        station_name=f[star_index+25:end_index]
        station_name=station_name.strip()
        station_list.append(station_name)
        
        
    
        doc_sub_id+=1

    
store_data(doc_sub_id, station_list, document_owner_list, OtherStationSupport_list, AltTransportInfo_list, StationTips_list)

