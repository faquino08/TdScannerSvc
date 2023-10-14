import sys
import logging
import psycopg2
import psycopg2.extras
import os
import re
from os.path import exists
import csv
import datetime
import time
import glob
import pandas as pd
import numpy as np
import locale
from io import StringIO
from sqlalchemy import create_engine
from pyparsing import Regex

logger = logging.getLogger(__name__)
class databaseHandler:
    def __init__(self,params_dic={}):
        '''
        Database wrapper for common SQL queries and handling database connection.
        params_dic  -> Dict with keys host, port, database, user, \
                            password for Postgres database
        '''
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
        self.params = params_dic
        self.logger = logger
        self.conn = None
        self.cur = None
        self.batch_size = 1000000
        self.connect()
        self.tableNames = []
        self.char_list = [
        ]
        self.chartwo_list =[
        ]
        self.symbol_list = [
        ]
        self.uniqueSymbol_list = [
            "Symbol",
        ]
        self.int_list = [
            "Month"
        ]
        self.bigint_list = [
            "Volume",
            "Market Cap",
        ]
        self.decimal_list = [
            "Last",
            "Vol Index",
            "Net Chng",
            "%Change",
            "Bid",
            "Ask",
            "High",
            "Low",
            "EPS",
        ]
        self.name_list = [
            "Description",
            "Sector",
            "Industry",
            "Sub-Industry"
        ]
        self.date_list = [
            "Expiration Date"
        ]
        self.datetime_list = [
            "Time"
        ]

    def exit(self):
        '''
        Exit class and close Postgres connection
        '''
        self.cur.close()
        self.conn.close()
        self.logger.info('Db Exit Status:')
        self.logger.info('Psycopg2:')
        self.logger.info(self.conn.closed)

    def connect(self):
        '''
        Connect to the PostgreSQL database server
        ''' 
        try:
            # connect to the PostgreSQL server
            self.logger.debug('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**self.params)
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.debug(error)
            sys.exit(1)
        self.logger.debug("Connection successful")
        return

    def composeSqlColumnsPlaceholders(self,dataSample=[]):
        '''
        Takes list and create string of placeholders for each entry in list for execute_mogrify.
        dataSample  -> (list) List of columns to insert
        '''
        result = "("
        i = 1
        while i <= len(dataSample):
            result += "%s,"
            i += 1
        result = result[:-1] + ")"
        return result

    def getColNamesDataTypes(self,panda,excluded=[],addlCols=[],constraints=''):
        '''
        Takes pandas dataframe and returns string formatting the columns for SQL Create Table query.
        excluded    -> (list) Columns from Dataframe to exclude from Sql query
        addlCols    -> (list) Additional columns to insert on top of Dataframe\ 
                        columns
        '''
        res = "("
        # Loop Through Columns and Append to
        for col in panda.columns:
            notExcluded = bool(col not in excluded)
            if (notExcluded):
                if col in self.symbol_list:
                    res += "%s varchar(14)," % '"{}"'.format(col)
                elif col in self.uniqueSymbol_list:
                    res += "%s varchar(14) primary key," % '"{}"'.format(col)
                elif col in self.name_list :
                    res += "%s varchar(255)," % '"{}"'.format(col)
                elif col in self.char_list:
                    res += "%s varchar(1)," % '"{}"'.format(col)
                elif col in self.chartwo_list:
                    res += "%s varchar(2)," % '"{}"'.format(col)
                elif col in self.int_list:
                    res += "%s int," % '"{}"'.format(col)
                elif col in self.bigint_list:
                    res += "%s bigint," % '"{}"'.format(col)
                elif col in self.date_list:
                    res += "%s date," % '"{}"'.format(col)
                elif col in self.datetime_list:
                    res += "%s timestamp without time zone," % '"{}"'.format(col)
                elif col in self.decimal_list:
                    res += "%s decimal," % '"{}"'.format(col)
                else:
                    res += "%s text," % '"{}"'.format(col)
        if len(addlCols) > 0:
            for col in addlCols:
                notExcluded = bool(col not in excluded)
                if (notExcluded):
                    res += "%s," % col
        if len(constraints) == 0:
            res = str(res[:-1]) + ")"
        else:
            res = str(res) + f" {constraints})"
        return res

    def getColNames(self,panda,unique=True,excluded=[],addlCols=[]):
        '''
        Takes pandas dataframe and returns string formatting the columns for SQL Select Table query.
        unique      -> (boolean) excludes the unique columns from the response \
                        when set to False
        excluded    -> (list) Columns from Dataframe to exclude from Sql query
        addlCols    -> (list) Additional columns to insert on top of Dataframe\ 
                        columns
        '''
        res = "("
        # Loop Through Columns and Append to
        for col in panda.columns:
            notExcluded = bool(col not in excluded)
            if (notExcluded):
                if col in self.symbol_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.uniqueSymbol_list and unique:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.name_list :
                    res += "%s," % '"{}"'.format(col)
                elif col in self.char_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.chartwo_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.int_list:
                    res += "%s int," % '"{}"'.format(col)
                elif col in self.bigint_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.date_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.datetime_list:
                    res += "%s," % '"{}"'.format(col)
                elif col in self.decimal_list:
                    res += "%s," % '"{}"'.format(col)
                else:
                    res += "%s," % '"{}"'.format(col)
        if len(addlCols) > 0:
            for col in addlCols:
                notExcluded = bool(col not in excluded)
                if (notExcluded):
                    res += "%s," % '"{}"'.format(col)
        res = str(res[:-1]) + ")"
        return res

    def getExcludedColNames(self, panda, unique=True,excluded=[],addlCols=[]):
        '''
        Get column names with excluded prepended to the names.
        panda       -> (Dataframe) columns to get for command
        unique      -> (boolean) excludes the unique columns from the response\
                         when set to False.
        excluded    -> (list) list of columns to exclude
        addlCols    -> (list) additional columns to include
        '''
        res = "("
        # Loop Through Columns and Append to
        for col in panda.columns:
            notExcluded = bool(col not in excluded)
            if (notExcluded):
                if col in self.symbol_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.uniqueSymbol_list and unique:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.name_list :
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.char_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.chartwo_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.int_list:
                    res += "%s int," % '"{}"'.format(col)
                elif col in self.bigint_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.date_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.datetime_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                elif col in self.decimal_list:
                    res += "excluded.%s," % '"{}"'.format(col)
                else:
                    res += "excluded.%s," % '"{}"'.format(col)
        if len(addlCols) > 0:
            for col in addlCols:
                notExcluded = bool(col not in excluded)
                if (notExcluded):
                    res += "%s," % '"{}"'.format(col)
        res = str(res[:-1]) + ")"
        return res
                        
    def execute_mogrify(self,index,table=None,date=None):
        '''
        Takes dataframe and inserts the data into the provided table using execute_mogrify.
        table           -> (str) Name of Postgres Table
        date            -> (str) Date for beginning EDGAR Ticker scrape from \
                            SEC filings
        '''
        if table in self.tableNames:
            if (len(index) > 0):
                str_placholders = self.\
                    composeSqlColumnsPlaceholders(dataSample=index[0])
                for i in range(0, len(index), self.batch_size):
                    args_str = ','.join(self.cur.mogrify(str_placholders,row).decode('utf-8') for row in index[i:i+self.batch_size])
                    self.logger.debug("Inserting into %s" % table)
                    try:
                        self.cur.execute('INSERT INTO %s VALUES %s' % (table,args_str))
                        self.conn.commit()
                    except (Exception, psycopg2.DatabaseError) as error:
                        self.logger.debug("Error: %s" % error)
                        self.conn.rollback()
        if table is not None:
            if table == "edgarindex":
                if (len(index) > 0):
                    str_placholders = self.\
                        composeSqlColumnsPlaceholders(dataSample=index[0])
                    for i in range(0, len(index), self.batch_size):
                        args_str = ','.join(self.cur.mogrify(str_placholders,row).decode('utf-8') for row in index[i:i+self.batch_size])
                        self.logger.debug(f"Inserting master index from EDGAR")
                        try:
                            self.cur.execute('INSERT INTO "edgarindex" VALUES' + args_str)
                            self.conn.commit()
                        except (Exception, psycopg2.DatabaseError) as error:
                            self.logger.debug("Error: %s" % error)
                            self.conn.rollback()
            if table == "edgartickerindex":
                if (len(index) > 0):
                    str_placholders = self.\
                        composeSqlColumnsPlaceholders(dataSample=index[0])
                    for i in range(0, len(index), self.batch_size):
                        args_str = ','.join(self.cur.mogrify(str_placholders,row).decode('utf-8') for row in index[i:i+self.batch_size])
                        self.logger.debug("Inserting tickers from recent SEC Filings (Starting: %s) into  edgartickerindex" % date)
                        try:
                            self.cur.execute('INSERT INTO "edgartickerindex" VALUES' + args_str)
                            self.conn.commit()
                        except (Exception, psycopg2.DatabaseError) as error:
                            self.logger.debug("Error: %s" % error)
                            self.conn.rollback()
            if table == "edgarfilings":
                if (len(index) > 0):
                    str_placholders = self.\
                        composeSqlColumnsPlaceholders(dataSample=index[0])
                    for i in range(0, len(index), self.batch_size):
                        if ((i+self.batch_size) < len(index)):
                            batch_max = i+self.batch_size
                        elif (i+self.batch_size >= len(index)):
                            batch_max = len(index)-1
                        if len(index) == 1:
                            batch_max = 1
                        tuples = [tuple(x) for x in index[i:batch_max]]
                        values = [self.cur.mogrify(str_placholders, tup).decode('utf8') for tup in tuples]
                        args_str = ",".join(values)
                        args_str = args_str.replace("\'NULL\'","NULL")
                        self.logger.info("Inserting filing data from Edgar...")
                        self.logger.debug('INSERT INTO public.edgarfilings VALUES %s ON CONFLICT ON CONSTRAINT accession DO NOTHING;' % args_str)
                        try:
                            self.cur.execute('INSERT INTO public.edgarfilings VALUES %s ON CONFLICT ON CONSTRAINT accession DO NOTHING;' % args_str)
                            self.conn.commit()
                        except (Exception, psycopg2.DatabaseError) as error:
                            self.logger.debug("Error: %s" % error)
                            self.conn.rollback()
        else:
            raise Exception("Need to provide table for execute_mogrify.")

    def createTable(self,panda=pd.DataFrame(),table=None,addlCols=[],drop=False,constraints=''):
        '''
        Create new empty table based on columns in Dataframes.
        panda       -> (Dataframe) Data to insert in Postgres
        table       -> (str) Name of Postgres table
        addlCols    -> (list) List of additional columns to insert not in panda
        drop        -> (boolean) Whether to drop old table or not
        '''
        # Drop Old Table
        if drop:
            drop_sql = f"DROP TABLE IF EXISTS {table};"
            self.logger.info("Dropping %s" % table)
            self.logger.debug(drop_sql)
            try:
                self.cur.execute(drop_sql)
                self.conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                self.log.debug("Error: %s" % error)
                self.conn.rollback()
        # Create New Table
        if table is not None:
            self.csv_cols = self.getColNamesDataTypes(panda,addlCols=addlCols,constraints=constraints)
            sqlCom = "CREATE TABLE IF NOT EXISTS %s %s" % (table,self.csv_cols)
            self.logger.info("Creating %s" % table)
            self.logger.debug(sqlCom)
            try:
                self.cur.execute(sqlCom)
                self.conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                self.logger.info("Error: %s" % error)
                self.conn.rollback()
            return

    def getLastDate(self,table,column):
        '''
        Get largest date in Postgres table.
        table   -> (str) Name of Postgres table
        column  -> (str) Name of Postgres date column
        '''
        lastTimeSql = "SELECT MAX(\"{}\") FROM {}"
        sqlComm = lastTimeSql.format(column,table)
        try:
            self.cur.execute(sqlComm)
            lastDate = self.cur.fetchone()[0]
            return lastDate
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.debug("Error: %s" % error)
            self.conn.rollback()
            return None

    def getLastDateForSymbol(self,table,column,symCol,symbol):
        '''
        Get largest date in Postgres table for specific entry.
        table       -> (str) Name of Postgres table
        column      -> (str) Name of Postgres date column
        symCol      -> (str) Name of column to filter
        symbol      -> (str) Value to filter for in table
        '''
        lastTimeSql = "SELECT MAX(\"{}\") FROM {} WHERE \"{}\"='{}'"
        sqlComm = lastTimeSql.format(column,table,symCol,symbol)
        try:
            self.cur.execute(sqlComm)
            lastDate = self.cur.fetchone()[0]
            return lastDate
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.debug("Error: %s" % error)
            self.conn.rollback()
            return None

    def getNewScannerEntries(self):
        '''
        Function to get csv files of index scans and options attributes in the FTP Server receiving folder.
        '''
        files = glob.glob("/home/powerauto/data/*.csv")
        fileNameFormat = re.compile('\d{4}-\d{2}-\d{2}-\w*Scanner.csv')
        scans = [file for file in files if fileNameFormat.search(file) ]
        scansLength = len(scans)
        if (scansLength > 0):
            i = 0
            while i < scansLength: 
                with open(scans[i]) as file:        
                    fileName =scans[i]
                    suc = self.parseCsv(file,fileName) 

                    if suc == 0: # IF execute values succeeded
                        file.close()
                        delCmd = fileName
                        os.remove(delCmd)
                    i += 1
        else:
            self.logger.info("")
            self.logger.info("No scans to insert")
        return

    def getNewSectorEntries(self):
        '''
        Function to get csv files of sector scans and in the FTP Server receiving folder.
        '''
        files = glob.glob("/home/powerauto/data/*.csv")
        fileNameFormat = re.compile('\d{4}-\d{2}-\d{2}-Sector\w*.csv')
        scans = [file for file in files if fileNameFormat.search(file) ]
        scansLength = len(scans)
        if (scansLength > 0):
            i = 0
            while i < scansLength: 
                with open(scans[i]) as file:                      
                    #lastEntry = self.getLastDate("edgarindex","FILING_DATE")
                    '''if lastEntry is not None:
                        self.tsv_results = [row for row in csv_file if datetime.date.fromisoformat(row[3]) > lastEntry and datetime.date.fromisoformat(row[3])+datetime.timedelta(days=2)  <= todays_Date]
                    else:'''
                    fileName =scans[i]
                    suc = self.parseSectorCsv(file,fileName)
                    #self.logger.info("csv to list:",index)
                    if suc == 0: # IF execute values succeeded
                        #self.execute_mogrify(self.tsv_results,"edgarindex")
                        file.close()
                        delCmd = fileName
                        os.remove(delCmd)
                        #Linux
                        #os.system('cd ./index & rm -rf master.csv &')
                    i += 1
        else:
            self.logger.info("")
            self.logger.info("No scans to insert")
        return
    
    def getNewCalendarEntries(self):
        '''
        Function to get csv file of calendar events exported from TD Ameritrade and in the FTP Server receiving folder.
        '''
        files = glob.glob("/home/powerauto/data/*.csv")
        fileNameFormat = re.compile('\d{4}-\d{2}-\d{2}-TdCalendar.csv')
        scans = [file for file in files if fileNameFormat.search(file)]
        scansLength = len(scans)
        if (scansLength > 0):
            i = 0
            while i < scansLength: 
                with open(scans[i]) as file:                      
                    fileName =scans[i]
                    suc = self.parseCalendarCsv(scans[i],fileName)
                    #self.logger.info("csv to list:",index)
                    if suc == 0: # IF execute values succeeded
                        #self.execute_mogrify(self.tsv_results,"edgarindex")
                        file.close()
                        delCmd = fileName
                        os.remove(delCmd)
                        #Linux
                        #os.system('cd ./index & rm -rf master.csv &')
                    i += 1
        else:
            self.logger.info("")
            self.logger.info("No scans to insert")
        return

    def execute_values(self, df, table, excluded=[]):
        '''
        Takes dataframe and inserts the data into the provided table using execute_values.
        df          -> (Dataframe) Dataframe to insert
        table       -> (str) Name of Postgres Table
        excluded    -> (list) List of column names to exclude
        '''
        # Get Lists of Column Names in different forms
        colNames = self.getColNames(df)
        self.colNamesNoPK = self.getColNames(df,False,excluded=excluded) # Get Column Names without Primary Key
        self.excludedColNames = self.getExcludedColNames(df,excluded=excluded)
        # Create a list of tupples from the dataframe values
        tuples = []
        for x in df.to_numpy():
            tuples.append(tuple(x))

        if(table in self.tableNames):
            insert_sql = f'''
                INSERT INTO {table} {colNames} \
                    VALUES %s \
                    ON CONFLICT ("Symbol") DO UPDATE SET \
                    {self.colNamesNoPK} = {self.excludedColNames};
            '''
            if table == 'calendar_TdScan':
                insert_sql = f'''
                INSERT INTO {table} {colNames} \
                    VALUES %s \
                    ON CONFLICT ON CONSTRAINT uniqueevents DO UPDATE SET \
                    {self.colNamesNoPK} = {self.excludedColNames};
            '''
            self.logger.debug(insert_sql)
        try:
            psycopg2.extras.execute_values(self.cur, insert_sql, tuples)
            self.conn.commit()
        except Exception as error:
            #print_psycopg2_exception(error)
            print("Error: %s" % error)
            self.logger.error(error)
            self.conn.rollback()
            self.logger.info('\n\n\n')
            self.logger.info(insert_sql)
            return 1
        print("execute_values() done")
        return 0

    def cleanCsv(self,panda,unique=True,excluded=[],sector=''):
        '''
        Clean the raw dataframe from reading the csv file with pandas.read_csv.
        panda       -> (Dataframe) output of pandas.read_csv
        unique      -> (boolean) whether to include unique cols in command
        excluded    -> (list) list of columns to exclude from command
        '''
        sectorNames = {
            "SectorCommunication": "Communication Services",
            "SectorDiscretionary": "Consumer Discretionary",
            "SectorEnergy": "Energy",
            "SectorFinancial": "Financials",
            "SectorHealth": "Health Care",
            "SectorIndustrial": "Industrials",
            "SectorInfoTech": "Information Technology",
            "SectorMaterials": "Materials",
            "SectorRealEstate": "Real Estate",
            "SectorStaple": "Consumer Staples",
            "SectorUtilities": "Utilities"
        }
        formatColumns = {}
        # Loop Through Columns and Append to
        for col in panda.columns:
            notExcluded = bool(col not in excluded)
            if (notExcluded):
                if col in self.symbol_list:
                    panda[col] = panda[col].replace(["<empty>"],[np.nan], regex=True)
                    panda[col].astype(str)
                    formatColumns[col] = str
                elif col in self.uniqueSymbol_list and unique:
                    panda[col] = panda[col].replace(["<empty>"],[np.nan], regex=True)
                    panda[col].astype(str)
                    formatColumns[col] = str
                elif col in self.name_list:
                    panda[col] = panda[col].replace(["<empty>","'"],[np.nan,""], regex=True)
                    if col == "Sector" and len(sector) > 0:
                        panda[col] = sectorNames[sector]
                    panda[col].astype(str)
                    formatColumns[col] = str
                elif col in self.char_list:
                    panda[col] = panda[col].replace(["<empty>"],[np.nan], regex=True)
                    panda[col].astype(np.char)
                    formatColumns[col] = np.char
                elif col in self.chartwo_list:
                    panda[col] = panda[col].replace(["<empty>"],[np.nan], regex=True)
                    panda[col].astype(str)
                    formatColumns[col] = str
                elif col in self.int_list:
                    res += "%s int," % '"{}"'.format(col)
                elif col in self.bigint_list:
                    panda[col] = panda[col].replace(["<empty>",","],[0,""], regex=True)
                    panda[col] = panda[col].replace(["K","M"],["*1e3","*1e6"], regex=True).map(pd.eval).astype(np.int64)
                    formatColumns[col] = np.int64
                elif col in self.date_list:
                    formatColumns[col] = str
                elif col in self.datetime_list:
                    formatColumns[col] = str
                elif col in self.decimal_list:
                    panda[col] = panda[col].replace(["<empty>","%",","],[np.nan,"",""], regex=True)
                    panda[col] = panda[col].replace("++",np.nan)
                    panda[col] = panda[col].replace("--",np.nan)
                    
                    for index, row in panda.iterrows():
                        if "'" in str(row[col]):
                            treasuryFuture = row[col]
                            divider = treasuryFuture.find("'")
                            dollars = float(treasuryFuture[:divider])
                            cents = treasuryFuture[divider+1:]
                            if len(cents) >= 3:
                                cents = (float(cents)/10)/32
                            else:
                                cents = (float(cents))/32
                            panda[col][index] = dollars + cents
                        
                    panda[col].astype(float)
                    formatColumns[col] = float
                else:
                    formatColumns[col] = str
        return panda
    
    def cleanCalendarCsv(self,eventsByMonth=[]):
        cleanCsv = []
        i = 0
        currentMonth = datetime.datetime.today().month
        lookahead = 12 + (currentMonth - 1)
        if len(eventsByMonth) > 0:
            while i < lookahead:
                try:
                    eventsByMonth[i]['Time'] = pd.to_datetime(eventsByMonth[i]['Time'],format='%b %d %Y %I:%M %p')
                    cleanCsv.append(eventsByMonth[i])
                    i += 1
                except:
                    break
            eventsToAdd = [month for month in cleanCsv]
            eventsToAddDf = pd.concat(eventsToAdd)
            return eventsToAddDf
        else:
            return None

    def parseCsv(self,file,filename):
        '''
        Function to read the csv files of index scans and options attributes and insert it into the Postgres Database.
        file        -> (FileIO) fileio of opened csv file
        filename    -> (string) name of the csv file
        '''
        df = pd.read_csv(file,skiprows=3)
        self.csv_results = []
        self.csv_cols = []

        # Get Table Name and Scan Date
        tableNameStartIndex = filename.rindex('-')
        tableNameEndIndex = filename.rindex('.')
        scanDateStartIndex = filename.rindex('/')
        scanDate = filename[scanDateStartIndex+1:tableNameStartIndex]
        tableName = filename[tableNameStartIndex+1:tableNameEndIndex]
        tableName = tableName.replace('Scanner','')
        tableName = tableName.replace('Scan','')
        tableName += '_TdScan'
        self.tableNames.append(tableName)

        self.createTable(df,tableName,['"Updated" DATE default now()','"Scanned" DATE','"Added" DATE default now()' ])
        df["Updated"] = datetime.date.fromtimestamp(time.time())
        df["Scanned"] = datetime.datetime.strptime(scanDate,'%Y-%m-%d')
        df = self.cleanCsv(df)
        suc = self.execute_values(df,tableName)
        return suc

    def parseSectorCsv(self,file,filename):
        '''
        Function to read the csv files of sector scans and insert it into the Postgres Database.
        file        -> (FileIO) fileio of opened csv file
        filename    -> (string) name of the csv file
        '''
        df = pd.read_csv(file,skiprows=3)
        self.csv_results = []
        self.csv_cols = []

        # Get Table Name and Scan Date
        tableNameStartIndex = filename.rindex('-')
        tableNameEndIndex = filename.rindex('.')
        scanDateStartIndex = filename.rindex('/')
        scanDate = filename[scanDateStartIndex+1:tableNameStartIndex]
        sector = filename[tableNameStartIndex+1:tableNameEndIndex]

        tableName = "sectors_TdScan"
        self.tableNames.append(tableName)

        self.createTable(df,tableName,['"Updated" DATE default now()','"Scanned" DATE','"Added" DATE default now()' ])
        df["Updated"] = datetime.date.fromtimestamp(time.time())
        df["Scanned"] = datetime.datetime.strptime(scanDate,'%Y-%m-%d')
        df = self.cleanCsv(df,sector=sector)
        suc = self.execute_values(df,tableName)
        return suc
    
    def parseCalendarCsv(self,file,filename):
        '''
        Function to read the csv file of calendar events and insert it into the Postgres Database.
        file        -> (FileIO) fileio of opened csv file
        filename    -> (string) name of the csv file
        '''
        with open(file,'r') as calendarCsv:
            calendarStr = calendarCsv.read()
        calendarCsv.close()
        calendarArr = re.split(r"\n\w{1,20} \d{1,4}\nTime,Symbol,Event,Description\n",calendarStr)
        calendarLabels = re.findall(r"January \d{4}|February \d{4}|March \d{4}|April \d{4}|May \d{4}|June \d{4}|July \d{4}|August \d{4}|September \d{4}|October \d{4}|November \d{4}|December \d{4}",calendarStr)
        calendarArr = calendarArr[1:]
        eventsByMonth = []
        i = 0
        for month in calendarArr:
            year = calendarLabels[i][-4:]
            month = "Time,Symbol,Event,Description\n" + month
            month = StringIO(month)
            month = pd.read_csv(month)
            month['Time'] = month['Time'].str[:6] + f' {year} ' + month['Time'].str[7:]
            month['Time'] = month['Time'].str.replace('  ',' ')
            month['Time'] = month['Time'].str.replace(' 0:',' 12:')
            
            eventsByMonth.append(month)
            i += 1
            #if i > 12:
                #i = 0
                #year += 1
        '''# Eliminate Header at Top
        calendarStr = re.sub(r"ï»¿Calendar for  all events\n\n\w{1,20} \d{1,4}\nTime,Symbol,Event,Description\n","",calendarStr)
        # Eliminate Monthly Subheaders Top
        calendarStr = re.sub(r"\n\w{1,20} \d{1,4}\nTime,Symbol,Event,Description\n","",calendarStr)
        calendarStr = "Time,Symbol,Event,Description\n" + calendarStr
        df = StringIO(calendarStr)
        df = pd.read_csv(df)'''
        self.csv_results = []
        self.csv_cols = []

        # Get Table Name and Scan Date
        tableNameStartIndex = filename.rindex('-')
        tableNameEndIndex = filename.rindex('.')
        scanDateStartIndex = filename.rindex('/')
        scanDate = filename[scanDateStartIndex+1:tableNameStartIndex]
        sector = filename[tableNameStartIndex+1:tableNameEndIndex]

        tableName = "calendar_TdScan"
        self.tableNames.append(tableName)

        df = self.cleanCalendarCsv(eventsByMonth)
        df['Month'] = df['Time'].dt.month
        self.createTable(df,tableName,['"Updated" DATE default now()','"Scanned" DATE','"Added" DATE default now()' ],constraints='constraint uniqueEvents UNIQUE ("Time","Symbol","Description")')
        df["Updated"] = datetime.date.fromtimestamp(time.time())
        df["Scanned"] = datetime.datetime.strptime(scanDate,'%Y-%m-%d')
        suc = self.execute_values(df,tableName)
        return suc

def print_psycopg2_exception(err):
    '''
    Function that handles and parses psycopg2 exceptions
    '''
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()

    # get the line number when exception occured
    line_num = traceback.tb_lineno

    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_num)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)

    # psycopg2 extensions.Diagnostics object attribute
    print ("\nextensions.Diagnostics:", err.diag)

    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")