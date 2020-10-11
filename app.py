#import things 
from flask import Flask, jsonify

import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session  
from sqlalchemy import create_engine, func  

#SET UP THE DATABASE

#create engine
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement 
Station = Base.classes.station

#FLASK SET UP 

app = Flask(__name__)

#FLASK ROUTES
@app.route("/")
def home():
    return (
        f'<h1>Welcome to Climate Analysis!</h1><br/>'
        f'Available Routes:<br/>'
        f'Precipitation: /api/v1.0/precipitation<br/>'
        f'Stations: /api/v1.0/stations<br/>'
        f'Temperature Observations: /api/v1.0/tobs<br/>'
        f'/api/v1.0/<start><br/>'
        f'/api/v1.0/<start>/<end><br/>'
    )
# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    'retrieving results for dates & precipitation values'
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precps = []
    for result in results:
        column = {}
        column['date'] = result.date
        column['prcp'] = result.prcp
        precps.append(column)
    return jsonify(precps)

# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    'retrieving results for stations'
    # create session
    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    session.close()

    all_stations = []
    for result in results:
        column = {}
        column['station'] = result.station
        column['name'] = result.name
        all_stations.append(column)
    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
@app.route('/api/v1.0/tobs')
def temp():
    'retrieving results for temp observations for the last year from the most active station'
    # create session
    session = Session(engine)

    #get the last year info 
    last_date_in_df = session.query(Measurement.date).order_by(Measurement.date.desc()).first[0] 
    last_date_in_df = dt.date(2017, 8, 23)
    yr_from_last = last_date_in_df - dt.timedelta(days=365)

    #get the most active station
    most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    #filter out the data for the last year in df from the station USC00519281
    results = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date > yr_from_last).filter(Measurement.station == 'USC00519281').all()

    session.close()

    tobs = []
    for result in results:
        column = {}
        column["tobs"] = result.tobs
        column["date"] = result.date
        tobs.append(column)

    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)

