'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/layout/Header';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line, ResponsiveContainer, AreaChart, Area, RadialBarChart, RadialBar } from 'recharts';

interface Stats {
  total: number;
  byEstado: Array<{ _id: string; count: number }>;
  byProvincia: Array<{ _id: string; count: number }>;
  byActividad: Array<{ _id: string; count: number }>;
  byFuncion: Array<{ _id: string; count: number }>;
  yearlyTrends: Array<{ year: number; count: number }>;
  patronosStats: {
    totalPatronos: number;
    avgPatronos: number;
    maxPatronos: number;
    minPatronos: number;
  };
  fundadoresStats: {
    totalFundadores: number;
    avgFundadores: number;
  };
  activeFundacionesWithContact: number;
  activitiesDistribution: Array<{ _id: number; count: number }>;
  avgPatronosPerFoundation: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C', '#8DD1E1', '#D084D0'];

export default function Analytics() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/fundaciones/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
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

  if (!stats) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <p className="text-center text-gray-600">Error al cargar las estadísticas</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analíticas de Fundaciones
          </h1>
          <p className="text-gray-600">
            Visualización y análisis de datos de {stats.total.toLocaleString('es-ES')} fundaciones
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Fundaciones</h3>
            <p className="text-3xl font-bold text-gray-900">{stats.total.toLocaleString('es-ES')}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Fundaciones Activas</h3>
            <p className="text-3xl font-bold text-green-600">
              {stats.byEstado.find(s => s._id === 'Activa')?.count?.toLocaleString('es-ES') || '0'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {(((stats.byEstado.find(s => s._id === 'Activa')?.count || 0) / stats.total) * 100).toFixed(1)}%
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Con Contacto</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.activeFundacionesWithContact.toLocaleString('es-ES')}</p>
            <p className="text-xs text-gray-500 mt-1">Activas con info</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Patronos</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.patronosStats.totalPatronos.toLocaleString('es-ES')}</p>
            <p className="text-xs text-gray-500 mt-1">Promedio: {stats.patronosStats.avgPatronos.toFixed(1)}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Total Fundadores</h3>
            <p className="text-3xl font-bold text-orange-600">{stats.fundadoresStats.totalFundadores.toLocaleString('es-ES')}</p>
            <p className="text-xs text-gray-500 mt-1">Promedio: {stats.fundadoresStats.avgFundadores.toFixed(1)}</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Tipos de Función</h3>
            <p className="text-3xl font-bold text-pink-600">{stats.byFuncion.length}</p>
            <p className="text-xs text-gray-500 mt-1">Clasificaciones</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Estado Distribution */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución por Estado</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.byEstado}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ _id, percent }) => (percent && percent > 0.05) ? `${_id} ${(percent * 100).toFixed(0)}%` : ''}
                  outerRadius={90}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="_id"
                >
                  {stats.byEstado.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value.toLocaleString('es-ES')} fundaciones`, name]} />
                <Legend 
                  verticalAlign="bottom" 
                  height={36}
                  formatter={(value) => value.length > 15 ? value.substring(0, 15) + '...' : value}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top Provinces */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Provincias</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.byProvincia}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="_id" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Yearly Trends */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendencia Anual de Constitución</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.yearlyTrends} margin={{ left: 20, right: 30, top: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="year" 
                  type="number"
                  scale="linear"
                  domain={['dataMin', 'dataMax']}
                />
                <YAxis label={{ value: 'Fundaciones', angle: -90, position: 'insideLeft' }} />
                <Tooltip 
                  formatter={(value) => [`${value} fundaciones`, 'Constituidas']}
                  labelFormatter={(year) => `Año ${year}`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#8884d8" 
                  strokeWidth={2}
                  name="Fundaciones Constituidas"
                  dot={{ r: 3, fill: '#8884d8' }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Top Activities */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Actividades</h3>
            {stats.byActividad.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-gray-500">
                No hay datos de actividades disponibles
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={450}>
                <BarChart data={stats.byActividad} margin={{ left: 20, right: 20, top: 20, bottom: 100 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="_id"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={11}
                    interval={0}
                    tick={{ fontSize: 11 }}
                    tickFormatter={(value) => value.length > 15 ? value.substring(0, 15) + '...' : value}
                  />
                  <YAxis 
                    label={{ value: 'Fundaciones', angle: -90, position: 'insideLeft' }}
                    fontSize={11}
                    domain={[0, 'dataMax']}
                  />
                  <Tooltip 
                    formatter={(value) => [`${value.toLocaleString('es-ES')} fundaciones`, 'Cantidad']}
                    labelFormatter={(label) => `Actividad: ${label}`}
                  />
                  <Bar dataKey="count" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        
        {/* Additional Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-8">
          
          {/* Functions Distribution */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribución por Función</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.byFuncion}
                  cx="50%"
                  cy="45%"
                  labelLine={false}
                  label={({ percent }) => (percent && percent > 0.08) ? `${(percent * 100).toFixed(0)}%` : ''}
                  outerRadius={75}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="_id"
                >
                  {stats.byFuncion.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name) => [`${value.toLocaleString('es-ES')} fundaciones`, name]}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={50}
                  fontSize={10}
                  formatter={(value) => value.length > 20 ? value.substring(0, 20) + '...' : value}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          {/* Activities per Foundation Distribution */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividades por Fundación</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.activitiesDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="_id" 
                  label={{ value: 'Número de Actividades', position: 'insideBottom', offset: -5 }}
                />
                <YAxis label={{ value: 'Fundaciones', angle: -90, position: 'insideLeft' }} />
                <Tooltip 
                  labelFormatter={(value) => `${value} actividades`}
                  formatter={(value) => [`${value} fundaciones`, 'Cantidad']}
                />
                <Bar dataKey="count" fill="#FFBB28" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          {/* Patronos Statistics */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Estadísticas de Patronos</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Total Patronos</span>
                <span className="text-lg font-bold text-blue-600">{stats.patronosStats.totalPatronos.toLocaleString('es-ES')}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Promedio por Fundación</span>
                <span className="text-lg font-bold text-green-600">{stats.patronosStats.avgPatronos.toFixed(1)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Máximo</span>
                <span className="text-lg font-bold text-purple-600">{stats.patronosStats.maxPatronos}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
                <span className="text-sm font-medium text-gray-700">Mínimo</span>
                <span className="text-lg font-bold text-orange-600">{stats.patronosStats.minPatronos}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Provinces Table */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Fundaciones por Provincia</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Provincia
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cantidad
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.byProvincia.slice(0, 10).map((provincia, index) => (
                    <tr key={provincia._id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {provincia._id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {provincia.count.toLocaleString('es-ES')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Activities Table */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actividades Principales</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actividad
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cantidad
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.byActividad.slice(0, 10).map((actividad, index) => (
                    <tr key={actividad._id}>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        <div className="max-w-xs truncate" title={actividad._id}>
                          {actividad._id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {actividad.count.toLocaleString('es-ES')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {/* Functions Table */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Funciones Principales</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Función
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Cantidad
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stats.byFuncion.map((funcion, index) => (
                    <tr key={funcion._id}>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        <div className="max-w-xs truncate" title={funcion._id}>
                          {funcion._id}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {funcion.count.toLocaleString('es-ES')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        {/* Summary Insights */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-sm p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Resumen Ejecutivo</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Sector Más Activo</h3>
              <p className="text-xl font-bold text-blue-600 mb-2">
                {stats.byFuncion[0]?._id || 'N/A'}
              </p>
              <p className="text-sm text-gray-600">
                {stats.byFuncion[0]?.count.toLocaleString('es-ES')} fundaciones ({((stats.byFuncion[0]?.count / stats.total) * 100 || 0).toFixed(1)}%)
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Provincia Líder</h3>
              <p className="text-xl font-bold text-green-600 mb-2">
                {stats.byProvincia[0]?._id || 'N/A'}
              </p>
              <p className="text-sm text-gray-600">
                {stats.byProvincia[0]?.count.toLocaleString('es-ES')} fundaciones ({((stats.byProvincia[0]?.count / stats.total) * 100 || 0).toFixed(1)}%)
              </p>
            </div>
            
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Gobernanza</h3>
              <p className="text-xl font-bold text-purple-600 mb-2">
                {stats.patronosStats.avgPatronos.toFixed(1)}
              </p>
              <p className="text-sm text-gray-600">
                Patronos promedio por fundación
              </p>
            </div>
          </div>
          
          <div className="mt-6 bg-white rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Análisis de Conectividad</h3>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-2">Fundaciones activas con información de contacto</p>
                <div className="flex items-center space-x-4">
                  <span className="text-2xl font-bold text-blue-600">
                    {stats.activeFundacionesWithContact.toLocaleString('es-ES')}
                  </span>
                  <span className="text-sm text-gray-500">
                    de {stats.byEstado.find(s => s._id === 'Activa')?.count?.toLocaleString('es-ES') || '0'} activas
                  </span>
                </div>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-green-600">
                  {(((stats.activeFundacionesWithContact / ((stats.byEstado.find(s => s._id === 'Activa')?.count || 1))) * 100) || 0).toFixed(1)}%
                </p>
                <p className="text-sm text-gray-500">Conectividad</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}