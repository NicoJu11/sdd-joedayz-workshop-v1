# Banco de ideas del workshop

**Para participantes que no trajeron su propio codebase.**


> **Idioma:** Traducción de [`IDEA-BANK.md`](./IDEA-BANK.md). Los *seed* `CLAUDE.md`, nombres de skills, comandos `git clone` y ejemplos técnicos se mantienen en inglés (es lo que Claude Code espera).

Cada proyecto abajo es un escenario autocontenido en el que puedes entrar. Están diseñados para:
- Mostrar complejidad de dominio genuina (no CRUD con pasos de más)
- Producir skills distintas según el ángulo que tomes
- Soportar los 6 ejercicios del workshop sin sentirse forzados
- Ser lo bastante interesantes para sostener 6 horas de foco

Elige uno. Clónalo o haz scaffold. Dedica 10 minutos a leer el brief del escenario. Luego adelante.

---

## Cómo usar esto

1. **Elige un proyecto** que te interese (o el más cercano a tu industria)
2. **Clona el repo** (o usa el scaffold rápido si está listo)
3. **Lee el brief del escenario** — te da la “situación” en la que entras
4. **Corre el Ejercicio 1** como si fuera tu codebase real
5. Usa el **seed CLAUDE.md** como punto de partida del Ejercicio 2 (edítalo; no copies a ciegas)
6. La lista de **domain skills por descubrir** es una pista — deja que los ejercicios las saquen de forma natural

---

## Proyecto 1: QuantumTrade — Gestión de órdenes en tiempo real

**Tagline:** “Un order book es una estructura de datos. Un sistema de trading es una opinión sobre el tiempo.”

**Repo a clonar:**
```bash
git clone https://github.com/nwillc/kretail  # Java trading simulation
# OR scaffold:
mvn archetype:generate -DgroupId=io.quantumtrade -DartifactId=quantum-trade -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
```

**Brief del escenario:**
Entraste a un desk de trading propietario hace tres meses. El sistema lo escribieron dos quants senior que se fueron. Procesa ~50.000 eventos de órdenes por segundo, mantiene un order book en memoria por instrumento y dispara risk checks antes de cada ejecución. Los dos últimos incidentes de producción fueron por *state drift* entre el order book y el risk engine en ventanas de alta volatilidad. Tu trabajo: entender el sistema lo bastante bien para añadir un nuevo tipo de orden (iceberg — órdenes grandes que solo muestran una rebanada de su tamaño real) sin romper el matching engine.

**Por qué es buen material SDD:**
- El matching tiene reglas exactas (price-time priority) → obliga a skills precisas
- El cálculo de riesgo tiene umbrales, límites y excepciones → produce una sección real de constraints en CLAUDE.md
- Los bugs de state drift requieren skills de verificación con invariantes concretas
- “Iceberg order” es un feature real con edge cases no obvios (partial fills, cantidad oculta)

**Domain skills que emergen de forma natural:**
- `order-book-invariants` — what must always be true (bid < ask, time priority within price level)
- `order-lifecycle` — NEW → PARTIAL_FILL → FILLED / CANCELLED state machine
- `risk-check-sequence` — which checks fire in what order and why
- `matching-engine-rules` — price-time priority, market vs limit, fill-or-kill semantics
- `iceberg-order-mechanics` — hidden quantity, slice replenishment, anti-gaming rules

**Seed CLAUDE.md:**
```markdown
# QuantumTrade — Claude Development Guide

## Proyecto Overview
Real-time order management and matching engine. Java 21.
Processes limit orders, market orders, and cancel requests per instrument.
In-memory order book (no persistence during market hours).

## Architecture
Event-driven pipeline: `OrderGateway` → `RiskEngine` → `MatchingEngine` → `ExecutionReport`
- `gateway/` — inbound order normalisation and validation
- `risk/` — pre-trade checks (position limits, credit limits, instrument restrictions)
- `matching/` — order book per instrument, FIFO matching within price level
- `reporting/` — execution reports, fills, cancels

## Key Conventions
- Orders are immutable after creation — use `OrderBuilder` to construct
- Order state transitions are explicit enum steps — never set status directly
- All risk checks throw checked `RiskViolationException` — never swallow
- Price is stored as long (pence/cents) to avoid floating point — NEVER use double for money

## Current Work
- Adding iceberg order support (show slice, hide remainder)
- Known bug: partial fill + cancel race condition in `OrderBook.cancel()` line 247

## Constraints
- NEVER use floating point for price or quantity
- NEVER modify order state outside of `Order.transition()`
- Risk engine must complete in < 50µs per order (see `RiskBenchmarkTest`)
- No external calls during market hours — everything in-memory
```

---

## Proyecto 2: AstroNav — Planificador de misiones espaciales

**Tagline:** “La mecánica orbital no le importa la fecha de tu sprint.”

**Repo a clonar:**
```bash
git clone https://github.com/orekit/orekit  # Professional orbital mechanics library (Java)
# Lighter alternative:
git clone https://github.com/petrushy/Orekit-Java-tutorial
```

**Brief del escenario:**
Un operador pequeño de satélites maneja una constelación de seis satélites de observación terrestre. Heredaste el software de planificación de misión cuando el contratista original se fue. El sistema planifica ventanas de imagen (cuándo un satélite está sobre un objetivo), calcula presupuestos de maniobra (cuánto combustible quema un repunteo) y agenda downlinks a estaciones terrestres. El mes pasado, un cálculo malo de combustible hizo que un satélite ejecutara un burn mayor al planeado — ahora está en una órbita ligeramente incorrecta y la recuperación tomará tres semanas. Tu tarea: entender el pipeline de cálculo de maniobras lo bastante bien para añadir validación de inputs que habría atrapado el error.

