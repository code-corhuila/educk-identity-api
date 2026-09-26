"""
despachador_flujo_continuo_trello.py - Despachador de Flujo Continuo con Grounding Real
========================================================================================
EduTrack — Sistemas Distribuidos 2026-B
Líder Técnica: @XimenaChala

Funcionalidades Clave:
1. Grounding Real (Cero Tareas Ficticias):
   Inspecciona físicamente cada repositorio local antes de crear una tarjeta para verificar
   qué componente, archivo o migración falta por construir según la especificación de Corte 2 (educk-docs).
2. Descripción Enriquecida:
   Incluye repositorio y puerto exacto, ruta del archivo a crear/modificar, estado local
   y criterios de aceptación técnicos detallados.
3. Mantenimiento de Flujo Continuo:
   Garantiza CUPO ESTRICTO DE 5 TARJETAS ACTIVAS EJECUTABLES por integrante (Ximena, Celeste, Juan Camilo, Stephan).
4. Límite de Responsabilidad del Bot:
   El bot ÚNICAMENTE redacta la tarjeta con directrices arquitectónicas y diagnóstico en disco.
   Los 4 desarrolladores humanos escriben el código, corren tests, abren PRs y mueven las tarjetas.
5. Candados de Seguridad:
   - Anti-Spam: Realiza GET a la lista destino antes de POST; omite si el título ya existe.
   - Anti-Bloqueo: Omite del conteo activo las tarjetas con etiqueta 'Bloqueado'.
"""

import os
import sys
import json
import certifi
import requests
from pathlib import Path

# Configurar bundle de certificados SSL de certifi para validación estricta en Python 3.12
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Configuración de salida UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

AUTO_DIR = Path(__file__).parent.resolve()
MUSIC_DIR = AUTO_DIR.parent.resolve()
CONFIG_FILE = AUTO_DIR / "trello_config.json"
ENV_FILE = AUTO_DIR / ".env"

# Auto-cargar .env si existe
if ENV_FILE.exists():
    try:
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip()
                if k and v and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

from gestor_colores_y_miembros import TEAM_MEMBERS_DIRECTORY

# Mapeo de listas destino en Trello
LIST_FRONTEND = "6aaf06e126a2d747dfe4f97b"  # Aplicación Web (Frontend)
LIST_BACKEND  = "6aaf06dbf860942835979e03"  # Backend & Bases de Datos
LIST_DONE     = "6aaf1756df3b5bcabf0307c9"  # ✅ Aprobado y Mergeado
LIST_REVIEW   = "6aaf17a63d79b6e2b696aa08"  # Realizado y revisar
LIST_FIX      = "6aaf17553a39d35efea465a1"  # ⚠️ Corregir

LABELS_MAP = {
    "celestedussan": "6aaf2085118b66f80314ebd8",           # Celeste (sky)
    "juancamilopenagosmolina": "6aaef11b808b8de50ad92384", # Verde (green)
    "stephanvargasquiroga": "6aaef11b808b8de50ad92388",    # Morado (purple)
    "ximenachala": "6aaef11b808b8de50ad92385"             # Amarillo (yellow)
}

# ==============================================================================
# CATÁLOGO DE TAREAS CORTE 2 (GROUNDED EN educk-docs Y ESPECIFICACIÓN ARQUITECTURAL)
# ==============================================================================

