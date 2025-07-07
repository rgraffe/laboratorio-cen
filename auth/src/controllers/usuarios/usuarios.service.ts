import { db } from '../../db';
import { usuarios } from '../../tables/usuarios';
import { CreateUserParams } from '../../types/types';
import bcrypt from 'bcrypt';
// Crear usuario
export const createUser = async ({
  Nombre,
  Correo,
  Tipo,
  Contraseña,
}: CreateUserParams) => {
  try {
    // Validar input
    if (!Nombre || !Correo || !Tipo || !Contraseña) {
      throw new Error('Todos los campos son obligatorios');
    }

    // Validar que Tipo sea uno de los valores permitidos
    const allowedTipos = ['ADMINISTRADOR', 'PROFESOR', 'ESTUDIANTE'] as const;
    if (!allowedTipos.includes(Tipo as (typeof allowedTipos)[number])) {
      throw new Error('Tipo de usuario no válido');
    }

    // Encriptar la contraseña antes de guardar
    const hashedPassword = await bcrypt.hash(Contraseña, 10);
    console.log('insertando usuario');
    // Insertar en la tabla de usuarios
    const insertedUser = await db
      .insert(usuarios)
      .values({
        Nombre,
        Correo,
        Tipo: Tipo as 'ADMINISTRADOR' | 'PROFESOR' | 'ESTUDIANTE',
        Contraseña: hashedPassword,
      })
      .returning({ Id: usuarios.Id });

    if (insertedUser.length === 0) {
      throw new Error('Error al crear el usuario');
    }

    return {
      message: 'Usuario creado correctamente',
      userId: insertedUser[0].Id,
    };
  } catch (error) {
    console.error('Error creating tecnico:', error);
    throw new Error('Error al crear el tecnico');
  }
};

// Devuelve todos los usuarios sin la contraseña
export const getAllUsers = async () => {
  try {
    const users = await db
      .select({
        Id: usuarios.Id,
        Nombre: usuarios.Nombre,
        Correo: usuarios.Correo,
        Tipo: usuarios.Tipo,
      })
      .from(usuarios);

    return users;
  } catch (error) {
    console.error('Error al obtener usuarios:', error);
    throw new Error('Error al obtener usuarios');
  }
};
