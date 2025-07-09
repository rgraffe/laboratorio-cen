import { Router } from 'express';
import {
  createEquipoHandler,
  getAllEquiposHandler,
  getEquipoByIdHandler,
  updateEquipoHandler,
  deleteEquipoHandler,
} from './equipos.controller';

const router = Router();

router.post('/', createEquipoHandler);
router.get('/', getAllEquiposHandler);
router.get('/:id', getEquipoByIdHandler);
router.put('/:id', updateEquipoHandler);
router.delete('/:id', deleteEquipoHandler);

export default router;
