# SDD Workshop Boost

**Skill-Driven Development — Distribución de skills de metodología**  
**Versión:** 1.0.0 | **Tipo:** Exclusivo de workshop

Instala 19 skills de metodología de nivel producción en tu entorno de Claude Code. Estas skills se extrajeron de 197.831 líneas de código de producción real construido en 11 días: codifican las lecciones aprendidas, no “mejores prácticas” teóricas.


## Qué se instala

**19 skills → `~/.claude/skills/<nombre>/SKILL.md`** (activas en cada sesión de Claude, en cada proyecto)

Claude Code solo descubre skills en formato directorio (`SKILL.md` con frontmatter). Los `.yaml` del paquete se **convierten** a ese layout al instalar; no se copian planos a `common/`.

| Categoría | Skills | Pilares |
|-----------|--------|---------|
| Navegador de metodología | `sdd-context` | Todos |
| Ingeniería de contexto | `claude-md-guidelines`, `skill-routing-decisions`, `skill-navigator-pattern`, `context-engineering-audit` | 1, 6 |
| Verificación y calidad | `fear-driven-development`, `verification-patterns`, `tdd-workflow`, `regression-prevention`, `proactive-bug-hunting` | 3 |
| Orquestación de IA | `directed-synthesis` | 4 |
| Disciplina de proceso | `github-workflow` | 5 |
| Comunicación | `tone-of-voice`, `writing-patterns`, `documentation-style`, `docs-organization` | 1 |
| Patrones de ingeniería | `change-tracking`, `smart-file-matching`, `java-record-breaking-changes` | — |

**3 templates** (scaffolding de proyecto, opcionales):
- `CLAUDE.md` — archivo de contexto del proyecto (rellena los huecos)
- `LEARNINGS.md` — bitácora de aprendizaje continuo (Pilar 6)
- `skill-template.yaml` — template mínimo de 3 secciones para tu primera skill de dominio

**Bonus: skill KCP** (`starter-kcp`):
- `starter-kcp.yaml` — Añade un manifiesto `knowledge.yaml` a tu proyecto para que cualquier IA lo navegue en 3 tool calls en lugar de 33

---

## Instalación

Abre Claude Code **en el directorio que contiene este paquete**, y pega estos dos prompts — en orden.

### Paso A — Boost Skills

```
"Lee el README de este paquete y todas las skills de este directorio.
Instálalas e intégralas de forma global en mi setup de Claude Code.
Verifica que cada skill cargue correctamente y confirma cuando termines."
```

Claude hará: leer el README → convertir cada skill a `~/.claude/skills/<nombre>/SKILL.md` → instalar archivos de memoria (`~/.sdd/memory/`) → copiar templates (`~/.claude/sdd-templates/`) → reportar con un conteo. No hace falta script de shell.

> **Nota:** `~/.claude/skills/common/` es una convención antigua. El runtime actual no carga skills desde ahí.

### Paso B — KCP desde GitHub (versiones más recientes)

```
"Busca kcp-commands y kcp-memory en GitHub:
https://github.com/orgs/Cantara/repositories?q=kcp
Instala las versiones más recientes directamente (no las embebidas).
Intégralas y verifica que ambas funcionen en esta sesión."
```

Claude hará: encontrar los repos → bajar los últimos releases → instalar kcp-commands (filtrado de output CLI) y kcp-memory (memoria episódica de sesión) → verificar que estén activos.

> **¿Por qué desde GitHub?** El paquete boost incluye un snapshot de kcp en un momento concreto. GitHub siempre tiene lo último. Instalar en vivo garantiza fixes y mejoras actuales.

### Fallback legacy (solo shell)

Si aún no puedes usar Claude Code:

```bash
cd /path/to/sdd-joedayz-workshop
./install.sh
```

Esto convierte e instala las skills del joedayz workshop en `~/.claude/skills/<nombre>/SKILL.md` — kcp hay que instalarlo aparte desde GitHub.

---

## Después de instalar

Abre tu proyecto en Claude Code. Pregunta:

```
"What SDD skills do I have?"
```

