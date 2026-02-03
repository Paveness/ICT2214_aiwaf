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

// 4. GET LOGS (With Search, Pagination & Advanced Time Filtering)
app.get('/api/logs', (req, res) => {
  const { 
    search, attack_type, limit = 20, page = 1, 
    time_mode = 'preset', // 'preset', 'before', 'after', 'between'
    time_preset,          // '5m', '24h', etc.
    start_date,           // 'YYYY-MM-DD HH:MM:SS'
    end_date              // 'YYYY-MM-DD HH:MM:SS'
  } = req.query;

  const offset = (page - 1) * limit;
  const params = [];
  let whereClause = "WHERE 1=1";

  // --- TIME FILTER LOGIC ---
  if (time_mode === 'preset' && time_preset && time_preset !== 'all') {
    let interval = "24 HOUR";
    switch (time_preset) {
      case '5m': interval = "5 MINUTE"; break;
      case '30m': interval = "30 MINUTE"; break;
      case '1h': interval = "1 HOUR"; break;
      case '24h': interval = "24 HOUR"; break;
      case '7d': interval = "7 DAY"; break;
      case '30d': interval = "30 DAY"; break;
      case '1y': interval = "1 YEAR"; break;
    }
    whereClause += ` AND timestamp >= DATE_SUB(NOW(), INTERVAL ${interval})`;
  } 
  else if (time_mode === 'before' && end_date) {
    whereClause += " AND timestamp <= ?";
    params.push(end_date);
  }
  else if (time_mode === 'after' && start_date) {
    whereClause += " AND timestamp >= ?";
    params.push(start_date);
  }
  else if (time_mode === 'between' && start_date && end_date) {
    whereClause += " AND timestamp BETWEEN ? AND ?";
    params.push(start_date, end_date);
  }

  // --- OTHER FILTERS ---
  if (search) {
    whereClause += " AND (source_ip LIKE ? OR request_path LIKE ?)";
    params.push(`%${search}%`, `%${search}%`);
  }
  
  if (attack_type && attack_type !== 'All') {
    whereClause += " AND attack_type = ?";
    params.push(attack_type);
  }

  // Query 1: Get Total Count
  const countSql = `SELECT COUNT(*) as total FROM event_logs ${whereClause}`;
  
  db.query(countSql, params, (err, countResult) => {
    if (err) return res.status(500).json({ error: "Database error" });
    
    const totalLogs = countResult[0].total;
    const totalPages = Math.ceil(totalLogs / limit);

    // Query 2: Get Data
    const dataSql = `SELECT * FROM event_logs ${whereClause} ORDER BY timestamp DESC LIMIT ? OFFSET ?`;
    const dataParams = [...params, parseInt(limit), parseInt(offset)];

    db.query(dataSql, dataParams, (err, results) => {
      if (err) return res.status(500).json({ error: "Database error" });
      res.json({
        logs: results,
        pagination: {
          current_page: parseInt(page),
          total_pages: totalPages,
          total_logs: totalLogs
        }
      });
    });
  });
});

// 5. GET FILTER OPTIONS (Dynamic Attack Types)
app.get('/api/filters', (req, res) => {
  // 'DISTINCT' ensures we don't get duplicates (e.g. 100 'XSS' rows -> just 1 'XSS' result)
  const sql = "SELECT DISTINCT attack_type FROM event_logs ORDER BY attack_type ASC";
  
  db.query(sql, (err, results) => {
    if (err) {
      console.error(err);
      return res.status(500).json({ error: "Database error" });
    }
    // Transform the result from [{attack_type: 'XSS'}, {attack_type: 'SQLi'}] 
    // to a simple list: ['XSS', 'SQLi']
    const types = results.map(row => row.attack_type);
    res.json(types);
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});