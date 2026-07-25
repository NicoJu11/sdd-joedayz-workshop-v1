# SDD Workshop Boost

**Skill-Driven Development — Distribución de skills de metodología**  
**Versión:** 1.0.0 | **Tipo:** Exclusivo de workshop

Instala 19 skills de metodología de nivel producción en tu entorno de Claude Code. Estas skills se extrajeron de 197.831 líneas de código de producción real construido en 11 días: codifican las lecciones aprendidas, no “mejores prácticas” teóricas.


## Qué se instala

**19 skills → `~/.claude/skills/common/`** (activas en cada sesión de Claude, en cada proyecto)

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

Abre Claude Code **en el directorio que contiene este paquete boost**, y pega estos dos prompts — en orden.

### Paso A — Boost Skills

```
"Lee el README del boost-package y todas las skills de este directorio.
Instálalas e intégralas de forma global en mi setup de Claude Code.
Verifica que cada skill cargue correctamente y confirma cuando termines."
```

Claude hará: leer el README → copiar todas las skills a `~/.claude/skills/common/` → instalar archivos de memoria → crear templates → reportar con un conteo. No hace falta script de shell.

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
cd /path/to/sdd-workshop-boost
./install.sh
```

Esto instala solo las skills del boost — kcp hay que instalarlo aparte desde GitHub.

---

## Después de instalar

Abre tu proyecto en Claude Code. Pregunta:

```
"What SDD skills do I have?"
```

Claude leerá `sdd-context.yaml` y te guiará por la metodología completa.

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
1. Copia `templates/skill-template.yaml` a `.claude/skills/[nombre-de-tu-skill].yaml`
2. Responde: “¿Qué le sigo explicando a Claude sobre mi codebase?”
3. Escríbelo una vez, en la skill. No lo vuelvas a explicar.
4. Prueba: abre una sesión nueva de Claude, pídele que haga la cosa. ¿Siguió tu skill?

**Cuándo crear un navigator:** Cuando tengas 10+ skills de dominio, lee `skill-navigator-pattern.yaml`.

---