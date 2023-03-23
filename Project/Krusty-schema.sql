DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS storage;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS loadedPallets;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS loadingBills;
DROP TABLE IF EXISTS recipeItems;

CREATE TABLE ingredients(
    ingredientName TEXT,
    amount INT,
    unit TEXT,
    deliveryDate DATE,
    deliveryAmount INT,
    PRIMARY KEY (ingredientName)
);

CREATE TABLE storage(
    palletNumber INT,
    productionDate DATETIME,
    blocked BIT,
    recipeName TEXT,
    PRIMARY KEY (palletNumber),
    FOREIGN KEY (recipeName) REFERENCES recipes(recipeName)
);

CREATE TABLE orders(
    orderID INT,
    amount INT,
    deliveryDate DATE,
    deliveredDate DATE,
    customerName TEXT,
    recipeName TEXT,
    PRIMARY KEY (orderID),
    FOREIGN KEY (customerName) REFERENCES customers(customerName),
    FOREIGN KEY (recipeName) REFERENCES recipes(recipeName)
);

CREATE TABLE loadingBills(
    billID INT,
    PRIMARY KEY (billID)  
);

CREATE TABLE recipes(
    recipeName TEXT,
    PRIMARY KEY (recipeName)
);

CREATE TABLE loadedPallets(
    palletNumber INT,
    billID INT,
    orderID INT,
    PRIMARY KEY (palletNumber),
    FOREIGN KEY (billID) REFERENCES loadingBills(billID),
    FOREIGN KEY (orderID) REFERENCES orders(orderID)
);

CREATE TABLE customers(
    customerName    TEXT,
    address         TEXT,
    PRIMARY KEY (customerName)    
);

CREATE TABLE recipeItems(
    amount      FLOAT,
    recipeName  TEXT,
    ingredientName  TEXT,
    FOREIGN KEY (recipeName) REFERENCES recipes(recipeName),
    FOREIGN KEY (ingredientName) REFERENCES ingredients(ingredientName),
    PRIMARY KEY (recipeName, ingredientName)
);