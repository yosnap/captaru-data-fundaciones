'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/components/layout/Header';
import { Eye, ChevronDown, ChevronUp, ArrowLeft } from 'lucide-react';

interface Foundation {
  _id: number;
  nombre: string;
  numRegistro: string;
  estado: string;
  nif?: string;
  fechaConstitucion?: string;
  fechaInscripcion?: string;
  fines?: string;
  direccionEstatutaria?: {
    domicilio?: string;
    provincia?: string;
    codigoPostal?: number;
    telefono?: string;
    email?: string;
    web?: string;
  };
  direccionNotificacion?: {
    domicilio?: string;
    provincia?: string;
    localidad?: string;
    codigoPostal?: number;
  };
  actividades: Array<{
    nombre: string;
    clasificacion1?: string;
    clasificacion2?: string;
    funcion1?: string;
  }>;
  fundadores: Array<{ nombre: string }>;
  patronos: Array<{ nombre: string; cargo?: string }>;
  directivos: Array<{ nombre: string; cargo?: string }>;
  organos: Array<{ nombre: string }>;
}

export default function Data() {
  const searchParams = useSearchParams();
  const foundationId = searchParams.get('id');
  
  const [fundaciones, setFundaciones] = useState<Foundation[]>([]);
  const [singleFoundation, setSingleFoundation] = useState<Foundation | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());
  const [selectedFundacion, setSelectedFundacion] = useState<Foundation | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [activeActivityTab, setActiveActivityTab] = useState(0);
  const [modalActiveActivityTab, setModalActiveActivityTab] = useState(0);

  useEffect(() => {
    console.log('Modal state changed:', showModal, selectedFundacion?.nombre);
  }, [showModal, selectedFundacion]);

  useEffect(() => {
    if (foundationId) {
      fetchSingleFoundation(parseInt(foundationId));
    } else {
      fetchFundaciones();
    }
  }, [foundationId]);

  const fetchFundaciones = async () => {
    try {
      const response = await fetch('/api/fundaciones?limit=50');
      const data = await response.json();
      setFundaciones(data.data);
    } catch (error) {
      console.error('Error fetching fundaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSingleFoundation = async (id: number) => {
    try {
      const response = await fetch('/api/fundaciones', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id }),
      });
      const data = await response.json();
      setSingleFoundation(data);
    } catch (error) {
      console.error('Error fetching single foundation:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleRow = (id: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  const openModal = (fundacion: Foundation) => {
    console.log('Opening modal for:', fundacion.nombre);
    setSelectedFundacion(fundacion);
    setModalActiveActivityTab(0);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedFundacion(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  // Single foundation view
  if (singleFoundation) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8">
          <div className="mb-6">
            <button
              onClick={() => window.history.back()}
              className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
            >
              <ArrowLeft size={16} className="mr-2" />
              Volver
            </button>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {singleFoundation.nombre}
            </h1>
            <p className="text-gray-600">
              Información detallada de la fundación
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Información Básica
                  </h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>ID:</strong> {singleFoundation._id}</p>
                    <p><strong>Número de Registro:</strong> {singleFoundation.numRegistro}</p>
                    <p><strong>NIF:</strong> {singleFoundation.nif || 'N/A'}</p>
                    <p><strong>Estado:</strong> 
                      <span className={`ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        singleFoundation.estado === 'ACTIVA'
                          ? 'bg-green-100 text-green-800'
                          : singleFoundation.estado === 'EXTINGUIDA'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {singleFoundation.estado}
                      </span>
                    </p>
                    <p><strong>Fecha de Constitución:</strong> {singleFoundation.fechaConstitucion || 'N/A'}</p>
                    <p><strong>Fecha de Inscripción:</strong> {singleFoundation.fechaInscripcion || 'N/A'}</p>
                  </div>
                </div>

                {/* Address Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Dirección Estatutaria
                  </h3>
                  {singleFoundation.direccionEstatutaria ? (
                    <div className="space-y-2 text-sm">
                      <p><strong>Domicilio:</strong> {singleFoundation.direccionEstatutaria.domicilio || 'N/A'}</p>
                      <p><strong>Provincia:</strong> {singleFoundation.direccionEstatutaria.provincia || 'N/A'}</p>
                      <p><strong>Código Postal:</strong> {singleFoundation.direccionEstatutaria.codigoPostal || 'N/A'}</p>
                      <p><strong>Teléfono:</strong> {singleFoundation.direccionEstatutaria.telefono || 'N/A'}</p>
                      <p><strong>Email:</strong> {singleFoundation.direccionEstatutaria.email || 'N/A'}</p>
                      <p><strong>Web:</strong> {singleFoundation.direccionEstatutaria.web || 'N/A'}</p>
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No disponible</p>
                  )}
                </div>

                {/* Activities */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Actividades ({singleFoundation.actividades.length})
                  </h3>
                  {singleFoundation.actividades.length > 0 ? (
                    singleFoundation.actividades.length === 1 ? (
                      <div className="p-3 bg-gray-50 rounded text-sm">
                        <p><strong>Nombre:</strong> {singleFoundation.actividades[0].nombre}</p>
                        {singleFoundation.actividades[0].clasificacion1 && (
                          <p><strong>Clasificación:</strong> {singleFoundation.actividades[0].clasificacion1}</p>
                        )}
                        {singleFoundation.actividades[0].funcion1 && (
                          <p><strong>Función:</strong> {singleFoundation.actividades[0].funcion1}</p>
                        )}
                      </div>
                    ) : (
                      <div>
                        {/* Activity Tabs */}
                        <div className="flex flex-wrap border-b border-gray-200 mb-3">
                          {singleFoundation.actividades.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setActiveActivityTab(index)}
                              className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                                activeActivityTab === index
                                  ? 'border-blue-500 text-blue-600'
                                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                              }`}
                            >
                              Actividad {index + 1}
                            </button>
                          ))}
                        </div>
                        {/* Active Activity Content */}
                        <div className="p-3 bg-gray-50 rounded text-sm">
                          <p><strong>Nombre:</strong> {singleFoundation.actividades[activeActivityTab].nombre}</p>
                          {singleFoundation.actividades[activeActivityTab].clasificacion1 && (
                            <p><strong>Clasificación:</strong> {singleFoundation.actividades[activeActivityTab].clasificacion1}</p>
                          )}
                          {singleFoundation.actividades[activeActivityTab].funcion1 && (
                            <p><strong>Función:</strong> {singleFoundation.actividades[activeActivityTab].funcion1}</p>
                          )}
                        </div>
                      </div>
                    )
                  ) : (
                    <p className="text-gray-500 text-sm">No hay actividades registradas</p>
                  )}
                </div>

                {/* Patronos */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Patronos ({singleFoundation.patronos.length})
                  </h3>
                  {singleFoundation.patronos.length > 0 ? (
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {singleFoundation.patronos.map((patron, index) => (
                        <div key={`patron-${index}`} className="text-sm p-2 bg-gray-50 rounded">
                          <p><strong>{patron.nombre}</strong></p>
                          {patron.cargo && <p className="text-gray-600">{patron.cargo}</p>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No hay patronos registrados</p>
                  )}
                </div>
              </div>

              {/* Fines */}
              {singleFoundation.fines && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-4">
                    Fines
                  </h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                      {singleFoundation.fines}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Datos Detallados
          </h1>
          <p className="text-gray-600">
            Vista detallada de la información de las fundaciones
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fundación
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Registro
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Provincia
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {fundaciones.map((fundacion) => (
                  <React.Fragment key={fundacion._id}>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <button
                            onClick={() => toggleRow(fundacion._id)}
                            className="mr-2 p-1 hover:bg-gray-200 rounded"
                          >
                            {expandedRows.has(fundacion._id) ? (
                              <ChevronUp size={16} />
                            ) : (
                              <ChevronDown size={16} />
                            )}
                          </button>
                          <div>
                            <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                              {fundacion.nombre}
                            </div>
                            <div className="text-sm text-gray-500">
                              ID: {fundacion._id}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {fundacion.numRegistro}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          fundacion.estado === 'ACTIVA'
                            ? 'bg-green-100 text-green-800'
                            : fundacion.estado === 'EXTINGUIDA'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {fundacion.estado}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {fundacion.direccionEstatutaria?.provincia || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            openModal(fundacion);
                          }}
                          className="text-blue-600 hover:text-blue-900 flex items-center space-x-1 transition-colors"
                          type="button"
                        >
                          <Eye size={16} />
                          <span>Ver detalles</span>
                        </button>
                      </td>
                    </tr>
                    
                    {expandedRows.has(fundacion._id) && (
                      <tr>
                        <td colSpan={5} className="px-6 py-4 bg-gray-50">
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">Información Básica</h4>
                              <p><strong>NIF:</strong> {fundacion.nif || 'N/A'}</p>
                              <p><strong>Fecha Constitución:</strong> {fundacion.fechaConstitucion || 'N/A'}</p>
                              <p><strong>Fecha Inscripción:</strong> {fundacion.fechaInscripcion || 'N/A'}</p>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">Contacto</h4>
                              <p><strong>Email:</strong> {fundacion.direccionEstatutaria?.email || 'N/A'}</p>
                              <p><strong>Teléfono:</strong> {fundacion.direccionEstatutaria?.telefono || 'N/A'}</p>
                              <p><strong>Web:</strong> {fundacion.direccionEstatutaria?.web || 'N/A'}</p>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">Estadísticas</h4>
                              <p><strong>Actividades:</strong> {fundacion.actividades.length}</p>
                              <p><strong>Patronos:</strong> {fundacion.patronos.length}</p>
                              <p><strong>Directivos:</strong> {fundacion.directivos.length}</p>
                            </div>
                          </div>
                          
                          {fundacion.fines && (
                            <div className="mt-4">
                              <h4 className="font-semibold text-gray-700 mb-2">Fines</h4>
                              <p className="text-gray-600 text-sm">{fundacion.fines}</p>
                            </div>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Modal */}
      {showModal && selectedFundacion && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              closeModal();
            }
          }}
        >
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  {selectedFundacion.nombre}
                </h2>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Basic Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Información Básica
                  </h3>
                  <div className="space-y-2 text-sm">
                    <p><strong>ID:</strong> {selectedFundacion._id}</p>
                    <p><strong>Número de Registro:</strong> {selectedFundacion.numRegistro}</p>
                    <p><strong>NIF:</strong> {selectedFundacion.nif || 'N/A'}</p>
                    <p><strong>Estado:</strong> {selectedFundacion.estado}</p>
                    <p><strong>Fecha de Constitución:</strong> {selectedFundacion.fechaConstitucion || 'N/A'}</p>
                    <p><strong>Fecha de Inscripción:</strong> {selectedFundacion.fechaInscripcion || 'N/A'}</p>
                  </div>
                </div>

                {/* Address Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Dirección Estatutaria
                  </h3>
                  {selectedFundacion.direccionEstatutaria ? (
                    <div className="space-y-2 text-sm">
                      <p><strong>Domicilio:</strong> {selectedFundacion.direccionEstatutaria.domicilio || 'N/A'}</p>
                      <p><strong>Provincia:</strong> {selectedFundacion.direccionEstatutaria.provincia || 'N/A'}</p>
                      <p><strong>Código Postal:</strong> {selectedFundacion.direccionEstatutaria.codigoPostal || 'N/A'}</p>
                      <p><strong>Teléfono:</strong> {selectedFundacion.direccionEstatutaria.telefono || 'N/A'}</p>
                      <p><strong>Email:</strong> {selectedFundacion.direccionEstatutaria.email || 'N/A'}</p>
                      <p><strong>Web:</strong> {selectedFundacion.direccionEstatutaria.web || 'N/A'}</p>
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No disponible</p>
                  )}
                </div>

                {/* Activities */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Actividades ({selectedFundacion.actividades.length})
                  </h3>
                  {selectedFundacion.actividades.length > 0 ? (
                    selectedFundacion.actividades.length === 1 ? (
                      <div className="p-3 bg-gray-50 rounded text-sm">
                        <p><strong>Nombre:</strong> {selectedFundacion.actividades[0].nombre}</p>
                        {selectedFundacion.actividades[0].clasificacion1 && (
                          <p><strong>Clasificación:</strong> {selectedFundacion.actividades[0].clasificacion1}</p>
                        )}
                        {selectedFundacion.actividades[0].funcion1 && (
                          <p><strong>Función:</strong> {selectedFundacion.actividades[0].funcion1}</p>
                        )}
                      </div>
                    ) : (
                      <div>
                        {/* Activity Tabs */}
                        <div className="flex flex-wrap border-b border-gray-200 mb-3">
                          {selectedFundacion.actividades.map((_, index) => (
                            <button
                              key={index}
                              onClick={() => setModalActiveActivityTab(index)}
                              className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
                                modalActiveActivityTab === index
                                  ? 'border-blue-500 text-blue-600'
                                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                              }`}
                            >
                              Actividad {index + 1}
                            </button>
                          ))}
                        </div>
                        {/* Active Activity Content */}
                        <div className="p-3 bg-gray-50 rounded text-sm">
                          <p><strong>Nombre:</strong> {selectedFundacion.actividades[modalActiveActivityTab].nombre}</p>
                          {selectedFundacion.actividades[modalActiveActivityTab].clasificacion1 && (
                            <p><strong>Clasificación:</strong> {selectedFundacion.actividades[modalActiveActivityTab].clasificacion1}</p>
                          )}
                          {selectedFundacion.actividades[modalActiveActivityTab].funcion1 && (
                            <p><strong>Función:</strong> {selectedFundacion.actividades[modalActiveActivityTab].funcion1}</p>
                          )}
                        </div>
                      </div>
                    )
                  ) : (
                    <p className="text-gray-500 text-sm">No hay actividades registradas</p>
                  )}
                </div>

                {/* Patronos */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">
                    Patronos ({selectedFundacion.patronos.length})
                  </h3>
                  {selectedFundacion.patronos.length > 0 ? (
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {selectedFundacion.patronos.slice(0, 10).map((patron, index) => (
                        <div key={`patron-${index}`} className="text-sm">
                          <p><strong>{patron.nombre}</strong></p>
                          {patron.cargo && <p className="text-gray-600">{patron.cargo}</p>}
                        </div>
                      ))}
                      {selectedFundacion.patronos.length > 10 && (
                        <p className="text-sm text-gray-500">... y {selectedFundacion.patronos.length - 10} más</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm">No hay patronos registrados</p>
                  )}
                </div>
              </div>

              {/* Fines */}
              {selectedFundacion.fines && (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mb-4">
                    Fines
                  </h3>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {selectedFundacion.fines}
                  </p>
                </div>
              )}

              <div className="mt-6 flex justify-end">
                <button
                  onClick={closeModal}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}