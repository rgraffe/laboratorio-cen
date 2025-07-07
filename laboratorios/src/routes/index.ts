import { Router } from 'express';
import laboratorioRoutes from '../controllers/laboratorios/laboratorios.routes';
import equipoRoutes from '../controllers/equipos/equipos.routes';
const router = Router();

router.use('/laboratorios', laboratorioRoutes);
router.use('/equipos', equipoRoutes);

export default router;
