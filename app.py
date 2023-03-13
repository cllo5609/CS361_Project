# Author: Clinton Lohr

"""
This program is used to run and gather data from other services. It is used to gather weather data by calling a weather
API. Requests are made in the form of a text file and returned to a user using another text file. Input for this
program is in the form of a string and must be as follows: "city name (required), state abbreviation, country code,
units of measurement". The returned weather data is filtered to only include necessary information before being
returned to the user in the form of a string.
"""

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import gmaps
import time

# read map API key from text file and store as a variable
file = open("map_api_key.txt", "r")
api_key = file.readline()
gmaps.configure(api_key=api_key)

# set up Flask architecture and SQL database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)


class UserEntry(db.Model):
    """
    This class is used to create new entries by the user for their user experience data.
    """

    id = db.Column(db.Integer, primary_key=True)                    # random ID attributed to entry
    location = db.Column(db.String(100), nullable=False)            # mountain visited
    visited = db.Column(db.Integer, default=0)                      # count of times visited
    ranking = db.Column(db.Integer, default=0)                      # ranking of visited mountain
    content = db.Column(db.String(50), nullable=True)               # additional comments
    date_created = db.Column(db.DateTime, default=datetime.utcnow)  # date created, used to keep order of entries

    def __repr__(self):
        """
        represents class of objects as a string.
        """

        return '<Entry %r>' % self.id


# routes to homepage of application
@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Renders the homepage
    :return: renders the homepage template
    """
    return render_template('index.html')


# routes to "results" page of application
@app.route('/results', methods=['GET', 'POST'])
def results():
    """
    This function is responsible for getting the information from the get request form, parsing the data into variables
    and calling the weather microservice and wikipedia microservice.
    :return: rendered "results" page template
    """

    if request.method == 'GET':
        # gather form data
        ski_info = request.args.get('resort')

        # default entry if no information is provided
        if ski_info is None or ski_info == "Get Info":
            resort = "Arapahoe Basin"
            location = "Silverthorne"
            wiki_search = "Arapahoe Basin"

        # separates valid input into descriptive variables
        else:
            resort, location, wiki_search = ski_info.split(",")

        # call weather microservice
        weather_data = weather_service(location)

        # call Wikipedia microservice
        wiki_data = wiki_service(wiki_search)

        return render_template('results.html', data=weather_data, resort=resort, info=wiki_data)


def weather_service(location):
    """
    This function is used to write data from a request to a text file, calls the weather microservice, and reads
    the response from the weather microservice text file.
    :param location: represents the location to gather weather
    :return: parsed weather data in the form of a string
    """

    # write request information
    f = open("weather_request.txt", "w")
    f.write(location)
    f.close()
    time.sleep(1)

    # read response information
    f = open("weather_response.txt", "r")
    weather_data = f.readline()
    weather_data = weather_data.split(',')

    return weather_data


def wiki_service(wiki_search):
    """
    This function is used to write data from a request to a text file, calls the Wikipedia scraper microservice, and
    reads the response from the weather microservice text file.
    :param wiki_search: represents the ski area we wish to do a Wikipedia search on
    :return: parsed Wikipedia data in the form of a string
    """

    # write request information
    wiki_data = []
    f = open("request.txt", "w")
    f.write(wiki_search)
    f.close()
    time.sleep(1)

    # read response information
    f = open("response.txt", "r")
    info_lines = f.readlines()
    info_len = len(info_lines)

    # separates data from "/n" in text file
    for i in range(info_len):
        wiki_response_data = info_lines[i]
        new_data = wiki_response_data.split("\n")
        wiki_data.append(new_data)

    return wiki_data

# routes to "resorts" page of application
@app.route('/resorts', methods=['GET', 'POST'])
def resorts():
    """
    This function is responsible for the resorts page. Handles POST requests if a user wishes to store experience data
    in the database. If no post request is made, the "resorts" page is rendered.
    :return: renders "resorts" template
    """

    # if new entry is being made
    if request.method == "POST":
        mountain = request.form["mountain"]
        visits = request.form["visits"]
        rank = request.form["rank"]
        content = request.form["content"]

        new_entry = UserEntry(location=mountain, visited=visits, ranking=rank, content=content)

        # attempts to add the new entry to the database.

        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect("resorts")

        # error message if new entry was not added to the database
        except:
            return "Something went wrong. Please re-enter you entry."

    # renders "resorts" page if no POST request is made
    else:
        entries = UserEntry.query.order_by(UserEntry.date_created).all()
        return render_template('resorts.html', entries=entries)


# delete function for database entries
@app.route('/delete/<int:id>')
def delete(id):
    """
    Handles deleting user base entries
    :param id: represents the ID number of an entry
    :return: redirects to "resorts" template
    """

    entry_to_delete = UserEntry.query.get_or_404(id)

    # attempts to delete database entry
    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect("/resorts")

    # error message if database entry was not deleted
    except:
        return "Error: Unable to delete entry"

# routes to the "edit" page and "resorts" page of the application
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    """
    This function is used to edit database entries. Gets updated data results from user and updates database entry.
    :param id: represents the ID number of an entry
    :return: redirects to "resorts" template
    """

    # gets the requested entry from the database
    entry = UserEntry.query.get_or_404(id)

    # runs if user has updated data and made a POST request to update the database
    if request.method == "POST":
        entry.location = request.form["mountain"]
        entry.visited = request.form["visits"]
        entry.ranking = request.form["rank"]
        entry.content = request.form["content"]

        # attempts to commit updated results to the database
        try:
            db.session.commit()
            return redirect("/resorts")

        # error message if data was not updated
        except:
            return "Error: Unable to update entry"

    # renders the "edit_user_data" template
    else:
        return render_template("edit_user_data.html", entry=entry)

# routes to "faq" page of application
@app.route('/faq')
def faq():
    """
    Renders the "faq" template
    :return: rendered "faq" template
    """

    return render_template('faq.html')


if __name__ == "__main__":
    app.run(debug=True)
