CREATE TABLE Pictures (id SERIAL PRIMARY KEY, name TEXT, data BYTEA, permission INTEGER, visible INTEGER);
CREATE TABLE Users (id SERIAL PRIMARY KEY, username TEXT, password TEXT,admin INTEGER, pic_id INTEGER, online INTEGER);
CREATE TABLE Topics (id SERIAL PRIMARY KEY, user_id INTEGER, topic TEXT, info TEXT, time TIMESTAMP, pic_id INTEGER, visits INTEGER, theme INTGER);
CREATE TABLE Messages (id SERIAL PRIMARY KEY, topic_id INTEGER, user_id INTEGER, content TEXT, pic_id INTEGER, time TIMESTAMP);
CREATE TABLE PrivateMessageUsers (id SERIAL PRIMARY KEY, user_id_1 INTEGER, user_id_2 INTEGER, UNIQUE(user_id_1, user_id_2));
CREATE TABLE PrivateMessages (id SERIAL PRIMARY KEY, private_room_id INTEGER, user_id INTEGER, content TEXT, pic_id INTEGER, time TIMESTAMP);
CREATE TABLE Visitors (id SERIAL PRIMARY KEY, ip_address TEXT, last_visit TIMESTAMP);
