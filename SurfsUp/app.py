# Import the dependencies.
from flask import Flask
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from sqlalchemy import desc

#################################################
# Database Setup
#################################################
#To figure out the first part used exercise 10.3.10
###Correctly generate the engine to the correct sqlite file (2 points)
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
###Use automap_base() and reflect the database schema (2 points)
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(bind=engine)
###
###tables = Base.classes.keys()
###print(tables)
#################################################
# Flask Setup
#################################################
climate_app = Flask(__name__)
#################################################
# Flask Routes
#################################################
###List all of the available routes, exercise 10.3.10
@climate_app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"The last 12 months of percipitation data:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"List of all stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"The last year of temperature data for the most active station:<br/>"
        f"/api/v1.0/tobs"
    )
#need to add the additional avilable routes above#############


#Route for the last 12 months of percipitation data with
#date as the key and prcp(precipitation) as the value
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@climate_app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of percipitation data"""
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    date_prcp = {}
    for date, prcp in results:
        date_prcp[date]=prcp
    return jsonify(date_prcp)

#Route for list of all stations
#Looked up how to return a list of all stations on stack overflow
@climate_app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Measurement.station).all()
    stations_list = [station.station for station in results]
    return jsonify(stations_list)

#Finding the most active station
#Code to find the most active station from the climate_starter jupyter notebook
most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(desc(func.count(Measurement.station))).first()
most_active_station = most_active_station[0]
#Route to the last year of temperature data for the most active station
@climate_app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(Measurement.date, Measurement.station, Measurement.tobs).filter(Measurement.date >= query_date, Measurement.station==most_active_station).all()
    tobs_list = [tobs.tobs for tobs in results]
    return jsonify(tobs_list)


###need to add to the end############
#make sure to change to TRUE
if __name__ == "__main__":
   climate_app.run(debug=False)   







