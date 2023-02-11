PRAGMA foreign_keys = off;

DROP TABLE IF EXISTS Theater;
DROP TABLE IF EXISTS Screening;
DROP TABLE IF EXISTS Movie;
DROP TABLE IF EXISTS Ticket;
DROP TABLE IF EXISTS User;

PRAGMA foreign_keys = on;

CREATE TABLE Theater(
    Name TEXT NOT NULL,
    Capacity INT NOT NULL,
    PRIMARY KEY (Name)
);
CREATE TABLE Movie(
    Title VARCHAR(255) NOT NULL,
    Production_year DATE NOT NULL,
    IMDB_key VARCHAR(255) NOT NULL,
    Running_time TIME NOT NULL,
    PRIMARY KEY (IMDB_key)
);
CREATE TABLE Screening(
    IMDB_key VARCHAR(255),
    Screening_ID VARCHAR(255),
    Theater_name TEXT,
    Start_time DATETIME NOT NULL,
    Seats INT NOT NULL,
    FOREIGN KEY (IMDB_key) REFERENCES Movie(IMDB_key),
    FOREIGN KEY (Theater_name) REFERENCES Theater(Name)
    PRIMARY KEY (Screening_ID)
);
CREATE TABLE User(
    User_name VARCHAR(255) NOT NULL,
    Full_name VARCHAR(255) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    PRIMARY KEY (User_name)
);
CREATE TABLE Ticket(
    User_name VARCHAR(255),
    Screening_ID VARCHAR(255),
    Ticket_ID TEXT DEFAULT (lower(hex(randomblob(16)))),
    FOREIGN KEY (User_name) REFERENCES User(User_name),
    FOREIGN KEY (Screening_ID) REFERENCES Screening(Screening_ID),
    PRIMARY KEY (User_name, Ticket_ID)
);

BEGIN TRANSACTION;

INSERT OR REPLACE
INTO   Theater(Name, Capacity)
VALUES ('Kino der Toten', '200');

INSERT OR REPLACE
INTO   Movie(Title, Production_year, IMDB_key, Running_time)
VALUES  ('The House That Jack Built', '2018', 'tt4003440', '02:32:00'),
        ('Melancholia', '2011', 'tt1527186', '02:15:00'),
        ('Antichrist', '2009', 'tt0870984', '01:48:00'),
        ('Dogville', '2003', 'tt0276919', '02:58:00');

INSERT OR REPLACE
INTO   Screening(IMDB_key, Screening_ID, Theater_name, Start_time, Seats)
VALUES ('tt0870984', '1', 'Kino der Toten', '2023-02-14 19:00:00', '100');

INSERT OR REPLACE
INTO User(User_name, Full_name, Password)
VALUES  ('hannus', 'Hannes Östergren', 'password'),
        ('anotherUser', 'John Doe', 'seven');

INSERT OR REPLACE
INTO Ticket(User_name, Screening_ID)
VALUES ('hannus', '1');

END TRANSACTION;
