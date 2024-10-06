import { Context, Next } from "hono";
import { verify } from "jsonwebtoken";
import { env } from "../lib/env";

export const jwtMiddleware = async (c: Context, next: Next) => {
    const authHeader = c.req.header('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return c.json({ error: 'No token provided' }, 401);
    }
  
    const token = authHeader.split(' ')[1];
    try {
      const decoded = verify(token, env.JWT_SECRET!) as { id: number };
      c.set('jwtPayload', decoded);
      await next();
    } catch (error) {
      return c.json({ error: 'Invalid token' }, 401);
    }
  };