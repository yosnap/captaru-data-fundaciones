'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/layout/Header';
import { Search, ChevronRight, Building, MapPin, Calendar, Filter } from 'lucide-react';

interface Foundation {
  _id: number;
  nombre: string;
  numRegistro: string;
  estado: string;
  nif?: string;
  direccionEstatutaria?: {
    provincia?: string;
    localidad?: string;
  };
  fechaConstitucion?: string;
}

interface ApiResponse {
  data: Foundation[];
  total: number;
  page: number;
  totalPages: number;
}

interface FilterOption {
  _id: string;
  count: number;
}

interface FilterOptions {
  provincias: FilterOption[];
  estados: FilterOption[];
  actividades: FilterOption[];
  funciones: FilterOption[];
}

export default function Home() {
  const router = useRouter();
  const [fundaciones, setFundaciones] = useState<Foundation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState({
    provincia: '',
    estado: '',
    actividad: '',
    funcion: '',
  });
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({
    provincias: [],
    estados: [],
    actividades: [],
    funciones: []
  });
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchFundaciones();
    fetchFilterOptions();
  }, [page, search, filters, sortBy, sortOrder]);

  const fetchFilterOptions = async () => {
    try {
      const response = await fetch('/api/fundaciones/filters');
      const data: FilterOptions = await response.json();
      setFilterOptions(data);
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const fetchFundaciones = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20',
        sortBy,
        sortOrder,
        ...(search && { search }),
        ...(filters.provincia && { provincia: filters.provincia }),
        ...(filters.estado && { estado: filters.estado }),
        ...(filters.actividad && { actividad: filters.actividad }),
        ...(filters.funcion && { funcion: filters.funcion }),
      });

      const response = await fetch(`/api/fundaciones?${params}`);
      const data: ApiResponse = await response.json();
      
      setFundaciones(data.data);
      setTotalPages(data.totalPages);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching fundaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchFundaciones();
  };

  const handleFoundationClick = (fundacion: Foundation) => {
    router.push(`/data?id=${fundacion._id}`);
  };

  const clearFilters = () => {
    setFilters({ provincia: '', estado: '', actividad: '', funcion: '' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Base de Datos de Fundaciones Españolas
          </h1>
          <p className="text-gray-600">
            Explora y analiza información de {total.toLocaleString('es-ES')} fundaciones
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="text"
                    placeholder="Buscar por nombre, NIF o fines..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                </div>
              </div>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Buscar
              </button>
            </div>

            <div className="flex gap-4 items-center flex-wrap">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                <Filter size={16} />
                Filtros
              </button>
              
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Ordenar por:</label>
                <select
                  className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="name">Nombre</option>
                  <option value="date">Fecha de Constitución</option>
                </select>
                <select
                  className="px-3 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500"
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                >
                  <option value="asc">Ascendente</option>
                  <option value="desc">Descendente</option>
                </select>
              </div>
              
              {(filters.provincia || filters.estado || filters.actividad || filters.funcion) && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Limpiar filtros
                </button>
              )}
            </div>
            
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
                <select
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={filters.provincia}
                  onChange={(e) => setFilters({ ...filters, provincia: e.target.value })}
                >
                  <option value="">Todas las provincias</option>
                  {filterOptions.provincias.map((provincia) => (
                    <option key={provincia._id} value={provincia._id}>
                      {provincia._id} ({provincia.count.toLocaleString('es-ES')})
                    </option>
                  ))}
                </select>

                <select
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={filters.estado}
                  onChange={(e) => setFilters({ ...filters, estado: e.target.value })}
                >
                  <option value="">Todos los estados</option>
                  {filterOptions.estados.map((estado) => (
                    <option key={estado._id} value={estado._id}>
                      {estado._id} ({estado.count.toLocaleString('es-ES')})
                    </option>
                  ))}
                </select>
                
                <select
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={filters.actividad}
                  onChange={(e) => setFilters({ ...filters, actividad: e.target.value })}
                >
                  <option value="">Todas las actividades</option>
                  {filterOptions.actividades.map((actividad) => (
                    <option key={actividad._id} value={actividad._id}>
                      {actividad._id} ({actividad.count.toLocaleString('es-ES')})
                    </option>
                  ))}
                </select>
                
                <select
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={filters.funcion}
                  onChange={(e) => setFilters({ ...filters, funcion: e.target.value })}
                >
                  <option value="">Todas las funciones</option>
                  {filterOptions.funciones.map((funcion) => (
                    <option key={funcion._id} value={funcion._id}>
                      {funcion._id} ({funcion.count.toLocaleString('es-ES')})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </form>
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            <div className="grid gap-4">
              {fundaciones.map((fundacion) => (
                <div
                  key={fundacion._id}
                  className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition cursor-pointer"
                  onClick={() => handleFoundationClick(fundacion)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {fundacion.nombre}
                      </h3>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-2">
                          <Building size={16} />
                          <span>{fundacion.numRegistro}</span>
                        </div>
                        
                        {fundacion.direccionEstatutaria?.provincia && (
                          <div className="flex items-center space-x-2">
                            <MapPin size={16} />
                            <span>{fundacion.direccionEstatutaria.provincia}</span>
                          </div>
                        )}
                        
                        {fundacion.fechaConstitucion && (
                          <div className="flex items-center space-x-2">
                            <Calendar size={16} />
                            <span>{fundacion.fechaConstitucion}</span>
                          </div>
                        )}
                        
                        <div>
                          <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${
                            fundacion.estado === 'Activa' 
                              ? 'bg-green-100 text-green-800 border border-green-200' 
                              : fundacion.estado === 'Extinguida'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : fundacion.estado === 'Inactiva'
                              ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                              : fundacion.estado === 'Suspendida'
                              ? 'bg-orange-100 text-orange-800 border border-orange-200'
                              : 'bg-gray-100 text-gray-800 border border-gray-200'
                          }`}>
                            {fundacion.estado}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <ChevronRight className="text-gray-400 ml-4" size={20} />
                  </div>
                </div>
              ))}
            </div>

            {/* Results Summary */}
            <div className="mt-6 flex justify-between items-center text-sm text-gray-600">
              <div>
                Mostrando {Math.min((page - 1) * 20 + 1, total)} - {Math.min(page * 20, total)} de {total.toLocaleString('es-ES')} resultados
              </div>
              {(filters.provincia || filters.estado || filters.actividad || filters.funcion || search) && (
                <div className="text-blue-600">
                  <Filter size={14} className="inline mr-1" />
                  Filtros aplicados
                </div>
              )}
            </div>

            {/* Pagination */}
            <div className="mt-4 flex justify-center">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Anterior
                </button>
                
                <span className="px-4 py-2 text-gray-700 bg-gray-50 rounded-lg">
                  Página {page} de {totalPages}
                </span>
                
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Siguiente
                </button>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
