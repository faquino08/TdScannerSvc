import logging
import requests
from statistics import median_grouped
import sys
import datetime
import pytz
from os import path, environ
from urllib import request
import json
import argparse

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from flask import Flask, request, g
from flask_restful import Api
from flask_apscheduler import APScheduler

from constants import POSTGRES_LOCATION, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, DEBUG
from database import db

from DataBroker.tos_reader import tos_reader, sector_reader, calendar_reader

# Custom Convert
import werkzeug
from werkzeug.routing import PathConverter
from packaging import version

class EverythingConverter(PathConverter):
    regex = '.*?'

# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True

def create_app(db_location,debug=False):
    '''
    Function that creates our Flask application.
    This function creates the Flask app, Flask-Restful API,
    and Flask-SQLAlchemy connection
    db_location     -> Connection string to the database
    debug           -> Boolean of whether to log debug messages
    '''
    est = pytz.timezone('US/Eastern')
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
            handlers=[logging.FileHandler(f'./logs/tdScannerReader_{datetime.datetime.now(tz=est).date()}.txt'), logging.StreamHandler()],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            datefmt="%m-%d %H:%M",
            handlers=[logging.FileHandler(f'./logs/tdScannerReader_{datetime.datetime.now(tz=est).date()}.txt'), logging.StreamHandler()],
        )
    logger = logging.getLogger(__name__)
    app = Flask(__name__)
    app.config.from_object(Config())
    app.url_map.converters['everything'] = EverythingConverter
    app.config["SQLALCHEMY_DATABASE_URI"] = db_location
    if environ.get("FLASK_ENV") == "production":
        app.config["SERVER_NAME"] = "172.21.34.8:5000"
    db.init_app(app)
    # initialize scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    params = {
            "host": f'{POSTGRES_LOCATION}',
            "port": f'{POSTGRES_PORT}',
            "database": f'{POSTGRES_DB}',
            "user": f'{POSTGRES_USER}',
            "password": f'{POSTGRES_PASSWORD}'
        }

    @app.route('/run-tos-reader', methods=['POST'])
    def run_tos_reader():
        logger.info(request.args)
        #reminder_text = request.args['text']
        reminder_delay = int(request.args['delay'])
        addTos_Reader(scheduler, reminder_delay)
        return json.dumps({
        'status':'success',
        #'text': reminder_text,
        'delay': reminder_delay
        })

    @app.route('/run-sector-reader', methods=['POST'])
    def run_sector_reader():
        logger.info(request.args)
        #reminder_text = request.args['text']
        reminder_delay = int(request.args['delay'])
        if len(request.args['calcTdEquity']) == 0:
            calcTdEquity = False
        else:
            calcTdEquity = json.loads(request.args['calcTdEquity'].lower())
        addSector_Reader(scheduler, reminder_delay)
        logger.info(calcTdEquity)
        if calcTdEquity:
            requests.post('http://tdhistory-api:18080/runequityfreqtable?delay=120')
        return json.dumps({
        'status':'success',
        #'text': reminder_text,
        'delay': reminder_delay
        })

    @app.route('/run-calendar-reader', methods=['POST'])
    def run_calendar_reader():
        logger.info(request.args)
        #reminder_text = request.args['text']
        reminder_delay = int(request.args['delay'])
        addCalendar_Reader(scheduler, reminder_delay)
        return json.dumps({
        'status':'success',
        #'text': reminder_text,
        'delay': reminder_delay
        })

    scheduler.start()
    return app

def addTos_Reader(scheduler, delay):
    '''
    Add workflow for reading csv files of index scans and options attributes to AP Scheduler.
    scheduler   -> APScheduler Object
    delay       -> (int) Second to wait before running flow
    '''
    logger = logging.getLogger(__name__)
    scheduled_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    job_id = 'tos_reader'
    scheduler.add_job(id=job_id,func=tos_reader, trigger='date',\
        run_date=scheduled_time)
    logger.info('Tos Reader Job Added')

def addSector_Reader(scheduler, delay):
    '''
    Add workflow for reading csv files of sector scans to AP Scheduler.
    scheduler   -> APScheduler Object
    delay       -> (int) Second to wait before running flow
    '''
    logger = logging.getLogger(__name__)
    scheduled_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    job_id = 'sector_reader'
    scheduler.add_job(id=job_id,func=sector_reader, trigger='date',\
        run_date=scheduled_time)
    logger.info('Sector Reader Job Added')

def addCalendar_Reader(scheduler, delay):
    '''
    Add workflow for reading csv file of calendar scan to AP Scheduler.
    scheduler   -> APScheduler Object
    delay       -> (int) Second to wait before running flow
    '''
    logger = logging.getLogger(__name__)
    scheduled_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
    job_id = 'calendar_reader'
    scheduler.add_job(id=job_id,func=calendar_reader, trigger='date',\
        run_date=scheduled_time)
    logger.info('Calendar Reader Job Added')

app = create_app(f"postgresql://{POSTGRES_LOCATION}/{POSTGRES_DB}",DEBUG)