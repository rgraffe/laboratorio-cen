import { pgTable, varchar, serial, pgEnum, text } from 'drizzle-orm/pg-core';

export const laboratorios = pgTable('Laboratorios', {
  IdLaboratorio: serial('IdLaboratorio').primaryKey(),
  Nombre: varchar('Nombre', { length: 100 }).unique().notNull(),
  Descripcion: varchar('Descripción', { length: 150 }).notNull(),
});
