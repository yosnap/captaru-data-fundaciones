'use client';

import { useState } from 'react';
import Header from '@/components/layout/Header';
import { Download, Settings, Check, AlertCircle } from 'lucide-react';

interface ExportFilters {
  search: string;
  provincia: string;
  estado: string;
  actividad: string;
}

const availableFields = [
  { key: '_id', label: 'ID', category: 'basic' },
  { key: 'nombre', label: 'Nombre', category: 'basic' },
  { key: 'numRegistro', label: 'Número de Registro', category: 'basic' },
  { key: 'nif', label: 'NIF', category: 'basic' },
  { key: 'estado', label: 'Estado', category: 'basic' },
  { key: 'fechaConstitucion', label: 'Fecha Constitución', category: 'basic' },
  { key: 'fechaInscripcion', label: 'Fecha Inscripción', category: 'basic' },
  { key: 'fines', label: 'Fines', category: 'basic' },
  
  // Dirección Estatutaria
  { key: 'direccionEstatutaria.domicilio', label: 'Domicilio Estatutario', category: 'address' },
  { key: 'direccionEstatutaria.provincia', label: 'Provincia Estatutaria', category: 'address' },
  { key: 'direccionEstatutaria.codigoPostal', label: 'Código Postal Estatutario', category: 'address' },
  { key: 'direccionEstatutaria.telefono', label: 'Teléfono', category: 'address' },
  { key: 'direccionEstatutaria.email', label: 'Email', category: 'address' },
  { key: 'direccionEstatutaria.web', label: 'Web', category: 'address' },
  
  // Dirección Notificación
  { key: 'direccionNotificacion.domicilio', label: 'Domicilio Notificación', category: 'address' },
  { key: 'direccionNotificacion.provincia', label: 'Provincia Notificación', category: 'address' },
  { key: 'direccionNotificacion.localidad', label: 'Localidad Notificación', category: 'address' },
  
  // Arrays (will be joined)
  { key: 'actividades', label: 'Actividades', category: 'related' },
  { key: 'fundadores', label: 'Fundadores', category: 'related' },
  { key: 'patronos', label: 'Patronos', category: 'related' },
  { key: 'directivos', label: 'Directivos', category: 'related' },
  { key: 'organos', label: 'Órganos', category: 'related' },
];

const fieldCategories = {
  basic: 'Información Básica',
  address: 'Direcciones',
  related: 'Información Relacionada'
};

export default function Export() {
  const [filters, setFilters] = useState<ExportFilters>({
    search: '',
    provincia: '',
    estado: '',
    actividad: ''
  });
  
  const [selectedFields, setSelectedFields] = useState<string[]>([
    '_id', 'nombre', 'numRegistro', 'estado', 'direccionEstatutaria.provincia'
  ]);
  
  const [format, setFormat] = useState<'csv' | 'json'>('csv');
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleFieldToggle = (fieldKey: string) => {
    setSelectedFields(prev => 
      prev.includes(fieldKey) 
        ? prev.filter(f => f !== fieldKey)
        : [...prev, fieldKey]
    );
  };

  const selectAllFields = (category: string) => {
    const categoryFields = availableFields
      .filter(field => field.category === category)
      .map(field => field.key);
    
    setSelectedFields(prev => {
      const newFields = [...prev];
      categoryFields.forEach(field => {
        if (!newFields.includes(field)) {
          newFields.push(field);
        }
      });
      return newFields;
    });
  };

  const clearAllFields = (category: string) => {
    const categoryFields = availableFields
      .filter(field => field.category === category)
      .map(field => field.key);
    
    setSelectedFields(prev => prev.filter(field => !categoryFields.includes(field)));
  };

  const handleExport = async () => {
    if (selectedFields.length === 0) {
      alert('Por favor, selecciona al menos un campo para exportar');
      return;
    }

    setIsExporting(true);
    setExportStatus('idle');

    try {
      const response = await fetch('/api/fundaciones/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filters,
          fields: selectedFields,
          format
        })
      });

      if (!response.ok) {
        throw new Error('Error en la exportación');
      }

      // Download the file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `fundaciones_export_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setExportStatus('success');
    } catch (error) {
      console.error('Export error:', error);
      setExportStatus('error');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Exportar Datos
          </h1>
          <p className="text-gray-600">
            Personaliza y exporta los datos de fundaciones en formato CSV o JSON
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Filters Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Settings className="mr-2" size={20} />
                Filtros de Datos
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Buscar
                  </label>
                  <input
                    type="text"
                    placeholder="Nombre, NIF o fines..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value})}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provincia
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={filters.provincia}
                    onChange={(e) => setFilters({...filters, provincia: e.target.value})}
                  >
                    <option value="">Todas las provincias</option>
                    <option value="Madrid">Madrid</option>
                    <option value="Barcelona">Barcelona</option>
                    <option value="Valencia">Valencia</option>
                    <option value="Sevilla">Sevilla</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={filters.estado}
                    onChange={(e) => setFilters({...filters, estado: e.target.value})}
                  >
                    <option value="">Todos los estados</option>
                    <option value="ACTIVA">Activa</option>
                    <option value="INACTIVA">Inactiva</option>
                    <option value="EXTINGUIDA">Extinguida</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Formato de Exportación
                  </label>
                  <div className="flex space-x-4">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="format"
                        value="csv"
                        checked={format === 'csv'}
                        onChange={(e) => setFormat(e.target.value as 'csv' | 'json')}
                        className="mr-2"
                      />
                      CSV
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="format"
                        value="json"
                        checked={format === 'json'}
                        onChange={(e) => setFormat(e.target.value as 'csv' | 'json')}
                        className="mr-2"
                      />
                      JSON
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Export Button */}
            <button
              onClick={handleExport}
              disabled={isExporting || selectedFields.length === 0}
              className={`w-full px-6 py-3 rounded-lg font-medium transition flex items-center justify-center space-x-2 ${
                isExporting || selectedFields.length === 0
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isExporting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Exportando...</span>
                </>
              ) : (
                <>
                  <Download size={20} />
                  <span>Exportar Datos</span>
                </>
              )}
            </button>

            {/* Export Status */}
            {exportStatus === 'success' && (
              <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-lg flex items-center">
                <Check className="mr-2" size={16} />
                Exportación completada exitosamente
              </div>
            )}

            {exportStatus === 'error' && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center">
                <AlertCircle className="mr-2" size={16} />
                Error durante la exportación. Inténtalo de nuevo.
              </div>
            )}
          </div>

          {/* Field Selection */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Seleccionar Campos ({selectedFields.length} seleccionados)
              </h2>

              {Object.entries(fieldCategories).map(([categoryKey, categoryLabel]) => {
                const categoryFields = availableFields.filter(field => field.category === categoryKey);
                const selectedCategoryFields = categoryFields.filter(field => selectedFields.includes(field.key));
                
                return (
                  <div key={categoryKey} className="mb-6">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-md font-medium text-gray-800">{categoryLabel}</h3>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => selectAllFields(categoryKey)}
                          className="text-xs text-blue-600 hover:text-blue-800"
                        >
                          Seleccionar todos
                        </button>
                        <button
                          onClick={() => clearAllFields(categoryKey)}
                          className="text-xs text-gray-600 hover:text-gray-800"
                        >
                          Limpiar
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {categoryFields.map(field => (
                        <label
                          key={field.key}
                          className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedFields.includes(field.key)}
                            onChange={() => handleFieldToggle(field.key)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="text-sm text-gray-700 truncate" title={field.label}>
                            {field.label}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}