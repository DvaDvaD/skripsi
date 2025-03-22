const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const swaggerUi = require('swagger-ui-express'); // Import swagger-ui-express
const YAML = require('yamljs'); // Import yamljs for loading YAML files

const app = express();
app.use(express.json());

// --- Load OpenAPI Spec ---
const openApiSpec = YAML.load('./openapi.yaml'); // Load the YAML file
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openApiSpec)); // Serve Swagger UI


// --- Database Setup --- (same as before)
const db = new sqlite3.Database('./mydatabase.db', (err) => {
  if (err) {
    console.error(err.message);
    throw err;
  }
  console.log('Connected to the SQLite database.');

  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)`, (err) => { if (err) { console.error(err); throw err; } });
    db.run(`CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))`, (err) => { if (err) { console.error(err); throw err; } });
  });
});

// --- Authentication --- (same as before)
const JWT_SECRET = 'your-very-secret-key'; // CHANGE IN PRODUCTION

function generateToken(user) {
  return jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
}

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (token == null) return res.sendStatus(401);
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
}

// --- User Registration --- (same as before)
app.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ message: 'Username and password are required.' });
    const hashedPassword = await bcrypt.hash(password, 10);
    db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashedPassword], function (err) {
      if (err) {
        if (err.message.includes('UNIQUE constraint failed')) return res.status(409).json({ message: 'Username already exists.' });
        console.error(err);
        return res.status(500).json({ message: 'Internal Server Error' });
      }
      res.status(201).json({ message: 'User registered successfully.', userId: this.lastID });
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

// --- User Login --- (same as before)
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ message: 'Username and password are required.' });
  db.get('SELECT * FROM users WHERE username = ?', [username], async (err, user) => {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    if (user && await bcrypt.compare(password, user.password)) {
      const token = generateToken(user);
      res.json({ token });
    } else {
      res.status(401).json({ message: 'Invalid credentials' });
    }
  });
});

// --- CRUD Operations (same as before) ---

// Create Item
app.post('/items', authenticateToken, (req, res) => {
  const { name, description } = req.body;
  if (!name) return res.status(400).json({ message: 'Name is required.' });
  db.run('INSERT INTO items (name, description, user_id) VALUES (?, ?, ?)', [name, description, req.user.id], function (err) {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    res.status(201).json({ message: 'Item created successfully', id: this.lastID });
  });
});

// Get All Items (for logged-in user)
app.get('/items', authenticateToken, (req, res) => {
  db.all('SELECT * FROM items WHERE user_id = ?', [req.user.id], (err, rows) => {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    res.json(rows);
  });
});

// Get Item by ID (check ownership)
app.get('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  db.get('SELECT * FROM items WHERE id = ? AND user_id = ?', [itemId, req.user.id], (err, row) => {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    if (!row) return res.status(404).json({ message: 'Item not found or you do not have permission.' });
    res.json(row);
  });
});

// Update Item (check ownership)
app.put('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  const { name, description } = req.body;
  if (!name) {  // Basic validation.  Could be more comprehensive.
    return res.status(400).json({ message: 'Name is required.' });
  }

  db.get('SELECT * FROM items WHERE id = ?', [itemId], (err, item) => {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    if (!item) return res.status(404).json({ message: 'Item not found.' });
    if (item.user_id !== req.user.id) return res.status(403).json({ message: 'You do not have permission.' });
    db.run('UPDATE items SET name = ?, description = ? WHERE id = ?', [name, description, itemId], function (err) {
      if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
      if (this.changes === 0) return res.status(404).json({ message: 'Item not found.' });
      res.json({ message: 'Item updated successfully' });
    });
  });
});

// Delete Item (check ownership)
app.delete('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  db.get('SELECT * FROM items WHERE id = ?', [itemId], (err, item) => {
    if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
    if (!item) return res.status(404).json({ message: 'Item not found.' });
    if (item.user_id !== req.user.id) return res.status(403).json({ message: 'You do not have permission.' });
    db.run('DELETE FROM items WHERE id = ?', [itemId], function (err) {
      if (err) { console.error(err); return res.status(500).json({ message: 'Internal Server Error' }); }
      if (this.changes === 0) return res.status(404).json({ message: 'Item not found.' });
      res.json({ message: 'Item deleted successfully' });
    });
  });
});



// --- Start the Server ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Swagger UI available at http://localhost:${PORT}/api-docs`); // Add this line
});