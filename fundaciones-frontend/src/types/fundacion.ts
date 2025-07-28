export interface Direccion {
  domicilio?: string;
  localidad?: string;
  codigoPostal?: number;
  provincia?: string;
  telefono?: string;
  fax?: string;
  email?: string;
  web?: string;
}

export interface Actividad {
  nombre: string;
  clasificacion1?: string;
  clasificacion2?: string;
  clasificacion3?: string;
  clasificacion4?: string;
  funcion1?: string;
  funcion2?: string;
}

export interface Persona {
  nombre: string;
  cargo?: string;
}

export interface Fundacion {
  _id: number;
  nombre: string;
  numRegistro: string;
  fechaConstitucion?: string;
  fechaInscripcion?: string;
  nif?: string;
  fechaExtincion?: string;
  estado: string;
  fines?: string;
  direccionEstatutaria?: Direccion;
  direccionNotificacion?: Direccion;
  actividades: Actividad[];
  fundadores: Persona[];
  patronos: Persona[];
  directivos: Persona[];
  organos: { nombre: string }[];
  metadata?: {
    fechaActualizacion: Date;
    fuenteDatos: string;
  };
}

export interface FundacionFilters {
  search?: string;
  provincia?: string;
  estado?: string;
  actividad?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}