**Por qué es buen material SDD:**
- Las restricciones físicas (mecánica orbital) son absolutas — las respuestas incorrectas tienen consecuencias catastróficas
- Los sistemas de coordenadas (ECI, ECEF, topocéntrico) causan bugs sutiles sin fin → obliga a skills precisas
- El combustible es finito y no renovable → produce una sección rica de constraints
- El escenario del error le da al Ejercicio 1 un “mayor riesgo técnico” obvio

**Domain skills que emergen de forma natural:**
- `coordinate-systems` — when to use which system and how to convert
- `fuel-budget-rules` — delta-V calculation, safety margins, constraint ordering
- `imaging-window-constraints` — sun angle, cloud cover, off-nadir limit
- `ground-station-visibility` — elevation mask, link budget basics
- `maneuver-validation` — invariants that must hold before commanding a burn

**Seed CLAUDE.md:**
```markdown
# AstroNav Mission Planner — Claude Development Guide

## Proyecto Overview
Mission planning for LEO Earth observation satellites. Java 21.
Uses Orekit for orbital propagation. Six-satellite constellation.

## Architecture
Layered: `MissionPlanner` → `WindowCalculator` → `ManeuverPlanner` → `ScheduleOptimiser`
- `propagation/` — orbit propagation (wraps Orekit TLEPropagator)
- `windows/` — access window calculation for targets and ground stations
- `maneuver/` — delta-V calculation, fuel budgeting, burn sequencing
- `scheduling/` — multi-satellite, multi-target schedule optimisation
- `validation/` — pre-command checks (fuel, attitude, comms coverage)

## Key Conventions
- All angles in RADIANS internally — convert at display boundary only
- All times in UTC as Orekit `AbsoluteDate` — NEVER use java.util.Date
- Fuel quantities in kg with 3 decimal precision
- Coordinate frames must be explicit in variable names: `posECI`, `posECEF`

## Constraints
- NEVER command a maneuver without running `ManeuverValidator.validate()` first
- NEVER assume Keplerian propagation for burns > 3 days out — use numerical propagator
- Minimum fuel reserve: 2.5 kg (emergency deorbit budget) — hard stop
- All delta-V calculations must include attitude settling time (0.3 deg/s slew rate)
```

---

## Proyecto 3: EcoGrid — Gestión de energía renovable

**Tagline:** “La red no sabe que es verde. Tú tienes que hacer que se comporte como si lo fuera.”

**Repo a clonar:**
```bash
git clone https://github.com/OperatorFabric/operatorfabric-core  # Grid ops platform
# Lighter: start from spring initializr with WebSocket + InfluxDB deps
```

**Brief del escenario:**
Una cooperativa energética comunitaria opera un microgrid: 400 kW de solar, 200 kWh de batería y 80 hogares más un edificio comercial pequeño. Tu software equilibra oferta (solar + descarga de batería + importación de red) contra demanda en intervalos de 5 minutos. El reto: la batería se degrada más rápido si la ciclas de forma demasiado agresiva, los forecasts solares fallan 15–20% a horizonte de 4 horas, y el inquilino comercial tiene un contrato de demand response (bajar carga a pedido a cambio de tarifas menores). Nuevo requisito: implementar peak-shaving — mantener la importación total de red bajo 50 kW usando la batería como buffer.

**Por qué es buen material SDD:**
- Las restricciones físicas (degradación de batería, límites de inversor) crean fronteras duras
- La incertidumbre del forecast exige razonamiento probabilístico → patrones ricos de verificación
- El contrato de demand response es una restricción legal/negocio que anula el óptimo técnico
- Peak-shaving tiene criterios de aceptación claros que mapean perfecto a casos de test

**Domain skills que emergen de forma natural:**
- `battery-lifecycle-rules` — depth of discharge limits, cycle counting, temperature derating
- `solar-forecast-handling` — confidence intervals, clipping behaviour, curtailment logic
- `demand-response-protocol` — signal types, response times, settlement calculation
- `peak-shaving-algorithm` — dispatch order, ramp rates, headroom reservation
- `grid-tariff-structure` — peak/off-peak windows, capacity charges, export rates

**Seed CLAUDE.md:**
```markdown
# EcoGrid Controller — Claude Development Guide

## Proyecto Overview
Real-time energy management for a 400 kW solar + 200 kWh battery microgrid.
Java 21, Spring Boot, InfluxDB for time-series, WebSocket for real-time dispatch.
5-minute dispatch cycle. 80 residential + 1 commercial connection.

## Architecture
Control loop: `ForecastEngine` → `DispatchOptimiser` → `DeviceController` → `MeterLogger`
- `forecast/` — solar irradiance model, load prediction, uncertainty bands
- `optimiser/` — battery dispatch, import/export decisions, peak-shaving
- `devices/` — inverter control, battery BMS interface, smart meter reads
- `settlement/` — demand response tracking, tariff calculation, reporting

## Key Conventions
- All power in kW (float), all energy in kWh (float) — label variables clearly
- Battery state of charge: 0.0–1.0 (not percentage) in all internal calculations
- Device commands are idempotent — safe to retry on comms failure
- Forecasts include confidence: `Forecast(value, p10, p90)` — never a bare number

## Constraints
- NEVER discharge battery below 15% SoC (BMS warranty condition)
- NEVER exceed 50 kW grid import — peak-shaving hard limit
- Demand response signals must be acknowledged within 10 seconds — async required
- All dispatch commands logged to audit trail before execution
```

