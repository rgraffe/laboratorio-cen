import { Router } from 'express';
import authRoutes from '../controllers/auth/auth.routes';
import usuarioRoutes from '../controllers/usuarios/usuarios.routes';
const router = Router();

router.use('/login', authRoutes);
router.use('/users', usuarioRoutes);
export default router;