ROADMAP_CATALOG = {
    "celestedussan": [
        {
            "id_task": "celeste_c2_01",
            "name": "Portal Académico: Filtros por Materia y Cálculo de Promedio (:3002)",
            "repo": "educk-academic-portal",
            "puerto": "3002",
            "target_list": LIST_FRONTEND,
            "target_file": "src/App.jsx",
            "que": "Implementar selector de materia y cálculo en tiempo real del promedio de corte en la tabla de calificaciones.",
            "criterios_tecnicos": [
                "Selector dropdown interactivo para filtrar notas por asignatura (Matemáticas, Sistemas Distribuidos, etc.).",
                "Cálculo automático del promedio ponderado/aritmético de corte sobre las calificaciones filtradas.",
                "Badge de estado visual del promedio (Verde si >= 3.0, Rojo si < 3.0).",
                "Diseño responsivo sin desbordamientos en resoluciones estándar de pantalla."
            ],
            "branch": "feat/HU-001-grade-filter-and-average-ui",
            "commit_msg": "feat(portal): filtros por materia y promedio ponderado en notas",
            "why": "Requerimiento HU-001 para que acudientes y docentes filtren notas por asignatura y visualicen el promedio de corte.",
            "verification_keywords": ["filtro", "promedio", "selector", "materia"]
        },
        {
            "id_task": "celeste_c2_02",
            "name": "Portal Asistencia: Selector de Fecha y Resumen de Sesión (:3003)",
            "repo": "educk-attendance-portal",
            "puerto": "3003",
            "target_list": LIST_FRONTEND,
            "target_file": "src/App.jsx",
            "que": "Añadir control de selección de fecha de clase, botón de guardar y panel resumen con total de presentes, ausentes y retardos.",
            "criterios_tecnicos": [
                "Selector de fecha (date picker) para registrar el pase de lista de una sesión específica.",
                "Controles individuales por estudiante para alternar estado: Presente, Ausente, Tarde o Justificado.",
                "Panel KPI superior con contadores en tiempo real de Presentes, Ausentes y Justificados.",
                "Botón de guardado con feedback visual de confirmación para el docente."
            ],
            "branch": "feat/HU-005-attendance-session-summary",
            "commit_msg": "feat(portal): selector de fecha y resumen KPI de asistencia de sesion",
            "why": "Requerimiento HU-005 para pase de lista diario fechado con consolidado inmediato de inasistencias.",
            "verification_keywords": ["fecha", "resumen", "presente", "ausente"]
        },
        {
            "id_task": "celeste_c2_03",
            "name": "Portal Identidad: Estado de Sesión, Rol y Logout (:3001)",
            "repo": "educk-identity-portal",
            "puerto": "3001",
            "target_list": LIST_FRONTEND,
            "target_file": "src/App.jsx",
            "que": "Implementar vista post-autenticación con tarjeta de perfil, badge de rol (Docente/Acudiente) y botón de cierre de sesión.",
            "criterios_tecnicos": [
                "Tarjeta de perfil que muestre Nombre, Email y Rol institucional tras iniciar sesión.",
                "Badge visual con el color correspondiente al rol del usuario según el Design System.",
                "Botón de Logout que limpie el token de sesión y restablezca el formulario de acceso.",
                "Manejo de mensajes de error ante credenciales incorrectas en el login."
            ],
            "branch": "feat/HU-003-session-user-profile",
            "commit_msg": "feat(portal): visualizacion de perfil autenticado y accion de logout",
            "why": "Requerimiento HU-003 para gestion visual de sesiones activas y seguridad en el cliente.",
            "verification_keywords": ["logout", "perfil", "rol", "badge"]
        },
        {
            "id_task": "celeste_c2_04",
            "name": "Portal Shell: Navegación Unificada de Microfrontends (:3000)",
            "repo": "educk-front",
            "puerto": "3000",
            "target_list": LIST_FRONTEND,
            "target_file": "src/App.jsx",
            "que": "Integrar iframe o contenedor dinámico para renderizar los microfrontends (:3001, :3002, :3003, :3005) desde el menú lateral del Shell.",
            "criterios_tecnicos": [
                "Menú lateral con enlaces a Identidad (:3001), Académico (:3002), Asistencia (:3003) y Comunicación (:3005).",
                "Área central con contenedor iframe o dynamic view que cargue el microfrontend seleccionado sin recargar la página completa.",
                "Indicadores visuales de estado activo/inactivo para cada microfrontend satélite.",
                "Diseño general consistente con la paleta de colores institucional EduTrack."
            ],
            "branch": "feat/GW-001-shell-microfrontend-embedding",
            "commit_msg": "feat(shell): integracion de portales desacoplados en panel central",
            "why": "Arquitectura de microfrontends desacoplados unificados bajo el contenedor principal EduTrack.",
            "verification_keywords": ["iframe", "navegacion", "microfrontend", "shell"]
        },
        {
            "id_task": "celeste_c2_05",
            "name": "Portal Comunicación: Visualización de Circulares y Avisos (:3005)",
            "repo": "educk-communication-portal",
            "puerto": "3005",
            "target_list": LIST_FRONTEND,
            "target_file": "src/App.jsx",
            "que": "Crear vista de bandeja de comunicados institucionales emitidos con filtros por categoría y fecha.",
            "criterios_tecnicos": [
                "Listado de comunicados con título, fecha de emisión, autor y preview del contenido.",
                "Filtro por tipo de circular (Urgente, General, Académico).",
                "Vista modal de lectura detallada al hacer clic sobre un comunicado.",
                "Indicador visual de comunicado leído / no leído."
            ],
            "branch": "feat/HU-004-communication-notices-board",
            "commit_msg": "feat(portal): bandeja de circulares institucionales con filtros por tipo",
            "why": "Requerimiento HU-004 y ADR-005 para canal de comunicación unificado hacia acudientes.",
            "verification_keywords": ["comunicado", "circular", "categoria", "bandeja"]
        }
    ],
    "juancamilopenagosmolina": [
        {
            "id_task": "camilo_c2_01",
            "name": "Persistencia Académica: Script Flyway de Índices de Rendimiento (:5432)",
            "repo": "educk-academic-db",
            "puerto": "5432",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V2__performance_indexes.sql",
            "que": "Crear migración Flyway V2__performance_indexes.sql con índices B-Tree en grades(student_id, subject_id) para optimizar consultas de boletines.",
            "criterios_tecnicos": [
                "Script SQL compatible con Flyway y PostgreSQL 16.",
                "Creación de índice compuesto B-Tree: `CREATE INDEX IF NOT EXISTS idx_grades_student_subject ON grades(student_id, subject_id);`",
                "Creación de índice en asignaciones: `CREATE INDEX IF NOT EXISTS idx_assignments_subject ON assignments(subject_id, due_date);`",
                "Ejecución idempotente y sin errores de sintaxis DDL."
            ],
            "branch": "feat/HU-001-academic-indexes-v2",
            "commit_msg": "feat(db): indices compuestos flyway para optimizacion de calificaciones",
            "why": "Optimización de base de datos PostgreSQL bajo estándar ADR-003 para consultas masivas de notas.",
            "verification_keywords": ["create index", "grades", "student_id"]
        },
        {
            "id_task": "camilo_c2_02",
            "name": "Persistencia Asistencia: Migración Flyway para Justificaciones (:5433)",
            "repo": "educk-attendance-db",
            "puerto": "5433",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V2__justifications.sql",
            "que": "Crear migración Flyway V2__justifications.sql añadiendo soporte para motivo de justificación y adjunto en tabla attendance_events.",
            "criterios_tecnicos": [
                "Script SQL compatible con Flyway y PostgreSQL 16.",
                "Alteración de tabla: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS justification_reason VARCHAR(500);`",
                "Añadir columna de timestamp: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS justified_at TIMESTAMP;`",
                "Añadir columna de enlace a comprobante: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS attachment_url VARCHAR(255);`"
            ],
            "branch": "feat/HU-005-attendance-justifications-schema",
            "commit_msg": "feat(db): soporte de justificaciones medicas en eventos de asistencia",
            "why": "Requerimiento HU-005 para justificación de inasistencias por parte de acudientes.",
            "verification_keywords": ["alter table", "justification", "attendance_events"]
        },
        {
            "id_task": "camilo_c2_03",
            "name": "Backend Asistencia: Validación de Invariantes y Estados de Asistencia (:8083)",
            "repo": "educk-attendance-api",
            "puerto": "8083",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/attendance/application/service/AttendanceService.java",
            "que": "Implementar validación de invariantes de dominio: impedir asistencia en fechas futuras y restringir estados a PRESENT, ABSENT, LATE, JUSTIFIED.",
            "criterios_tecnicos": [
                "Validación de fecha: Lanzar excepción de dominio si la fecha del evento de asistencia es posterior a `LocalDate.now()`.",
                "Validación de estados válidos mediante Enum `AttendanceStatus` (PRESENT, ABSENT, LATE, JUSTIFIED).",
                "Disparo del evento AMQP `StudentAbsent` hacia RabbitMQ cuando el estado registrado sea ABSENT.",
                "Pruebas unitarias que confirmen el rechazo de registros en fechas futuras."
            ],
            "branch": "feat/HU-005-attendance-invariants-validation",
            "commit_msg": "feat(attendance): validacion estricta de invariantes y fechas en pase de lista",
            "why": "Requerimiento HU-005 para garantizar consistencia temporal y evitar registros erróneos de asistencia.",
            "verification_keywords": ["future", "absent", "invariants", "localdate"]
        },
        {
            "id_task": "camilo_c2_04",
            "name": "Backend Académico: Cálculo Ponderado de Corte y Promedio (:8082)",
            "repo": "educk-academic-api",
            "puerto": "8082",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/academic/application/service/GradeService.java",
            "que": "Implementar lógica de cálculo de nota definitiva por asignatura evaluando ponderaciones y retornando estado APROBADO (>= 3.0) o REPROBADO.",
            "criterios_tecnicos": [
                "Validación de rango: Cada calificación debe ubicarse en el rango de 0.0 a 5.0.",
                "Cálculo ponderado multiplicando notas por porcentaje de evaluación (suma total = 100%).",
                "Retorno estructurado con estado: `APROBADO` si nota >= 3.0, `REPROBADO` si < 3.0.",
                "Disparo de evento AMQP `GradeCreated` con payload JSON ante cada inserción de calificación."
            ],
            "branch": "feat/HU-001-grade-weighted-average",
            "commit_msg": "feat(academic): calculo de promedio de corte y determinacion de aprobacion",
            "why": "Requerimiento HU-001 para consolidación de notas académicas y boletines institucionales.",
            "verification_keywords": ["weighted", "aprobado", "reprobado", "promedio"]
        },
        {
            "id_task": "camilo_c2_05",
            "name": "Persistencia Comunicación: Esquema Inicial de Circulares (:5434)",
            "repo": "educk-communication-db",
            "puerto": "5434",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V1__init_communication.sql",
            "que": "Crear migración inicial Flyway para el microservicio de comunicación con tablas announcements y acknowledgments.",
            "criterios_tecnicos": [
                "Esquema DDL para PostgreSQL 16 con aislamiento total (ADR-003).",
                "Tabla `announcements` con id UUID PRIMARY KEY, title, content, author_id, created_at.",
                "Tabla `acknowledgments` (acuse de recibo por acudiente) con claves foráneas e índices.",
                "Script idempotente con timestamps UTC."
            ],
            "branch": "feat/HU-004-communication-db-schema",
            "commit_msg": "feat(db): esquema inicial flyway para circulares y comunicados",
            "why": "Aislamiento de persistencia del módulo de comunicación bajo ADR-003 y ADR-005.",
            "verification_keywords": ["create table", "announcements", "acknowledgments", "uuid"]
        },
        {
            "id_task": "camilo_c2_06",
            "name": "Backend Académico: Transactional Outbox para Eventos GradeCreated (:8082)",
            "repo": "educk-academic-api",
            "puerto": "8082",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/academic/infrastructure/persistence/OutboxEventEntity.java",
            "que": "Implementar entidad y repositorio para outbox_events en academic-api según ADR-007 para garantizar publicación atómica de GradeCreated.",
            "criterios_tecnicos": [
                "Entidad JPA `OutboxEventEntity` con id UUID, aggregateType, aggregateId, eventType, payload JSONB y status.",
                "Repositorio Spring Data `OutboxEventRepository` con método para consultar eventos PENDING.",
                "Alineado con ADR-007 para eliminar peligro de dual-write en calificaciones.",
                "Inserción de evento en la misma transacción `@Transactional` que guarda la calificación."
            ],
            "branch": "feat/HU-001-academic-transactional-outbox",
            "commit_msg": "feat(academic): entidad y repositorio outbox para eventos GradeCreated",
            "why": "Garantiza entrega confiable de eventos GradeCreated bajo ADR-007.",
            "verification_keywords": ["outbox", "outboxevent", "aggregate_type"]
        },
        {
            "id_task": "camilo_c2_07",
            "name": "Backend Asistencia: Transactional Outbox para Inasistencias StudentAbsent (:8083)",
            "repo": "educk-attendance-api",
            "puerto": "8083",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/attendance/infrastructure/persistence/AttendanceOutboxEntity.java",
            "que": "Implementar persistencia en outbox_events para eventos StudentAbsent bajo la misma transacción ACID de la sesión de asistencia.",
            "criterios_tecnicos": [
                "Entidad `AttendanceOutboxEntity` con mapeo a tabla `outbox_events`.",
                "Inclusión de payload con Lamport Timestamp para orden causal (ADR-007).",
                "Desacople de llamadas directas a RabbitMQ durante el pase de lista.",
                "Pruebas unitarias de inserción en outbox."
            ],
            "branch": "feat/HU-005-attendance-outbox-entity",
            "commit_msg": "feat(attendance): entidad outbox para persistencia atomica de StudentAbsent",
            "why": "Garantiza orden causal y tolerancia a fallos en inasistencias bajo ADR-007.",
            "verification_keywords": ["outbox", "studentabsent", "aggregate_id"]
        },
        {
            "id_task": "camilo_c2_08",
            "name": "Persistencia Académica: Migración Flyway de Tabla Outbox Events (:5432)",
            "repo": "educk-academic-db",
            "puerto": "5432",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V3__outbox_events_schema.sql",
            "que": "Crear script Flyway V3__outbox_events_schema.sql con tabla outbox_events, estado PENDING/PUBLISHED e índices según ADR-007.",
            "criterios_tecnicos": [
                "Tabla `outbox_events` con columnas id UUID PRIMARY KEY, aggregate_type, aggregate_id, event_type, payload JSONB, status, created_at.",
                "Índice B-Tree en `(status, created_at)` para consulta rápida del poller.",
                "Script SQL idempotente para PostgreSQL 16 y Flyway 10.x.",
                "Alineado con ADR-003 y ADR-007."
            ],
            "branch": "feat/HU-001-academic-db-outbox-v3",
            "commit_msg": "feat(db): esquema flyway para tabla outbox_events en academic_db",
            "why": "Soporte de persistencia para el patrón Transactional Outbox bajo ADR-007.",
            "verification_keywords": ["outbox_events", "create table", "aggregate_type"]
        },
        {
            "id_task": "camilo_c2_09",
            "name": "Persistencia Asistencia: Migración Flyway de Tabla Outbox Events (:5433)",
            "repo": "educk-attendance-db",
            "puerto": "5433",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V3__outbox_events_schema.sql",
            "que": "Crear script Flyway V3__outbox_events_schema.sql con tabla outbox_events para desacoplar el broker RabbitMQ según ADR-007.",
            "criterios_tecnicos": [
                "Tabla `outbox_events` con columnas id UUID PRIMARY KEY, aggregate_type, aggregate_id, event_type, payload JSONB, status, created_at.",
                "Índice compuesto en `(status, created_at)`.",
                "Script SQL compatible con Flyway 10.x.",
                "Alineado con ADR-003 y ADR-007."
            ],
            "branch": "feat/HU-005-attendance-db-outbox-v3",
            "commit_msg": "feat(db): esquema flyway para tabla outbox_events en attendance_db",
            "why": "Persistencia requerida para resiliencia en eventos de inasistencia bajo ADR-007.",
            "verification_keywords": ["outbox_events", "create table", "payload"]
        },
        {
            "id_task": "camilo_c2_10",
            "name": "Backend Académico: Pruebas Unitarias de Casos de Uso con Mockito (:8082)",
            "repo": "educk-academic-api",
            "puerto": "8082",
            "target_list": LIST_BACKEND,
            "target_file": "src/test/java/com/corhuila/edutrack/academic/application/RegisterGradeUseCaseTest.java",
            "que": "Construir pruebas unitarias con JUnit 5 y Mockito para RegisterGradeUseCase verificando cobertura mayor al 80% requerida por Quality Gate.",
            "criterios_tecnicos": [
                "Pruebas unitarias de caso feliz: registro de calificación válida [0.0 - 5.0] y persistencia en repositorio.",
                "Prueba de excepción: rechazo de calificaciones fuera de rango (< 0.0 o > 5.0).",
                "Verificación de invocación a puerto de eventos Mockito `verify(publisherPort).publish(...)`.",
                "Ejecución limpia con `mvn test`."
            ],
            "branch": "feat/HU-001-academic-unit-tests",
            "commit_msg": "feat(academic): pruebas unitarias con mockito para RegisterGradeUseCase",
            "why": "Cumplimiento del umbral de 80% de cobertura y Quality Gate de pruebas en CI.",
            "verification_keywords": ["registergrade", "mockito", "test", "assertthat"]
        }
    ],
    "stephanvargasquiroga": [
        {
            "id_task": "stephan_c2_01",
            "name": "Backend Identidad: Endpoint de Validación de Token JWT /validate (:8081)",
            "repo": "educk-identity-api",
            "puerto": "8081",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/identity/infrastructure/web/AuthController.java",
            "que": "Implementar endpoint POST /api/v1/auth/validate para verificar firma JWT, vigencia y retornar claims del usuario autenticado.",
            "criterios_tecnicos": [
                "Endpoint `POST /api/v1/auth/validate` que reciba token JWT en el encabezado `Authorization: Bearer <token>`.",
                "Validación criptográfica de firma HMAC/RSA y comprobación de fecha de expiración.",
                "Respuesta JSON estructurada: `{\"valid\": true, \"userId\": \"UUID\", \"email\": \"...\", \"role\": \"ROLE_DOCENTE\"}`.",
                "Manejo de error HTTP 401 Unauthorized si el token es inválido o se encuentra expirado."
            ],
            "branch": "feat/HU-003-jwt-validate-endpoint",
            "commit_msg": "feat(auth): endpoint /api/v1/auth/validate para verificacion de firmas jwt",
            "why": "Requerimiento HU-003 para validación centralizada de sesiones desde el API Gateway.",
            "verification_keywords": ["/validate", "validate", "valid", "claims"]
        },
        {
            "id_task": "stephan_c2_02",
            "name": "API Gateway: Filtro Global de Autenticación y Propagación de Headers (:8080)",
            "repo": "educk-api-gateway",
            "puerto": "8080",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/resources/application.yml",
            "que": "Configurar filtro de enrutamiento que intercepte Authorization: Bearer, llame a :8081/validate e inyecte X-User-Id y X-User-Role hacia los microservicios.",
            "criterios_tecnicos": [
                "Rutas de Spring Cloud Gateway configuradas hacia los puertos 8081 (identity), 8082 (academic), 8083 (attendance).",
                "Filtro global de seguridad que intercepte peticiones protegidas y valide el token contra `:8081/api/v1/auth/validate`.",
                "Inyección de encabezados HTTP downstream: `X-User-Id`, `X-User-Role`, `X-User-Email`.",
                "Rutas públicas exentas de validación: `/api/v1/auth/login` y endpoints `/health`."
            ],
            "branch": "feat/GW-001-gateway-auth-filter",
            "commit_msg": "feat(gateway): filtro global de autorizacion y propagacion de headers",
            "why": "Estándar de seguridad perimetral para desacoplar la validación de tokens en cada microservicio.",
            "verification_keywords": ["routes", "filters", "x-user-id", "validate"]
        },
        {
            "id_task": "stephan_c2_03",
            "name": "Worker AMQP: Plantillas de Mensajes y Log de Notificaciones (:8084)",
            "repo": "educk-worker",
            "puerto": "8084",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/worker/infrastructure/amqp/NotificationEventListener.java",
            "que": "Implementar formateo amigable de alertas en NotificationEventListener para eventos GradeCreated y StudentAbsent, guardando registro en notification_log.",
            "criterios_tecnicos": [
                "Consumer `@RabbitListener` conectado a las colas `edutrack.academic.grades` y `edutrack.attendance.absences`.",
                "Plantilla de mensaje para notas: 'Estimado Acudiente, su acudido ha recibido una nueva calificación en {subject}: {score}'.",
                "Plantilla de mensaje para inasistencias: 'Alerta: Se registró una inasistencia en la fecha {date}'.",
                "Log estructurado del despacho con timestamp UTC, canal (EMAIL/SMS/WHATSAPP) y destinatario."
            ],
            "branch": "feat/HU-002-worker-notification-templates",
            "commit_msg": "feat(worker): plantillas amigables y registro auditable de alertas amqp",
            "why": "Requerimiento HU-002 para notificaciones automáticas asíncronas a acudientes.",
            "verification_keywords": ["rabbitlistener", "gradecreated", "studentabsent", "template"]
        },
        {
            "id_task": "stephan_c2_04",
            "name": "Backend Identidad: Rotación de Refresh Tokens y Cierre de Sesión (:8081)",
            "repo": "educk-identity-api",
            "puerto": "8081",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/identity/application/service/IdentityService.java",
            "que": "Añadir endpoint POST /api/v1/auth/refresh para renovación de tokens expirados y revocación segura de sesiones.",
            "criterios_tecnicos": [
                "Endpoint `POST /api/v1/auth/refresh` con verificación del token en tabla `refresh_tokens`.",
                "Revocación inmediata del Refresh Token anterior tras su uso (One-Time Token Rotation).",
                "Emisión de un nuevo Access Token con validez de 15 minutos.",
                "Endpoint `POST /api/v1/auth/logout` que invalide el Refresh Token en base de datos."
            ],
            "branch": "feat/HU-003-token-rotation-logout",
            "commit_msg": "feat(auth): rotacion de refresh tokens y revocacion de sesiones",
            "why": "Seguridad institucional para evitar sesiones perpetuas y mitigar robo de tokens.",
            "verification_keywords": ["refresh", "refreshtoken", "rotation", "logout"]
        },
        {
            "id_task": "stephan_c2_05",
            "name": "Persistencia Identidad: Migración Flyway de Tabla Refresh Tokens (:5431)",
            "repo": "educk-identity-db",
            "puerto": "5431",
            "target_list": LIST_BACKEND,
            "target_file": "migrations/V2__refresh_tokens.sql",
            "que": "Crear script Flyway V2__refresh_tokens.sql con tabla para persistir tokens de refresco, expiración y estado de revocación.",
            "criterios_tecnicos": [
                "Tabla `refresh_tokens` con id UUID PRIMARY KEY, user_id UUID REFERENCES users(id), token_hash VARCHAR(255) NOT NULL UNIQUE, expires_at TIMESTAMP WITH TIME ZONE NOT NULL, revoked BOOLEAN DEFAULT FALSE.",
                "Índice B-Tree en `(user_id, token_hash)` para acelerar la revocación y consulta.",
                "Script idempotente compatible con PostgreSQL 16 y Flyway 10.x.",
                "Alineado con ADR-003 y ADR-008 para invalidación de sesiones."
            ],
            "branch": "feat/HU-003-identity-refresh-tokens-schema",
            "commit_msg": "feat(db): esquema flyway para almacenamiento de refresh tokens y revocacion",
            "why": "Soporte de persistencia bajo ADR-003 para rotación segura de tokens en identity-api.",
            "verification_keywords": ["refresh_tokens", "token_hash", "revoked", "create table"]
        },
        {
            "id_task": "stephan_c2_06",
            "name": "API Gateway: Enrutamiento Dinámico con Rate Limiting y CORS (:8080)",
            "repo": "educk-api-gateway",
            "puerto": "8080",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/gateway/config/CorsConfig.java",
            "que": "Configurar política centralizada de CORS para los puertos :3000 a :3005 y filtro de Rate Limiting por IP/Token.",
            "criterios_tecnicos": [
                "Clase de configuración WebFlux CorsWebFilter permitiendo orígenes `http://localhost:3000` a `3005`.",
                "Métodos HTTP permitidos: GET, POST, PUT, DELETE, PATCH, OPTIONS.",
                "Encabezados permitidos: Authorization, Content-Type, Idempotency-Key, X-User-Id.",
                "Alineado con ADR-008 para seguridad perimetral sin colisiones de CORS."
            ],
            "branch": "feat/GW-002-gateway-cors-and-ratelimit",
            "commit_msg": "feat(gateway): configuracion centralizada de cors y politicas perimetrales",
            "why": "Permite comunicación fluida de los microfrontends hacia el Gateway bajo ADR-008.",
            "verification_keywords": ["cors", "corswebfilter", "allowedorigins"]
        },
        {
            "id_task": "stephan_c2_07",
            "name": "Backend Identidad: Pruebas de Integración con Testcontainers PostgreSQL (:8081)",
            "repo": "educk-identity-api",
            "puerto": "8081",
            "target_list": LIST_BACKEND,
            "target_file": "src/test/java/com/corhuila/edutrack/identity/infrastructure/AuthIntegrationTest.java",
            "que": "Construir prueba de integración para login y emisión de JWT levantando contenedor efímero de PostgreSQL con Testcontainers.",
            "criterios_tecnicos": [
                "Configuración de `@Testcontainers` y `PostgreSQLContainer('postgres:16-alpine')`.",
                "Prueba de autenticación exitosa `POST /api/v1/auth/login` con retorno de access_token.",
                "Validación de hashing BCrypt de contraseña contra base de datos real en Docker.",
                "Alineado con la estrategia de pruebas automatizadas en CI (Finding 10)."
            ],
            "branch": "feat/HU-003-auth-testcontainers-integration",
            "commit_msg": "feat(auth): prueba de integracion con testcontainers postgresql",
            "why": "Verificación de integración real de persistencia y emisión de tokens para Quality Gate.",
            "verification_keywords": ["testcontainers", "postgresqlcontainer", "login"]
        }
    ],
    "ximenachala": [
        {
            "id_task": "ximena_c2_01",
            "name": "Infraestructura Global: Orquestación Docker Compose y Red Unificada (:5672/:6379)",
            "repo": "educk-infra",
            "puerto": "5672",
            "target_list": LIST_BACKEND,
            "target_file": "docker-compose.yml",
            "que": "Configurar la red unificada 'edutrack-net', servicios PostgreSQL (:5431-:5435), RabbitMQ (:5672/:15672) y Redis (:6379) con healthchecks.",
            "criterios_tecnicos": [
                "Definición de red global bridge `edutrack-net`.",
                "5 contenedores PostgreSQL independientes con volúmenes nombrados y puertos 5431-5435.",
                "Servicio RabbitMQ 3.13 con exchange topics y plugin de management activo en puerto 15672.",
                "Servicio Redis en puerto 6379 para lista negra (ADR-008) y caché de idempotencia."
            ],
            "branch": "chore/compose-global-network-stack",
            "commit_msg": "chore(infra): stack docker compose unificado con red edutrack-net",
            "why": "Permite levantar toda la infraestructura del sistema con un solo comando docker compose up.",
            "verification_keywords": ["edutrack-net", "rabbitmq", "redis", "healthcheck"]
        },
        {
            "id_task": "ximena_c2_02",
            "name": "Worker AMQP: Deduplicación con Redis y Cola Dead Letter DLQ (:8085)",
            "repo": "educk-worker",
            "puerto": "8085",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/corhuila/edutrack/worker/infrastructure/amqp/IdempotentConsumer.java",
            "que": "Implementar deduplicación de eventos GradeCreated y StudentAbsent con Redis y enrutamiento a Dead Letter Queue (DLQ).",
            "criterios_tecnicos": [
                "Deduplicación atómica en Redis mediante `eventId` (UUIDv4) con TTL de 24 horas.",
                "Descarte o confirmación inmediata (`basicAck`) si el evento ya fue procesado.",
                "Política de reintentos (3 intentos con backoff exponencial) antes de enviar a `notifications.dlq`.",
                "Pruebas unitarias de deduplicación con Mockito."
            ],
            "branch": "feat/worker-amqp-deduplication",
            "commit_msg": "feat(worker): consumidor amqp con deduplicacion por eventId y cola dlq",
            "why": "Requerimiento de resiliencia y procesamiento asíncrono de eventos bajo ADR-007.",
            "verification_keywords": ["eventid", "redis", "dlq", "deduplication"]
        },
        {
            "id_task": "ximena_c2_03",
            "name": "Portal Shell: Barra Superior y Control de Acceso por Roles (:3000)",
            "repo": "educk-front",
            "puerto": "3000",
            "target_list": LIST_FRONTEND,
            "target_file": "src/components/Navbar.jsx",
            "que": "Construir la barra de navegación superior institucional con indicador de usuario activo y menú desplegable de perfil.",
            "criterios_tecnicos": [
                "Navbar superior con logo oficial EduTrack y nombre del colegio.",
                "Chip de sesión que muestre el rol institucional del usuario (Directivo, Docente, Acudiente).",
                "Menú desplegable para cerrar sesión y cambiar de portal dinámicamente.",
                "Soporte para tema claro y diseño responsive."
            ],
            "branch": "feat/shell-navbar-and-rbac",
            "commit_msg": "feat(shell): navbar institucional con visualizacion de rol y logout",
            "why": "Requerimiento de usabilidad y contenedor principal de microfrontends bajo ADR-006.",
            "verification_keywords": ["navbar", "logout", "rol", "usuario"]
        },
        {
            "id_task": "ximena_c2_04",
            "name": "Backend Comunicación: Soporte de Cabecera Idempotency-Key en Mensajes (:8085)",
            "repo": "edutrack",
            "puerto": "8085",
            "target_list": LIST_BACKEND,
            "target_file": "src/main/java/com/edutrack/communication/infrastructure/web/MessageController.java",
            "que": "Implementar validación de cabecera Idempotency-Key en POST /api/v1/messages para evitar duplicados en reintentos de red.",
            "criterios_tecnicos": [
                "Intercepción de cabecera `Idempotency-Key` (UUIDv4) en el endpoint de envío de mensajes.",
                "Verificación en base de datos (`idempotency_keys`) antes de persistir un nuevo mensaje.",
                "Retorno del payload previo con HTTP 200 OK si la clave ya fue procesada.",
                "Persistencia atómica de mensaje y clave de idempotencia en la misma transacción."
            ],
            "branch": "feat/HU-004-message-idempotency",
            "commit_msg": "feat(comms): soporte de cabecera Idempotency-Key en mensajes de corte 2",
            "why": "Requerimiento NFR-003 y ADR-005 para prevenir mensajes duplicados ante reintentos de red.",
            "verification_keywords": ["idempotency", "idempotency-key", "uuid", "messages"]
        },
        {
            "id_task": "ximena_c2_05",
            "name": "Portal Comunicación: Envío de Mensajes Directos con Bloqueo de Botón (:3005)",
            "repo": "educk-communication-portal",
            "puerto": "3005",
            "target_list": LIST_FRONTEND,
            "target_file": "src/components/MessageComposer.jsx",
            "que": "Construir el formulario interactivo para redactar y enviar mensajes directos con generación de Idempotency-Key y bloqueo de botón.",
            "criterios_tecnicos": [
                "Formulario con campos de destinatario, asunto y cuerpo del mensaje.",
                "Bloqueo inmediato del botón 'Enviar' (`isSending = true; disabled`) durante la petición HTTP.",
                "Generación automática de `Idempotency-Key` (UUIDv4) por cada intento de envío.",
                "Alerta visual de confirmación de entrega exitosa o manejo de error con reconexión."
            ],
            "branch": "feat/HU-004-message-composer-ui",
            "commit_msg": "feat(portal): compositor de mensajes con generacion de idempotency-key",
            "why": "Requerimiento HU-004 para comunicación directa y prevención de doble clic en cliente.",
            "verification_keywords": ["composer", "idempotency", "disabled", "enviar"]
        }
    ]
}

