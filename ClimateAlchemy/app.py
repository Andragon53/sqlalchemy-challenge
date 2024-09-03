# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
stations = Base.classes.station
measurements = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List available api routes."""
    return (
        f"Welcome to the AP Vacation Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/ (start-date) <br/>"
        f"/api/v1.0/ (start-date) / (end-date) <br/>"
        f"[ format dates as YYYY-MM-DD, with zero-number padding if necessary ] "
    )

@app.route("/api/v1.0/precipitation")
def precipData():
    """Return JSON data of the last year's precipitation records."""
    precipQuery = session.query(measurements.date, measurements.prcp).filter(measurements.date >= '2016-08-23').all()
    
    # add all rows of the query to list, formatted as {date: prcp}
    precipRecords = []
    for date, prcp in precipQuery:
        new_entry = {}
        new_entry[date] = prcp
        precipRecords.append(new_entry)

    return jsonify(precipRecords)

@app.route("/api/v1.0/stations")
def stationPing():
    """Return a JSON list of the stations."""

    stationQuery = session.query(stations.station).distinct().all()
    allStations = list(np.ravel(stationQuery))
    return jsonify(allStations)

@app.route("/api/v1.0/tobs")
def tempData():
    """Return JSON data of the last year's temperature records from the most active station."""
    tempQuery = session.query(measurements.date, measurements.tobs).\
    filter(stations.station == measurements.station).\
    filter(stations.station == 'USC00519281').\
    filter(measurements.date >= '2016-08-23').all()

    # add all rows of the query to list, formatted as {date: tobs}
    tempRecords = []
    for date, tobs in tempQuery:
        new_entry = {}
        new_entry[date] = tobs
        tempRecords.append(new_entry)

    return jsonify(tempRecords)

@app.route("/api/v1.0/<start>")
def openTempStats(start):
    """Return JSON data of the max, min, and average temperature from the period of time starting at the specified date."""

    fixStart = start.replace(" ", "")
    statFromDateQuery = session.query(func.min(measurements.tobs), func.max(measurements.tobs), func.avg(measurements.tobs)).\
    filter(stations.station == measurements.station).\
    filter(measurements.date >= fixStart).all()

    # add the query's results to a list for jsonify
    statsDisplay = []
    for min, max, avg in statFromDateQuery:
        statsDisplay.append(min)
        statsDisplay.append(max)
        statsDisplay.append(avg)
    
    return jsonify(statsDisplay)

@app.route("/api/v1.0/<start>/<end>")
def closedTempStats(start, end):
    """Return JSON data of the max, min, and average temperature from the period of time starting at the first specified date, and ending at the other specified date."""

    fixStart = start.replace(" ", "")
    fixEnd = end.replace(" ", "")
    statPeriodQuery = session.query(func.min(measurements.tobs), func.max(measurements.tobs), func.avg(measurements.tobs)).\
    filter(stations.station == measurements.station).\
    filter(measurements.date >= fixStart).\
    filter(measurements.date <= fixEnd).all()
    
    # add the query's results to a list for jsonify
    statsDisplay = []
    for min, max, avg in statPeriodQuery:
        statsDisplay.append(min)
        statsDisplay.append(max)
        statsDisplay.append(avg)
    
    return jsonify(statsDisplay)



if __name__ == "__main__":
    app.run(debug=True)
