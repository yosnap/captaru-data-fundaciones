const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

async function createDatabaseBackup() {
  const client = new MongoClient('mongodb://localhost:27017');
  
  try {
    await client.connect();
    console.log('✅ Conectado a MongoDB');
    
    const db = client.db('fundaciones_espana');
    const collection = db.collection('fundaciones');
    
    // Obtener todos los documentos
    console.log('📥 Obteniendo todos los datos...');
    const allData = await collection.find({}).toArray();
    
    console.log(`📊 Total de documentos: ${allData.length}`);
    
    // Crear el backup como archivo JSON
    const backupData = {
      database: 'fundaciones_espana',
      collection: 'fundaciones',
      exportDate: new Date().toISOString(),
      totalDocuments: allData.length,
      data: allData
    };
    
    const backupPath = path.join(__dirname, 'database-backup.json');
    fs.writeFileSync(backupPath, JSON.stringify(backupData, null, 2));
    
    console.log(`✅ Backup creado en: ${backupPath}`);
    console.log(`📏 Tamaño del archivo: ${(fs.statSync(backupPath).size / 1024 / 1024).toFixed(2)} MB`);
    
    // Crear también un script de restauración
    const restoreScript = `const { MongoClient } = require('mongodb');
const fs = require('fs');

async function restoreDatabase() {
  const client = new MongoClient(process.env.MONGODB_URI || 'mongodb://localhost:27017');
  
  try {
    await client.connect();
    console.log('✅ Conectado a MongoDB');
    
    const backupData = JSON.parse(fs.readFileSync('./database-backup.json', 'utf8'));
    
    const db = client.db('fundaciones_espana');
    const collection = db.collection('fundaciones');
    
    // Limpiar colección existente
    await collection.deleteMany({});
    console.log('🗑️  Colección limpiada');
    
    // Insertar datos del backup
    console.log(\`📥 Restaurando \${backupData.totalDocuments} documentos...\`);
    await collection.insertMany(backupData.data);
    
    console.log('✅ Base de datos restaurada correctamente');
    
    // Verificar
    const count = await collection.countDocuments();
    console.log(\`📊 Documentos restaurados: \${count}\`);
    
  } catch (error) {
    console.error('❌ Error al restaurar:', error);
  } finally {
    await client.close();
  }
}

restoreDatabase();`;

    fs.writeFileSync(path.join(__dirname, 'restore-database.js'), restoreScript);
    console.log('✅ Script de restauración creado: restore-database.js');
    
  } catch (error) {
    console.error('❌ Error:', error);
  } finally {
    await client.close();
  }
}

createDatabaseBackup();