---

## Proyecto 4: NeuralProxy — AI Gateway y rate limiter

**Tagline:** “Cada token es dinero. Cada timeout es un usuario que se fue.”

**Repo a clonar:**
```bash
git clone https://github.com/spring-projects/spring-ai  # Spring AI framework
# Or: a custom API gateway scaffold with Spring WebFlux + Redis
```

**Brief del escenario:**
Tu empresa construyó un AI gateway interno que enruta requests LLM de 12 equipos de producto a varios proveedores (Anthropic, OpenAI, Azure OpenAI). El gateway aplica presupuestos de tokens por equipo, maneja failover entre proveedores, cachea requests idénticos y registra todo para atribución de costos. El mes pasado, un equipo corrió un job de procesamiento masivo sin rate limiting — $8.000 de gasto API inesperado en 6 horas. Tu tarea: añadir un tope duro de gasto por equipo por día que falle abierto (fallback a un modelo más barato) en lugar de fallar cerrado (devolver error).

**Por qué es buen material SDD:**
- El conteo de tokens tiene edge cases por proveedor → obliga a skills de dominio cuidadosas
- El rate limiting tiene semántica sutil (sliding window vs fixed window, token bucket)
- “Fail open” vs “fail closed” es una decisión de diseño explícita con comportamiento testeable
- La atribución de costos exige contabilidad exacta → produce skills fuertes de verificación
- El dominio ES tooling de IA — los participantes sienten relevancia inmediata

**Domain skills que emergen de forma natural:**
- `token-counting-rules` — tiktoken vs Anthropic counting, system prompt tokens, tool definitions
- `rate-limit-algorithms` — sliding window, token bucket, when to use which
- `provider-failover-rules` — which providers are equivalent, model capability tiers
- `cost-attribution-model` — team, project, user hierarchy for spend tracking
- `cache-invalidation-policy` — what makes two requests "identical" for caching

**Seed CLAUDE.md:**
```markdown
# NeuralProxy API Gateway — Claude Development Guide

## Proyecto Overview
AI model gateway for internal use. Java 21, Spring WebFlux (reactive), Redis.
Routes to Anthropic, OpenAI, Azure OpenAI. 12 internal product teams.

## Architecture
Reactive pipeline: `RequestRouter` → `BudgetGuard` → `ProviderClient` → `ResponseLogger`
- `routing/` — model selection, provider mapping, failover logic
- `budget/` — per-team spending caps, token counting, Redis counters
- `providers/` — provider-specific clients (Anthropic, OpenAI, Azure)
- `cache/` — semantic cache (exact match + embedding similarity)
- `audit/` — request/response logging, cost attribution, anomaly detection

## Key Conventions
- All monetary values in USD cents (long) — NEVER use double for money
- Token counts are estimates until response arrives — use `estimatedTokens` / `actualTokens`
- Provider clients are interchangeable via `ModelProvider` interface
- Every external call has a 30s timeout and at most 2 retries

## Constraints
- NEVER log prompt content for PII-sensitive teams (flagged in team config)
- Budget checks must complete in < 5ms (Redis, no DB hit on hot path)
- Failover to cheaper model on budget breach — NEVER return 429 directly
- All provider credentials via environment variables — never in config files
```

---

## Proyecto 5: MediSched — Motor de agenda clínica

**Tagline:** “Una cita perdida es una molestia. La cita equivocada es una responsabilidad.”

**Repo a clonar:**
```bash
# No single canonical open-source example — scaffold:
mvn archetype:generate -DgroupId=no.medisched -DartifactId=medisched-core -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
```

**Brief del escenario:**
Una cadena de clínicas ambulatorias opera un sistema de agendas para consultas de especialistas. Cada tipo de cita tiene prerrequisitos (referidos, tests preparatorios, ayuno), cada especialista tiene patrones de disponibilidad (algunos solo ven ciertas categorías de pacientes), y el sistema debe cumplir garantías de tiempo de espera por categoría de prioridad. Un incidente reciente de seguridad del paciente se rastreó a una reserva que saltó un check de prerrequisito cuando el sistema referente estaba caído. Tu tarea: añadir un “grace mode” donde el sistema sigue reservando pero marca las citas con prerrequisitos omitidos para revisión clínica manual.

**Por qué es buen material SDD:**
- Healthcare mezcla reglas absolutas (seguridad del paciente) con reglas de negocio (metas de espera)
- Las cadenas de prerrequisitos son problemas de grafo → lógica de traversal compleja
- “Grace mode” es un patrón clásico de degradación elegante con estado testeable
- Las categorías de prioridad del paciente exigen un modelo de dominio explícito, no solo un enum

**Domain skills que emergen de forma natural:**
- `appointment-prerequisite-graph` — how to traverse required preconditions
- `specialist-availability-model` — session types, capacity, patient category restrictions
- `priority-category-rules` — what P1/P2/P3 means for waiting time guarantees
- `grace-mode-semantics` — what bookings are allowed, what flags get set, who reviews
- `referral-validity-rules` — expiry, scope, referring-clinician requirements

