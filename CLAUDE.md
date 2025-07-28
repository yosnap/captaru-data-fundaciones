# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This project is a comprehensive web application for managing and analyzing Spanish foundations data. It consists of:

1. **Data Source**: `BBDD de fundaciones España actualizada 040724.xls` - Excel database of 5,657 Spanish foundations
2. **Migration Scripts**: Python scripts to analyze and migrate Excel data to MongoDB
3. **Frontend Application**: Next.js/TypeScript web application with analytics and export features

## Project Structure

```
├── BBDD de fundaciones España actualizada 040724.xls    # Original Excel data
├── migration-scripts/                                   # Python migration tools
│   ├── analyze-excel.py                                # Excel structure analysis
│   ├── migrate-to-mongodb.py                          # MongoDB migration script
│   └── excel_analysis.json                            # Analysis results
├── fundaciones-frontend/                              # Next.js application
│   ├── src/app/                                       # App router pages
│   │   ├── page.tsx                                   # Main dashboard
│   │   ├── analytics/page.tsx                         # Analytics charts
│   │   ├── export/page.tsx                           # Data export tool
│   │   ├── data/page.tsx                             # Detailed data view
│   │   └── api/fundaciones/                          # API routes
│   ├── src/components/                               # React components
│   └── src/lib/                                      # Utilities and DB connection
├── requirements.txt                                   # Python dependencies
└── venv/                                             # Python virtual environment
```

## Common Development Commands

### Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Excel analysis
python migration-scripts/analyze-excel.py

# Run MongoDB migration (requires MongoDB running)
python migration-scripts/migrate-to-mongodb.py
```

### Next.js Frontend
```bash
cd fundaciones-frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Data Architecture

### Excel Data Structure
- **5,657 foundations** with 256 columns
- Key fields: name, registration number, NIF, status, addresses, activities, board members
- Nested structures for: addresses, activities (up to 4), founders (up to 30), board members (up to 31), executives (up to 12)

### MongoDB Schema
```javascript
{
  _id: number,                    // Foundation ID
  nombre: string,                 // Name
  numRegistro: string,           // Registration number
  estado: string,                // Status (ACTIVA, INACTIVA, EXTINGUIDA)
  nif: string,                   // Tax ID
  direccionEstatutaria: {...},   // Statutory address
  direccionNotificacion: {...},  // Notification address
  actividades: [...],            // Activities array
  fundadores: [...],             // Founders array
  patronos: [...],               // Board members array
  directivos: [...],             // Executives array
  organos: [...],                // Governing bodies array
  metadata: {...}                // Migration metadata
}
```

## API Endpoints

- `GET /api/fundaciones` - Paginated foundation listing with filters
- `GET /api/fundaciones/stats` - Statistics and analytics data  
- `POST /api/fundaciones/export` - Custom data export (CSV/JSON)

## Key Features

1. **Data Management**: View, search, and filter 5,657 foundations
2. **Analytics Dashboard**: Charts showing distribution by province, status, activities, yearly trends
3. **Export System**: Customizable CSV/JSON export with field selection
4. **Responsive Design**: Mobile-friendly interface with Tailwind CSS

## Environment Setup

### Required Environment Variables
```bash
# MongoDB connection
MONGODB_URI=mongodb://localhost:27017/fundaciones_espana  
MONGODB_DB_NAME=fundaciones_espana
```

### MongoDB Setup
- Use local MongoDB instance or MongoDB Atlas
- Database name: `fundaciones_espana`
- Collection: `fundaciones`
- Indexes created on: nombre, nif, estado, direccionEstatutaria.provincia

## Working with the Data

- Excel file has Spanish content and nested XML-like column structure
- Date format: DD/MM/YY (040724 = July 4, 2024)  
- Migration script handles data cleaning and restructuring
- Frontend uses TypeScript interfaces for type safety