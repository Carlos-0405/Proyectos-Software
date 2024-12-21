<?php
$host = 'localhost';
$dbname = 'gestionrutas';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $query = "SELECT * FROM registros ORDER BY fecha_registro DESC";
    $stmt = $pdo->prepare($query);
    $stmt->execute();
    
    $registros = $stmt->fetchAll(PDO::FETCH_ASSOC);
    
    echo json_encode(['data' => $registros]);
    
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
?>