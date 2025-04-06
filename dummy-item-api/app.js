const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const morgan = require('morgan'); // <--- Import morgan

const app = express();

// --- Middleware Setup ---
app.use(express.json()); // For parsing application/json

// --- Request Logging Middleware (using morgan) ---
// Use the 'dev' format for concise output suitable for development, includes method, URL, status, response time.
// Other common formats: 'tiny', 'short', 'common', 'combined'
app.use(morgan('dev')); // <--- Add morgan middleware here

// --- Load OpenAPI Spec ---
try {
  const openApiSpec = YAML.load('./openapi.yaml'); // Load the YAML file
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openApiSpec)); // Serve Swagger UI
} catch (e) {
  console.error("Failed to load or parse openapi.yaml:", e);
  // Decide how to handle this - maybe exit or serve without docs
}


// --- Database Setup ---
const db = new sqlite3.Database('./mydatabase.db', (err) => {
  if (err) {
    console.error("Database Connection Error:", err.message);
    // Consider exiting the process if the DB connection fails critically
    process.exit(1);
  }
  console.log('Connected to the SQLite database.');

  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL)`, (err) => {
      if (err) { console.error("Error creating users table:", err); throw err; }
      console.log("Users table checked/created.");
    });
    db.run(`CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))`, (err) => {
      if (err) { console.error("Error creating items table:", err); throw err; }
      console.log("Items table checked/created.");
    });
  });
});

// --- Authentication ---
// IMPORTANT: Use environment variables for secrets in production!
const JWT_SECRET = process.env.JWT_SECRET || 'your-very-secret-key'; // CHANGE IN PRODUCTION

function generateToken(user) {
  // Include only necessary, non-sensitive information
  return jwt.sign({ id: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
}

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Format: "Bearer TOKEN"

  if (token == null) {
    console.log('Auth failed: No token provided');
    return res.status(401).json({ message: 'Authentication token required.' }); // Unauthorized
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      console.log('Auth failed: Invalid/Expired token', err.message);
      // Differentiate between expired and invalid tokens if needed
      if (err.name === 'TokenExpiredError') {
        return res.status(401).json({ message: 'Token expired.' }); // Still 401, but specific message
      }
      return res.status(403).json({ message: 'Invalid token.' }); // Forbidden
    }
    // Attach user payload to the request object
    req.user = user;
    next(); // Proceed to the next middleware or route handler
  });
}

// --- User Registration ---
app.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Basic validation
    if (!username || typeof username !== 'string' || username.length < 3) {
      return res.status(400).json({ message: 'Username is required (string, min 3 chars).' });
    }
    if (!password || typeof password !== 'string' || password.length < 6) {
      return res.status(400).json({ message: 'Password is required (string, min 6 chars).' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, hashedPassword], function (err) {
      if (err) {
        // Handle specific errors
        if (err.message.includes('UNIQUE constraint failed')) {
          return res.status(409).json({ message: 'Username already exists.' }); // Conflict
        }
        // Log the generic error for server-side debugging
        console.error("Registration DB error:", err);
        return res.status(500).json({ message: 'Internal Server Error during registration.' });
      }
      // Return limited success information
      res.status(201).json({ message: 'User registered successfully.', userId: this.lastID });
    });
  } catch (error) {
    console.error("Registration unexpected error:", error);
    res.status(500).json({ message: 'Internal Server Error during registration.' });
  }
});

// --- User Login ---
app.post('/login', (req, res) => {
  const { username, password } = req.body;

  // Validation
  if (!username || typeof username !== 'string' || !password || typeof password !== 'string') {
    return res.status(400).json({ message: 'Username and password are required and must be strings.' });
  }

  db.get('SELECT * FROM users WHERE username = ?', [username], async (err, user) => {
    if (err) {
      console.error("Login DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error during login.' });
    }

    // Check if user exists and password is correct
    if (user && await bcrypt.compare(password, user.password)) {
      // User authenticated successfully
      const token = generateToken(user);
      res.json({ token }); // Send the JWT back to the client
    } else {
      // Authentication failed (user not found or password incorrect)
      // Use a generic message to avoid revealing which part was wrong
      res.status(401).json({ message: 'Invalid credentials.' }); // Unauthorized
    }
  });
});

// --- CRUD Operations for Items ---

// Create Item
app.post('/items', authenticateToken, (req, res) => {
  const { name, description } = req.body; // Description is optional

  // Validate required fields
  if (!name || typeof name !== 'string' || name.trim() === '') {
    return res.status(400).json({ message: 'Item name is required and cannot be empty.' });
  }
  // Optional: Validate description type if provided
  if (description && typeof description !== 'string') {
     return res.status(400).json({ message: 'Item description must be a string.' });
  }

  const userId = req.user.id; // Get user ID from the authenticated token payload

  db.run('INSERT INTO items (name, description, user_id) VALUES (?, ?, ?)', [name.trim(), description, userId], function (err) {
    if (err) {
      console.error("Create item DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error creating item.' });
    }
    // Respond with success and the ID of the newly created item
    res.status(201).json({ message: 'Item created successfully', id: this.lastID });
  });
});

// Get All Items (for the logged-in user)
app.get('/items', authenticateToken, (req, res) => {
  const userId = req.user.id;

  db.all('SELECT id, name, description FROM items WHERE user_id = ?', [userId], (err, rows) => { // Select specific columns
    if (err) {
      console.error("Get all items DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error fetching items.' });
    }
    res.json(rows); // Send the list of items
  });
});

// Get Specific Item by ID (check ownership)
app.get('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  const userId = req.user.id;

  // Validate item ID format (basic check)
  if (!/^\d+$/.test(itemId)) {
    return res.status(400).json({ message: 'Invalid item ID format.' });
  }

  db.get('SELECT id, name, description FROM items WHERE id = ? AND user_id = ?', [itemId, userId], (err, row) => {
    if (err) {
      console.error("Get item by ID DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error fetching item.' });
    }
    if (!row) {
      // Item not found OR belongs to another user - give a 404 for security
      return res.status(404).json({ message: 'Item not found or access denied.' });
    }
    res.json(row); // Send the specific item details
  });
});

// Update Item (check ownership)
app.put('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  const userId = req.user.id;
  const { name, description } = req.body;

  // Validate item ID format
  if (!/^\d+$/.test(itemId)) {
    return res.status(400).json({ message: 'Invalid item ID format.' });
  }
  // Validate input data
  if (!name || typeof name !== 'string' || name.trim() === '') {
    return res.status(400).json({ message: 'Item name is required and cannot be empty.' });
  }
   if (description && typeof description !== 'string') {
     return res.status(400).json({ message: 'Item description must be a string.' });
  }

  // Check ownership before attempting update for efficiency and security
  db.get('SELECT user_id FROM items WHERE id = ?', [itemId], (err, item) => {
    if (err) {
      console.error("Update item (check) DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error checking item ownership.' });
    }
    if (!item) {
      return res.status(404).json({ message: 'Item not found.' });
    }
    if (item.user_id !== userId) {
      // User does not own this item
      return res.status(403).json({ message: 'Forbidden: You do not have permission to update this item.' });
    }

    // If ownership confirmed, proceed with the update
    db.run('UPDATE items SET name = ?, description = ? WHERE id = ?', [name.trim(), description, itemId], function (err) {
      if (err) {
        console.error("Update item DB error:", err);
        return res.status(500).json({ message: 'Internal Server Error updating item.' });
      }
      // `this.changes` tells us if any rows were actually updated
      if (this.changes === 0) {
         // This case might be redundant due to the ownership check, but good practice
         return res.status(404).json({ message: 'Item not found (or no changes needed).' });
      }
      res.json({ message: 'Item updated successfully' });
    });
  });
});

// Delete Item (check ownership)
app.delete('/items/:id', authenticateToken, (req, res) => {
  const itemId = req.params.id;
  const userId = req.user.id;

  // Validate item ID format
  if (!/^\d+$/.test(itemId)) {
    return res.status(400).json({ message: 'Invalid item ID format.' });
  }

  // Check ownership first
  db.get('SELECT user_id FROM items WHERE id = ?', [itemId], (err, item) => {
    if (err) {
      console.error("Delete item (check) DB error:", err);
      return res.status(500).json({ message: 'Internal Server Error checking item ownership.' });
    }
    if (!item) {
      return res.status(404).json({ message: 'Item not found.' });
    }
    if (item.user_id !== userId) {
      return res.status(403).json({ message: 'Forbidden: You do not have permission to delete this item.' });
    }

    // If ownership confirmed, proceed with deletion
    db.run('DELETE FROM items WHERE id = ?', [itemId], function (err) {
      if (err) {
        console.error("Delete item DB error:", err);
        return res.status(500).json({ message: 'Internal Server Error deleting item.' });
      }
      if (this.changes === 0) {
        // Redundant check, but safe
        return res.status(404).json({ message: 'Item not found.' });
      }
      res.json({ message: 'Item deleted successfully' }); // Or send status 204 No Content
      // res.status(204).send();
    });
  });
});


// --- Global Error Handler (Optional but Recommended) ---
// Catches errors passed via next(err)
app.use((err, req, res, next) => {
  console.error("Unhandled Error:", err.stack || err);
  res.status(err.status || 500).json({
     message: err.message || 'Internal Server Error',
     // Optionally include stack trace in development
     ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});


// --- Start the Server ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  // Log Swagger UI URL only if it was successfully loaded
  if (app.get('//api-docs')) { // Check if the route was added
     console.log(`Swagger UI available at http://localhost:${PORT}/api-docs`);
  } else {
     console.log("Swagger UI endpoint not available (check openapi.yaml).");
  }
});

// --- Graceful Shutdown (Optional but Recommended) ---
process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing SQLite database connection.');
  db.close((err) => {
    if (err) {
      console.error("Error closing database:", err.message);
    } else {
      console.log('Database connection closed.');
    }
    process.exit(err ? 1 : 0);
  });
});