# ==============================================================================
# FUNCIONES DE GROUNDING REAL E INSPECCIÓN EN DISCO
# ==============================================================================

def load_trello_config():
    cfg = {}
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    key = os.environ.get("TRELLO_KEY") or cfg.get("api_key", "")
    token = os.environ.get("TRELLO_TOKEN") or cfg.get("token", "")
    board_id = os.environ.get("TRELLO_BOARD_ID") or cfg.get("board_id", "6aaef11b808b8de50ad9237e")

    return {"api_key": key, "token": token, "board_id": board_id}

def inspect_repository_grounding(task: dict) -> dict:
    """
    Real Grounding: Inspecciona físicamente el repositorio en disco para verificar
    qué componente, archivo o migración falta por construir.
    """
    repo_name = task["repo"]
    target_file = task["target_file"]
    keywords = task.get("verification_keywords", [])

    repo_dir = MUSIC_DIR / repo_name
    if not repo_dir.exists():
        return {
            "status": f"🔴 Repositorio `{repo_name}` no existe localmente.",
            "file_exists": False,
            "needs_work": True,
            "details": f"Falta clonar o verificar {repo_name}"
        }

    file_path = repo_dir / target_file
    if not file_path.exists():
        return {
            "status": f"🔴 Pendiente: El archivo `{target_file}` aún NO existe en `{repo_name}`.",
            "file_exists": False,
            "needs_work": True,
            "details": f"Ruta exacta esperada: {target_file}"
        }

    # El archivo existe, revisar si ya contiene la lógica solicitada
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        content = ""

    missing_kw = [kw for kw in keywords if kw.lower() not in content]
    if missing_kw:
        return {
            "status": f"🟡 En progreso: El archivo base `{target_file}` existe pero faltan componentes: {', '.join(missing_kw)}.",
            "file_exists": True,
            "needs_work": True,
            "details": f"Faltan implementar los requisitos: {missing_kw}"
        }

    return {
        "status": f"🟢 Completo: El archivo `{target_file}` ya cuenta con la implementación técnica.",
        "file_exists": True,
        "needs_work": False,
        "details": "Componente ya existente en el repositorio local."
    }