**Seed CLAUDE.md:**
```markdown
# MediSched Core — Claude Development Guide

## Proyecto Overview
Clinical appointment scheduling engine. Java 21, Spring Boot, PostgreSQL.
Outpatient specialist consultations. Four clinic locations, ~35 specialist types.

## Architecture
Layered: `BookingFacade` → `EligibilityChecker` → `SlotFinder` → `AppointmentRepository`
- `eligibility/` — referral validation, prerequisite graph traversal, priority classification
- `scheduling/` — slot search, specialist matching, capacity management
- `booking/` — appointment creation, confirmation, cancellation, rescheduling
- `audit/` — clinical audit trail, prerequisite bypass logging, review workflow

## Key Conventions
- Patient identifiers are always `PatientRef` (wrapper) — NEVER raw String
- Appointment states: PENDING_PREREQUISITES → READY → CONFIRMED → ATTENDED / DNA / CANCELLED
- All prerequisite checks return `EligibilityResult` (eligible, ineligible, grace-eligible)
- Clinical audit records are append-only — NEVER update or delete

## Constraints
- NEVER book a CONFIRMED appointment without a complete prerequisite chain (unless grace mode)
- Grace mode bookings MUST set `requiresManualReview = true`
- Patient data access requires `ContextHolder.hasRole(CLINICAL_STAFF)` — always check
- Waiting time targets are SLA obligations — log every breach immediately
```

---

## Proyecto 6: ChessEngine — Generación y evaluación de jugadas

**Tagline:** “32 piezas. 64 casillas. Más estados que átomos en el universo observable.”

**Repo a clonar:**
```bash
git clone https://github.com/bhlangonijr/chesslib  # Production Java chess library
# 300+ tests, real position evaluation, full move generation — perfect for Exercise 1
```

**Brief del escenario:**
Estás construyendo una herramienta de enseñanza de ajedrez que debe explicar por qué las jugadas son buenas o malas, no solo qué jugada hacer. El motor subyacente genera jugadas legales y evalúa posiciones. Tu nuevo feature: un “coaching mode” que, para cualquier posición, identifica las 3 mejores candidatas Y explica el tema estratégico de cada una (p. ej. “abre el archivo f para la torre”, “horquilla al rey y la dama”, “controla el puesto de avanzada d5”). Requiere entender no solo legalidad sino intención — exactamente donde las skills de dominio fuertes pagan.

**Por qué es buen material SDD:**
- Las reglas de ajedrez son precisas y completas — lo incorrecto es inequívocamente incorrecto
- Los temas estratégicos exigen vocabulario (clavadas, horquillas, outposts, archivos abiertos) → skills de dominio ricas
- La evaluación de posición tiene múltiples heurísticas en competencia → obliga a reglas de prioridad explícitas
- La librería chesslib existente está bien estructurada y tiene buena cobertura de tests sobre la que construir

**Domain skills que emergen de forma natural:**
- `piece-movement-rules` — legal moves per piece type including edge cases (en passant, castling)
- `tactical-pattern-vocabulary` — fork, pin, skewer, discovered attack, overloading
- `strategic-theme-detection` — open files, weak squares, pawn structure evaluation
- `position-evaluation-hierarchy` — material first, then structure, then dynamics
- `coaching-mode-explanation-format` — how to express strategic intent in plain language

**Seed CLAUDE.md:**
```markdown
# ChessEngine — Claude Development Guide

## Proyecto Overview
Java chess engine with coaching mode. Built on chesslib (bhlangonijr/chesslib).
Features: move generation, position evaluation, tactical pattern detection, coaching explanations.

## Architecture
- `engine/` — move generation (wraps chesslib), legal move filtering
- `evaluation/` — position scoring (material + structure + dynamics)
- `tactics/` — pattern detection (forks, pins, skewers, discovered attacks)
- `strategy/` — positional themes (open files, weak squares, outposts, pawn structure)
- `coaching/` — explanation generation, candidate move ranking, theme articulation

## Key Conventions
- Positions represented as FEN strings at API boundaries — always validate on entry
- Squares: algebraic notation (e4, d5) — NEVER integer indices in public APIs
- Evaluation scores: centipawns (int), positive = good for White
- Moves: `Move(from, to, promotion)` — always explicit, never implicit string parsing

## Constraints
- NEVER generate illegal moves — legal move generation is the hard invariant
- Evaluation must be side-relative (always from-the-side-to-move perspective)
- Coaching explanations must use standard chess vocabulary — no invented terms
- Engine must evaluate any position in < 100ms for interactive use
```

---

## Proyecto 7: ThreatHunter — Motor de detección de amenazas

**Tagline:** “Un falso negativo cuesta millones. Un falso positivo erosiona la confianza hasta que nadie revisa las alertas.”

**Repo a clonar:**
```bash
git clone https://github.com/opensearch-project/security-analytics  # OpenSearch security analytics
# Lighter alternative:
git clone https://github.com/Cantara/Whydah-SecurityTokenService  # SSO security service (Java)
```

**Brief del escenario:**
Tu empresa opera un motor de detección de amenazas tipo SIEM que procesa 800.000 eventos de log por minuto desde 400 servidores. Correlaciona eventos contra reglas de detección, asigna risk scores a entidades (usuarios, IPs, servicios) y escala anomalías al SOC. El problema: la fatiga de alertas es tan mala que los analistas ignoran el 70% — así que el único incidente real del trimestre pasado pasó desapercibido 11 días. Tu tarea: implementar un “suppression engine” que agrupe alertas relacionadas en una narrativa de incidente y suprima alertas hijas cuando hay un incidente padre abierto — sin ocultar por accidente amenazas genuinamente distintas.

**Por qué es buen material SDD:**
- Las reglas de detección tienen condiciones complejas (AND/OR, ventanas temporales, correlación de entidades)
- La lógica de supresión exige semántica precisa — “related” debe definirse exactamente
- El manejo de falsos positivos es un trade-off de negocio escrito en código
- El incidente de 11 días es un ancla perfecta para el “mayor riesgo técnico” del Ejercicio 1

