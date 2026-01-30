require('dotenv').config();
const express = require('express');
const mysql = require('mysql2');
const bcrypt = require('bcrypt');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// 1. Database Connection
const db = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT || 3306,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Test the connection when server starts
db.getConnection((err, connection) => {
  if (err) {
    console.error('❌ Database connection failed:', err.message);
  } else {
    console.log('✅ Connected to MySQL Database');
    connection.release();
  }
});

// 2. REGISTRATION ENDPOINT
app.post('/api/register', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: "Username and password are required" });
  }

  try {
    // Hash the password (Security Best Practice)
    const salt = await bcrypt.genSalt(10);
    const hash = await bcrypt.hash(password, salt);

    const sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)";
    db.query(sql, [username, hash], (err, result) => {
      if (err) {
        if (err.code === 'ER_DUP_ENTRY') {
           return res.status(400).json({ error: "Username already exists" });
        }
        return res.status(500).json({ error: "Database error" });
      }
      res.status(201).json({ message: "User registered successfully" });
    });
  } catch (error) {
    res.status(500).json({ error: "Encryption error" });
  }
});

// 3. LOGIN ENDPOINT
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;

  const sql = "SELECT * FROM users WHERE username = ?";
  db.query(sql, [username], async (err, results) => {
    if (err) return res.status(500).json({ error: "Database error" });
    
    // User not found
    if (results.length === 0) {
      return res.status(401).json({ error: "Invalid credentials" });
    }

    const user = results[0];

    // Compare the provided password with the stored hash
    const isMatch = await bcrypt.compare(password, user.password_hash);

    if (isMatch) {
      // Send back safe user info (exclude password)
      res.json({ 
        id: user.id, 
        username: user.username, 
        role: user.role 
      });
    } else {
      res.status(401).json({ error: "Invalid credentials" });
    }
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});