# ==============================================================================
# GUÍAS TÉCNICAS PASO A PASO POR TAREA (ARQUITECTURA, LIBRERÍAS Y CÓDIGO)
# ==============================================================================

TASK_DEVELOPMENT_GUIDES = {
    # --------------------------------------------------------------------------
    # CELESTE DUSSAN - FRONTEND PORTALS (REACT 18 + VITE)
    # --------------------------------------------------------------------------
    "celeste_c2_01": {
        "librerias": "React 18, Vite, CSS / TailwindCSS (`useState`, `useMemo`)",
        "arquitectura": "Microfrontend satélite desacoplado (:3002). Separación estricta entre estado reactivo en cliente y renderizado visual sin recarga.",
        "pasos": [
            "Abre `src/App.jsx` y declara el estado del filtro: `const [selectedSubject, setSelectedSubject] = useState('ALL');`.",
            "Renderiza un control interactivo `<select>` encima de la tabla con las asignaturas únicas de los estudiantes.",
            "Aplica `useMemo` para filtrar las calificaciones y calcular el promedio ponderado en tiempo real: `const promedio = useMemo(() => { const filtradas = selectedSubject === 'ALL' ? grades : grades.filter(g => g.subject === selectedSubject); if (!filtradas.length) return 0; return (filtradas.reduce((acc, g) => acc + (g.score * g.percentage), 0) / 100).toFixed(1); }, [selectedSubject, grades]);`.",
            "Diseña un Badge visual con estilo condicional: color verde (`#10b981`) si `promedio >= 3.0`, o rojo (`#ef4444`) si está en riesgo de reprobación.",
            "Verifica que la tabla se ajuste fluidamente en pantallas móviles y de escritorio."
        ]
    },
    "celeste_c2_02": {
        "librerias": "React 18, Vite, CSS Grid/Flexbox",
        "arquitectura": "Microfrontend satélite desacoplado (:3003). Manejo de estado inmutable para pase de lista de asistencia diaria.",
        "pasos": [
            "En `src/App.jsx`, añade un selector de fecha `<input type=\"date\" value={sessionDate} onChange={e => setSessionDate(e.target.value)} />` inicializado con la fecha actual en formato ISO (`YYYY-MM-DD`).",
            "Para cada estudiante en la tabla o lista, implementa un grupo de botones o selector para alternar su estado entre: `PRESENT`, `ABSENT`, `LATE` y `JUSTIFIED`.",
            "Añade un panel KPI superior con contadores en tiempo real que totalicen: Total Presentes, Total Ausentes y Justificados.",
            "Implementa el botón 'Guardar Asistencia' que invoque la función de confirmación y muestre una alerta o banner de éxito visual.",
            "Asegura que el diseño respete la paleta de colores institucional de eduTrack."
        ]
    },
    "celeste_c2_03": {
        "librerias": "React 18, Vite, Fetch API / LocalStorage",
        "arquitectura": "Microfrontend satélite de identidad (:3001). Aislamiento de credenciales en cliente y gestión del ciclo de vida de sesión.",
        "pasos": [
            "En `src/App.jsx`, implementa una vista condicional post-autenticación que se active tras un login exitoso o si existe un token en memoria.",
            "Construye una tarjeta de perfil que renderice Nombre, Correo y Rol institucional del usuario logueado (`DIRECTIVO`, `DOCENTE`, `ACUDIENTE`).",
            "Muestra un Badge con el color institucional del rol según las directrices de UX/UI (Directivo: Azul, Docente: Verde, Acudiente: Morado).",
            "Crea el botón de 'Cerrar Sesión' (Logout) que limpie el token de `localStorage`/estado y restablezca el formulario inicial de login.",
            "Añade manejo amigable de errores si las credenciales son incorrectas."
        ]
    },
    "celeste_c2_04": {
        "librerias": "React 18, Vite, CSS Modules / Responsive Iframe",
        "arquitectura": "Microfrontend Host Shell (ADR-006 en :3000). Contenedor orquestador que incrusta portales satélite sin colisión de estilos globales.",
        "pasos": [
            "En `src/App.jsx` de `educk-front`, construye una barra de navegación lateral (Sidebar) con accesos a Identidad (:3001), Académico (:3002), Asistencia (:3003) y Comunicación (:3005).",
            "Define un estado reactivo `activePortal` con la URL del microfrontend seleccionado actualmente.",
            "En el contenedor principal, renderiza un `<iframe>` responsivo: `<iframe src={activePortal} style={{ width: '100%', height: 'calc(100vh - 70px)', border: 'none' }} title=\"Portal Satélite\" />`.",
            "Añade indicadores de estado visual (hover/active) en el menú lateral para señalar qué microfrontend está cargado.",
            "Verifica que la transición entre portales sea instantánea y sin recargar la página completa."
        ]
    },
    "celeste_c2_05": {
        "librerias": "React 18, Vite, CSS",
        "arquitectura": "Microfrontend satélite de comunicación (:3005). Tablero de circulares y avisos bajo ADR-005.",
        "pasos": [
            "En `src/App.jsx`, construye una vista de bandeja de comunicados institucionales en formato de tarjetas o tabla.",
            "Añade un selector de filtro por categoría: 'Todas', 'Urgente', 'General', 'Académico'.",
            "Implementa una vista modal para leer el comunicado completo al hacer clic sobre una fila, mostrando autor y fecha de emisión.",
            "Incluye un badge o icono visual indicando si el comunicado ya fue 'Leído' o permanece 'Sin leer'.",
            "Verifica que la modal sea accesible y se cierre correctamente al presionar ESC o el botón de cerrar."
        ]
    },

    # --------------------------------------------------------------------------
    # JUAN CAMILO PENAGOS - BACKEND & BASES DE DATOS (JAVA 21 / FLYWAY POSTGRESQL)
    # --------------------------------------------------------------------------
    "camilo_c2_01": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Database-per-service (ADR-003). Migración versionada inmutable e idempotente en `educk-academic-db` (:5432).",
        "pasos": [
            "Crea la carpeta `migrations/` si no existe y añade el archivo `V2__performance_indexes.sql` (con doble guion bajo).",
            "Escribe la sentencia DDL para optimizar consultas de boletines: `CREATE INDEX IF NOT EXISTS idx_grades_student_subject ON grades(student_id, subject_id);`",
            "Añade el índice para filtrado por entregas: `CREATE INDEX IF NOT EXISTS idx_assignments_subject ON assignments(subject_id, due_date);`",
            "Verifica que el archivo use codificación UTF-8 sin BOM y que no incluya bloques manuales `BEGIN` o `COMMIT` (Flyway gestiona la transacción automáticamente).",
            "Prueba la sintaxis SQL conectándote a PostgreSQL en el puerto :5432."
        ]
    },
    "camilo_c2_02": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Database-per-service (ADR-003). Evolución de esquema relacional en `educk-attendance-db` (:5433).",
        "pasos": [
            "Crea el archivo `migrations/V2__justifications.sql` en `educk-attendance-db`.",
            "Añade la columna para el motivo de la justificación: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS justification_reason VARCHAR(500);`",
            "Añade la columna de marca temporal UTC: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS justified_at TIMESTAMP WITH TIME ZONE;`",
            "Añade la columna para enlaces de adjuntos: `ALTER TABLE attendance_events ADD COLUMN IF NOT EXISTS attachment_url VARCHAR(255);`",
            "Comprueba que el script sea idempotente utilizando `IF NOT EXISTS` en cada sentencia DDL."
        ]
    },
    "camilo_c2_03": {
        "librerias": "Java 21, Spring Boot 3, Spring Data JPA",
        "arquitectura": "Arquitectura Hexagonal (Ports & Adapters). Capa de Aplicación (`application/service/`). Regla: El servicio de aplicación no debe acoplarse a frameworks web ni librerías de persistencia.",
        "pasos": [
            "En `AttendanceService.java`, valida que la fecha del registro no sea futura: lanza `InvalidAttendanceDateException` si `sessionDate.isAfter(LocalDate.now())`.",
            "Valida que el estado pertenezca al enum de dominio `AttendanceStatus` (`PRESENT`, `ABSENT`, `LATE`, `JUSTIFIED`).",
            "Si el estado registrado es `ABSENT`, invoca el puerto de salida `AttendanceEventPublisherPort` para publicar el evento `StudentAbsent` hacia RabbitMQ.",
            "Inyecta las dependencias mediante constructor (sin `@Autowired` en campos) para facilitar pruebas unitarias.",
            "Ejecuta `mvn test` para validar que todas las aserciones de prueba pasen limpiamente."
        ]
    },
    "camilo_c2_04": {
        "librerias": "Java 21, Spring Boot 3, Spring Data JPA",
        "arquitectura": "Arquitectura Hexagonal. Lógica de negocio en capa de Aplicación para el microservicio Académico (:8082).",
        "pasos": [
            "En `GradeService.java`, valida que el valor numérico de la nota se ubique estrictamente entre `0.0` y `5.0`.",
            "Implementa el cálculo ponderado: multiplica el valor de cada nota por su porcentaje de evaluación (asegurando que la suma de porcentajes no exceda el 100%).",
            "Determina el estado académico: asigna `APROBADO` si la nota definitiva es `>= 3.0` o `REPROBADO` si es estrictamente menor a 3.0.",
            "Publica el evento de dominio `GradeCreated` a través del puerto de mensajería para activar el worker de notificaciones.",
            "Anota el método principal con `@Transactional` para garantizar persistencia atómica en PostgreSQL."
        ]
    },
    "camilo_c2_05": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Database-per-service (ADR-003, ADR-005). Esquema de persistencia aislado para `educk-communication-db` (:5434).",
        "pasos": [
            "Crea el archivo `migrations/V1__init_communication.sql` en `educk-communication-db`.",
            "Escribe la sentencia para crear la tabla de comunicados: `CREATE TABLE IF NOT EXISTS announcements (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), title VARCHAR(200) NOT NULL, content TEXT NOT NULL, category VARCHAR(50) NOT NULL, author_id UUID NOT NULL, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);`",
            "Escribe la tabla de acuses de recibo: `CREATE TABLE IF NOT EXISTS acknowledgments (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), announcement_id UUID NOT NULL REFERENCES announcements(id) ON DELETE CASCADE, recipient_id UUID NOT NULL, read_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, CONSTRAINT uq_announcement_recipient UNIQUE(announcement_id, recipient_id));`",
            "Crea índices B-Tree en `announcements(created_at)` y `acknowledgments(recipient_id)` para acelerar consultas de acudientes.",
            "Asegura compatibilidad DDL estricta con PostgreSQL 16."
        ]
    },
    "camilo_c2_06": {
        "librerias": "Java 21, Spring Boot 3, Spring Data JPA, Jackson",
        "arquitectura": "Patrón Transactional Outbox (ADR-007) en el microservicio Académico (:8082). Elimina el riesgo de dual-write y asegura consistencia eventual con RabbitMQ.",
        "pasos": [
            "Crea `OutboxEventEntity.java` en `infrastructure/persistence/` con anotaciones `@Entity` y `@Table(name = \"outbox_events\")`.",
            "Declara los campos: `UUID id`, `String aggregateType`, `String aggregateId`, `String eventType`, `String payload` (JSONB) y `String status` (`PENDING`, `PUBLISHED`).",
            "Crea la interfaz `OutboxEventRepository extends JpaRepository<OutboxEventEntity, UUID>` con método `List<OutboxEventEntity> findByStatusOrderByCreatedAtAsc(String status)`.",
            "En el caso de uso `RegisterGradeUseCase`, persiste la calificación y guarda la entidad outbox dentro de la misma transacción `@Transactional`.",
            "Verifica que ante un fallo de base de datos, el evento no se guarde ni se publique."
        ]
    },
    "camilo_c2_07": {
        "librerias": "Java 21, Spring Boot 3, Spring Data JPA",
        "arquitectura": "Transactional Outbox & Causal Ordering (ADR-007). Desacopla la publicación de inasistencias en `educk-attendance-api` (:8083).",
        "pasos": [
            "Crea `AttendanceOutboxEntity.java` mapeando la tabla `outbox_events`.",
            "Incluye en el payload JSON una marca temporal lógica de Lamport (timestamp secuencial) para permitir orden causal en el consumidor asíncrono.",
            "Crea el adaptador de salida `OutboxAttendanceEventPublisher` que guarde en `outbox_events` con estado `PENDING` en lugar de enviar directamente a RabbitMQ.",
            "Asegura que la persistencia de la asistencia y el evento outbox ocurran en el mismo bloque `@Transactional`.",
            "Añade pruebas unitarias verificando la inserción de eventos en la tabla outbox."
        ]
    },
    "camilo_c2_08": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Transactional Outbox Pattern (ADR-007). Soporte relacional en `educk-academic-db` (:5432).",
        "pasos": [
            "Crea el archivo `migrations/V3__outbox_events_schema.sql` en `educk-academic-db`.",
            "Define la tabla `outbox_events`: `id UUID PRIMARY KEY DEFAULT gen_random_uuid(), aggregate_type VARCHAR(100) NOT NULL, aggregate_id VARCHAR(100) NOT NULL, event_type VARCHAR(100) NOT NULL, payload JSONB NOT NULL, status VARCHAR(20) NOT NULL DEFAULT 'PENDING', created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP`.",
            "Crea un índice compuesto para optimizar el polling asíncrono: `CREATE INDEX IF NOT EXISTS idx_outbox_status_created ON outbox_events(status, created_at);`",
            "Asegura compatibilidad con PostgreSQL 16 y Flyway 10.x."
        ]
    },
    "camilo_c2_09": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Transactional Outbox Pattern (ADR-007). Soporte relacional en `educk-attendance-db` (:5433).",
        "pasos": [
            "Crea el archivo `migrations/V3__outbox_events_schema.sql` en `educk-attendance-db`.",
            "Escribe la sentencia DDL para crear la tabla `outbox_events` con soporte para payloads JSONB.",
            "Añade el índice `CREATE INDEX IF NOT EXISTS idx_attendance_outbox_status ON outbox_events(status, created_at);` para acelerar el procesamiento de inasistencias pendientes.",
            "Comprueba que el script se aplique limpiamente mediante Flyway."
        ]
    },
    "camilo_c2_10": {
        "librerias": "Java 21, JUnit 5, Mockito (`org.mockito:mockito-junit-jupiter`), AssertJ",
        "arquitectura": "Arquitectura Hexagonal. Pruebas unitarias de casos de uso (Capa de Aplicación). Cobertura mínima obligatoria: 80% (Quality Gate CI).",
        "pasos": [
            "Crea la clase `RegisterGradeUseCaseTest.java` en `src/test/java/.../application/` anotada con `@ExtendWith(MockitoExtension.class)`.",
            "Declara `@Mock` para los puertos de salida: `GradeRepositoryPort` y `GradeEventPublisherPort`.",
            "Declara `@InjectMocks` para el caso de uso `RegisterGradeUseCase`.",
            "Escribe el test de caso feliz: simula una nota válida (`4.5`), llama al caso de uso y verifica con `verify(gradeRepositoryPort).save(...)` y `assertThat(result.score()).isEqualTo(4.5)`.",
            "Escribe el test de excepción: pasa una nota inválida (`5.5`) y comprueba que lance `InvalidGradeException` sin interactuar con la base de datos (`verifyNoInteractions(gradeRepositoryPort)`).",
            "Ejecuta `mvn test` en terminal y confirma que pase en verde con 0 fallos."
        ]
    },

    # --------------------------------------------------------------------------
    # STEPHAN VARGAS - BACKEND, GATEWAY & WORKER (SPRING CLOUD / SECURITY / AMQP)
    # --------------------------------------------------------------------------
    "stephan_c2_01": {
        "librerias": "Java 21, Spring Boot 3, Spring Security 6, jjwt (`io.jsonwebtoken`)",
        "arquitectura": "Arquitectura Hexagonal. Adaptador Web Primario en `infrastructure/web/AuthController.java` para el microservicio de Identidad (:8081).",
        "pasos": [
            "En `AuthController.java`, declara el método `@PostMapping(\"/api/v1/auth/validate\")`.",
            "Recibe el encabezado de autorización usando `@RequestHeader(HttpHeaders.AUTHORIZATION) String authHeader`.",
            "Valida que el encabezado comience por `\"Bearer \"` y extrae el token JWT.",
            "Invoca el servicio de dominio para verificar la firma HMAC-SHA256 y la fecha de expiración.",
            "Si es válido, responde HTTP 200 OK con payload: `{\"valid\": true, \"userId\": \"...\", \"email\": \"...\", \"role\": \"ROLE_...\"}`.",
            "Si el token es inválido o está expirado, captura la excepción y retorna HTTP 401 Unauthorized estructurado."
        ]
    },
    "stephan_c2_02": {
        "librerias": "Java 21, Spring Cloud Gateway, Spring WebFlux",
        "arquitectura": "Perimeter Security Gateway (ADR-008 en :8080). Centralización de autenticación y propagación de identidad hacia microservicios.",
        "pasos": [
            "En `src/main/resources/application.yml` de `educk-api-gateway`, declara las rutas para cada microservicio backend (:8081, :8082, :8083).",
            "Configura el filtro global `AuthenticationFilter` para interceptar peticiones entrantes a rutas protegidas.",
            "Realiza una llamada reactiva (`WebClient`) hacia `http://localhost:8081/api/v1/auth/validate` enviando el Bearer token.",
            "Si el servicio de identidad valida el token, enriquece la petición downstream inyectando las cabeceras `X-User-Id`, `X-User-Role` y `X-User-Email`.",
            "Excluye de la validación los endpoints públicos `/api/v1/auth/login` y los healthchecks `/actuator/health`."
        ]
    },
    "stephan_c2_03": {
        "librerias": "Java 21, Spring Boot 3, Spring AMQP (RabbitMQ), SLF4J",
        "arquitectura": "Procesamiento Asíncrono de Eventos y Notificaciones (ADR-004, ADR-007) en `educk-worker` (:8084).",
        "pasos": [
            "Crea la clase `NotificationEventListener.java` anotada con `@Component` y `@Slf4j`.",
            "Añade un método con `@RabbitListener(queues = \"edutrack.academic.grades\")` para procesar el payload del evento `GradeCreated`.",
            "Formatea el mensaje para acudientes: 'Estimado Acudiente, su acudido ha recibido una nueva calificación en {materia}: {nota}'.",
            "Añade un segundo listener `@RabbitListener(queues = \"edutrack.attendance.absences\")` para el evento `StudentAbsent`.",
            "Registra en consola y base de datos el log estructurado del despacho con timestamp UTC, canal (EMAIL/SMS) y destinatario."
        ]
    },
    "stephan_c2_04": {
        "librerias": "Java 21, Spring Boot 3, Spring Data JPA, BCrypt",
        "arquitectura": "Arquitectura Hexagonal. Capa de Aplicación (`IdentityService.java`) para rotación segura de tokens y revocación de sesiones.",
        "pasos": [
            "En `IdentityService.java`, crea el método `refreshToken(String tokenString)` para renovar credenciales expiradas.",
            "Busca el token en la base de datos y valida que no esté revocado (`revoked == false`) y que su fecha `expiresAt` sea futura.",
            "Aplica la regla de 'One-Time Rotation': marca el token actual como `revoked = true` e inserta un nuevo par de Access Token y Refresh Token.",
            "Implementa el método `logout(UUID userId)` que invalide todos los tokens de refresco activos del usuario.",
            "Lanza una excepción de autenticación si se intenta reutilizar un token ya revocado (mitigación de token replay)."
        ]
    },
    "stephan_c2_05": {
        "librerias": "PostgreSQL 16, Flyway 10.x",
        "arquitectura": "Database-per-service (ADR-003). Persistencia de sesiones en `educk-identity-db` (:5431).",
        "pasos": [
            "Crea el archivo `migrations/V2__refresh_tokens.sql` en `educk-identity-db`.",
            "Escribe la sentencia DDL para crear la tabla: `CREATE TABLE IF NOT EXISTS refresh_tokens (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE, token_hash VARCHAR(255) NOT NULL UNIQUE, expires_at TIMESTAMP WITH TIME ZONE NOT NULL, revoked BOOLEAN DEFAULT FALSE, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);`",
            "Crea el índice B-Tree: `CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id, token_hash);`",
            "Verifica que el script sea compatible con la ejecución automática de Flyway."
        ]
    },
    "stephan_c2_06": {
        "librerias": "Java 21, Spring WebFlux, Spring Cloud Gateway",
        "arquitectura": "Perimeter Security Gateway (ADR-008 en :8080). Política centralizada de CORS y protección perimetral.",
        "pasos": [
            "Crea la clase `CorsConfig.java` anotada con `@Configuration` en el paquete de configuración del Gateway.",
            "Declara un bean `@Bean public CorsWebFilter corsWebFilter()` configurando una instancia de `CorsConfiguration`.",
            "Agrega la lista de orígenes autorizados: `http://localhost:3000` (Shell), `:3001` (Identidad), `:3002` (Académico), `:3003` (Asistencia) y `:3005` (Comunicación).",
            "Permite los métodos HTTP: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`.",
            "Autoriza las cabeceras requeridas: `Authorization`, `Content-Type`, `Idempotency-Key`, `X-User-Id`, `X-User-Role`."
        ]
    },
    "stephan_c2_07": {
        "librerias": "Java 21, Spring Boot Test, Testcontainers (`org.testcontainers:postgresql`)",
        "arquitectura": "Pruebas de Integración con Contenedores Efímeros en CI (Finding 10). Valida la persistencia real y autenticación en `educk-identity-api` (:8081).",
        "pasos": [
            "Crea `AuthIntegrationTest.java` en `src/test/java/.../infrastructure/` anotada con `@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)` y `@Testcontainers`.",
            "Declara el contenedor efímero: `@Container static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>(\"postgres:16-alpine\");`",
            "Configura dinámicamente las propiedades de Spring mediante `@DynamicPropertySource` inyectando URL, usuario y clave del contenedor.",
            "Escribe la prueba enviando una petición HTTP real `POST /api/v1/auth/login` con credenciales de prueba pre-cargadas.",
            "Valida que la respuesta retorne código HTTP 200 y contenga un token JWT válido.",
            "Ejecuta `mvn test -Dtest=AuthIntegrationTest` para verificar el ciclo de vida del contenedor."
        ]
    },

    # --------------------------------------------------------------------------
    # XIMENA CHALA - INFRAESTRUCTURA, WORKER AMQP, SHELL & COMUNICACIÓN
    # --------------------------------------------------------------------------
    "ximena_c2_01": {
        "librerias": "Docker Compose v2, PostgreSQL 16 Alpine, RabbitMQ 3.13 Management, Redis 7.2",
        "arquitectura": "Infraestructura Global Orquestada (ADR-003, ADR-004, ADR-007, ADR-008). Red unificada `edutrack-net`.",
        "pasos": [
            "Abre `docker-compose.yml` en `educk-infra` y define la red compartida `networks: edutrack-net: driver: bridge`.",
            "Declara los 5 contenedores PostgreSQL independientes: `identity-db` (:5431), `academic-db` (:5432), `attendance-db` (:5433), `notifications-db` (:5434) y `communication-db` (:5435), cada uno con volumen persistente.",
            "Configura el contenedor `rabbitmq` exponiendo puertos :5672 (AMQP) y :15672 (Management UI) con healthcheck de `rabbitmq-diagnostics ping`.",
            "Configura el contenedor `redis` en el puerto :6379 para la lista negra de tokens y deduplicación de eventos.",
            "Verifica que todos los contenedores levanten saludablemente ejecutando `docker compose up -d`."
        ]
    },
    "ximena_c2_02": {
        "librerias": "Java 21, Spring Boot 3, Spring AMQP (RabbitMQ), Spring Data Redis",
        "arquitectura": "Consumidor Idempotente y Resiliencia con Dead Letter Queue (ADR-007) en `educk-worker` (:8085).",
        "pasos": [
            "En `IdempotentConsumer.java`, inyecta `StringRedisTemplate` y `RabbitTemplate`.",
            "En el método `@RabbitListener`, extrae el identificador único del evento (`eventId`, UUIDv4).",
            "Ejecuta una operación atómica en Redis: `Boolean isNew = redisTemplate.opsForValue().setIfAbsent(\"event:dedup:\" + eventId, \"PROCESSING\", Duration.ofHours(24));`.",
            "Si `isNew == false`, detecta entrega duplicada y ejecuta un `basicAck` inmediato descartando el mensaje sin reenviar notificaciones.",
            "Configura Dead Letter Exchange (`edutrack.dlx`) y la cola `notifications.dlq` con reintentos exponenciales (máximo 3 intentos) para aislar mensajes con payload corrupto."
        ]
    },
    "ximena_c2_03": {
        "librerias": "React 18, Vite, CSS Flexbox, localStorage API",
        "arquitectura": "Microfrontend Host Shell (ADR-006 en :3000). Componente transversal de cabecera con persistencia de sesión activa y control de acceso visual (RBAC).",
        "pasos": [
            "Define el contrato de props en `src/components/Navbar.jsx`: `Navbar({ title, activePort, user, onLogout })` con valores por defecto defensivos o lectura desde `localStorage.getItem('edutrack_user')`.",
            "Implementa el estado del menú desplegable con `useState(false)` y cierre automático al interactuar fuera.",
            "Maqueta el `<header>` superior con altura fija (64px), branding 'EduTrack Platform', título dinámico del módulo actual y badge estilizado del puerto activo (`http://localhost:${activePort}`).",
            "Renderiza el Badge RBAC en el extremo derecho con código de color dinámico por rol (Docente en ámbar, Directivo en púrpura, Estudiante en verde, Acudiente en índigo).",
            "Añade botón de avatar con iniciales (ej. 'XZ') y menú flotante con datos del usuario y acción de logout (`removeItem` de tokens y llamada a `onLogout`).",
            "Integra el componente dentro de `src/App.jsx` pasando el estado del módulo y enrutador de microfrontends."
        ]
    },
    "ximena_c2_04": {
        "librerias": "Java 21, Spring Boot 3, Spring Web, Spring Data JPA",
        "arquitectura": "Arquitectura Hexagonal (Adaptador Web en `infrastructure/web/`) con Idempotencia HTTP (ADR-005, NFR-003) en `edutrack` (:8085).",
        "pasos": [
            "En `MessageController.java`, actualiza el endpoint `@PostMapping(\"/api/v1/messages\")` para exigir el encabezado `@RequestHeader(\"Idempotency-Key\") UUID idempotencyKey`.",
            "Consulta en la capa de persistencia si ya existe un registro asociado a ese `idempotencyKey`.",
            "Si la clave ya existe, retorna inmediatamente la respuesta almacenada previamente con código HTTP 200 OK, garantizando que no se cree un mensaje duplicado.",
            "Si es una clave nueva, procesa el envío del mensaje y guarda la clave en la tabla de idempotencia en la misma transacción `@Transactional` respondiendo HTTP 201 Created.",
            "Agrega una prueba unitaria que valide que dos peticiones con la misma clave solo produzcan un único registro."
        ]
    },
    "ximena_c2_05": {
        "librerias": "React 18, Vite, Axios / Fetch API",
        "arquitectura": "Microfrontend satélite de Comunicación (:3005). Interfaz cliente resiliente contra doble clic e idempotente.",
        "pasos": [
            "Crea el componente `MessageComposer.jsx` en `src/components/` con campos de destinatario, asunto y área de texto para el mensaje.",
            "En el evento `handleSubmit`, genera un identificador único mediante `const idempotencyKey = crypto.randomUUID();`.",
            "Deshabilita inmediatamente el botón de envío (`setIsSubmitting(true)`) para prevenir clics repetidos mientras viaja la petición de red.",
            "Realiza la petición HTTP enviando el header `'Idempotency-Key': idempotencyKey`.",
            "Muestra una notificación visual de confirmación de envío y limpia los campos del formulario tras recibir HTTP 201."
        ]
    }
}

