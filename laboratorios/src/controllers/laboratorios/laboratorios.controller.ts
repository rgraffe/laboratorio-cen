import { Request, Response } from 'express';
import {
  createLaboratorio,
  getAllLaboratorios,
  getLaboratorioById,
  updateLaboratorio,
  deleteLaboratorio,
} from './laboratorios.service';

// Crear laboratorio
export const createLaboratorioHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const laboratorio = await createLaboratorio(req.body);
    res.status(201).json({ data: laboratorio });
  } catch (error) {
    console.error('Error in createLaboratorioHandler: ', error);
    res.status(500).json({ error: 'Error al crear el laboratorio: ' + error });
  }
};

// Obtener todos los laboratorios
export const getAllLaboratoriosHandler = async (
  _req: Request,
  res: Response
): Promise<void> => {
  try {
    const laboratorios = await getAllLaboratorios();
    res.status(200).json({ data: laboratorios });
  } catch (error) {
    console.error('Error in getAllLaboratoriosHandler: ', error);
    res.status(500).json({ error: 'Error al obtener laboratorios: ' + error });
  }
};

// Obtener laboratorio por ID
export const getLaboratorioByIdHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const laboratorio = await getLaboratorioById(id);
    if (!laboratorio) {
      res.status(404).json({ error: 'Laboratorio no encontrado' });
      return;
    }
    res.status(200).json({ data: laboratorio });
  } catch (error) {
    console.error('Error in getLaboratorioByIdHandler: ', error);
    res
      .status(500)
      .json({ error: 'Error al obtener el laboratorio: ' + error });
  }
};

// Actualizar laboratorio
export const updateLaboratorioHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const laboratorio = await updateLaboratorio(id, req.body);
    if (!laboratorio) {
      res.status(404).json({ error: 'Laboratorio no encontrado' });
      return;
    }
    res.status(200).json({ data: laboratorio });
  } catch (error) {
    console.error('Error in updateLaboratorioHandler: ', error);
    res
      .status(500)
      .json({ error: 'Error al actualizar el laboratorio: ' + error });
  }
};

// Eliminar laboratorio
export const deleteLaboratorioHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const deleted = await deleteLaboratorio(id);
    if (!deleted) {
      res.status(404).json({ error: 'Laboratorio no encontrado' });
      return;
    }
    res.status(200).json({ message: 'Laboratorio eliminado correctamente' });
  } catch (error) {
    console.error('Error in deleteLaboratorioHandler: ', error);
    res
      .status(500)
      .json({ error: 'Error al eliminar el laboratorio: ' + error });
  }
};
