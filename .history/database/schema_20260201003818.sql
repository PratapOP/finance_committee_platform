CREATE DATABASE IF NOT EXISTS finance_committee;
USE finance_committee;

CREATE TABLE fc_members (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120),
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(200),
    role VARCHAR(50)
);

CREATE TABLE sponsors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150),
    industry VARCHAR(100),
    contact_person VARCHAR(120),
    email VARCHAR(120),
    phone VARCHAR(20),
    total_invested FLOAT,
    created_at DATETIME
);

CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150),
    date DATE,
    budget FLOAT,
    footfall INT,
    revenue FLOAT
);

CREATE TABLE sponsorships (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sponsor_id INT,
    event_id INT,
    amount FLOAT,
    status VARCHAR(50),
    roi FLOAT,
    FOREIGN KEY (sponsor_id) REFERENCES sponsors(id),
    FOREIGN KEY (event_id) REFERENCES events(id)
);
