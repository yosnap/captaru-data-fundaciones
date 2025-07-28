import { NextRequest, NextResponse } from 'next/server';
import { connectToDatabase } from '@/lib/mongodb';

export async function GET(request: NextRequest) {
  try {
    const { db } = await connectToDatabase();
    
    // Get comprehensive statistics
    const [
      totalFundaciones,
      estadoStats,
      provinciaStats,
      actividadStats,
      funcionStats,
      patronosStats,
      fundadoresStats,
      activeFundaciones,
      activitiesPerFoundation,
      avgPatronosPerFoundation
    ] = await Promise.all([
      // Total count
      db.collection('fundaciones').countDocuments(),
      
      // By estado
      db.collection('fundaciones').aggregate([
        { $group: { _id: '$estado', count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ]).toArray(),
      
      // By provincia
      db.collection('fundaciones').aggregate([
        { $match: { 'direccionEstatutaria.provincia': { $exists: true, $ne: null } } },
        { $group: { _id: '$direccionEstatutaria.provincia', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ]).toArray(),
      
      // By actividad
      db.collection('fundaciones').aggregate([
        { $unwind: '$actividades' },
        { $match: { 'actividades.clasificacion1': { $exists: true, $ne: null } } },
        { $group: { _id: '$actividades.clasificacion1', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $limit: 10 }
      ]).toArray(),
      
      // By funcion
      db.collection('fundaciones').aggregate([
        { $unwind: '$actividades' },
        { $match: { 'actividades.funcion1': { $exists: true, $ne: null } } },
        { $group: { _id: '$actividades.funcion1', count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ]).toArray(),
      
      // Patronos statistics
      db.collection('fundaciones').aggregate([
        { $match: { patronos: { $exists: true, $ne: [] } } },
        { $project: { patronosCount: { $size: '$patronos' } } },
        { $group: {
          _id: null,
          totalPatronos: { $sum: '$patronosCount' },
          avgPatronos: { $avg: '$patronosCount' },
          maxPatronos: { $max: '$patronosCount' },
          minPatronos: { $min: '$patronosCount' }
        }}
      ]).toArray(),
      
      // Fundadores count
      db.collection('fundaciones').aggregate([
        { $match: { fundadores: { $exists: true, $ne: [] } } },
        { $project: { fundadoresCount: { $size: '$fundadores' } } },
        { $group: {
          _id: null,
          totalFundadores: { $sum: '$fundadoresCount' },
          avgFundadores: { $avg: '$fundadoresCount' }
        }}
      ]).toArray(),
      
      // Active foundations with contact info
      db.collection('fundaciones').countDocuments({
        estado: 'Activa',
        $or: [
          { 'direccionEstatutaria.email': { $exists: true, $ne: null, $ne: '' } },
          { 'direccionEstatutaria.web': { $exists: true, $ne: null, $ne: '' } },
          { 'direccionEstatutaria.telefono': { $exists: true, $ne: null, $ne: '' } }
        ]
      }),
      
      // Activities distribution
      db.collection('fundaciones').aggregate([
        { $project: { actividadesCount: { $size: '$actividades' } } },
        { $group: {
          _id: '$actividadesCount',
          count: { $sum: 1 }
        }},
        { $sort: { _id: 1 } }
      ]).toArray(),
      
      // Average patronos per foundation
      db.collection('fundaciones').aggregate([
        { $match: { patronos: { $exists: true, $ne: [] } } },
        { $group: {
          _id: null,
          avgPatronos: { $avg: { $size: '$patronos' } }
        }}
      ]).toArray()
    ]);
    
    // Get yearly trends (based on fechaConstitucion) - dates are in DD/MM/YYYY format
    const yearlyTrends = await db.collection('fundaciones').aggregate([
      { 
        $match: { 
          fechaConstitucion: { $exists: true, $ne: null, $ne: '' },
          fechaConstitucion: { $regex: /^\d{2}\/\d{2}\/\d{4}$/ }
        } 
      },
      {
        $project: {
          year: { $substr: ['$fechaConstitucion', 6, 4] }  // Extract year from DD/MM/YYYY
        }
      },
      {
        $group: {
          _id: '$year',
          count: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } },
      {
        $match: {
          _id: { $gte: '1990' }
        }
      }
    ]).toArray();
    
    return NextResponse.json({
      total: totalFundaciones,
      byEstado: estadoStats,
      byProvincia: provinciaStats,
      byActividad: actividadStats,
      byFuncion: funcionStats,
      yearlyTrends: yearlyTrends.map(item => ({
        year: parseInt(item._id),
        count: item.count
      })),
      patronosStats: patronosStats[0] || { totalPatronos: 0, avgPatronos: 0, maxPatronos: 0, minPatronos: 0 },
      fundadoresStats: fundadoresStats[0] || { totalFundadores: 0, avgFundadores: 0 },
      activeFundacionesWithContact: activeFundaciones,
      activitiesDistribution: activitiesPerFoundation,
      avgPatronosPerFoundation: avgPatronosPerFoundation[0]?.avgPatronos || 0
    });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}