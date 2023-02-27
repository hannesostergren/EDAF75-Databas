
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import unquote


PORT=7007


db = sqlite3.connect("movies.sqlite")

@get('/ping')
def ret_pong():
    return "pong\n"

@post('/reset')
def post_reset():
    c = db.cursor()
    operations = ["""PRAGMA foreign_keys=OFF""",
        """DROP TABLE IF EXISTS theaters""",
        """DROP TABLE IF EXISTS screenings""",
        """DROP TABLE IF EXISTS movies""",
        """DROP TABLE IF EXISTS tickets""",
        """DROP TABLE IF EXISTS users""",
        """PRAGMA foreign_keys=ON"""]
    
    for op in operations :
        c.execute(op)
    
    create_operations = [
        """CREATE TABLE theaters 	(
            th_name		TEXT,
            capacity	INTEGER,
            PRIMARY KEY 	(th_name)
        )""",

        """CREATE TABLE movies	(
            m_name		TEXT,
            p_year		INTEGER,
            imdb_key	TEXT,
            PRIMARY KEY 	(imdb_key)
        )""",

        """CREATE TABLE screenings	(
            start_time	TIME,
            date		DATE,
            s_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
            remaining_seats INT,
            imdb_key	TEXT,
            th_name		TEXT,

            PRIMARY KEY 	(s_id),
            FOREIGN KEY	(imdb_key) 	REFERENCES movies(imdb_key),
            FOREIGN KEY 	(th_name) 	REFERENCES theaters(th_name)
        )""",

        """CREATE TABLE tickets	(
            ti_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
        -- foreign keys:
            username	TEXT,
            s_id		TEXT,

            PRIMARY KEY	(ti_id),
            FOREIGN KEY 	(username) 	REFERENCES users(username),
            FOREIGN KEY	(s_id) 		REFERENCES screenings(s_id)
        )""",

        """CREATE TABLE users	(
            username	TEXT,
            fullName	TEXT,
            pwd         TEXT,
            PRIMARY KEY 	(username)
        )"""]
    for op in create_operations :
        c.execute(op)
        
    insert_operations = [
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Kino', '10');
        """,
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Regal', '16');
        """,
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Skandia', '100');
        """
    ]
    for op in insert_operations:
        c.execute(op)
    
    c.execute(
        """
        SELECT   *
        FROM     theaters
        """
    )
    db.commit()
    found = [{'name': th_name} for th_name in c]
    response.status = 200
    return {"data": found}
    #"Kino", 10 seats
    #"Regal", 16 seats
    #"Skandia", 100 seats

@get('/reset')
def get_reset():
    c = db.cursor()
    operations = ["""PRAGMA foreign_keys=OFF""",
        """DROP TABLE IF EXISTS theaters""",
        """DROP TABLE IF EXISTS screenings""",
        """DROP TABLE IF EXISTS movies""",
        """DROP TABLE IF EXISTS tickets""",
        """DROP TABLE IF EXISTS users""",
        """PRAGMA foreign_keys=ON"""]
    
    for op in operations :
        c.execute(op)

    create_operations = [
        """CREATE TABLE theaters 	(
            th_name		TEXT,
            capacity	INTEGER,
            PRIMARY KEY 	(th_name)
        )""",

        """CREATE TABLE movies	(
            m_name		TEXT,
            p_year		INTEGER,
            imdb_key	TEXT,
            PRIMARY KEY 	(imdb_key)
        )""",

        """CREATE TABLE screenings	(
            start_time	TIME,
            date		DATE,
            s_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
            remaining_seats INT,
            imdb_key	TEXT,
            th_name		TEXT,

            PRIMARY KEY 	(s_id),
            FOREIGN KEY	(imdb_key) 	REFERENCES movies(imdb_key),
            FOREIGN KEY 	(th_name) 	REFERENCES theaters(th_name)
        )""",

        """CREATE TABLE tickets	(
            ti_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
        -- foreign keys:
            username	TEXT,
            s_id		TEXT,

            PRIMARY KEY	(ti_id),
            FOREIGN KEY 	(username) 	REFERENCES users(username),
            FOREIGN KEY	(s_id) 		REFERENCES screenings(s_id)
        )""",

        """CREATE TABLE users	(
            username	TEXT,
            fullName	TEXT,
            pwd         TEXT,
            PRIMARY KEY 	(username)
        )"""]
    for op in create_operations :
        c.execute(op)
        
    insert_operations = [
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Kino', '10');
        """,
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Regal', '16');
        """,
        """
        INSERT OR REPLACE
        INTO   theaters(th_name, capacity)
        VALUES ('Skandia', '100');
        """
    ]
    for op in insert_operations:
        c.execute(op)
    
    c.execute(
        """
        SELECT   *
        FROM     theaters
        """
    )
    db.commit()
    found = [{'name': th_name} for th_name in c]
    response.status = 200
    return {"data": found}
    #"Kino", 10 seats
    #"Regal", 16 seats
    #"Skandia", 100 seats

@get('/theaters')
def get_theaters():
    c = db.cursor()
    c.execute(
        """
        SELECT *
        FROM theaters"""
    )
    found = [{"th_name" : th_name} for th_name in c]
    response.status = 200
    return {"data": found}

@get('/users')
def get_users():
    c = db.cursor()
    c.execute(
        """
        SELECT username, fullName
        FROM users
        """
    )
    found = [{"username" : username, "fullName" : full_name} for username, full_name in c]
    response.status = 200
    return {"data": found}

@get('/users/<username>/test')
def get_test(username):
    c = db.cursor()
    c.execute(
        """
        SELECT s_id
        FROM tickets
        """
    )
    found = [{"s_id": sid}
             for sid in c]
    response.status = 200
    return {"data": found}

@get('/users/<username>/tickets')
def get_users_tickets(username):
    c = db.cursor()
    c.execute(
        """
        SELECT date, start_time, th_name, m_name, p_year, count()
        FROM tickets
        LEFT JOIN screenings USING (s_id)
        LEFT JOIN movies USING (imdb_key)
        WHERE username = ?
        GROUP BY s_id
        """,
        [username]
    )
    found = [{"date": date, "startTime": start_time, "theater": th_name, "title": m_name, "year" : p_year, "nbrOfTickets" : nbrOfTickets}
             for date, start_time, th_name, m_name, p_year, nbrOfTickets in c]
    response.status = 200
    return {"data": found}
    

@get('/movies')
def get_movies():
    c = db.cursor()
    query = """
        SELECT imdb_key, m_name, p_year
        FROM movies
        WHERE 1 = 1
        """
    params = []
    if request.query.title:
        query += " AND m_name = ?"
        params.append(unquote(request.query.title))
    if request.query.year:
        query += " AND p_year = ?"
        params.append(request.query.year)
    # if request.query.imdbKey:
    #     query += " AND imdb_key = ?"
    #     params.append(unquote(request.query.imdbKey))
    c.execute(query, params)
    found = [{"imdbKey" : imdb_key, "title" : title, "year" : year} for imdb_key, title, year in c]
    response.status = 200
    return {"data" : found}

@get('/movies/<imdbKey>')
def get_movies_imdb(imdbKey):
    c = db.cursor()
    c.execute(
        """
        SELECT imdb_key, m_name, p_year
        FROM movies
        WHERE imdb_key = ?
        """,
        [imdbKey]
    )
    found = [{"imdbKey" : imdb_key, "title" : title, "year" : year} for imdb_key, title, year in c]
    response.status = 200
    return {"data" : found}

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute("""
        SELECT s_id, date, start_time, m_name, p_year, th_name, remaining_seats
        FROM screenings
        LEFT JOIN movies USING (imdb_key)
        """
    )
    found = [{"performanceId" : s_id, "date" : date, "startTime" : start_time, "title" : m_name, "year" : p_year, "theater" : th_name, "remainingSeats" : capacity}
             for s_id, date, start_time, m_name, p_year, th_name, capacity in c]
    response.status = 200
    return {"data" : found}


@post('/tickets')
def post_tickets():
    ticket = request.json
    c = db.cursor()
    # leta upp hashade lösen till användaren
    c.execute("""
        SELECT pwd
        FROM users
        WHERE username = ?
    """,
    [ticket['username']]
    )
    found_pwd, = c.fetchone()
    # kontrollera att angivet lösenord hashas till rätt värde
    if found_pwd == hash(ticket['pwd']):
        # leta upp spelningen
        c.execute(
            """
            SELECT s_id
            FROM screenings
            WHERE s_id = ?
            """,
            [ticket['performanceId']]
        )
        found = c.fetchone()
        if not found:
            response.status = 400
            return "No such performance"
        else:
            # testa att sänka remaining_seats med ett, OM det var större än 0 
            # vi kontrollerar under om en ändring faktiskt gjordes, 
            # annars fanns det inga platser kvar, och ingen ändring sker
            c.execute(
                """
                UPDATE screenings SET remaining_seats = remaining_seats - 1
                WHERE s_id = ? AND remaining_seats > 0
                RETURNING remaining_seats
                """,
                [ticket['performanceId']]
            )
            found = c.fetchone()
            if not found:
                response.status = 400
                return "No tickets left"
            db.commit()
            # skapa ticket
            c.execute(
                """
                INSERT
                INTO tickets(username, s_id)
                VALUES (?, ?)
                RETURNING ti_id
                """,
                [ticket['username'], ticket['performanceId']]
            )
            found = c.fetchone()
            if not found:
                response.status = 400
                return "Error"
            else:
                db.commit()
                response.status = 201
                ti_id, = found
                return f"/tickets/{ti_id}\n"
    else:
        response.status = 401
        return "Wrong user credentials"

@post('/users')
def post_users():
    users = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO users(username, fullName, pwd)
        VALUES (?, ?, ?)
        RETURNING username
        """,
        [users['username'], users['fullName'], hash(users['pwd'])]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return ""
    else:
        db.commit()
        response.status = 201
        username, = found
        return f"/users/{username}\n"

@post('/movies')
def post_movies():
    movie = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT OR IGNORE
        INTO       movies(m_name, p_year, imdb_key)
        VALUES     (?, ?, ?)
        RETURNING  imdb_key
        """,
        [movie['title'], movie['year'], movie['imdbKey']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return ""
    else:
        db.commit()
        response.status = 201
        imdb_key, = found
        return f"/movies/{imdb_key}\n"

@post('/performances')
def post_performance():
    performance = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT *
        FROM movies
        WHERE imdb_key = ?
        """,
        [performance['imdbKey']]
    )
    mv_found = c.fetchone()
    if not mv_found:
        response.status = 400
        return "No such movie or theater\n"
    
    c.execute(
        """
        SELECT capacity
        FROM theaters
        WHERE th_name = ?
        """,
        [performance['theater']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return "No such movie or theater\n"
    cap, = found
    c.execute(
        """
        INSERT
        INTO screenings(start_time, date, imdb_key, th_name, remaining_seats)
        VALUES (?, ?, ?, ?, ?)
        RETURNING s_id
        """,
        [performance['time'], performance['date'], performance['imdbKey'], performance['theater'], cap]
    )
    found = c.fetchone()
    db.commit()
    response.status = 201
    s_id, = found
    return f"/performances/{s_id}\n"

def hash(msg):
    import hashlib
    return hashlib.sha256(msg.encode('utf-8')).hexdigest()

@get('/students')
def get_students():
    query = """
        SELECT   s_id, s_name, gpa, size_hs
        FROM     students
        WHERE    1 = 1
        """
    params = []
    if request.query.name:
        query += " AND s_name = ?"
        params.append(unquote(request.query.name))
    if request.query.minGpa:
        query += " AND gpa >= ?"
        params.append(float(request.query.minGpa))
    c = db.cursor()
    c.execute(query, params)
    found = [{"id": s_id, "name": s_name, "gpa": gpa, "sizeHS": size_hs}
             for s_id, s_name, gpa, size_hs in c]
    response.status = 200
    return {"data": found}


@post('/students')
def post_student():
    student = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO       students(s_name, gpa, size_hs)
        VALUES     (?, ?, ?)
        RETURNING  s_id
        """,
        [student['name'], student['gpa'], student['sizeHS']]
    )
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Illegal..."
    else:
        db.commit()
        response.status = 201
        s_id, = found
        return f"http://localhost:{PORT}/{s_id}"


@get('/students/<s_id>/applications')
def get_student_applications(s_id):
    c = db.cursor()
    c.execute(
        """
        SELECT  s_id, c_name, major, decision
        FROM    applications
        JOIN    students
        USING   (s_id)
        WHERE   s_id = ?
        """,
        [s_id]
    )
    found = [{"id": s_id, "college": c_name, "major": major, "decision": decision}
             for s_id, c_name, major, decision in c]
    response.status = 200
    return {"data": found}


run(host='localhost', port=PORT)