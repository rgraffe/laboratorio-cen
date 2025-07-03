import jwt from 'jsonwebtoken';
import { authParams } from '../types/types';
import { db } from '../db';
import { usuarios } from '../tables/usuarios';
import { eq } from 'drizzle-orm';
import { comparePassword } from '../utils/password';

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

export const login = async ({ Correo, Contraseña }: authParams) => {
  try {
    // Validate input
    if (!Correo || !Contraseña) {
      throw new AuthError('Correo y Contraseña son campos obligatorios');
    }

    const result = await db
      .select()
      .from(usuarios)
      .where(eq(usuarios.Correo, Correo));

    if (result.length === 0) {
      throw new AuthError('El usuario no existe');
    }

    const Usuarios = result[0];

    if (!Usuarios?.Contraseña) {
      throw new AuthError('El usuario no tiene contraseña asignada');
    }

    const isPasswordValid = await comparePassword(
      Contraseña,
      Usuarios.Contraseña
    );

    if (!isPasswordValid) {
      throw new AuthError('Contraseña incorrecta');
    }

    // Genera el token
    const token = jwt.sign(
      { userId: Usuarios.Id, tipo: Usuarios?.Tipo },
      process.env.JWT_SECRET!,
      { expiresIn: '15d' }
    );

    // Excluye la contraseña del usuario antes de devolverlo
    const { Contraseña: _, ...usuarioSinContraseña } = Usuarios;
    return { token, usuario: usuarioSinContraseña };
  } catch (error) {
    if (error instanceof AuthError) throw error;
    console.error('Error autenticando usuario:', error);
    throw new Error('Error al autenticar usuario');
  }
};
