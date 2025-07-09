// Tipos para Laboratorios
export type Laboratorio = {
  IdLaboratorio: number;
  Nombre: string;
  Descripcion: string;
};

export type CreateLaboratorioParams = {
  Nombre: string;
  Descripcion: string;
};

// Tipos para Equipos
export type Equipo = {
  IdEquipo: number;
  Nombre: string;
  Modelo: string;
  Estado: 'Operativo' | 'Mantenimiento' | 'Dañado';
  IdLaboratorio: number;
};

export type CreateEquipoParams = {
  Nombre: string;
  Modelo: string;
  Estado: 'Operativo' | 'Mantenimiento' | 'Dañado';
  IdLaboratorio: number;
};
