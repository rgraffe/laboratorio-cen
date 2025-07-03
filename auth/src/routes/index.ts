import { Router } from 'express';
import authRoutes from '../controllers/auth/auth.routes';
const router = Router();

router.use('/login', authRoutes);

export default router;
