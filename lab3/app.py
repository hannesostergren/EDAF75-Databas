
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import unquote


PORT=7007


db = sqlite3.connect("movies.sqlite")

@get('/ping')
def ret_pong():
    return "pong\n"

@get('/reset')
def get_reset():
    c = db.cursor()
    operations = ["""DROP TABLE IF EXISTS theaters""",
        """DROP TABLE IF EXISTS screenings""",
        """DROP TABLE IF EXISTS movies""",
        """DROP TABLE IF EXISTS tickets""",
        """DROP TABLE IF EXISTS customers"""]
    
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
            duration	INTEGER,
            PRIMARY KEY 	(imdb_key)
        )""",

        """CREATE TABLE screenings	(
            start_time	TIME,
            date		DATE,
            s_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
        -- foreign keys:
            imdb_key	TEXT,
            th_name		TEXT,

            PRIMARY KEY 	(s_id),
            FOREIGN KEY	(imdb_key) 	REFERENCES movies(imdb_key),
            FOREIGN KEY 	(th_name) 	REFERENCES theatres(th_name)
        )""",

        """CREATE TABLE tickets	(
            ti_id		TEXT DEFAULT (lower(hex(randomblob(16)))),
        -- foreign keys:
            username	TEXT,
            s_id		TEXT,

            PRIMARY KEY	(ti_id),
            FOREIGN KEY 	(username) 	REFERENCES customers(username),
            FOREIGN KEY	(s_id) 		REFERENCES screenings(s_id)
        )""",

        """CREATE TABLE customers	(
            username	TEXT,
            password	TEXT,
            full_name	TEXT,
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
    found = [{'name': th_name} for th_name in c]
    response.status = 200
    return {"data": found}
    #"Kino", 10 seats
    #"Regal", 16 seats
    #"Skandia", 100 seats

@get('/users')
def get_users(s_id):
    c = db.cursor()
    c.execute(
        """
        SELECT   s_id, s_name, gpa, size_hs
        FROM     students
        WHERE    s_id = ?
        """,
        [s_id]
    )
    found = [{"id": s_id, "name": s_name, "gpa": gpa, "sizeHS": size_hs}
             for s_id, s_name, gpa, size_hs in c]
    response.status = 200
    return {"data": found}


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