import datetime,numpy
import pandas as pd
from pandas import DataFrame
from pymysql import connect,cursors

conn = connect(host='rm-uf67kg347rhjfep5c1o.mysql.rds.aliyuncs.com', user='hongze_admin', password='hongze_2018',
               port=3306, db='stock', charset='utf8mb4', cursorclass=cursors.DictCursor)
indexmarket = pd.read_sql(
    "",
    con=conn)
conn.close()