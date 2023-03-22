DELETE FROM ingredients;
DELETE FROM storage;
DELETE FROM recipes;
DELETE FROM orders;
DELETE FROM loadedPallets;
DELETE FROM customers;
DELETE FROM loadingBills;
DELETE FROM recipeItems;

INSERT INTO ingredients(ingredientName, amount, unit, deliveryDate, deliveryAmount)
VALUES  ('Flour', 1000, 'g', 2021-01-01, 1000),
        ('Butter', 10000, 'g', 2023-03-16, 5000);
        

INSERT INTO recipes(recipeName)
VALUES 
        ("Nut ring"),
        ("Nut cookie"),
        ("Amneris"),
        ("Tango"),
        ("Almond delight"),
        ("Berliner")

INSERT INTO recipeItems(recipeName, ingredientName, amount)
VALUES
        ("Nut ring", "Flour",                   450),
        ("Nut ring", "Butter",                  450),
        ("Nut ring", "Icing sugar",             190),
        ("Nut ring", "Roasted, chopped nuts",   225),

        ("Nut cookie", "Fine-ground nuts",      750),
        ("Nut cookie", "Ground, roasted nuts",  625),
        ("Nut cookie", "Bread crumbs",          125),
        ("Nut cookie", "Sugar",                 375),
        ("Nut cookie", "Egg whites",            3.5),
        ("Nut cookie", "Chocolate",             50),

        ("Amneris", "Marzipan",                 750),
        ("Amneris", "Butter",                   250),
        ("Amneris", "Eggs",                     250),
        ("Amneris", "Potato starch",            25),
        ("Amneris", "Wheat flour",              25),

        ("Tango", "Butter",                     200),
        ("Tango", "Sugar",                      250),
        ("Tango", "Flour",                      300),
        ("Tango", "Sodium bicarbonate",         4),
        ("Tango", "Vanilla",                    2),

        ("Almond delight", "Butter",            400),
        ("Almond delight", "Sugar",             270),
        ("Almond delight", "Chopped almonds",   279),
        ("Almond delight", "Flour",             400),
        ("Almond delight", "Cinnamon",          10),

        ("Berliner", "Flour",                   350),
        ("Berliner", "Butter",                  250),
        ("Berliner", "Icing sugar",             100),
        ("Berliner", "Eggs",                    50),
        ("Berliner", "Vanilla sugar",           5),
        ("Berliner", "Chocolate",               50)

