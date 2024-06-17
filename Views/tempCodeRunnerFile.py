SELECT p.nombre AS titulo, d.nombre AS departamento,
            pc.candidato_id, c.nombre AS nombre_candidato, c.email, c.telefono
            FROM puestos p
            JOIN puestos_departamentos pd ON p.id = pd.puesto_id
            JOIN departamentos d ON pd.departamento_id = d.id
            LEFT JOIN puestos_candidatos pc ON p.id = pc.puesto_id
            LEFT JOIN candidatos c ON pc.candidato_id = c.id;