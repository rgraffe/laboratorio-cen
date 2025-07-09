import { Request, Response } from 'express';
import { AuthError, login } from './auth.service';

export const loginHandler = async (
  req: Request,
  res: Response
): Promise<void> => {
  const { email, password } = req.body;
  try {
    console.log('RECIBIDO ENTRO A LOGINHADNLER');
    const user = await login(req.body);
    res.status(201).json({
      data: user,
    });
    return;
  } catch (error: any) {
    if (error instanceof AuthError) {
      res.status(401).json({
        error: 'Correo o contraseña incorrectos',
      });
      return;
    }
    console.error('Error in loginHandler:', error);
    res.status(500).json({
      error: 'Error al autenticar coordinador',
    });
  }
};
