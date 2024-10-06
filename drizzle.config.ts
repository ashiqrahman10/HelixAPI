import { defineConfig } from 'drizzle-kit'
export default defineConfig({
    dialect: "sqlite", // "mysql" | "sqlite" | "postgresql"
    schema: "./src/lib/schema.ts",
    out: "./drizzle",
    dbCredentials:{
      url: "helix.db"
    }
  });