**Domain skills que emergen de forma natural:**
- `detection-rule-semantics` — how rules combine conditions, thresholds, and time windows
- `entity-risk-scoring` — how to accumulate, decay, and reset risk scores over time
- `alert-correlation-rules` — what makes two alerts "related" for grouping purposes
- `suppression-policy` — parent/child alert relationships, suppression expiry, override conditions
- `incident-narrative-assembly` — what facts to include, chronological ordering, entity graph

**Seed CLAUDE.md:**
```markdown
# ThreatHunter Detection Engine — Claude Development Guide

## Proyecto Overview
Real-time security threat detection and alert correlation. Java 21, Spring Boot, Kafka, Redis.
Processes syslog, cloud audit logs, and application events. 400 monitored hosts.

## Architecture
Pipeline: `LogIngester` → `RuleEngine` → `RiskScorer` → `CorrelationEngine` → `AlertManager`
- `ingestion/` — log parsing, normalisation, enrichment (GeoIP, asset lookup)
- `rules/` — detection rule evaluation (Sigma rule format compatible)
- `scoring/` — entity risk accumulation, temporal decay, baseline deviation
- `correlation/` — alert grouping, incident assembly, suppression logic
- `escalation/` — SOC notification, ticket creation, runbook attachment

## Key Conventions
- All events have `EventId` (UUID) and `CorrelationId` for grouping — both always set
- Risk scores: 0–100 (int). Thresholds: INFO=20, LOW=40, MEDIUM=60, HIGH=80, CRITICAL=95
- Detection rules return `DetectionResult(matched, confidence, evidence)` — never boolean
- Entity identifiers normalised before scoring: IPs as `InetAddress`, users as `PrincipalId`

## Constraints
- NEVER suppress a CRITICAL alert — only MEDIUM and below are suppressible
- Risk scores MUST decay: halved every 24h if no new contributing events
- All suppression decisions logged with reason — audit trail required
- Rule engine must process each event in < 2ms (Kafka consumer SLA)
```

---

## Proyecto 8: RulesForge — Compilador DSL de reglas de negocio

**Tagline:** “La lógica de negocio pertenece al negocio. Un compilador hace que eso sea literalmente verdad.”

**Repo a clonar:**
```bash
git clone https://github.com/antlr/grammars-v4  # Browse for a business rules grammar
# Or the FEEL (Friendly Enough Expression Language) reference impl:
git clone https://github.com/camunda/feel-scala  # DMN decision tables
# Java DSL example:
git clone https://github.com/droolsjbpm/drools  # JBoss Drools (full rules engine)
```

**Brief del escenario:**
Una aseguradora evalúa 40.000 solicitudes de préstamo al día con reglas de elegibilidad que cambian trimestralmente. Hoy las reglas están embebidas en Java — cada cambio de negocio exige sprint, code review, release y regresión. Estás construyendo un compilador DSL que permite a los underwriters escribir reglas en una sintaxis tipo inglés estructurado, compilada a bytecode ejecutable. El manager de underwriting ya escribió 12 reglas de muestra en la sintaxis propuesta. Tu tarea: implementar el parser y el motor de evaluación para los primeros 4 tipos de regla (threshold, range, ratio, exclusion).

**Por qué es buen material SDD:**
- El parsing tiene reglas formales de gramática → escritura de skills extremadamente precisa
- Cada tipo de regla es un concepto de dominio distinto con su propia semántica de evaluación
- La restricción de “inglés estructurado” obliga a decisiones explícitas de vocabulario
- El pipeline de compilación (lex → parse → validate → emit) tiene fronteras de etapa claras

**Domain skills que emergen de forma natural:**
- `dsl-grammar-vocabulary` — keywords, operators, literal types, precedence rules
- `rule-type-semantics` — threshold vs range vs ratio vs exclusion evaluation logic
- `ast-node-taxonomy` — what nodes exist, what they contain, invariants per type
- `validation-pass-rules` — what makes a rule syntactically valid vs semantically valid
- `evaluation-context-model` — what facts are in scope during rule evaluation

**Seed CLAUDE.md:**
```markdown
# RulesForge DSL Compiler — Claude Development Guide

## Proyecto Overview
Business rules DSL for insurance underwriting. Java 21.
Compiles structured-English rule definitions to executable evaluation trees.
Processes 40,000 applications/day. Rules change quarterly without code deployment.

## Architecture
Compiler pipeline: `Lexer` → `Parser` → `ASTBuilder` → `SemanticValidator` → `Evaluator`
- `lexer/` — tokenisation (ANTLR4 generated)
- `parser/` — grammar rules, AST construction
- `ast/` — node types (RuleNode, ConditionNode, ThresholdNode, RangeNode, etc.)
- `validation/` — semantic checks (type compatibility, fact references, circular conditions)
- `evaluation/` — tree-walk evaluator, fact context, result collector

## Key Conventions
- AST nodes are sealed interfaces — exhaustive pattern matching in evaluator
- All numeric comparisons use `BigDecimal` — no floating point in financial rules
- Parser errors use `ParseError(line, col, message)` — always include position
- `EvaluationContext` is immutable — facts loaded once per application

## Constraints
- NEVER evaluate a rule that failed semantic validation
- Rule identifiers must be globally unique — `RuleRegistry` enforces this
- Evaluation must be deterministic and side-effect free
- Max rule depth: 10 nested conditions (stack overflow prevention)
```

---

## Proyecto 9: FleetMind — Coordinación de flota de drones

