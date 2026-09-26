# 🧭 ROAM — Agentic AI Travel Planner

<p align="center">
  <strong>Plan less. Explore more.</strong>
</p>

<p align="center">
  An agentic AI travel planner that understands natural-language travel goals, researches real-world information, reasons over constraints, builds personalized itineraries, and dynamically re-plans when requirements change.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js&logoColor=white)
![AI](https://img.shields.io/badge/AI-Agentic_Planning-FF6F00?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</p>

---

## ✨ Overview

**ROAM** is an agentic AI travel planning system designed to solve a problem that conventional travel chatbots often simplify:

> Travel planning is not just text generation. It is a constraint satisfaction and optimization problem.

A user might say:

> *"Plan a 5-day trip from Delhi for 2 people under ₹50,000, focused on nature and food, with a relaxed itinerary."*

ROAM transforms that natural-language request into structured requirements, researches relevant real-world information, evaluates possible destinations, estimates costs, validates feasibility, and generates a personalized itinerary.

More importantly, ROAM can **adapt when the user changes their mind**.

For example:

> *"Actually, our budget is only ₹35,000. Keep the trip 5 days and don't make it hectic."*

Instead of merely editing the previous response, ROAM re-evaluates the constraints and generates a new feasible plan.

---

# 🎯 Problem

Most AI travel assistants primarily generate plausible-sounding itineraries from model knowledge.

That creates several problems:

- Travel information can become outdated.
- Budgets may not add up.
- Travel times may be unrealistic.
- Activities may conflict with opening hours.
- Recommendations may not match the user's preferences.
- Changing one requirement can invalidate the entire itinerary.
- External web content can contain untrusted instructions.
- A polished response does not necessarily mean a feasible travel plan.

ROAM approaches travel planning as a **grounded, constraint-aware planning problem**.

---

# 💡 Core Idea

ROAM separates a travel request into:

### Hard Constraints

Requirements that should not be violated.

Examples:

- Maximum budget
- Number of travelers
- Trip duration
- Required travel dates
- Accessibility requirements

### Soft Preferences

Things the planner should optimize for.

Examples:

- Nature
- Food
- Adventure
- Culture
- Relaxed pace
- Photography
- Luxury
- Local experiences

This allows the agent to reason about trade-offs instead of blindly generating an itinerary.

---

# 🧠 How ROAM Works

```text
                    USER REQUEST
                         │
                         ▼
              ┌─────────────────────┐
              │ Intent Understanding │
              │ & Constraint Parsing │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Structured Trip     │
              │ Specification       │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Agentic Planner /   │
              │ Orchestrator        │
              └──────────┬──────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        Web/Search     Routes       Weather
            │            │            │
            ▼            ▼            ▼
        Stays/Food    Activities   Transport
            │            │            │
            └────────────┼────────────┘
                         ▼
              ┌─────────────────────┐
              │ Evidence & Grounding│
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Constraint & Budget │
              │ Validation          │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ Itinerary Generator │
              └──────────┬──────────┘
                         │
                         ▼
                  PERSONALIZED PLAN
                         │
                         ▼
                 USER MODIFIES PLAN
                         │
                         └──────────────┐
                                        ▼
                                  RE-PLANNING
