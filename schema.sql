CREATE TABLE Pictures (id SERIAL PRIMARY KEY, name TEXT, data BYTEA, permission INTEGER);
CREATE TABLE Users (id SERIAL PRIMARY KEY, username TEXT, password TEXT,admin TEXT, pic_id INTEGER REFERENCES Pictures);
CREATE TABLE Topics (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES Users, topic TEXT, info TEXT, time TIMESTAMP);
CREATE TABLE Messages (id SERIAL PRIMARY KEY, topic_id INTEGER REFERENCES Topics, user_id INTEGER REFERENCES Users, content TEXT, pic_id INTEGER REFERENCES Pictures, time TIMESTAMP);
CREATE TABLE PrivateMessageUsers (id SERIAL PRIMARY KEY, user_id_1 INTEGER REFERENCES Users, user_id_2 INTEGER REFERENCES Users, UNIQUE(user_id_1, user_id_2));
CREATE TABLE PrivateMessages (id SERIAL PRIMARY KEY, private_room_id INTEGER REFERENCES PrivateMessageUsers, user_id INTEGER REFERENCES Users, content TEXT, pic_id INTEGER REFERENCES Pictures, time TIMESTAMP);
CREATE TABLE Visitors (id SERIAL PRIMARY KEY, ip_address TEXT, last_visit TIMESTAMP);