**Tagline:** “Un drone es un robot. Cien drones son un sistema distribuido con rotores.”

**Repo a clonar:**
```bash
git clone https://github.com/ArduPilot/ardupilot  # Real drone autopilot (C++, heavy)
# Java mission planning alternative:
git clone https://github.com/dronekit/dronekit-java
# Or scaffold a lighter coordinator:
mvn archetype:generate -DgroupId=no.fleetmind -DartifactId=fleet-coordinator -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
```

**Brief del escenario:**
Una empresa de logística opera 120 drones de entrega en tres hubs de distribución. Tu software asigna misiones a drones, planifica rutas que evitan espacio aéreo restringido y entre ellos, monitorea batería en vuelo y replanifica automáticamente cuando un drone reporta un problema. La semana pasada, dos drones fueron asignados al mismo pad de aterrizaje a la vez — colisión menor, ambos reparados, pero el claim de seguro dispara una revisión completa del sistema. Tu tarea: implementar un sistema de reserva de pads con locking exclusivo que evite la race condition de doble asignación.

**Por qué es buen material SDD:**
- Los bugs de concurrencia (doble asignación) exigen invariantes explícitas → skills fuertes de verificación
- Las restricciones de espacio aéreo son regulatorias — no se pueden “optimizar” fuera
- La gestión de batería tiene constraints duros (nunca bajo 20%) y blandos (preferir > 40% al asignar)
- La planificación de rutas tiene objetivos en competencia (camino más corto vs menos conflicto aéreo) → obliga a prioridad explícita

**Domain skills que emergen de forma natural:**
- `drone-state-machine` — IDLE → ASSIGNED → IN_FLIGHT → LANDING → CHARGING state transitions
- `airspace-restriction-types` — permanent NFZ, temporary (NOTAM), dynamic (weather), conflict zones
- `battery-management-rules` — assignment threshold, return-to-home trigger, emergency landing criteria
- `pad-reservation-protocol` — lock acquisition, exclusive access, timeout and release rules
- `route-planning-constraints` — separation minima, altitude layers, no-cross zones

**Seed CLAUDE.md:**
```markdown
# FleetMind Coordinator — Claude Development Guide

## Proyecto Overview
Drone fleet coordination for last-mile logistics. Java 21, Spring Boot, Redis (distributed locks).
120 drones, 3 hubs, ~800 deliveries/day. Real-time telemetry via WebSocket.

## Architecture
- `assignment/` — mission-to-drone matching, availability checking, capacity planning
- `routing/` — path planning (A* on airspace grid), conflict detection, replanning
- `airspace/` — restriction zones, NOTAM integration, dynamic exclusion management
- `telemetry/` — real-time drone state, battery monitoring, anomaly detection
- `ground/` — landing pad management, charging scheduling, maintenance queuing

## Key Conventions
- Drone positions as `GeoCoordinate(lat, lon, altMetres)` — always WGS84
- All pad reservations via `PadReservationService` — NEVER update pad state directly
- Battery level: 0.0–1.0 (not percentage). Minimum for new assignment: 0.40
- Mission states logged with timestamps — full audit trail required

## Constraints
- NEVER assign a mission to a drone below 40% battery
- NEVER assign two drones to the same pad simultaneously (use distributed lock)
- Return-to-home triggers at 25% battery regardless of mission state
- Restricted airspace violations are BLOCKING — route must reroute, never penetrate
```

---

## Proyecto 10: BioSeq — Pipeline de análisis genómico

**Tagline:** “Tres mil millones de pares de bases. Tu trabajo es encontrar el que importa.”

**Repo a clonar:**
```bash
git clone https://github.com/samtools/htsjdk  # Java genomics toolkit (used by GATK)
# Or the teaching-friendly:
git clone https://github.com/biojava/biojava  # BioJava — sequence analysis library
```

**Brief del escenario:**
Un laboratorio de genómica clínica secuencia biopsias tumorales para identificar mutaciones accionables — variantes en el ADN del paciente que indican qué terapia contra el cáncer tiene más probabilidad de funcionar. Tu pipeline alinea reads contra el genoma de referencia, llama variantes (posiciones donde el tumor difiere del tejido normal), filtra artefactos de secuenciación y anota variantes con significancia clínica. Una auditoría de calidad reciente encontró que el 8% de las variantes reportadas eran artefactos de regiones de baja calidad que el filtro debió atrapar. Tu tarea: mejorar el filtro de calidad de variantes sin aumentar el false negative rate (perder variantes reales es peor que reportar artefactos).

**Por qué es buen material SDD:**
- Los filtros de calidad tienen dos tipos de error (FP y FN) que se intercambian → obliga a documentar umbrales explícitos en skills
- Las coordenadas genómicas exigen manejo cuidadoso (0-based vs 1-based, naming de cromosomas)
- La anotación clínica tiene implicaciones regulatorias — la clasificación debe ser trazable
- El hallazgo de auditoría le da al Ejercicio 1 una deuda técnica específica y cuantificada

**Domain skills que emergen de forma natural:**
- `variant-calling-criteria` — minimum read depth, allele frequency thresholds, strand bias limits
- `quality-filter-thresholds` — which metrics to filter on and why, sensitivity/specificity trade-off
- `genomic-coordinate-conventions` — 0-based vs 1-based, UCSC vs Ensembl chromosome naming
- `clinical-variant-classification` — pathogenic / likely pathogenic / VUS / likely benign / benign
- `artefact-signature-patterns` — oxidative damage, FFPE artefacts, strand bias, low complexity regions

