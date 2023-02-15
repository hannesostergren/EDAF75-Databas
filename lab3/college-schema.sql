DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS colleges;
DROP TABLE IF EXISTS students;

CREATE TABLE students(
  s_id        INTEGER,
  s_name      TEXT,
  gpa         REAL,
  size_hs     INT,
  PRIMARY KEY (s_id)
);

CREATE TABLE colleges(
  c_name      TEXT,
  state       TEXT,
  enrollment  INT,
  PRIMARY KEY (c_name)
);

CREATE TABLE applications(
  s_id        INTEGER,
  c_name      TEXT,
  major       TEXT,
  decision    CHAR(1) DEFAULT 'N',
  PRIMARY KEY (s_id, c_name, major),
  FOREIGN KEY (s_id) REFERENCES students(s_id),
  FOREIGN KEY (c_name) REFERENCES colleges(c_name)
);
