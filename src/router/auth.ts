import { Hono } from 'hono';
import { eq } from 'drizzle-orm';
import { db } from '../lib/db';
import { users } from '../lib/schema';
import bcrypt from 'bcrypt';
import { userCreateSchema } from '../lib/validation';
import { jwtMiddleware } from '../middleware/jwt';
import { sign } from 'jsonwebtoken';
import { env } from '../lib/env';

const auth = new Hono();

// JWT secret (should be stored in an environment variable in production)
const JWT_SECRET = env.JWT_SECRET

// Signup route
auth.post('/signup', async (c) => {
  const body = await c.req.json();
  
  // Validate input
  const result = userCreateSchema.safeParse(body);
  if (!result.success) {
    return c.json({ error: 'Invalid input', details: result.error.errors }, 400);
  }

  const { username, email, password, fullName, role, dateOfBirth, phoneNumber, address } = result.data;

  // Check if user already exists
  const existingUser = await db.select().from(users).where(eq(users.email, email));
  if (existingUser.length > 0) {
    return c.json({ error: 'User already exists' }, 400);
  }

  // Hash password
  const hashedPassword = await bcrypt.hash(password, 10);

  // Create new user
  const [newUser] = await db.insert(users).values({
    username,
    email,
    hashedPassword,
    fullName,
    role,
    dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
    phoneNumber,
    address,
  }).returning();

  // Generate JWT
  const token = sign({ id: newUser.id }, JWT_SECRET);

  return c.json({ token, user: { ...newUser, hashedPassword: undefined } });
});

// Signin route
auth.post('/signin', async (c) => {
  const { email, password } = await c.req.json();

  // Find user
  const [user] = await db.select().from(users).where(eq(users.email, email));
  if (!user) {
    return c.json({ error: 'Invalid credentials' }, 401);
  }

  // Check password
  const isValidPassword = await bcrypt.compare(password, user.hashedPassword);
  if (!isValidPassword) {
    return c.json({ error: 'Invalid credentials' }, 401);
  }

  // Generate JWT
  const token = sign({ id: user.id }, JWT_SECRET);

  return c.json({ token, user: { ...user, hashedPassword: undefined } });
});

// Get user details route (protected)
// Middleware to verify JWT token


// Apply JWT middleware to protected routes
auth.use('/me', jwtMiddleware);

auth.get('/me', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload')?.id!;

  const [user] = await db.select().from(users).where(eq(users.id, userId));
  if (!user) {
    return c.json({ error: 'User not found' }, 404);
  }

  return c.json({ user: { ...user, hashedPassword: undefined } });
});

export default auth;