**Seed CLAUDE.md:**
```markdown
# BioSeq Analysis Pipeline — Claude Development Guide

## Proyecto Overview
Clinical tumour variant detection pipeline. Java 21, HTSJDK for BAM/VCF I/O.
Input: aligned sequencing reads (BAM). Output: annotated variant calls (VCF + clinical report).

## Architecture
Pipeline: `BamReader` → `VariantCaller` → `QualityFilter` → `Annotator` → `ReportGenerator`
- `alignment/` — BAM file processing, pileup generation, read quality assessment
- `calling/` — variant detection (SNVs, indels), allele frequency calculation
- `filtering/` — artefact removal, quality threshold application, blacklist regions
- `annotation/` — ClinVar lookup, gene function, clinical significance classification
- `reporting/` — variant report generation, QC metrics, audit trail

## Key Conventions
- Genomic positions are ALWAYS 0-based internally — convert to 1-based only at output
- Chromosome names normalised to UCSC format (chr1, chr2... chrX, chrY, chrM)
- Allele frequency: 0.0–1.0 (not percentage). Minimum reportable: 0.01 (1%)
- All filter decisions logged with reason — clinical audit requirement

## Constraints
- NEVER report a variant without a quality score — missing quality = filtered out
- Clinical classification MUST reference a ClinVar accession or state "novel"
- False negative rate target: < 2% for pathogenic variants — prioritise sensitivity
- All pipeline runs reproducible: random seed fixed, tool versions logged
```

---

## Proyecto 11: LegalVault — Motor de ciclo de vida de contratos

**Tagline:** “Cada contrato es una promesa. El trabajo del motor es recordarlas todas.”

**Repo a clonar:**
```bash
# No single canonical open-source example — scaffold:
mvn archetype:generate -DgroupId=io.legalvault -DartifactId=contract-engine -DarchetypeArtifactId=maven-archetype-quickstart -DinteractiveMode=false
# Or explore:
git clone https://github.com/hyperledger/fabric-samples  # Smart contracts on blockchain
```

**Brief del escenario:**
Un equipo de procurement gestiona 1.400 contratos de proveedores por €340M combinados. Tu motor extrae obligaciones del texto contractual, trackea su estado y dispara alertas cuando se acercan deadlines o se incumplen términos. Compliance acaba de descubrir que 23 contratos con cláusulas de auto-renovación se renovaron solos el mes pasado sin que nadie lo notara — la ventana de notice pasó antes de que disparara la alerta. Tu tarea: reescribir la lógica de notificación de renovación para que las alertas disparen a lead times configurables (90/30/7 días antes del deadline de opt-out), y añadir un gate de confirmación manual que impida auto-renovación salvo aprobación explícita.

**Por qué es buen material SDD:**
- Las obligaciones contractuales son un modelo de dominio rico (pago, entrega, compliance, renovación, terminación)
- La lógica temporal (deadlines, notice periods, fechas efectivas) exige aritmética de fechas precisa
- La consecuencia de negocio de los errores es muy concreta — exposición de €340M
- El bug de renovación le da al Ejercicio 1 un riesgo mayor obvio con un fallo real documentado

**Domain skills que emergen de forma natural:**
- `obligation-taxonomy` — payment, delivery, notice, renewal, reporting, compliance obligation types
- `date-arithmetic-rules` — business days vs calendar days, jurisdiction holidays, notice period counting
- `renewal-clause-semantics` — auto-renewal triggers, opt-out windows, confirmation requirements
- `contract-state-machine` — DRAFT → ACTIVE → PENDING_RENEWAL → RENEWED / TERMINATED
- `alert-escalation-rules` — lead time tiers, recipient routing by obligation type, confirmation tracking

**Seed CLAUDE.md:**
```markdown
# LegalVault Contract Engine — Claude Development Guide

## Proyecto Overview
Contract lifecycle management for procurement. Java 21, Spring Boot, PostgreSQL.
1,400 active contracts, €340M combined value. Integration with DocuSign and SAP.

## Architecture
- `extraction/` — obligation parsing from contract text (NLP + structured templates)
- `obligations/` — obligation model, status tracking, fulfilment recording
- `calendar/` — deadline calculation, business day logic, jurisdiction calendar
- `alerts/` — notification scheduling, escalation chains, confirmation workflows
- `audit/` — immutable obligation history, change tracking, breach documentation

## Key Conventions
- All dates as `LocalDate` (no time component for contract dates) — timezone irrelevant
- Monetary values as `Money(amount: BigDecimal, currency: Currency)` — never raw double
- Obligation IDs are immutable after creation — obligations are never updated, only superseded
- "Business days" always specifies jurisdiction: `BusinessCalendar.of(Jurisdiction.NO)`

## Constraints
- Auto-renewal MUST require explicit `RenewalApproval` record — no silent renewals
- Alerts for renewal opt-out windows fire at 90, 30, and 7 days — all three, always
- Obligation status changes are append-only (event sourced) — NEVER update status in place
- Contract value changes require dual approval (requestor + legal) — enforced in service layer
```

---

## Proyecto 12: GameServer — Server autoritativo multiplayer

**Tagline:** “Los clientes mienten. La latencia miente. El server es la única verdad.”

**Repo a clonar:**
```bash
git clone https://github.com/Alaskan-Fox/java-game-server  # Lightweight Java game server
# Or the networking layer:
git clone https://github.com/jhalterman/lyra  # Resilient RabbitMQ (for game messaging patterns)
# Full-featured example:
git clone https://github.com/OpenMUOnline/OpenMU  # C# but architecture is exemplary
```

