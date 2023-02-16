
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import unquote



db = sqlite3.connect("movies.sqlite")

c = db.cursor()

def get_tickets(username):
    c.execute(
        """
        SELECT date, start_time, th_name, m_name, p_year, count() OVER (PARTITION BY s_id)
        FROM tickets
        LEFT JOIN screenings USING (s_id)
        LEFT JOIN movies USING (imdb_key)
        """
    )
    found = [{"date": date, "startTime": start_time, "theater": th_name, "title": m_name, "year" : p_year, "nbrOfTickets" : nbrOfTickets}
            for date, start_time, th_name, m_name, p_year, nbrOfTickets in c]

    return {"data": found}

print(get_tickets("alice"))