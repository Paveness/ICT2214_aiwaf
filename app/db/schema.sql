-- database/schema.sql

-- 1. Create the database safely
CREATE DATABASE IF NOT EXISTS NeuroWAF_db;
USE NeuroWAF_db;

-- 2. Create the Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Store only bcrypt hashes!
    role VARCHAR(20) DEFAULT 'analyst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. (Optional) Insert a default Admin user for testing
-- The password hash below corresponds to 'password123'
-- Generated using bcrypt with 10 salt rounds.
INSERT IGNORE INTO users (username, password_hash, role) 
VALUES ('Admin', '$2b$10$w/X5sQ/..somerandomhashstring...', 'admin');



CREATE DATABASE IF NOT EXISTS NeuroWAF_db;
USE NeuroWAF_db;
CREATE TABLE event_logs (
  request_id CHAR(36) NOT NULL,
  log JSON NOT NULL,
  PRIMARY KEY (request_id)
);