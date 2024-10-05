require('dotenv').config();
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { Groq } = require('groq-sdk');

const app = express();
app.use(express.json());

const client = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

// Authentication
const SECRET_KEY = "your-secret-key";
const ALGORITHM = "HS256";
const ACCESS_TOKEN_EXPIRE_MINUTES = 30;

// Function to create access token
function createAccessToken(data, expiresIn = '15m') {
  return jwt.sign(data, SECRET_KEY, { expiresIn });
}

// Authentication endpoint
app.post("/token", async (req, res) => {
  const { username, password } = req.body;
  const user = await authenticateUser(username, password);
  if (!user) {
    return res.status(401).json({ detail: "Incorrect username or password" });
  }
  const accessToken = createAccessToken({ sub: user.username, role: user.role });
  res.json({ access_token: accessToken, token_type: "bearer" });
});

// Include routers for different actors
const doctorRouter = require('./routers/doctor');
const patientRouter = require('./routers/patient');
const labRouter = require('./routers/lab');
const systemRouter = require('./routers/system');

app.use('/doctor', doctorRouter);
app.use('/patient', patientRouter);
app.use('/lab', labRouter);
app.use('/system', systemRouter);

app.get("/", (req, res) => {
  res.json({ message: "Welcome to the HealthCare API" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});