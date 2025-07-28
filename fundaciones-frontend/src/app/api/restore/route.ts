import { NextRequest, NextResponse } from 'next/server';
import { connectToDatabase } from '@/lib/mongodb';

// Proteger el endpoint con una API key simple
const RESTORE_API_KEY = process.env.RESTORE_API_KEY || 'your-secure-api-key-here';

export async function POST(request: NextRequest) {
  try {
    // Verificar API key
    const apiKey = request.headers.get('x-api-key');
    if (apiKey !== RESTORE_API_KEY) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { data } = await request.json();
    
    if (!data || !Array.isArray(data)) {
      return NextResponse.json(
        { error: 'Invalid data format' },
        { status: 400 }
      );
    }

    const { db } = await connectToDatabase();
    const collection = db.collection('fundaciones');
    
    // Limpiar colección existente
    await collection.deleteMany({});
    
    // Insertar nuevos datos
    const result = await collection.insertMany(data);
    
    // Crear índices
    await collection.createIndex({ nombre: 1 });
    await collection.createIndex({ estado: 1 });
    await collection.createIndex({ nif: 1 });
    await collection.createIndex({ 'direccionEstatutaria.provincia': 1 });
    await collection.createIndex({ 'actividades.clasificacion1': 1 });
    
    return NextResponse.json({
      success: true,
      message: 'Database restored successfully',
      documentsInserted: result.insertedCount
    });
    
  } catch (error) {
    console.error('Restore error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

// Endpoint para restaurar por lotes (para archivos grandes)
export async function PUT(request: NextRequest) {
  try {
    // Verificar API key
    const apiKey = request.headers.get('x-api-key');
    if (apiKey !== RESTORE_API_KEY) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { batch, batchNumber, totalBatches, clearFirst } = await request.json();
    
    if (!batch || !Array.isArray(batch)) {
      return NextResponse.json(
        { error: 'Invalid batch format' },
        { status: 400 }
      );
    }

    const { db } = await connectToDatabase();
    const collection = db.collection('fundaciones');
    
    // Limpiar colección en el primer lote
    if (clearFirst && batchNumber === 1) {
      await collection.deleteMany({});
    }
    
    // Insertar lote
    const result = await collection.insertMany(batch);
    
    // Crear índices en el último lote
    if (batchNumber === totalBatches) {
      await collection.createIndex({ nombre: 1 });
      await collection.createIndex({ estado: 1 });
      await collection.createIndex({ nif: 1 });
      await collection.createIndex({ 'direccionEstatutaria.provincia': 1 });
      await collection.createIndex({ 'actividades.clasificacion1': 1 });
    }
    
    return NextResponse.json({
      success: true,
      message: `Batch ${batchNumber}/${totalBatches} processed`,
      documentsInserted: result.insertedCount
    });
    
  } catch (error) {
    console.error('Batch restore error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}