def get_task_development_guide(task: dict, member_info: dict) -> str:
    """
    Retorna la guía técnica estructurada paso a paso, librerías y reglas arquitectónicas
    para la tarea especificada.
    """
    t_id = task.get("id_task", "")
    guide = TASK_DEVELOPMENT_GUIDES.get(t_id)

    if guide:
        librerias = guide.get("librerias", "")
        arquitectura = guide.get("arquitectura", "")
        pasos = guide.get("pasos", [])
        pasos_str = "\n".join([f"{i+1}. {p}" for i, p in enumerate(pasos)])
        return f"""* **Librerías / Stack recomendado:** {librerias}
* **Regla Arquitectónica:** {arquitectura}

**Instrucciones detalladas de implementación paso a paso:**
{pasos_str}"""

    # Inferencia dinámica de respaldo para tareas futuras no catalogadas explícitamente
    repo = task.get("repo", "")
    target_file = task.get("target_file", "")
    criterios = task.get("criterios_tecnicos", [])

    if "portal" in repo or "front" in repo or target_file.endswith((".jsx", ".tsx", ".js", ".vue")):
        stack = "React 18, Vite, Hooks (`useState`, `useEffect`), CSS / Tailwind"
        arq = "Microfrontend satélite desacoplado. Mantén la lógica de presentación separada de servicios API y no bloquees la renderización."
    elif "-db" in repo or target_file.endswith(".sql"):
        stack = "PostgreSQL 16, Flyway 10.x migrations"
        arq = "Database-per-service (ADR-003). Scripts DDL versionados inmutables e idempotentes (`IF NOT EXISTS`)."
    elif "gateway" in repo:
        stack = "Java 21, Spring Boot 3, Spring Cloud Gateway, WebFlux, Redis"
        arq = "Perimeter Security Model (ADR-008). Filtros globales reactivos y propagación de headers."
    elif "worker" in repo:
        stack = "Java 21, Spring Boot 3, Spring AMQP (RabbitMQ), Spring Data Redis"
        arq = "Asynchronous Worker & Idempotent Consumer (ADR-007). Deduplicación con Redis y enrutamiento a DLQ."
    else:
        stack = "Java 21, Spring Boot 3, Spring Data JPA, Lombok"
        arq = "Arquitectura Hexagonal (Ports & Adapters). Capa de Dominio desacoplada de frameworks; puertos e interfaces en aplicación/dominio y adaptadores en infraestructura."

    pasos_str = "\n".join([f"{i+1}. {c}" for i, c in enumerate(criterios)]) if criterios else "1. Implementar la funcionalidad solicitada respetando el contrato de la tarea."

    return f"""* **Librerías / Stack recomendado:** {stack}
* **Regla Arquitectónica:** {arq}

**Instrucciones detalladas de implementación paso a paso:**
{pasos_str}"""

