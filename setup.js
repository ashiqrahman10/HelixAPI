import { createInterface } from 'readline';
import bcrypt from 'bcrypt';
import Database from 'better-sqlite3';

const rl = createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => {
  return new Promise((resolve) => {
    rl.question(query, resolve);
  });
};

async function setupAdminUser() {
  console.log('Setting up admin user...');

  const username = await question('Enter admin username: ');
  const email = await question('Enter admin email: ');
  const password = await question('Enter admin password: ');

  try {
    // Validate input (assuming userCreateSchema is defined elsewhere)
    const validatedInput = { username, email, password, role: 'admin' };

    const hashedPassword = await bcrypt.hash(validatedInput.password, 10);

    const db = new Database('helix.db'); // Replace with your actual database path

    const insertQuery = db.prepare(`
      INSERT INTO users (username, email, hashed_password, role)
      VALUES (?, ?, ?, ?)
    `);

    const result = insertQuery.run(
      validatedInput.username,
      validatedInput.email,
      hashedPassword,
      'admin'
    );

    if (result.changes > 0) {
      console.log('Admin user created successfully:', validatedInput.username);
    } else {
      console.log('Failed to create admin user');
    }

    db.close();
  } catch (error) {
    console.error('Error creating admin user:', error);
  } finally {
    rl.close();
  }
}

setupAdminUser();
