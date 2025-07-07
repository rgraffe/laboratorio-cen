import { Request, Response } from 'express';
import { createUser, getAllUsers } from './usuarios.service';

export const createUserHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  try {
    const user = await createUser(req.body);
    res.status(201).json({
      data: user,
    });
    return;
  } catch (error) {
    console.error('Error in createUserHandler: ', error);
    res.status(500).json({
      error: 'Error al crear el usuario' + error,
    });
    return;
  }
};

export const getAllUsersHandler = async (req: Request, res: Response) => {
  try {
    const usuarios = await getAllUsers();
    res.status(201).json({
      data: usuarios,
    });
    return;
  } catch (error) {
    console.log('Error en getAllUsersHandler', error);
    res.status(500).json({
      error: 'Error al obtener datos de usuarios' + error,
    });
    return;
  }
};
