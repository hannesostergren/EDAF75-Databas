
from bottle import get, post, run, request, response
import sqlite3
from urllib.parse import quote, unquote


PORT=8888

db = sqlite3.connect("database.db")

def url_decode(url_text):
    return unquote(url_text)

def url_encode(text):
    return quote(text)

@get('/ping')
def ret_pong():
    return "pong\n"

@post('/reset')
def post_reset():
    c = db.cursor()
    operations = ["""PRAGMA foreign_keys=OFF""",
        """DROP TABLE IF EXISTS ingredients""",
        """DROP TABLE IF EXISTS recipes""",
        """DROP TABLE IF EXISTS recipeItems""",
        """DROP TABLE IF EXISTS storage""",
        """DROP TABLE IF EXISTS orders""",
        """DROP TABLE IF EXISTS loadedPallets""",
        """DROP TABLE IF EXISTS customers""",
        """DROP TABLE IF EXISTS loadingBills""",
        """PRAGMA foreign_keys=ON"""]
    
    for op in operations :
        c.execute(op)
    
    create_operations = [
        """CREATE TABLE ingredients(
            ingredientName TEXT,
            amount INT,
            unit TEXT,
            deliveryDate DATE,
            deliveryAmount INT,
            PRIMARY KEY (ingredientName)
        )""",  

        """CREATE TABLE storage(
            palletNumber INT,
            productionDate DATETIME,
            blocked BIT,
            recipeName TEXT,
            PRIMARY KEY (palletNumber),
            FOREIGN KEY (recipeName) REFERENCES recipes(recipeName)
        )""",

        """CREATE TABLE orders(
            orderID INT,
            amount INT,
            deliveryDate DATE,
            deliveredDate DATE,
            customerName TEXT,
            recipeName TEXT,
            PRIMARY KEY (orderID),
            FOREIGN KEY (customerName) REFERENCES customers(customerName),
            FOREIGN KEY (recipeName) REFERENCES recipes(recipeName)   
        )""",

        """CREATE TABLE loadingBills(
            billID INT,
            PRIMARY KEY (billID)  
        )""",

        """CREATE TABLE recipes(
            recipeName TEXT,
            PRIMARY KEY (recipeName)
        )""",

        """CREATE TABLE loadedPallets(
            palletNumber INT,
            billID INT,
            orderID INT,
            PRIMARY KEY (palletNumber),
            FOREIGN KEY (billID) REFERENCES loadingBills(billID),
            FOREIGN KEY (orderID) REFERENCES orders(orderID)
        )""",

        """CREATE TABLE customers(
            customerName    TEXT,
            address         TEXT,
            PRIMARY KEY (customerName)    
        )""",

        """CREATE TABLE recipeItems(
            amount      FLOAT,
            recipeName  TEXT,
            ingredientName  TEXT,
            FOREIGN KEY (recipeName) REFERENCES recipes(recipeName),
            FOREIGN KEY (ingredientName) REFERENCES ingredients(ingredientName),
            PRIMARY KEY (recipeName, ingredientName)
        )"""
       ]
    for op in create_operations :
        c.execute(op)
        

    db.commit()
    response.status = 205
    return { "location": "/" }



@post('/customers')
def post_customers():
    customers = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO customers(customerName, address)
        VALUES (?, ?)
        RETURNING customerName
        """,
        [customers['customerName'], customers['address']]
    )
    found, = c.fetchone()
    db.commit()
    response.status = 201
    encodedCustomerName = url_encode(found)
    return { "location": "/customers/" + encodedCustomerName } 
        
@get('/customers')
def get_customers():
    c = db.cursor()
    c.execute(
        """ SELECT *
            FROM customers
        """
    )

    found = [{"customerName" : customerName, "address" : address} for customerName, address in c]
    response.status = 200
    return {"data": found}
    


@post('/ingredients')
def post_ingredients():
    ingredients = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO ingredients(ingredientName, amount, unit, deliveryDate, deliveryAmount)
        VALUES (?, 0, ?, '1970-01-01', 0)
        RETURNING ingredientName
        """,
        [ingredients['ingredient'], ingredients['unit']]
    )
    found, = c.fetchone()
    db.commit()
    response.status = 201
    encodedIngredientName = url_encode(found)
    return { "location": "/ingredients/" + encodedIngredientName } 

@post('/ingredients/<ingredientName>/deliveries')
def post_ingredient_delivery(ingredientName):
    ingredients = request.json
    ingredientName = url_decode(ingredientName)
    c = db.cursor()
    c.execute(
        """
        UPDATE ingredients
        SET amount = amount + ?,
            deliveryDate = ?,
            deliveryAmount = ?
        WHERE ingredientName = ?
        RETURNING ingredientName, amount, unit
        """,
        [ingredients['quantity'], ingredients['deliveryTime'], ingredients['quantity'], ingredientName]
    )
    found = c.fetchone()
    print(found)
    db.commit()
    response.status = 201
    result = {"ingredient" : found[0], "quantity" : found[1], "unit" : found[2]}
    
    return { "data": result} 


@get('/ingredients')
def get_ing():
    c = db.cursor()
    c.execute(
        """
        SELECT *
        FROM ingredients"""
    )
    found = [{"ingredient" : ingredient, "quantity" : quantity, "unit" : unit} for ingredient, quantity, unit in c]
    response.status = 200
    return {"data": found}

@post('/cookies')
def post_cookies():
    cookies = request.json
    c = db.cursor()
    # lägg till kakan
    c.execute(
            """
            INSERT
            INTO recipes(recipeName)
            VALUES (?)
            """,
            [cookies['name']]
        )
    # lägg till kakans recept
    for item in cookies['recipe'] :
        c.execute(
            """
            INSERT
            INTO recipeItems(recipeName, ingredientName, amount)
            VALUES (?, ?, ?) 
            RETURNING recipeName
            """,
            [cookies['name'], item['ingredient'], item['amount']]
        )
    found, = c.fetchone()
    db.commit()
    response.status = 201
    cookieName = url_encode(found)
    return { "location": "/customers/" + cookieName } 

@get('/cookies')
def get_cookies():
    c = db.cursor()
    c.execute(
        """ SELECT recipeName
            FROM recipes
        """
    )
    found = [{"name" : recipeName} for recipeName in c]
    response.status = 200
    return {"data": found}

@get('/cookies/<recipeName>/recipe')
def get_cookie_recipe(recipeName):
    c = db.cursor()
    recipeName = url_decode(recipeName)
    c.execute(
        """
        SELECT ingredientName, recipeItems.amount, unit
        FROM recipeItems 
            JOIN recipes USING (recipeName)
            JOIN ingredients USING (ingredientName)
        WHERE recipeName = ?
        """,
        [recipeName]
    )
    found = [{"ingredient": ingredientName, "amount":amount, "unit":unit} 
                        for ingredientName, amount, unit in c]
    response.status = 200
    return {"data": found}
# TODO: handle if no cookie found

@post('/cookies/<recipeName>/block')
def post_block_cookie(recipeName):
     c = db.cursor
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

@post('/cookies/<recipeName>/unblock')

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