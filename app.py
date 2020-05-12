# This python script uses flask and SQLAlchemy to simulate API requests of weather data of Honolulu, HI.

# Import Dependencies
# NumPy 
import numpy as np

# SQLAlchemy - create engine, automap, Session and aggregating function modules
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Flask
from flask import Flask, jsonify

# DateTime
import datetime

#Setup the SQLite database
# Create engine
engine = create_engine("sqlite:///data/hawaii.sqlite")

# Reflect database and tables
Base = automap_base()
Base.prepare(engine, reflect = True)

# Save table references
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)

#Setup Flask
app = Flask(__name__)

# Create a function that gets minimum, average, and maximum temperatures for a range of dates
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


# Set Flask Routes
@app.route("/")
def main():
    print(f"Welcome to the Honolulu Weather Data API. The available endpoints are given below:" )
    #List all available routes.
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Return a JSON representation of a dictionary where the date is the key and the value is the precipitation value
    session = Session(bind=engine)

    print("Received request for precipitation data.")

    # To find precipitation data for the last year, we first find the last date in the database
    final_date_query = session.query(func.max(func.strftime(f"%Y-%m-%d", Measurement.date))).all()

    max_date_string = final_date_query[0][0]

    max_date = datetime.datetime.strptime(max_date_string, f"%Y-%m-%d")

    # Then we set the beginning of our search query
    begin_date = max_date - datetime.timedelta(366)

    # Find dates and precipitation amounts
    precip_data = session.query(func.strftime(f"%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime(f"%Y-%m-%d", Measurement.date) >= begin_date).all()
    
    # Prepare the dictionary with the date as the key and the prcp value as the value
    results_dict = {}
    for result in precip_data:
        results_dict[result[0]] = result[1]
    
    session.close()

    return jsonify(results_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    # Return a list of stations
    print("Received request for station data.")
    session = Session(bind=engine)

    # Query the list of Stations
    stations_data = session.query(Station).all()

    # Create a list of dictionaries
    stations_list = []
    for station in stations_data:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)
    
    session.close()

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
   # Return a JSON list of temperature observations for the previous year.
    print("Received request for temperature data.")
    session = Session(bind=engine)
    
    # To find temperature data for the last year, we first find the last date in the database
    final_date_query = session.query(func.max(func.strftime(f"%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = datetime.datetime.strptime(max_date_string, f"%Y-%m-%d")

    # Set beginning of search query
    begin_date = max_date - datetime.timedelta(366)

    # Get temperature measurements for last year
    results = session.query(Measurement).\
        filter(func.strftime(f"%Y-%m-%d", Measurement.date) >= begin_date).all()

    # Create list of dictionaries (one for each observation)
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)
    
    session.close()

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    # Return a JSON list of the minimum, average, and maximum temperatures from start date to last date in the database.
    print("Received request for temperature data for a particular start date")
    session = Session(bind=engine)

    # First we find the last date in the database
    final_date_query = session.query(func.max(func.strftime(f"%Y-%m-%d", Measurement.date))).all()
    max_date = final_date_query[0][0]

    # Get the temperatures
    temps = calc_temps(start, max_date)

    # Create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': max_date}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})

    session.close()

    return jsonify(return_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Return a JSON list of the minimum, average, and maximum temperatures from start date to end date
    print("Received request for temperature data for a period of time.")
    session = Session(bind=engine)
    
    # Get the temperatures
    temps = calc_temps(start, end)

    # Create a list
    return_list = []
    date_dict = {'start_date': start, 'end_date': end}
    return_list.append(date_dict)
    return_list.append({'Observation': 'TMIN', 'Temperature': temps[0][0]})
    return_list.append({'Observation': 'TAVG', 'Temperature': temps[0][1]})
    return_list.append({'Observation': 'TMAX', 'Temperature': temps[0][2]})
   
    session.close()
    
    return jsonify(return_list)
    
# Code to actually run the app
if __name__ == "__main__":
    app.run(debug = True)