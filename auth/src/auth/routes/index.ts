import { Router } from 'express';
import authRoutes from '../auth.routes';
const router = Router();

router.use('/login', authRoutes);

export default router;
