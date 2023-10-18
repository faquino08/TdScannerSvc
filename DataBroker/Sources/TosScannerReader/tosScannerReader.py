import logging
import inspect
import time
from datetime import date, datetime

from DataBroker.Sources.TosScannerReader.database import databaseHandler

class tosScannerReader:
    def __init__(self,postgresParams={},debug=False):
        '''
        Class to read csv files received in folder and inserting the information into Postgres databses.
        postgresParams  -> (dict) Dict with keys host, port, database, user, \
                            password for Postgres database
        debug           -> (boolean) Whether to record debug logs
        '''
        if debug:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                    datefmt="%m-%d %H:%M:%S"
                )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                datefmt="%m-%d %H:%M:%S"
            )
        self.log = logging.getLogger(__name__)
        self.postgres = postgresParams

        # Connect to Postgres
        self.db = databaseHandler(self.postgres)
        self.startTime = time.time()
        caller = inspect.stack()[1][3].upper()
        
        # Create New Run in RunHistory
        self.db.cur.execute('''
            INSERT INTO PUBLIC.financedb_RUNHISTORY ("Process","Startime","SymbolsToFetch") VALUES ('%s','%s',0) RETURNING "Id";
        ''' % (caller,self.startTime))
        self.runId = self.db.cur.fetchone()[0]
        self.db.conn.commit()

        self.log.info(f'')
        self.log.info(f'')
        self.log.info(f'')
        self.log.info(f'ThinkorSwim Scanner')
        self.log.info(f'Starting Run at: {self.startTime}')

    def getNewScannerEntries(self):
        '''
        Wrapper function to get csv files of index scans and options attributes in the FTP Server receiving folder.
        '''
        startTime = time.time()
        self.log.info('')
        self.log.info(f'Getting Scan Files from Think or Swim Software')
        self.log.info(f'Start: {startTime}')
        self.db.getNewScannerEntries()

    def getNewSectorEntries(self):
        '''
        Wrapper function to get csv files of sector scans and in the FTP Server receiving folder.
        '''
        startTime = time.time()
        self.log.info('')
        self.log.info(f'Getting Sector Files from Think or Swim Software')
        self.log.info(f'Start: {startTime}')
        self.db.getNewSectorEntries()

    def getNewCalendarEntries(self):
        '''
        Wrapper function to get csv file of calendar scans and in the FTP Server receiving folder.
        '''
        startTime = time.time()
        self.log.info('')
        self.log.info(f'Getting Sector Files from Think or Swim Software')
        self.log.info(f'Start: {startTime}')
        self.db.getNewCalendarEntries()

    def exit(self):
        '''
        Exit class. Log Runtime. And close database handler.
        '''
        self.endTime = time.time()

        # Update RunHistory With EndTime
        self.db.cur.execute('''
            UPDATE PUBLIC.financedb_RUNHISTORY
            SET "Endtime"=%s,
                "SymbolsInsert"=0
            WHERE "Id"=%s
        ''' % (self.endTime,self.runId))
        self.db.conn.commit()

        self.log.info(f'Ending Run at: {self.endTime}')
        self.log.info(f'Runtime: {self.endTime-self.startTime}')
        self.db.exit()    