def build_card_description(task: dict, member_info: dict, grounding: dict) -> str:
    """
    Construye la descripción en Markdown para las tarjetas de Trello bajo las
    Nuevas Directrices Internas: Formato Técnico Optimizado.
    """
    puerto_val = f":{task.get('puerto')}" if task.get("puerto") else "No aplica (Infraestructura / Multi-puerto)"
    guia_tecnica = get_task_development_guide(task, member_info)

    return f"""📍 1. Ubicación y Objetivo

Repositorio: {task['repo']}
Puerto: {puerto_val}
Ruta del archivo: {task['target_file']}

Objetivo:
{task['que']}

---

🛠 2. Guía Técnica y Construcción (Paso a Paso)

{guia_tecnica}

---

💻 3. Operaciones de Terminal y Git

```bash
cd "{task['repo']}"
git checkout develop && git pull origin develop
git checkout -b {task['branch']}
# Realiza tus cambios en {task['target_file']}
git add .
git commit -m "{task['commit_msg']}" -m "Por qué: {task['why']}"
git push -u origin {task['branch']}
```

---

⬇️ Notas Administrativas y Responsabilidades:
🤖 El Bot Asistente audita el PR. 🧑💻 El Desarrollador Asignado (o su Agente) escribe el código, prueba y abre el PR moviendo la tarjeta a 'Realizado y revisar'.
"""

