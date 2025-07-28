import { NextResponse } from 'next/server';
import { connectToDatabase } from '@/lib/mongodb';

export async function GET() {
  try {
    const { db } = await connectToDatabase();
    const collection = db.collection('fundaciones');
    
    // Get provinces with counts
    const provinciasWithCounts = await collection.aggregate([
      { $match: { 'direccionEstatutaria.provincia': { $exists: true, $ne: null, $ne: '' } } },
      { $group: { _id: '$direccionEstatutaria.provincia', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    // Get states with counts
    const estadosWithCounts = await collection.aggregate([
      { $match: { estado: { $exists: true, $ne: null, $ne: '' } } },
      { $group: { _id: '$estado', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    // Get activities with counts
    const actividadesWithCounts = await collection.aggregate([
      { $unwind: '$actividades' },
      { $match: { 'actividades.clasificacion1': { $exists: true, $ne: null, $ne: '' } } },
      { $group: { _id: '$actividades.clasificacion1', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    // Get functions with counts
    const funcionesWithCounts = await collection.aggregate([
      { $unwind: '$actividades' },
      { $match: { 'actividades.funcion1': { $exists: true, $ne: null, $ne: '' } } },
      { $group: { _id: '$actividades.funcion1', count: { $sum: 1 } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    
    return NextResponse.json({
      provincias: provinciasWithCounts,
      estados: estadosWithCounts,
      actividades: actividadesWithCounts.filter(item => Boolean(item._id)),
      funciones: funcionesWithCounts.filter(item => Boolean(item._id))
    });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}