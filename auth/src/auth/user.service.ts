import bcrypt from 'bcryptjs';

// Simulación de base de datos (reemplaza por Drizzle ORM en producción)
let users: Array<{ id: number; email: string; password: string; type: string }> = [];

async function initializeUsers() {
  const hashedPassword = await bcrypt.hash('123456', 10);
  users = [
    { id: 1, email: 'test@example.com', password: hashedPassword, type: 'admin' }
  ];
}

initializeUsers();

export async function findUserByEmail(email: string) {
  return users.find(user => user.email === email);
}

export async function validatePassword(plain: string, hash: string) {
  return bcrypt.compare(plain, hash);
}