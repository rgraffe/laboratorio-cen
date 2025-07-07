import { Router } from 'express';
import {
  createLaboratorioHandler,
  getAllLaboratoriosHandler,
  getLaboratorioByIdHandler,
  updateLaboratorioHandler,
  deleteLaboratorioHandler,
} from './laboratorios.controller';

const router = Router();

router.post('/', createLaboratorioHandler);
router.get('/', getAllLaboratoriosHandler);
router.get('/:id', getLaboratorioByIdHandler);
router.put('/:id', updateLaboratorioHandler);
router.delete('/:id', deleteLaboratorioHandler);

export default router;
