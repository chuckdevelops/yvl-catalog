const express = require('express');
const path = require('path');
const app = express();
const PORT = 4173;

// Serve static files from the dist directory
app.use(express.static(path.join(__dirname, 'dist')));

// Fallback to index.html for SPA routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`You can also try http://127.0.0.1:${PORT}`);
});