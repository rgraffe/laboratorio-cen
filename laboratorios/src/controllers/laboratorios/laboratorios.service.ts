import { db } from '../../db'; // Ajusta la ruta si es necesario
import { laboratorios } from '../../tables/laboratorios';
import { CreateLaboratorioParams, Laboratorio } from '../../types/types';
import { eq } from 'drizzle-orm';

// Crear laboratorio
export const createLaboratorio = async ({
  Nombre,
  Descripcion,
}: CreateLaboratorioParams): Promise<Laboratorio> => {
  const [inserted] = await db
    .insert(laboratorios)
    .values({ Nombre, Descripcion })
    .returning();
  if (!inserted) throw new Error('No se pudo crear el laboratorio');
  return inserted;
};

// Obtener todos los laboratorios
export const getAllLaboratorios = async (): Promise<Laboratorio[]> => {
  return db.select().from(laboratorios);
};

// Obtener laboratorio por ID
export const getLaboratorioById = async (
  IdLaboratorio: number
): Promise<Laboratorio | null> => {
  const [lab] = await db
    .select()
    .from(laboratorios)
    .where(eq(laboratorios.IdLaboratorio, IdLaboratorio));
  return lab ?? null;
};

// Actualizar laboratorio
export const updateLaboratorio = async (
  IdLaboratorio: number,
  data: Partial<CreateLaboratorioParams>
): Promise<Laboratorio | null> => {
  const [updated] = await db
    .update(laboratorios)
    .set(data)
    .where(eq(laboratorios.IdLaboratorio, IdLaboratorio))
    .returning();
  return updated ?? null;
};

// Eliminar laboratorio
export const deleteLaboratorio = async (
  IdLaboratorio: number
): Promise<boolean> => {
  const result = await db
    .delete(laboratorios)
    .where(eq(laboratorios.IdLaboratorio, IdLaboratorio));
  return (result.rowCount ?? 0) > 0;
};