**Brief del escenario:**
Estás construyendo el server de un shooter táctico de 64 jugadores. Corre a 60 ticks/segundo, procesa inputs (movimiento, disparo, habilidades), simula física, valida que las acciones sean legales (no disparar a través de paredes, no moverse más rápido que el máximo) y hace broadcast de snapshots del mundo a todos los clientes. Los jugadores tienen latencias de 20ms a 250ms — el server debe manejar lag compensation (rewind del estado para validar disparos en el momento en que el cliente disparó, no cuando el server recibió el input). La semana pasada se encontró un exploit de speedhack — clientes enviaban inputs de movimiento que excedían la velocidad máxima en 400%. Tu tarea: implementar la validación de movimiento que lo atrape.

**Por qué es buen material SDD:**
- La simulación a tick-rate tiene requisitos estrictos de timing → constraints de performance precisos en skills
- Lag compensation (rewind de estado) es conceptualmente complejo → obliga a skills de dominio cuidadosas
- El anti-cheat es adversarial — el atacante conoce tus reglas — así que la validación debe ser conservadora
- El exploit de speedhack le da al Ejercicio 1 una vulnerabilidad de seguridad concreta y probada

**Domain skills que emergen de forma natural:**
- `tick-simulation-loop` — input processing order, physics step, snapshot broadcasting, timing guarantees
- `movement-validation-rules` — max speed, acceleration limits, wall collision, teleport detection
- `lag-compensation-model` — rewind depth limit, interpolation vs extrapolation, when to rewind vs reject
- `anti-cheat-signal-taxonomy` — speed anomalies, position discontinuities, impossible action timing
- `world-state-snapshot-format` — what to include, delta compression, priority by proximity

**Seed CLAUDE.md:**
```markdown
# GameServer — Authoritative Multiplayer Server — Claude Development Guide

## Proyecto Overview
Authoritative game server for 64-player tactical shooter. Java 21, Netty (UDP + TCP).
60 ticks/second simulation. Lag compensation up to 250ms. Anti-cheat validation on all inputs.

## Architecture
- `network/` — UDP packet handling (Netty), connection management, jitter buffer
- `simulation/` — world state, physics step, entity management (ECS pattern)
- `validation/` — input validation, anti-cheat checks, lag-compensated hit detection
- `snapshot/` — world state serialisation, delta compression, per-client priority queuing
- `replay/` — state history ring buffer (last 500 ticks = ~8 seconds), rewind for lag comp

## Key Conventions
- All positions as `Vec3(x, y, z)` with float precision — client uses same type
- Tick number is the authoritative timestamp — NEVER use wall clock for game logic
- Inputs validated before application — `ValidationResult(accepted, reason)` always returned
- State history is a fixed-size ring buffer — NEVER grow it dynamically

## Constraints
- NEVER trust client-reported position — server always derives position from inputs
- Maximum rewind depth: 250ms (15 ticks at 60Hz) — older inputs rejected, not rewound
- Movement validation tolerance: +5% over max speed (network jitter allowance), not +400%
- All anti-cheat violations logged with full input history for forensic review
```

---

## Notas para el facilitador

**Qué proyecto para qué audiencia:**

| Audiencia | Mejor fit | Por qué |
|-----------|-----------|---------|
| Java enterprise (banca, seguros) | QuantumTrade | Order management es análogo directo a sus sistemas |
| Cloud/DevOps/Platform | NeuralProxy | Viven en territorio gateway/middleware |
| Hardware o embedded | AstroNav o EcoGrid | Las restricciones físicas mapean a su dominio |
| Consultores (industria mixta) | MediSched o LegalVault | Reglas complejas, audit claro, relatables |
| Generalistas curiosos / estudiantes | ChessEngine o GameServer | Sin prerrequisito de dominio; reglas bien documentadas |
| Sostenibilidad / sector energético | EcoGrid | Relevancia directa |
| Security / SOC / DevSecOps | ThreatHunter | Espeja su día a día |
| Biotech / pharma / health-data | BioSeq | Dominio clínico, arquitectura de pipeline |
| Drones / robótica / autónomos | FleetMind | Coordinación multi-agente, restricciones físicas |
| Legal tech / procurement / GRC | LegalVault | Dominio contractual, lógica temporal, audit |
| Platform / language tooling | RulesForge | Compiladores, diseño DSL, gramáticas formales |
| Game dev / simulación | GameServer | Anti-cheat, lag compensation, simulación autoritativa |

**Asignación de tiempo para proyectos del idea bank:**
- 10 min: Leer el brief del escenario + clonar el repo
- 15 min: Ejercicio 1 (evaluación baseline)
- El resto sigue el flujo normal del workshop

**Preguntas frecuentes del facilitador:**

*"No conozco nada de este dominio — ¿cómo ayudo?"*
No necesitas. El punto es que Claude Code tampoco lo conoce — y verlo aprender de las skills que escribe el participante ES la demostración. Tu trabajo es preguntar “¿qué pondrías en la skill?”, no saber la respuesta.

*"El participante eligió ajedrez y solo quiere hablar de ajedrez."*
Está bien. La metodología SDD emerge del engagement con el dominio. Engagement profundo produce mejores skills que engagement superficial en muchos temas.

*"El repo no compila."*
Cae al comando de scaffold (`mvn archetype:generate`), crea 3 clases de dominio a mano (5 min) y corre el Ejercicio 1 sobre un codebase pequeño pero real. El ejercicio funciona con 100 líneas si el dominio está claro.

---

*Metodología y materiales: Totto (eXOReaction AS). Presentación ES: Jose Diaz Diaz.*
