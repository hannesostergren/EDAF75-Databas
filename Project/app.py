
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
            palletNumber TEXT DEFAULT (lower(hex(randomblob(16)))),
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
            palletNumber TEXT,
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
    for op in create_operations:
        c.execute(op)
        
    # ingredient_trigger()
    c.executescript(
        """
        DROP TRIGGER IF EXISTS ingredient_amount_not_negative
        ;
        CREATE TRIGGER ingredient_amount_not_negative
        AFTER UPDATE ON ingredients
        BEGIN

        SELECT IIF(
            NEW.amount < 0, 
            RAISE (ROLLBACK, "negative ingredient amount"),
            ':)'
        );
        
        END
        ;
        """
    )
    c.executescript(
        """
        DROP TRIGGER IF EXISTS remove_ingredients_for_baking
        ;
        CREATE TRIGGER remove_ingredients_for_baking
        BEFORE INSERT ON storage
        BEGIN
            UPDATE ingredients
            SET amount = amount - (
                SELECT 54 * amount
                FROM recipeItems
                WHERE ingredients.ingredientName = recipeItems.ingredientName AND
                    recipeItems.recipeName = NEW.recipeName
            )
            WHERE ingredientName in (
                SELECT ingredientName
                FROM recipeItems
                WHERE recipeName = NEW.recipeName
            )
            ;
        END
        ;
        """
    )
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
        [customers['name'], customers['address']]
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
        SELECT ingredientName, amount, unit
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
    for item in cookies['recipe']:
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
    return { "location": "/cookies/" + cookieName } 

@get('/cookies')
def get_cookies():
    c = db.cursor()
    c.execute(
        """
        SELECT recipeName
        FROM recipes
        """
    )
    #found = [{"name" : recipeName, "pallets" : pallets} for recipeName, pallets in c]
    found = [{"name" : recipeName} for recipeName, in c]
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
    if not found :
        response.status = 404
        return {"data": []}
    response.status = 200
    return {"data": found}

@get('/pallets')
def get_pallets():
    c = db.cursor()
    query = """
        SELECT palletNumber, recipeName, productionDate, blocked
        FROM storage
        WHERE 1 = 1
        """
    params = []
    if request.query.cookie:
        query += " AND recipeName = ?"
        params.append(unquote(request.query.cookie))
    if request.query.after:
        query += " AND productionDate > ?"
        params.append(unquote(request.query.after))
    if request.query.before:
        query += " AND productionDate < ?"
        params.append(unquote(request.query.before))
    
    c.execute(query, params)
    found = [{"id": palletID, "cookie": recipeName, "productionDate": productionDate, "blocked": blocked} 
                        for palletID, recipeName, productionDate, blocked in c]
    db.commit()
    response.status = 200
    return {"data": found }


@post('/pallets')
def post_pallets():
    cookie = request.json
    c = db.cursor()
    # running out of ingredients is handled by a trigger that will 
    # rollback the transaction

    try:
        c.execute(
            """
            INSERT
            INTO storage(productionDate, blocked, recipeName)
            VALUES (DATE('now'), 0, ?)
            RETURNING palletNumber
            """,
            [cookie['cookie']]
        )
        found, = c.fetchone()
        db.commit()
    except sqlite3.IntegrityError:
        response.status = 422
        return { "location": "" } 
        
    response.status = 201
    palletURL = url_encode(found)
    return { "location": "/pallets/" + palletURL }

@post('/cookies/<recipeName>/block')
def post_block_cookie(recipeName):
    c = db.cursor()
    query = """
        UPDATE storage
        SET blocked = 1
        WHERE recipeName = ?
        """
    params = [recipeName]
    if request.query.before:
        query += " AND productionDate < ?"
        params.append(unquote(request.query.before))
    if request.query.after:
        query += " AND productionDate > ?"
        params.append(unquote(request.query.after))
    c.execute(query, params)
    db.commit()
    response.status = 205
    return {""}
    

@post('/cookies/<recipeName>/unblock')
def post_unblock_cookie(recipeName):
    c = db.cursor()
    recipeName = url_decode(recipeName)
    query = """
            UPDATE storage
            SET blocked = 0
            WHERE recipeName = ?
        """
    params = [recipeName]
    if request.query.before:
        query += " AND productionDate < ?"
        params.append(unquote(request.query.before))
    if request.query.after:
        query += " AND productionDate > ?"
        params.append(unquote(request.query.after))
    c.execute(query, params)
    db.commit()
    response.status = 205
    return {""}



run(host='localhost', port=PORT)