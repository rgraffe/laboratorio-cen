import { Router } from 'express';
import { createUserHandler, getAllUsersHandler } from './usuarios.controller';

const router = Router();

router.post('/', createUserHandler);
router.get('/', getAllUsersHandler);
export default router;
