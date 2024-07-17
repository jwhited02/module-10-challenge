# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine(f"sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data including the date and precipitation value."""
    # Calculate the date one year from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query for the previous 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)


    # Query all stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations."""

    results = session.query(Station.station).all()

    session.close()

    # Convert the query results to a list of dictionaries
    stations = list(np.ravel(results))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations (TOBS) for the previous year."""
    
    # Calculate the date one year from the last date in the dataset
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= one_year_ago).all()

    session.close()
 
    # Convert the query results to a list
    tobs_data = list(np.ravel(results))
    return jsonify(tobs=tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # 'start' parameter is captured from the URL and passed to this function
    print(f"Received start date: {start}")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range."""
    try:
        # Convert start parameter to date object
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400

    # Query the minimum, average, and maximum temperatures for dates greater than or equal to the start date
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temps = list(np.ravel(results))

    return jsonify({
        "start_date": start,
        "min_temp": temps[0],
        "avg_temp": temps[1],
        "max_temp": temps[2]
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # 'start' and 'end' parameters are captured from the URL and passed to this function
    print(f"Received start date: {start} and end date: {end}")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range."""
    try:
        # Convert start and end parameters to date objects
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date format should be YYYY-MM-DD"}), 400

    # Query the minimum, average, and maximum temperatures for dates between the start and end date inclusive
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    # Convert the query results to a list of dictionaries
    temps = list(np.ravel(results))

    return jsonify({
        "start_date": start,
        "end_date": end,
        "min_temp": temps[0],
        "avg_temp": temps[1],
        "max_temp": temps[2]
    })

if __name__ == "__main__":
    app.run(debug=True)

