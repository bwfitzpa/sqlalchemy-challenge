# Import the dependencies.
from flask import Flask
from flask import Flask, jsonify
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from sqlalchemy import desc

#################################################
# Database Setup
#################################################
#To figure out the database setud used code from exercise 10.3.10
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
climate_app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#List all of the available routes
@climate_app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"The last 12 months of percipitation data:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of all stations:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"The last year of temperature data for the most active station:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"To return the min, max, and average temperatures from your given start<br/>" 
        f"date to the end date of the available data add your date to the given route,<br/>"
        f"date must be entered in the format yyyy-mm-dd<br/>"
        f"date must be within dataset range of 2010-01-01 to 2017-08-23, route:<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"To return the min, max, and average temperatures from your given start<br/>" 
        f"date to your give end date add your date and start to the given route,<br/>"
        f"including a slash(/) between start date and end date, format:/api/v1.0/<start>yyyy-mm-dd/yyyy-mm-dd,<br/>"
        f"where start date is first and end date is second,"
        f"date must be within dataset range of 2010-01-01 to 2017-08-23, route:<br/>"
        f"/api/v1.0/<start><br/><br/>"
    )

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
@climate_app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    results = session.query(Measurement.station).group_by(Measurement.station)
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

#Route that accepts a given start date as a parameter from the URL and then returns
#the min, max, and average temperatures calculated from the start date to the end date of the dataset
@climate_app.route("/api/v1.0/<start>")
def start_date(start):
    """Fetch the min, max, and average temperatures calculated from the 
       user given start date to the end date of the dataset, or a 404 if not."""
    #looked up the datetime conversion on stack overflow
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    tobs_start = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start).all()
    if not tobs_start or start_date<dt.date(2010, 1, 1):
        return jsonify({"error": f"Date {start} not found, check date format and that date is within the date range of the dataset."}), 404
    date_tobs_start_df = pd.DataFrame(tobs_start, columns=['date', 'temperature'])
    tmin = date_tobs_start_df['temperature'].min()
    tmax = date_tobs_start_df['temperature'].max()
    tavg = date_tobs_start_df['temperature'].mean()
    return jsonify({"min_temperature": tmin,
                    "max_temperature": tmax,
                    "average_temp": tavg})

#Route that accepts a user given start date and a user given end date as parameters from the URL and then returns
#the min, max, and average temperatures calculated from the start date to the end date
@climate_app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Fetch the min, max, and average temperatures calculated from the 
       user given start date to the user given end date, or a 404 if not."""
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
    tobs_start_end = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= start, Measurement.date <= end).all()
    if start_date > end_date:
        return jsonify({"error": f"The start date must be before the end date"}), 404
    if start_date<dt.date(2010, 1, 1) or end_date>dt.date(2017, 8, 23):
        return jsonify({"error": f"Dates must be between 2010-01-01 and 2017-08-23"}), 404
    if not tobs_start_end:
        return jsonify({"error": f"Date {start} and/or date {end} not found, check date format and that date is within the date range of the dataset."}), 404
    date_tobs_start_end_df = pd.DataFrame(tobs_start_end, columns=['date', 'temperature'])
    tmin = date_tobs_start_end_df['temperature'].min()
    tmax = date_tobs_start_end_df['temperature'].max()
    tavg = date_tobs_start_end_df['temperature'].mean()
    return jsonify({"min_temperature": tmin,
                    "max_temperature": tmax,
                    "average_temp": tavg})

if __name__ == "__main__":
   climate_app.run(debug=False)   

