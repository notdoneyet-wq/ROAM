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
```
# 🛡️ Security First

ROAM treats all externally retrieved information as **untrusted data**.

Web pages, reviews, search results, and other external content must never be allowed to override the agent's instructions or the user's requirements.

### Security measures

- Prompt-injection detection
- Structured and validated tool calls
- Input and output validation
- API-key and secret isolation
- Tool timeouts and call limits
- No arbitrary code execution from retrieved content
- Safe handling of malformed or malicious data
- Graceful recovery when external tools are unavailable

### Security Demonstration

ROAM includes a prompt-injection test where malicious external content attempts to instruct the agent to ignore the user's request or reveal sensitive information.

The agent should recognize this content as untrusted and continue following the actual travel requirements.

---

# 📚 Grounded Recommendations

ROAM is designed to distinguish between **verified information, estimates, and unavailable data**.

Important recommendations can be accompanied by supporting sources for:

- Travel routes and travel times
- Accommodation
- Activities
- Restaurants and local food
- Weather
- Pricing estimates

ROAM should never fabricate sources, prices, availability, travel times, or other real-world information.

When live information cannot be verified, the system clearly labels it as an estimate rather than presenting it as fact.

---

# 💰 Intelligent Budget Planning

Budget is treated as a planning constraint rather than simply a number displayed at the end.

ROAM can break estimated trip costs into categories such as:

```text
Transportation
Accommodation
Food
Activities
Local Transport
Emergency / Miscellaneous Buffer
```

The planner continuously checks the estimated total against the user's maximum budget.

If requirements conflict, ROAM explains the trade-off instead of silently violating a constraint.

For example:

```
Requested budget: ₹35,000

Current plan: ₹41,000

Status: OVER BUDGET

ROAM identifies the conflict and searches for
lower-cost alternatives rather than presenting
the ₹41,000 plan as a ₹35,000 trip.
```

🧠 Personalization

ROAM adapts the itinerary according to the user's actual travel preferences.

Supported preferences can include:

Nature
Food
Adventure
Culture
Photography
Nightlife
Luxury
Budget travel
Relaxed travel
Family travel
Solo travel
Local experiences

These preferences influence the actual planning process rather than simply appearing as labels in the interface.

For example, a user asking for a relaxed trip should receive fewer activities and more buffer time, while an adventure-focused request can prioritize activities and experiences with higher activity levels.

🗺️ Travel Experience

ROAM is intentionally designed to feel like a modern digital travel journal, not a generic AI chatbot.

The visual language is inspired by exploration, maps, nature, and local travel.

The interface uses:

Topographic map-inspired visuals
Forest and earth tones
Route lines and location markers
Editorial travel imagery
Day-by-day travel timelines
Visual budget breakdowns
Travel-inspired micro-interactions
Subtle motion and map interactions

The product deliberately avoids the typical:

Purple AI gradients
Generic chatbot aesthetics
Excessive glassmorphism
Neon futuristic effects
ChatGPT-style interface

The goal is to make ROAM feel like a travel product first and an AI product second.

🏗️ Architecture

```
ROAM
│
├── Frontend
│   ├── Trip Builder
│   ├── Trip Brief
│   ├── Itinerary
│   ├── Maps
│   ├── Budget
│   └── Sources
│
├── Agent
│   ├── Intent Understanding
│   ├── Constraint Extraction
│   ├── Planner / Orchestrator
│   ├── Destination Selection
│   ├── Constraint Engine
│   ├── Budget Engine
│   └── Re-planning
│
├── Tools
│   ├── Search
│   ├── Routes
│   ├── Weather
│   ├── Accommodation
│   ├── Food
│   └── Activities
│
├── Security
│   ├── Input Validation
│   ├── Tool Validation
│   ├── Prompt Injection Protection
│   └── Secret Isolation
│
└── Evaluation
    ├── Constraint Tests
    ├── Grounding Tests
    ├── Re-planning Tests
    ├── Security Tests
    └── Tool Failure Tests
```

🔄 Agent Workflow

At a high level, a travel request moves through the following pipeline:

```
Natural Language Request
          ↓
Intent Understanding
          ↓
Constraint Extraction
          ↓
Trip Specification
          ↓
Destination Research
          ↓
Tool Calls
          ↓
Evidence Collection
          ↓
Candidate Comparison
          ↓
Budget & Feasibility Validation
          ↓
Itinerary Generation
          ↓
Final Validation
          ↓
Personalized Travel Plan
          ↓
User Feedback / Requirement Change
          ↓
Dynamic Re-planning

```

🧪 Evaluation & Reliability

ROAM includes an evaluation layer designed to measure actual agent behavior rather than relying solely on subjective inspection.


🤝 Contributing

Contributions, ideas, and improvements are welcome.

1.Fork the repository.
2.Create a feature branch.
```
git checkout -b feature/your-feature
```
3.Make your changes.
4.Add or update tests where appropriate.
5.Commit your changes.
```
git commit -m "feat: add destination comparison"
```
6.Push the branch.
```
git push origin feature/your-feature
```
Open a Pull Request.

Please keep contributions focused on meaningful improvements to reliability, usability, security, agent behavior, or travel-planning functionality.

👨‍💻 Author

Sagar

Built as an exploration of agentic AI, constraint-aware planning, tool use, grounding, secure AI systems, and adaptive travel experiences.

<p align="center">
🧭 ROAM

Plan less. Explore more.

</p> 
