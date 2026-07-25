# Skill-Driven Development: Tutorial hands-on

**Metodología:** Skill-Driven Development (SDD)  
**Tiempo:** 6–8 horas (ritmo workshop) o a tu ritmo  
**Stack:** Agnóstico de lenguaje (ejemplos en Java/Spring Boot y TypeScript/React)


> **Idioma:** Traducción de [`WORKSHOP-DAY.md`](./WORKSHOP-DAY.md) — **Ejercicios 1–3** (los esenciales para la charla / día 1).  
> Ejercicios 4–6 → ver el original en inglés: [`WORKSHOP-DAY.md`](./WORKSHOP-DAY.md#exercise-4-trust-but-verify--the-template-pattern).  
> Los prompts a Claude se mantienen en inglés (mejor resultados técnicos).

---

## Por qué SDD (y no solo prompting)

La mayoría de los desarrolladores usan la IA como un buscador: hacen una pregunta, reciben una respuesta, siguen adelante. Cada sesión empieza de cero. La IA no conoce tu codebase, las convenciones de tu equipo, ni los errores que cometiste la semana pasada.

Skill-Driven Development trata a la IA como un **sistema**, no como una herramienta. Construyes una librería de skills reutilizables — cada una codifica conocimiento de dominio, instrucciones y criterios de verificación. Cada sesión arranca con esa librería cargada. Cada error que corriges mejora la librería. La IA se vuelve mejor en tu codebase cada día que la usas.

El efecto compuesto es real. En 11 días, un solo desarrollador construyó una librería Java de 197.831 líneas usando SDD — lo que toma 10–18 meses de forma tradicional. La librería de skills creció a 75 entradas. Cada skill nueva hizo más rápida la siguiente tarea. Para el día 11, la IA operaba al nivel de un arquitecto senior que hubiera estado en el proyecto desde el principio.

Más reciente: en un workshop de Item Consulting (marzo 2026), un participante entregó 15.500 líneas de código, 326 tests y 82% de cobertura en 2 días — partiendo de cero en un codebase desconocido. Misma metodología.

Este tutorial te enseña a construir ese sistema sobre **tu** codebase.

---

## Prerrequisitos

Antes de empezar, verifica:

```bash
claude --version          # debe imprimir el número de versión
claude doctor             # debe mostrar checkmarks verdes
```

También necesitas:
- **Un codebase** con al menos algo de código funcionando (idealmente un proyecto real que te importe)
- **Git** (`git status` debe funcionar en el directorio del proyecto)
- **Tu build tool** corriendo: `mvn test` o `npm test` o `gradle test` — algo debe pasar

**¿No tienes codebase?** Usa el **[IDEA-BANK.md](./IDEA-BANK.md)** — escenarios de proyecto prediseñados con repos para clonar, CLAUDE.md semilla y un brief. Elige uno, clónalo y sigue desde el Ejercicio 1. Toma ~10 minutos montarlo.

Si `claude doctor` falla, mira [la guía de setup](https://docs.anthropic.com/en/docs/claude-code) antes de continuar.

---

## Ejercicio 1: Evaluación baseline

Antes de mejorar nada, mide dónde estás. Eso crea tu punto de referencia — y a menudo saca a la luz cosas que no sabías que no sabías.

### Qué ejecutar

Abre Claude Code en el directorio de tu proyecto:

```bash
cd your-project
claude
```

Luego pregunta:

```
Analyse this codebase and give me:
1. Overall architecture pattern (MVC, hexagonal, layered, etc.)
2. Test count and estimated coverage
3. Three biggest technical risks or debt areas
4. How long the build takes
5. Dependencies that are outdated or unusual

Be specific. Use actual class names, file paths, and numbers where possible.
```

### Cómo se ve un buen output

```
Architecture: Layered (controller → service → repository). Spring Boot 3.2.
Standard MVC pattern — no hexagonal or clean architecture separation.

Tests: 47 unit tests, 12 integration tests. Maven Surefire reports ~61% line coverage.
No mutation testing configured.

Technical risks:
1. CustomerService.java (847 lines) — god class. Everything touches it.
   Methods: createCustomer, updateCustomer, deleteCustomer, sendWelcomeEmail,
   generateInvoice, processPayment... this needs breaking up.
2. No contract testing. OrderController and the downstream InventoryService share
   assumptions that aren't verified anywhere.
3. build.gradle still pins Spring Boot 2.7.18. EOL January 2024.

Build time: mvn test takes 3m 42s (slow — mostly integration tests hitting H2).

Unusual deps: commons-lang 2.6 (ancient, should be commons-lang3) and
guava 20.0 (current is 33.x).
```

### Registra lo que encontraste

Escribe tres oraciones resumiendo: cuál es la arquitectura, cuál es el riesgo más grande, y en qué te vas a enfocar hoy.

---

## Ejercicio 2: Escribe tu CLAUDE.md

`CLAUDE.md` es lo primero que Claude Code lee cuando lo abres en un proyecto. Es tu contexto persistente: convenciones, restricciones, conocimiento de dominio y acuerdos de trabajo. Cada sesión arranca con él. Lo escribes una vez y lo refinas con el tiempo.

### Crear el archivo

En la raíz de tu proyecto:

```bash
touch CLAUDE.md
```

Luego abre Claude Code y pregunta:

```
Based on your analysis of this codebase, help me write a CLAUDE.md file.
Include: project overview, architecture, key conventions, test strategy,
important constraints, and anything an experienced developer joining the
team would need to know in the first hour.

Format: markdown headers, be specific, use actual class and package names.
```

### Revisar y editar el borrador

Claude generará un punto de partida. Tu trabajo es:
1. Quitar todo lo que esté mal
2. Añadir lo que se saltó (sobre todo reglas de negocio que no puede inferir del código)
3. Hacer fuerte la sección de constraints — ahí es donde evitas que la IA haga tonterías

### Cómo se ve un buen CLAUDE.md

```markdown
# OrderService — Claude Development Guide

## Project Overview
REST API for order management. Java 21, Spring Boot 3.2, PostgreSQL.
Deployed to Azure Kubernetes. ~30K LOC, 59 tests.

## Architecture
Layered: Controller → Service → Repository
- `com.example.order.api` — REST controllers (request/response DTOs)
- `com.example.order.domain` — business logic (services, domain objects)
- `com.example.order.infrastructure` — JPA repositories, external API clients

## Key Conventions
- Naming: `*Controller`, `*Service`, `*Repository` — always suffix
- DTOs are immutable records: `public record CreateOrderRequest(String customerId, ...)`
- Never put business logic in controllers — it goes in services
- Repository methods return `Optional<T>` — never null

## Test Strategy
- Unit tests: JUnit 5 + AssertJ. No Spring context in unit tests.
- Integration tests: `@SpringBootTest` + Testcontainers (real PostgreSQL)
- Run: `mvn test` (unit), `mvn verify` (all including integration)
- Coverage threshold: 80% line coverage enforced in CI

## Constraints
- NEVER commit directly to main — always PR
- NEVER use field injection (@Autowired on fields) — constructor injection only
- NEVER catch and swallow exceptions — log or rethrow with context
- All database migrations via Flyway — no schema changes outside migrations
- CustomerService is a known god class — don't add more to it

## What's In Progress
- Breaking up CustomerService (PaymentService extracted Feb 2026)
- Upgrading Spring Boot from 2.7 to 3.2 (in progress, blocking tests on auth module)
```

### La sección más importante: Constraints

La sección de constraints le enseña a Claude qué **NO** hacer. Lista cosas que ya salieron mal. Lista los no-negociables de tu equipo. La IA los va a seguir.

---

## Ejercicio 3: Tus primeras tres skills

Una skill es un archivo `.yaml` reutilizable que le dice a Claude cómo hacer una tarea específica en tu codebase. Las skills viven en `~/.claude/skills/`. Se cargan bajo demanda.

Para empezar necesitas tres tipos:

1. **Skill de arquitectura** — cómo está estructurado tu sistema (patrones, naming, capas)
2. **Skill de dominio** — qué hace realmente tu dominio de negocio
3. **Skill de QA** — cómo verificas que el código es correcto

### Estructura de una skill

Todas las skills tienen la misma forma:

```yaml
name: skill-name
description: One sentence: what this skill enables
version: 1.0.0
tags: [relevant, tags]

instructions: |
  # [Skill Name]

  ## Context
  What the AI needs to know before starting

  ## Steps
  1. Step one
  2. Step two
  3. Step three

  ## Verification
  - How to confirm it worked
  - What tests to run
  - What to check manually
```

### Skill 1: Tu skill de arquitectura

Archivo: `~/.claude/skills/[project-name]-architecture.yaml`

Pídele a Claude que la redacte:

```
Create a Claude Code skill file for our architecture.
It should help any AI agent working on this codebase understand:
- Layer structure and what goes where
- Naming conventions
- How dependencies flow (what can call what)
- Common patterns used (factories, builders, events, etc.)
- Anti-patterns we explicitly avoid

Output a complete YAML skill file.
```

Edita el output. Añade lo que se saltó. Sobre todo: gotchas que ya te mordieron.

### Skill 2: Tu skill de dominio

Archivo: `~/.claude/skills/[domain-name]-domain.yaml`

```
Create a Claude Code skill that captures our domain model.
Include:
- The main domain concepts and what they mean (use our actual terminology)
- Key business rules (what's valid, what's not)
- Important invariants — things that must always be true
- Domain events or state machines if relevant
- Examples of correct domain usage

This is our business language, not our code structure.
```

Ejemplo de una skill de dominio fuerte:

```yaml
name: order-domain
description: Domain model and business rules for the order management system
version: 1.0.0
tags: [domain, business-rules, order]

instructions: |
  # Order Domain

  ## Core Concepts
  - **Order**: A request to purchase one or more products. Has a lifecycle:
    DRAFT → CONFIRMED → PICKING → SHIPPED → DELIVERED (or CANCELLED at any stage)
  - **LineItem**: A specific product + quantity within an order
  - **Customer**: Has a credit limit. Orders can be blocked if credit exceeded.
  - **Fulfilment**: The physical process of picking, packing, shipping

  ## Key Business Rules
  - An order CANNOT be confirmed if any LineItem has zero quantity
  - Customer credit check happens at CONFIRMATION, not at DRAFT creation
  - SHIPPED orders cannot be cancelled — must go through returns process
  - Prices are fixed at confirmation time, not order creation
  - A customer can have max 5 CONFIRMED orders pending at once

  ## Invariants
  - Order total = sum of (lineItem.price × lineItem.quantity)
  - Order status only moves forward (no going back from CONFIRMED to DRAFT)
  - Every order MUST have a customer — orphan orders are a data integrity error

  ## Common Mistakes
  - Confusing "order value" (at current prices) with "confirmed value" (at confirmation prices)
  - Assuming cancellation is always possible — check status first
  - Forgetting that credit check blocks confirmation, not creation
```

### Skill 3: Tu primera skill de QA

Archivo: `~/.claude/skills/[project-name]-qa.yaml`

```
Create a Claude Code QA skill for this codebase. It should guide any agent
doing test work to:
- Know what test types we use and when
- Know our test naming convention
- Know where test files live
- Know how to run tests and interpret output
- Know what counts as "done" from a quality perspective

Include our actual Maven/Gradle/npm commands.
```

### Usa tus skills nuevas

Pruébalas de inmediato:

```
Using the order-domain skill, add a new domain rule: customers with
SUSPENDED status cannot create new orders. Add the validation to
OrderService and write tests for it.
```

Observa cómo la IA aplica tus reglas de dominio y convenciones de naming automáticamente. Eso es la skill trabajando.

---

## Siguiente

Con los Ejercicios 1–3 tienes: baseline, `CLAUDE.md` y 3 skills (arquitectura, dominio, QA). Eso es el núcleo de Pillar 1 y el arranque de Pillar 3.

| Siguiente | Dónde |
|-----------|--------|
| Ex 4 — Patrón template (Sonnet diseña, Haiku ejecuta) | [`WORKSHOP-DAY.md`](./WORKSHOP-DAY.md#exercise-4-trust-but-verify--the-template-pattern) |
| Ex 5 — Expandir suite de tests | mismo archivo |
| Ex 6 — Skill QA review + LEARNINGS.md | mismo archivo |
| Instalar el boost | [`README.es.md`](./README.es.md) |
| Ensayar el demo | [`facilitator/demo-script.es.md`](./facilitator/demo-script.es.md) |

---

*Metodología y materiales: Totto (eXOReaction AS). Presentación ES: Jose Diaz Diaz.*
