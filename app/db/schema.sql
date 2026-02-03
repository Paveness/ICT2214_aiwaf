-- Disable FK checks so we can drop tables in any order
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS neurowaf_db;
USE neurowaf_db;

-- ==========================================
-- 1. USERS TABLE
-- Stores analyst accounts
-- ==========================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'analyst',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. WAF INSTANCES TABLE
-- Allows a user to manage multiple protected sites
-- ==========================================
DROP TABLE IF EXISTS waf_instances;
CREATE TABLE waf_instances (
    waf_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    target_host VARCHAR(255) NOT NULL,
    proxy_port INT DEFAULT 8000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==========================================
-- 3. CRAWLER SETTINGS TABLE
-- AI Crawler configuration per WAF instance
-- ==========================================
DROP TABLE IF EXISTS crawler_settings;
CREATE TABLE crawler_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    waf_id INT NOT NULL,
    login_endpoint VARCHAR(255),
    login_payload TEXT,
    excluded_endpoints TEXT,
    last_crawled DATETIME NULL,
    FOREIGN KEY (waf_id) REFERENCES waf_instances(waf_id) ON DELETE CASCADE
);

-- ==========================================
-- 4. EVENT LOGS TABLE
-- Using the 2-column JSON structure you requested
-- ==========================================
DROP TABLE IF EXISTS event_logs;
CREATE TABLE event_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    raw_log JSON NOT NULL
);

-- ==========================================
-- 5. MOCK DATA (Optional - to get you started)
-- ==========================================
-- Admin User
INSERT INTO users (username, password_hash, role) 
VALUES ('Admin', '$2b$10$YourHashedPasswordHere...', 'admin');

-- WAF Instance for Admin
INSERT INTO waf_instances (user_id, target_host, proxy_port)
VALUES (1, 'http://localhost:3000', 8000);