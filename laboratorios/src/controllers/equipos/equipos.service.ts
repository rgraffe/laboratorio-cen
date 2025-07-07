import { eq } from 'drizzle-orm';
import { db } from '../../db'; // Ajusta la ruta si es necesario
import { equipos } from '../../tables/equipos';
import { CreateEquipoParams, Equipo } from '../../types/types';

// Crear equipo
export const createEquipo = async ({
  Nombre,
  Modelo,
  Estado,
  IdLaboratorio,
}: CreateEquipoParams): Promise<Equipo> => {
  const [inserted] = await db
    .insert(equipos)
    .values({ Nombre, Modelo, Estado, IdLaboratorio })
    .returning();
  if (!inserted) throw new Error('No se pudo crear el equipo');
  return inserted;
};

// Obtener todos los equipos
export const getAllEquipos = async (): Promise<Equipo[]> => {
  return db.select().from(equipos);
};

// Obtener equipo por ID
export const getEquipoById = async (
  IdEquipo: number
): Promise<Equipo | null> => {
  const [equipo] = await db
    .select()
    .from(equipos)
    .where(eq(equipos.IdEquipo, IdEquipo));
  return equipo ?? null;
};

// Actualizar equipo
export const updateEquipo = async (
  IdEquipo: number,
  data: Partial<CreateEquipoParams>
): Promise<Equipo | null> => {
  const [updated] = await db
    .update(equipos)
    .set(data)
    .where(eq(equipos.IdEquipo, IdEquipo))
    .returning();
  return updated ?? null;
};

// Eliminar equipo
export const deleteEquipo = async (IdEquipo: number): Promise<boolean> => {
  const result = await db.delete(equipos).where(eq(equipos.IdEquipo, IdEquipo));
  return (result.rowCount ?? 0) > 0;
};
