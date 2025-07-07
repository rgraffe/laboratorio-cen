import routes from './routes';
import dotenv from 'dotenv';
import express from 'express';
import { db } from './db';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({ status: 'ok' });
});

(async () => {
  try {
    await db.execute('SELECT 1');
    console.log('Connected to PostgreSQL via Drizzle ORM');
  } catch (error) {
    console.error('Database connection failed: ', error);
    process.exit(1);
  }

  app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
  });
})();
