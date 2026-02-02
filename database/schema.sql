-- Finance Committee Platform Database Schema (MySQL Compatible)
-- Creates database and tables for MySQL

CREATE DATABASE IF NOT EXISTS finance_committee;
USE finance_committee;

-- Finance Committee Members Table
CREATE TABLE fc_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'finance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sponsors Table
CREATE TABLE sponsors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    contact_person VARCHAR(120),
    email VARCHAR(120),
    phone VARCHAR(20),
    total_invested DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Events Table
CREATE TABLE events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    date DATE NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    footfall INT DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sponsorships Table (Many-to-Many relationship)
CREATE TABLE sponsorships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sponsor_id INT NOT NULL,
    event_id INT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    roi DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sponsor_id) REFERENCES sponsors(id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX idx_sponsors_industry ON sponsors(industry);
CREATE INDEX idx_sponsors_total_invested ON sponsors(total_invested);
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_budget ON events(budget);
CREATE INDEX idx_sponsorships_status ON sponsorships(status);
CREATE INDEX idx_sponsorships_sponsor ON sponsorships(sponsor_id);
CREATE INDEX idx_sponsorships_event ON sponsorships(event_id);

-- Unique constraint for sponsor-event combinations
CREATE UNIQUE INDEX idx_unique_sponsorship ON sponsorships(sponsor_id, event_id);

-- Sample Data (Optional - remove for production)
INSERT INTO fc_members (name, email, password_hash, role) VALUES 
('Admin User', 'admin@fcommittee.com', 'pbkdf2:sha256:260000$salt$hash', 'admin'),
('Finance Lead', 'finance@fcommittee.com', 'pbkdf2:sha256:260000$salt$hash', 'finance');

INSERT INTO sponsors (name, industry, contact_person, email, phone) VALUES 
('TechCorp Solutions', 'Technology', 'John Smith', 'john@techcorp.com', '+1-555-0123'),
('Global Finance Inc', 'Finance', 'Sarah Johnson', 'sarah@gfinance.com', '+1-555-0124');

INSERT INTO events (name, date, budget, footfall, revenue) VALUES 
('Annual Tech Summit', '2024-03-15', 500000.00, 500, 750000.00),
('Finance Workshop', '2024-04-10', 250000.00, 100, 300000.00);