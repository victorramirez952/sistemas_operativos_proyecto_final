const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 8080;


app.use(express.static(path.join(__dirname, 'public')));

// sendFile will go here
app.get('/', async(req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(8080, () => {
  console.log("Server successfully running on port 8080");
});