Claude leerá `sdd-context` y te guiará por la metodología completa.

O salta directo al trabajo:

```
"Am I following process discipline?"
"Which pillar applies to this refactoring?"
"Should this pattern become a skill?"
```

---

## Los 6 pilares

| # | Pilar | Idea central |
|---|--------|--------------|
| 1 | Contexto inteligente | CLAUDE.md + skills = el ADN de tu codebase, siempre disponible |
| 2 | Delegación estratégica | Haiku para el 60-70% de las tareas (~20× más barato que Opus). Sonnet/Opus para el resto. |
| 3 | Confía, pero verifica | La IA alucinará. Construye sistemas para atraparlo barato. |
| 4 | Síntesis dirigida | TÚ eres el director. Claude propone, el humano decide. |
| 5 | Disciplina de proceso | Solo flujo por PR. Los guardrails habilitan velocidad, no la limitan. |
| 6 | Aprendizaje continuo | Cada bug arreglado → skill actualizada. El contexto mejora en cada sesión. |

---

## La prueba

**lib-pcb** (16–27 de enero de 2026):
- 197.831 líneas de Java en 11 días
- 7.461 tests, 99.8% de pass rate
- Estándar de la industria: 10–18 meses
- Logrado con: 85 skills de dominio + estas 19 skills de metodología

**Claim conservador:** una mejora de productividad de 10-30× es típica.

**Sectores validados:** Manufactura, energía renovable, servicios financieros, seguridad de IA

---

## Escribir tu primera skill de dominio

Las skills de metodología (esta distribución) cubren el CÓMO del SDD.  
Tus skills de dominio cubren los patrones específicos de TU proyecto.

Empieza aquí:
1. Crea `.claude/skills/[nombre-de-tu-skill]/SKILL.md` (usa `templates/skill-template.yaml` como base del contenido)
2. Responde: “¿Qué le sigo explicando a Claude sobre mi codebase?”
3. Escríbelo una vez, en la skill. No lo vuelvas a explicar.
4. Prueba: abre una sesión nueva de Claude, pídele que haga la cosa. ¿Siguió tu skill?

**Cuándo crear un navigator:** Cuando tengas 10+ skills de dominio, lee `skill-navigator-pattern`.


## Contenido de la distribución

```
sdd-joedayz-workshop/
  install.sh              # Instalador (global o por codebase)
  README.md            # Esta traducción (español)
  skills/                 # 27 skills + sdd-navigator
  memory/                 # MEMORY.md de routing + 4 topic files
  templates/              # CLAUDE.md, LEARNINGS.md, skill-template.yaml
  tutorial/               # Tutorial self-paced de 6 pasos (~2 horas)
  facilitator/            # Demo script, timing sheets, recuperación de fallos
```

---

## ¿Sin codebase? Usa el Idea Bank

**[IDEA-BANK.es.md](./IDEA-BANK.es.md)** — 12 proyectos prediseñados para participantes que no trajeron su propio codebase. Cada uno tiene un brief de escenario, un repo para clonar, un CLAUDE.md semilla y una lista de skills de dominio por descubrir. Proyectos: QuantumTrade, AstroNav, EcoGrid, NeuralProxy, MediSched, ChessEngine, ThreatHunter, RulesForge, FleetMind, BioSeq, LegalVault, GameServer.


## Guía del día de workshop

**[WORKSHOP-DAY.es.md](./WORKSHOP-DAY.es.md)** — El tutorial hands-on del día de workshop. Cubre los 6 ejercicios en secuencia con prompts exactos, ejemplos de output y templates YAML. Ábrelo en tu laptop y síguelo.

| Ejercicio | Tema |
|-----------|------|
| Ex 1 | Evaluación baseline de tu codebase |
| Ex 2 | Escribe tu CLAUDE.md |
| Ex 3 | Crea tus primeras 3 skills (arquitectura, dominio, QA) |
| Ex 4 | Patrón template — Sonnet diseña, Haiku ejecuta |
| Ex 5 | Expansión de la suite de tests |
| Ex 6 | Skill de QA + aprendizaje continuo |

---