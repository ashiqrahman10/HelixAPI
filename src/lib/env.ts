import { z } from 'zod';
import dotenv from 'dotenv';

dotenv.config();

const envSchema = z.object({
  JWT_SECRET: z.string().min(1, "JWT_SECRET must be provided"),
  PORT: z.string().transform(Number).pipe(z.number().positive()),
  FIREBASE_API_KEY: z.string().min(1, "FIREBASE_API_KEY must be provided"),
  FIREBASE_AUTH_DOMAIN: z.string().min(1, "FIREBASE_AUTH_DOMAIN must be provided"),
  FIREBASE_PROJECT_ID: z.string().min(1, "FIREBASE_PROJECT_ID must be provided"),
  FIREBASE_STORAGE_BUCKET: z.string().min(1, "FIREBASE_STORAGE_BUCKET must be provided"),
  FIREBASE_MESSAGING_SENDER_ID: z.string().min(1, "FIREBASE_MESSAGING_SENDER_ID must be provided"),
  FIREBASE_APP_ID: z.string().min(1, "FIREBASE_APP_ID must be provided"),
  EMAIL_USER: z.string().email("Invalid email for EMAIL_USER"),
  EMAIL_PASS: z.string().min(1, "EMAIL_PASS must be provided"),
});

const parseEnv = () => {
  const parsed = envSchema.safeParse(process.env);

  if (!parsed.success) {
    console.error("❌ Invalid environment variables:", parsed.error.flatten().fieldErrors);
    throw new Error("Invalid environment variables");
  }

  return parsed.data;
};

export const env = parseEnv();
