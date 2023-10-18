from DataBroker.Sources.TosScannerReader.tosScannerReader import tosScannerReader
from constants import POSTGRES_LOCATION, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, APP_NAME

def tos_reader():
    '''
    Wrapper function to run the workflow for reading csv files of index scans and options attributes.
    '''
    scansReader = tosScannerReader(postgresParams={
            "host": f'{POSTGRES_LOCATION}',
            "port": f'{POSTGRES_PORT}',
            "database": f'{POSTGRES_DB}',
            "user": f'{POSTGRES_USER}',
            "password": f'{POSTGRES_PASSWORD}',
            "application_name": f'{APP_NAME}TosReader'
        },debug=True)
    scansReader.getNewScannerEntries()
    scansReader.exit()

def sector_reader():
    '''
    Wrapper function to run the workflow for reading csv files of sector scans.
    '''
    scansReader = tosScannerReader(postgresParams={
            "host": f'{POSTGRES_LOCATION}',
            "port": f'{POSTGRES_PORT}',
            "database": f'{POSTGRES_DB}',
            "user": f'{POSTGRES_USER}',
            "password": f'{POSTGRES_PASSWORD}',
            "application_name": f'{APP_NAME}SectorReader'
        },debug=True)
    scansReader.getNewSectorEntries()
    scansReader.exit()

def calendar_reader():
    '''
    Wrapper function to run the workflow for reading csv files of sector scans.
    '''
    scansReader = tosScannerReader(postgresParams={
            "host": f'{POSTGRES_LOCATION}',
            "port": f'{POSTGRES_PORT}',
            "database": f'{POSTGRES_DB}',
            "user": f'{POSTGRES_USER}',
            "password": f'{POSTGRES_PASSWORD}',
            "application_name": f'{APP_NAME}SectorReader'
        },debug=True)
    scansReader.getNewCalendarEntries()
    scansReader.exit()