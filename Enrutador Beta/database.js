const mysql = require('mysql');

const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'Enrutador'
});

db.connect(err => {
    if (err) throw err;
    console.log('Conectado a la base de datos');
});

module.exports = db;