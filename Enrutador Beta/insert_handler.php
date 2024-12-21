<?php
// config.php - Configuración de la base de datos
$host = 'localhost';
$dbname = 'gestionrutas';
$username = 'root';
$password = '';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    http_response_code(500);
    echo json_encode(['error' => 'Error de conexión: ' . $e->getMessage()]);
    exit;
}

// Función para convertir el formato de fecha
function convertirFecha($fecha) {
    if (empty($fecha)) return null;
    
    // Detectar el formato de la fecha
    if (strpos($fecha, '/') !== false) {
        // Si la fecha incluye hora
        if (strpos($fecha, ':') !== false) {
            $datetime = DateTime::createFromFormat('d/m/Y H:i', $fecha);
        } else {
            $datetime = DateTime::createFromFormat('d/m/Y', $fecha);
        }
        
        if ($datetime === false) {
            return null;
        }
        
        return $datetime->format('Y-m-d');
    }
    
    return $fecha;
}

// Recibir los datos JSON
$data = json_decode(file_get_contents('php://input'), true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => 'No se recibieron datos válidos']);
    exit;
}

try {
    // Preparar la consulta SQL
    $sql = "INSERT INTO registros (
        asesor, 
        nombre_usuario, 
        direccion, 
        barrio_localidad, 
        telefono, 
        fecha_registro, 
        zona, 
        plan_internet, 
        ip, 
        comentarios
    ) VALUES (
        :asesor, 
        :nombre_usuario, 
        :direccion, 
        :barrio_localidad, 
        :telefono, 
        :fecha_registro, 
        :zona, 
        :plan_internet, 
        :ip, 
        :comentarios
    )";

    $stmt = $pdo->prepare($sql);

    // Insertar cada registro
    $pdo->beginTransaction();
    
    foreach ($data as $row) {
        // Convertir la fecha al formato correcto
        $fecha_registro = convertirFecha($row['Fecha Registro']);
        
        $stmt->execute([
            ':asesor' => $row['Asesor'] ?? null,
            ':nombre_usuario' => $row['Numero/nombre usuario'] ?? null,
            ':direccion' => $row['Dirección'] ?? null,
            ':barrio_localidad' => $row['Barrio/Localidad'] ?? null,
            ':telefono' => $row['Telefono'] ?? null,
            ':fecha_registro' => $fecha_registro,
            ':zona' => $row['Zona'] ?? null,
            ':plan_internet' => $row['Plan Internet'] ?? null,
            ':ip' => $row['IP'] ?? null,
            ':comentarios' => $row['Comentarios'] ?? null
        ]);
    }

    $pdo->commit();
    echo json_encode(['success' => true, 'message' => 'Datos insertados correctamente']);

} catch (PDOException $e) {
    $pdo->rollBack();
    http_response_code(500);
    echo json_encode(['error' => 'Error al insertar datos: ' . $e->getMessage()]);
}
?>