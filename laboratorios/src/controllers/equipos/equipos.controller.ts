import { Request, Response } from 'express';
import {
  createEquipo,
  getAllEquipos,
  getEquipoById,
  updateEquipo,
  deleteEquipo,
} from './equipos.service';

// Crear equipo
export const createEquipoHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const equipo = await createEquipo(req.body);
    res.status(201).json({ data: equipo });
  } catch (error) {
    console.error('Error in createEquipoHandler: ', error);
    res.status(500).json({ error: 'Error al crear el equipo: ' + error });
  }
};

// Obtener todos los equipos
export const getAllEquiposHandler = async (
  _req: Request,
  res: Response
): Promise<void> => {
  try {
    const equipos = await getAllEquipos();
    res.status(200).json({ data: equipos });
  } catch (error) {
    console.error('Error in getAllEquiposHandler: ', error);
    res.status(500).json({ error: 'Error al obtener equipos: ' + error });
  }
};

// Obtener equipo por ID
export const getEquipoByIdHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const equipo = await getEquipoById(id);
    if (!equipo) {
      res.status(404).json({ error: 'Equipo no encontrado' });
      return;
    }
    res.status(200).json({ data: equipo });
  } catch (error) {
    console.error('Error in getEquipoByIdHandler: ', error);
    res.status(500).json({ error: 'Error al obtener el equipo: ' + error });
  }
};

// Actualizar equipo
export const updateEquipoHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const equipo = await updateEquipo(id, req.body);
    if (!equipo) {
      res.status(404).json({ error: 'Equipo no encontrado' });
      return;
    }
    res.status(200).json({ data: equipo });
  } catch (error) {
    console.error('Error in updateEquipoHandler: ', error);
    res.status(500).json({ error: 'Error al actualizar el equipo: ' + error });
  }
};

// Eliminar equipo
export const deleteEquipoHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const id = Number(req.params.id);
    const deleted = await deleteEquipo(id);
    if (!deleted) {
      res.status(404).json({ error: 'Equipo no encontrado' });
      return;
    }
    res.status(200).json({ message: 'Equipo eliminado correctamente' });
  } catch (error) {
    console.error('Error in deleteEquipoHandler: ', error);
    res.status(500).json({ error: 'Error al eliminar el equipo: ' + error });
  }
};
