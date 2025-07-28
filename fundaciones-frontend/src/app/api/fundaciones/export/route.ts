import { NextRequest, NextResponse } from 'next/server';
import { connectToDatabase } from '@/lib/mongodb';

export async function POST(request: NextRequest) {
  try {
    const { db } = await connectToDatabase();
    const body = await request.json();
    
    const {
      filters = {},
      fields = [],
      format = 'csv'
    } = body;
    
    // Build query from filters
    const query: any = {};
    
    if (filters.search) {
      query.$or = [
        { nombre: { $regex: filters.search, $options: 'i' } },
        { nif: { $regex: filters.search, $options: 'i' } },
        { fines: { $regex: filters.search, $options: 'i' } }
      ];
    }
    
    if (filters.provincia) {
      query['direccionEstatutaria.provincia'] = filters.provincia;
    }
    
    if (filters.estado) {
      query.estado = filters.estado;
    }
    
    if (filters.actividad) {
      query['actividades.clasificacion1'] = { $regex: filters.actividad, $options: 'i' };
    }
    
    // Build projection
    const projection: any = {};
    if (fields.length > 0) {
      fields.forEach((field: string) => {
        projection[field] = 1;
      });
      // Always include _id
      projection._id = 1;
    }
    
    // Get data
    const fundaciones = await db.collection('fundaciones')
      .find(query)
      .project(projection)
      .toArray();
    
    if (format === 'csv') {
      // Convert to CSV
      const csv = convertToCSV(fundaciones, fields.length > 0 ? fields : null);
      
      return new NextResponse(csv, {
        headers: {
          'Content-Type': 'text/csv',
          'Content-Disposition': `attachment; filename="fundaciones_export_${new Date().toISOString().split('T')[0]}.csv"`
        }
      });
    } else {
      // Return JSON
      return NextResponse.json(fundaciones, {
        headers: {
          'Content-Type': 'application/json',
          'Content-Disposition': `attachment; filename="fundaciones_export_${new Date().toISOString().split('T')[0]}.json"`
        }
      });
    }
    
  } catch (error) {
    console.error('Export Error:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

function convertToCSV(data: any[], fields: string[] | null): string {
  if (data.length === 0) return '';
  
  // Flatten nested objects
  const flattenObject = (obj: any, prefix = ''): any => {
    return Object.keys(obj).reduce((acc: any, key) => {
      const pre = prefix.length ? prefix + '_' : '';
      
      if (obj[key] === null || obj[key] === undefined) {
        acc[pre + key] = '';
      } else if (typeof obj[key] === 'object' && !Array.isArray(obj[key]) && !(obj[key] instanceof Date)) {
        Object.assign(acc, flattenObject(obj[key], pre + key));
      } else if (Array.isArray(obj[key])) {
        acc[pre + key] = obj[key].map((item: any) => 
          typeof item === 'object' ? JSON.stringify(item) : item
        ).join('; ');
      } else {
        acc[pre + key] = obj[key];
      }
      
      return acc;
    }, {});
  };
  
  const flatData = data.map(item => flattenObject(item));
  
  // Get headers
  const headers = fields || Object.keys(flatData[0]);
  
  // Create CSV
  const csvRows = [];
  
  // Add headers
  csvRows.push(headers.map(h => `"${h}"`).join(','));
  
  // Add data
  for (const row of flatData) {
    const values = headers.map(header => {
      const value = row[header];
      if (value === null || value === undefined) return '""';
      const escaped = String(value).replace(/"/g, '""');
      return `"${escaped}"`;
    });
    csvRows.push(values.join(','));
  }
  
  return csvRows.join('\\n');
}