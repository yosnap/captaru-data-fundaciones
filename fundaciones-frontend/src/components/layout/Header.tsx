'use client';

import Link from 'next/link';
import { Home, BarChart3, Download, Database } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-gray-900">
              Fundaciones España
            </Link>
          </div>
          
          <nav className="flex space-x-8">
            <Link 
              href="/" 
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
            >
              <Home size={18} />
              <span>Inicio</span>
            </Link>
            
            <Link 
              href="/analytics" 
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
            >
              <BarChart3 size={18} />
              <span>Analíticas</span>
            </Link>
            
            <Link 
              href="/export" 
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
            >
              <Download size={18} />
              <span>Exportar</span>
            </Link>
            
            <Link 
              href="/data" 
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition"
            >
              <Database size={18} />
              <span>Datos</span>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}