def trello_request(method: str, url: str, **kwargs):
    """Ejecuta peticiones seguras a la API de Trello validando certificados TLS con certifi."""
    kwargs.setdefault("verify", certifi.where())
    kwargs.setdefault("timeout", 15)
    return requests.request(method, url, **kwargs)

def get_board_cards(key: str, token: str, board_id: str) -> list:
    url = f"https://api.trello.com/1/boards/{board_id}/cards?fields=name,desc,idList,idMembers,idLabels,labels&key={key}&token={token}"
    res = trello_request("GET", url)
    if res.status_code == 200:
        return res.json()
    return []

def is_card_blocked(card: dict) -> bool:
    """
    Regla de Seguridad 2 (Anti-Bloqueo por Dependencias):
    Si una tarjeta actual tiene una etiqueta que diga 'Bloqueado', se excluye del conteo ejecutable.
    """
    labels = card.get("labels", [])
    for lbl in labels:
        lbl_name = (lbl.get("name") or "").strip().lower()
        if "bloqueado" in lbl_name or "bloqueada" in lbl_name:
            return True
    return False

# ==============================================================================
# MOTOR PRINCIPAL DE DESPACHO Y RECONCILIACIÓN CONTINUA
# ==============================================================================

def ensure_minimum_active_cards(min_cards_per_member: int = 5, target_member_key: str = None) -> dict:
    """
    Entrada principal del flujo continuo.
    Si se provee `target_member_key` (ej. "ximenachala"), solo evalúa y asigna tareas para ese miembro,
    manteniendo intacto el tablero del resto del equipo.
    
    Garantiza que cada uno de los 4 integrantes (Ximena, Celeste, Juan Camilo, Stephan)
    tenga siempre un flujo estricto de exactamente `min_cards_per_member` (5) tarjetas activas
    ejecutables en el tablero de Trello con Grounding Real en los 18 repositorios.
    
    Reconciliación Automática:
    Si una tarjeta del catálogo fue movida prematuramente a 'Aprobado y Mergeado' pero el
    diagnóstico en disco confirma que el código aún está incompleto (needs_work == True),
    la rescata y regresa automáticamente a la columna activa correspondiente.
    """
    cfg = load_trello_config()
    key, token, board_id = cfg["api_key"], cfg["token"], cfg["board_id"]

    if not key or not token:
        print("❌ Error: Claves de Trello no configuradas en .env o trello_config.json.")
        return {}

    all_cards = get_board_cards(key, token, board_id)
    active_lists = [LIST_FRONTEND, LIST_BACKEND]

    print("================================================================================")
    print("🚀 DESPACHADOR DE FLUJO CONTINUO CON GROUNDING REAL (CORTE 2 — 4 INTEGRANTES)")
    print("================================================================================")
    print("⚖️  DIVISIÓN ESTRICTA DE RESPONSABILIDADES:")
    print("   🤖 ROL DEL BOT: Despacha especificaciones y diagnóstico en disco (0 código autogenerado).")
    print("   🧑‍💻 ROL DEL EQUIPO (4 HUMANOS): Ximena, Celeste, Juan Camilo y Stephan escriben el código,")
    print("      ejecutan pruebas, abren PRs y mueven las tarjetas a 'Realizado y revisar'.")
    print(f"   🎯 CUPO ESTRICTO: {min_cards_per_member} tareas activas ejecutables por integrante.")
    print("================================================================================")

    created_summary = {}

    # ==============================================================================
    # FASE 1: RECONCILIACIÓN PRECISA SOBRE 'APROBADO Y MERGEADO' (SIN DUPLICADOS)
    # ==============================================================================
    print("🔍 [RECONCILIACIÓN]: Auditando tarjetas en '✅ Aprobado y Mergeado' contra disco...")
    done_cards = [c for c in all_cards if c.get("idList") == LIST_DONE]
    all_catalog_tasks = [t for member_tasks in ROADMAP_CATALOG.values() for t in member_tasks]
    catalog_by_name = {t["name"].strip().lower(): t for t in all_catalog_tasks}

    task_to_member = {}
    for m_key, m_tasks in ROADMAP_CATALOG.items():
        for t in m_tasks:
            task_to_member[t["name"].strip().lower()] = m_key

    for c in done_cards:
        c_name = c.get("name", "").strip()
        t_ref = catalog_by_name.get(c_name.lower())
        if t_ref:
            m_key = task_to_member.get(c_name.lower())
            if target_member_key and m_key != target_member_key:
                continue
            gr = inspect_repository_grounding(t_ref)
            if gr["needs_work"]:
                m_key = task_to_member.get(c_name.lower())
                m_info = TEAM_MEMBERS_DIRECTORY.get(m_key, {})
                t_id = m_info.get("trello_id")
                curr_act = [card for card in all_cards if card.get("idList") in active_lists and t_id in card.get("idMembers", [])]
                if len(curr_act) < min_cards_per_member:
                    target_list = t_ref["target_list"]
                    desc = build_card_description(t_ref, m_info, gr)
                    lbl_id = LABELS_MAP.get(m_key)
                    put_url = f"https://api.trello.com/1/cards/{c['id']}?key={key}&token={token}"
                    payload = {
                        "idList": target_list,
                        "desc": desc,
                        "idMembers": [t_id],
                        "idLabels": [lbl_id] if lbl_id else []
                    }
                    res_put = trello_request("PUT", put_url, json=payload)
                    if res_put.status_code == 200:
                        c["idList"] = target_list
                        c["idMembers"] = [t_id]
                        c["desc"] = desc
                        col = "Frontend" if target_list == LIST_FRONTEND else "Backend"
                        print(f"   🔄 [RECONCILIADA]: '{c_name}' devuelta a columna activa ({col}) para {m_info.get('full_name')}.")

    for member_key, tasks in ROADMAP_CATALOG.items():
        if target_member_key and member_key != target_member_key:
            continue
        
        member_info = TEAM_MEMBERS_DIRECTORY.get(member_key, {})
        trello_id = member_info.get("trello_id")
        m_name = member_info.get("full_name", member_key)
        label_id = LABELS_MAP.get(member_key)

        # 1. Contar tarjetas activas asignadas al integrante (Anti-Bloqueo aplicado)
        member_active_cards = []
        blocked_cards = []
        for c in all_cards:
            if c.get("idList") in active_lists and trello_id in c.get("idMembers", []):
                if is_card_blocked(c):
                    blocked_cards.append(c)
                    print(f"   ⚠️ [ANTI-BLOQUEO]: Tarjeta '{c.get('name')}' tiene etiqueta 'Bloqueado'. Excluida del conteo.")
                else:
                    member_active_cards.append(c)

        status_suffix = f" ({len(blocked_cards)} bloqueada(s) por dependencias)" if blocked_cards else ""
        print(f"\n👤 {m_name} ({member_info.get('color_emoji')} {member_info.get('color_name')}):")
        print(f"   Tarjetas activas ejecutables: {len(member_active_cards)} de {min_cards_per_member} requeridas{status_suffix}.")

        cards_needed = min_cards_per_member - len(member_active_cards)
        created_for_member = []

        print(f"   ⚡ Verificando y asegurando las 5 tareas activas con Grounding Real...")

        for idx, task in enumerate(tasks):
            t_name = task["name"]
            target_list_id = task["target_list"]

            # Si ya tenemos 5 activas y ya revisamos las primeras 5 tareas del catálogo, terminamos
            if idx >= min_cards_per_member and cards_needed <= 0:
                break

            # 2. Grounding Real: Inspeccionar el repositorio en disco
            grounding = inspect_repository_grounding(task)
            if not grounding["needs_work"]:
                print(f"   ℹ️ [GROUNDING REAL]: Tarea '{t_name}' ya está construida en `{task['repo']}`. Se avanza a la siguiente...")
                continue

            # 3. Buscar si la tarjeta ya existe en el tablero
            card_match = next((c for c in all_cards if c.get("name", "").strip().lower() == t_name.strip().lower()), None)

            if card_match:
                curr_list = card_match.get("idList")
                card_id = card_match.get("id")

                if curr_list in active_lists:
                    # Ya está en una lista activa. Asegurar descripción completa con las 4 secciones, membresía y etiqueta
                    curr_members = card_match.get("idMembers", [])
                    curr_labels = card_match.get("idLabels", [])
                    curr_desc = card_match.get("desc", "")
                    has_new_format = ("📍 1. Ubicación y Objetivo" in curr_desc) and ("🛠 2. Guía Técnica y Construcción" in curr_desc) and ("💻 3. Operaciones de Terminal y Git" in curr_desc) and ("⬇️ Notas Administrativas" in curr_desc) and ("LÍMITE DE RESPONSABILIDAD" not in curr_desc)
                    up_payload = {}
                    if not has_new_format:
                        up_payload["desc"] = build_card_description(task, member_info, grounding)
                    if trello_id not in curr_members:
                        up_payload["idMembers"] = list(set(curr_members + [trello_id]))
                    if label_id and label_id not in curr_labels:
                        up_payload["idLabels"] = list(set(curr_labels + [label_id]))
                    if up_payload:
                        url_up = f"https://api.trello.com/1/cards/{card_id}?key={key}&token={token}"
                        trello_request("PUT", url_up, json=up_payload)
                        print(f"   📝 [DESCRIPCIÓN OPTIMIZADA]: '{t_name}' actualizada con el nuevo formato técnico.")
                    continue

                elif curr_list == LIST_DONE or curr_list in [LIST_REVIEW, LIST_FIX]:
                    # Tarjeta existente pero movida prematuramente a 'Aprobado y Mergeado' o en revisión/corregir
                    # El Grounding Real confirma que needs_work == True (archivo incompleto o inexistente)
                    print(f"   🔄 [RECONCILIACIÓN Y RESTAURACIÓN]: '{t_name}' estaba en 'Aprobado y Mergeado'. Regresando a columna activa...")
                    desc = build_card_description(task, member_info, grounding)
                    url_move = f"https://api.trello.com/1/cards/{card_id}?key={key}&token={token}"
                    payload = {
                        "idList": target_list_id,
                        "desc": desc,
                        "idMembers": [trello_id],
                        "idLabels": [label_id] if label_id else []
                    }
                    res_mv = trello_request("PUT", url_move, json=payload)
                    if res_mv.status_code == 200:
                        card_match["idList"] = target_list_id
                        card_match["idMembers"] = [trello_id]
                        card_match["desc"] = desc
                        member_active_cards.append(card_match)
                        created_for_member.append(t_name)
                        cards_needed -= 1
                        col_name = "Frontend" if target_list_id == LIST_FRONTEND else "Backend"
                        print(f"      ✅ Restaurada en columna activa ({col_name}).")
                        print(f"      📍 Repositorio: {task['repo']} (:{task['puerto']}) | Archivo: {task['target_file']}")
                        print(f"      🔎 Estado: {grounding['status']}")
                    else:
                        print(f"      ❌ Error al mover tarjeta '{t_name}': {res_mv.status_code} {res_mv.text}")
                    continue
                else:
                    # Está en otra lista (ej. Documentación Pendiente). Mover a target_list_id
                    desc = build_card_description(task, member_info, grounding)
                    url_move = f"https://api.trello.com/1/cards/{card_id}?key={key}&token={token}"
                    payload = {
                        "idList": target_list_id,
                        "desc": desc,
                        "idMembers": [trello_id],
                        "idLabels": [label_id] if label_id else []
                    }
                    res_mv = trello_request("PUT", url_move, json=payload)
                    if res_mv.status_code == 200:
                        card_match["idList"] = target_list_id
                        member_active_cards.append(card_match)
                        created_for_member.append(t_name)
                        cards_needed -= 1
                        print(f"      ✅ Movida a columna activa: '{t_name}'")
                    continue

            else:
                # 4. Crear la tarjeta en Trello con Grounding Real
                desc = build_card_description(task, member_info, grounding)
                url_create = f"https://api.trello.com/1/cards?key={key}&token={token}"
                payload = {
                    "name": t_name,
                    "desc": desc,
                    "idList": target_list_id,
                    "idMembers": [trello_id],
                    "idLabels": [label_id] if label_id else []
                }
                res_cr = trello_request("POST", url_create, json=payload)
                if res_cr.status_code == 200:
                    new_c = res_cr.json()
                    created_for_member.append(t_name)
                    cards_needed -= 1
                    all_cards.append(new_c)
                    member_active_cards.append(new_c)
                    print(f"   ✅ [DESPACHADA]: '{t_name}'")
                    print(f"      📍 Repositorio: {task['repo']} (:{task['puerto']}) | Archivo: {task['target_file']}")
                    print(f"      🔎 Estado: {grounding['status']}")
                else:
                    print(f"   ❌ Error al crear tarjeta '{t_name}': {res_cr.status_code} {res_cr.text}")
        created_summary[m_name] = created_for_member
        print(f"   ✅ Capacidad óptima: El integrante cuenta con {len(member_active_cards)} tarjetas ejecutables en curso.")

    # Limpieza de falsos positivos restantes en 'Aprobado y Mergeado'
    all_catalog_tasks = [t for member_tasks in ROADMAP_CATALOG.values() for t in member_tasks]
    catalog_by_name = {t["name"].strip().lower(): t for t in all_catalog_tasks}
    
    for c in all_cards:
        if c.get("idList") == LIST_DONE:
            c_name_clean = c.get("name", "").strip().lower()
            task_ref = catalog_by_name.get(c_name_clean)
            if task_ref:
                m_key = task_to_member.get(c_name_clean)
                if target_member_key and m_key != target_member_key:
                    continue
                gr = inspect_repository_grounding(task_ref)
                if gr["needs_work"]:
                    # Es una tarea futura que estaba erróneamente en Done; archivar para no falsear auditoría
                    c_id = c.get("id")
                    url_arch = f"https://api.trello.com/1/cards/{c_id}?key={key}&token={token}"
                    trello_request("PUT", url_arch, json={"closed": True})
                    print(f"\n🧹 [LIMPIEZA DE FALSO POSITIVO]: '{c.get('name')}' archivada desde 'Aprobado y Mergeado' (tarea futura no completada en disco).")

    # ==============================================================================
    # AUDITORÍA FINAL DE CUPO ESTRICTO (5/5 POR DESARROLLADOR)
    # ==============================================================================
    final_cards = get_board_cards(key, token, board_id)
    active_final = [c for c in final_cards if c.get("idList") in active_lists]

    counts = {}
    for m_key in ["ximenachala", "celestedussan", "juancamilopenagosmolina", "stephanvargasquiroga"]:
        t_id = TEAM_MEMBERS_DIRECTORY[m_key]["trello_id"]
        c_count = len([c for c in active_final if t_id in c.get("idMembers", []) and not is_card_blocked(c)])
        counts[m_key] = c_count

    audit_str = f"Ximena: {counts['ximenachala']}/5, Celeste: {counts['celestedussan']}/5, Camilo: {counts['juancamilopenagosmolina']}/5, Stephan: {counts['stephanvargasquiroga']}/5"

    print("\n================================================================================")
    print("📊 REPORTE DE AUDITORÍA FINAL:")
    print(f"'{audit_str}'")
    print("================================================================================")
    print("🏁 Despacho de flujo continuo finalizado con éxito.")
    print("================================================================================")
    return created_summary

if __name__ == "__main__":
    ensure_minimum_active_cards(min_cards_per_member=5)

