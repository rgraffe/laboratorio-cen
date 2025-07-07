import { serial, varchar, pgTable } from 'drizzle-orm/pg-core';
import { pgEnum } from 'drizzle-orm/pg-core';

export const estadoEnum = pgEnum('Estado', [
  'Operativo',
  'Mantenimiento',
  'Dañado',
]);

export const equipos = pgTable('Equipos', {
  IdEquipo: serial('IdEquipo').primaryKey(),
  Nombre: varchar('Nombre', { length: 100 }).notNull(),
  Modelo: varchar('Modelo', { length: 150 }).notNull(),
  Estado: estadoEnum('Estado').notNull(),
});
