import { NextRequest, NextResponse } from 'next/server';
import { connectToDatabase } from '@/lib/mongodb';

export async function GET(request: NextRequest) {
  try {
    const { db } = await connectToDatabase();
    const searchParams = request.nextUrl.searchParams;
    
    // Parse query parameters
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');
    const search = searchParams.get('search') || '';
    const provincia = searchParams.get('provincia') || '';
    const estado = searchParams.get('estado') || '';
    const actividad = searchParams.get('actividad') || '';
    const funcion = searchParams.get('funcion') || '';
    const sortBy = searchParams.get('sortBy') || 'name'; // 'name' or 'date'
    const sortOrder = searchParams.get('sortOrder') || 'asc'; // 'asc' or 'desc'
    
    // Build query
    const query: any = {};
    
    if (search) {
      query.$or = [
        { nombre: { $regex: search, $options: 'i' } },
        { nif: { $regex: search, $options: 'i' } },
        { fines: { $regex: search, $options: 'i' } }
      ];
    }
    
    if (provincia) {
      query['direccionEstatutaria.provincia'] = provincia;
    }
    
    if (estado) {
      query.estado = estado;
    }
    
    if (actividad) {
      query['actividades.clasificacion1'] = { $regex: actividad, $options: 'i' };
    }
    
    if (funcion) {
      query['actividades.funcion1'] = { $regex: funcion, $options: 'i' };
    }
    
    // Build sort criteria
    const sortCriteria: any = {};
    if (sortBy === 'date') {
      sortCriteria.fechaConstitucion = sortOrder === 'asc' ? 1 : -1;
    } else {
      sortCriteria.nombre = sortOrder === 'asc' ? 1 : -1;
    }
    
    // Get total count
    const total = await db.collection('fundaciones').countDocuments(query);
    
    // Get paginated results
    const fundaciones = await db.collection('fundaciones')
      .find(query)
      .sort(sortCriteria)
      .skip((page - 1) * limit)
      .limit(limit)
      .toArray();
    
    return NextResponse.json({
      data: fundaciones,
      total,
      page,
      limit,
      totalPages: Math.ceil(total / limit)
    });
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

// Get single foundation by ID
export async function POST(request: NextRequest) {
  try {
    const { db } = await connectToDatabase();
    const { id } = await request.json();
    
    const fundacion = await db.collection('fundaciones').findOne({ _id: parseInt(id) } as any);
    
    if (!fundacion) {
      return NextResponse.json(
        { error: 'Fundación no encontrada' },
        { status: 404 }
      );
    }
    
    return NextResponse.json(fundacion);
    
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}