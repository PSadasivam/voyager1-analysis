# Deep Space Research Platform — System Design & Technical Architecture

*Vision to Execution*

**Author:** Prabhu Sadasivam  
**Classification:** Public  

## Table of Contents

1. [Vision & Strategic Intent](#1-vision--strategic-intent)
2. [Platform Overview](#2-platform-overview)
3. [System Context & Integration Landscape](#3-system-context--integration-landscape)
4. [Architecture Principles](#4-architecture-principles)
5. [Technology Stack & Decision Rationale](#5-technology-stack--decision-rationale)
6. [Infrastructure Architecture](#6-infrastructure-architecture)
7. [Application Architecture](#7-application-architecture)
8. [Data Architecture](#8-data-architecture)
9. [API Design & Contract](#9-api-design--contract)
10. [Cross-Project Integration Strategy](#10-cross-project-integration-strategy)
11. [Resilience & Graceful Degradation](#11-resilience--graceful-degradation)
12. [Security Architecture](#12-security-architecture)
13. [Scalability & Growth Strategy](#13-scalability--growth-strategy)
14. [Operational Excellence](#14-operational-excellence)
15. [Risks, Constraints & Trade-Offs](#15-risks-constraints--trade-offs)
16. [Roadmap & Evolution Path](#16-roadmap--evolution-path)
17. [Appendix — Reference](#17-appendix--reference)

## 1. Vision & Strategic Intent

### 1.1 Mission

Build a unified, publicly accessible platform for deep-space scientific research that consolidates real-time telemetry from NASA missions, interstellar object observations, and theoretical cosmology simulations into an integrated analytical and visualization system — while maintaining near-zero operational cost and production-grade reliability.

### 1.2 Strategic Objectives

| Objective | Outcome |
|-----------|---------|
| **Scientific accessibility** | Make NASA mission data explorable by anyone through a web interface — no specialized tools required |
| **Cross-domain correlation** | Enable analytical connections across Voyager 1 telemetry, interstellar object tracking, space weather, and black hole cosmology |
| **Reproducible research** | Persist every data ingestion with provenance tracking so past analyses can be reproduced even after upstream APIs change |
| **Operational simplicity** | Run the entire platform on a single EC2 instance with automated recovery — no Kubernetes, no managed services, no vendor lock-in beyond commodity compute |
| **Architectural extensibility** | Design every component — schema, API, templates, ingestion — for additive extension without modifying existing contracts |

### 1.3 Why This Architecture

The deep-space research domain has a distinctive constraint profile:

- **Data is authoritative but unreliable in delivery.** NASA APIs return high-quality scientific data but can be intermittent, rate-limited, or structurally changed without notice.
- **Computation is bursty, not sustained.** Trajectory calculations and plot rendering spike on page load, then idle.
- **Users are readers, not writers.** The web interface is read-only; data ingestion is operator-initiated.
- **Budget is minimal.** A research platform should cost less than a coffee subscription to run.

These constraints drove every major architectural decision: server-side rendering over SPA frameworks, SQLite over managed databases, synthetic fallback over hard failures, and a single-instance deployment over distributed systems.

## 2. Platform Overview

The Deep Space Research Platform comprises five interconnected projects published under a single domain:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     prabhusadasivam.com                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  Deep Space Portal                                │   │
│  │   Flask web app · 12 HTML templates · 7 API endpoints            │   │
│  │   Nginx reverse proxy · Gunicorn WSGI · AWS deployment           │   │
│  └─────────┬────────────────────┬───────────────────────┬───────────┘   │
│            │                    │                       │               │
│  ┌─────────┴───────────┐ ┌─────┴───────────────┐ ┌────┴────────────┐   │
│  │   Voyager 1 Suite   │ │  3I/ATLAS Research   │ │  Black Hole     │   │
│  │   4 analysis modules│ │  Jupyter pipeline    │ │  Simulation     │   │
│  │   Trajectory, PWS,  │ │  Ephemerides + MAST  │ │  Bouncing       │   │
│  │   Density, Magneto  │ │  Orbital elements    │ │  cosmology      │   │
│  └─────────┬───────────┘ └──────────┬───────────┘ └───────┬────────┘   │
│            │                         │                       │           │
│            └─────────────┬───────────┘───────────────────────┘           │
│                          ▼                                               │
│              ┌───────────────────────┐                                   │
│              │    Unified Analytics  │                                   │
│              │    Database           │                                   │
│              │    (deep_space_db)    │                                   │
│              └───────────────────────┘                                   │
└──────────────────────────────────────────────────────────────────────────┘
```

| Project | Repository | Purpose |
|---------|-----------|---------|
| **Deep Space Portal** | `PSadasivam/deep-space-portal` | Flask web application, HTML templates, nginx config, deployment infrastructure — presentation layer for all research projects |
| **Voyager 1 Analysis** | `PSadasivam/voyager1-analysis` | Scientific analysis modules: trajectory, plasma waves, electron density, magnetometer — pure computation, no web dependencies |
| **3I/ATLAS Research** | `PSadasivam/3I-ATLAS-research` | Jupyter pipeline for interstellar comet C/2025 N1 (ATLAS): ephemerides, MAST archive queries, orbital elements |
| **Black Hole Simulation** | `PSadasivam/universe-inside-blackhole` | Bouncing cosmology: Schwarzschild radius of total universe mass using Planck 2018 parameters |
| **Unified Analytics DB** | `PSadasivam/deep-space-db` | SQLite database consolidating all research data with S3 backup and audit logging |

## 3. System Context & Integration Landscape

### 3.1 External System Dependencies

```
                              ┌─────────────────────┐
                              │    prabhusadasivam   │
                              │        .com          │
                              └──────────┬───────────┘
                                         │
         ┌──────────┬──────────┬─────────┼─────────┬───────────┬──────────┐
         ▼          ▼          ▼         ▼         ▼           ▼          ▼
    ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌───────┐ ┌────────┐ ┌──────┐
    │   JPL   │ │  NASA  │ │  NASA  │ │ NASA │ │ NASA  │ │  NOAA  │ │ MAST │
    │HORIZONS │ │  SPDF  │ │  PDS   │ │ NeoWs│ │ DONKI │ │  SWPC  │ │(STScI│
    │         │ │        │ │  PPI   │ │      │ │       │ │        │ │)     │
    └─────────┘ └────────┘ └────────┘ └──────┘ └───────┘ └────────┘ └──────┘
    Trajectory   Magneto-   Plasma     Near-    Solar     Kp Index   HST/JWST
    Ephemerides  meter CDF  Wave CDF   Earth    Flares    Forecast   Archive
                                       Objects  CMEs/GST
```

| Upstream System | Protocol | Auth | Failure Mode | Fallback Strategy |
|----------------|----------|------|-------------|-------------------|
| JPL HORIZONS | `astroquery` (HTTP) | None | Timeout / 5xx | Synthetic trajectory model |
| NASA SPDF | HTTPS file download | None | 404 / timeout | Synthetic magnetometer data |
| NASA PDS PPI | HTTPS file download | None | 404 / timeout | Synthetic plasma wave generator |
| NASA NeoWs | REST JSON | API key (env var) | Rate limit / 5xx | 15-min stale cache |
| NASA DONKI | REST JSON | API key (env var) | Rate limit / 5xx | 15-min stale cache |
| NOAA SWPC | REST JSON | None | Timeout | 15-min stale cache |
| MAST (STScI) | `astroquery` (HTTP) | None | Timeout | Cached CSVs |
| MPC | Static files | None | N/A | Local JSON/obs files |

**Key design decision:** Every external dependency has an explicit fallback path. The platform never returns an error page due to upstream API failure.

### 3.2 Downstream Consumers

| Consumer | Interface | Usage |
|----------|-----------|-------|
| Web browsers | HTTPS (HTML + embedded base64 images) | Primary end-user interface |
| Search engines | `/sitemap.xml`, `/robots.txt`, SEO meta tags | Discovery and indexing |
| LLM/AI crawlers | `/ai-index` structured knowledge page | Machine-readable research index |
| SQLite clients | File-based `.db` access | Ad-hoc research queries |
| Jupyter notebooks | `pandas.read_sql()` via `sqlite3` | Analytical workflows |

---

## 4. Architecture Principles

These principles govern all design decisions across the platform:

| # | Principle | Rationale | Application |
|---|-----------|-----------|-------------|
| 1 | **Graceful degradation over hard failure** | NASA APIs are unreliable; pages must always render | Synthetic fallback generators for every data source |
| 2 | **Server-side rendering over client-side frameworks** | Eliminates JavaScript build toolchain, reduces attack surface, ensures SEO | Flask + Jinja2 templates with base64-embedded plots |
| 3 | **Zero third-party runtime dependencies where possible** | Minimizes supply chain risk and dependency management | `deep_space_db` uses Python stdlib only; web app pins exact versions |
| 4 | **Additive extension, not modification** | New research projects should not require changes to existing code | New tables, new ingestion functions, new Flask routes — each additive |
| 5 | **Data provenance on every record** | Research integrity requires knowing where data came from | `source` column on every row; `ingestion_log` table |
| 6 | **Cost proportional to value** | Research infrastructure should not cost more than the research itself | SQLite (free), single EC2 (~$15/mo), S3 (< $0.01/mo) |
| 7 | **Operational simplicity over architectural elegance** | One person operates the entire platform | Single process, single instance, systemd restart, git-pull deploys |

## 5. Technology Stack & Decision Rationale

### 5.1 Stack Overview

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.11+ (EC2), 3.13 (local) |
| Web framework | Flask | Latest stable |
| WSGI server | Gunicorn | 2 workers |
| Reverse proxy | Nginx | Amazon Linux default |
| TLS | Let's Encrypt / Certbot | Auto-renewing |
| Compute | AWS EC2 t3.small | 2 vCPU, 2 GB RAM |
| Static IP | AWS Elastic IP | Associated to EC2 |
| DNS | GoDaddy | A + CNAME records |
| Database | SQLite 3 (WAL) | Bundled with Python |
| Backup storage | AWS S3 | Versioned, private |
| Process management | systemd | `Restart=always` |
| Scientific computing | NumPy, SciPy, Matplotlib, Astropy, Astroquery | Pinned in requirements.txt |

### 5.2 Key Technology Decisions

**Why Flask over Django/FastAPI:**  
Django's ORM, admin panel, and auth middleware are unnecessary for a read-only research site. FastAPI's async model adds complexity with no benefit when every request is a synchronous NASA API call followed by matplotlib rendering. Flask provides the minimal surface needed: routing, Jinja2 templates, and request handling.

**Why server-side matplotlib over D3.js/Plotly:**  
Scientific plots require precise control over axes, annotations, colormaps, and dual-axis layouts that matplotlib provides natively. Embedding plots as base64 PNGs in JSON responses eliminates JavaScript rendering, client-side library loading, and cross-browser compatibility issues. The trade-off (no client-side interactivity) is acceptable for a research presentation platform.

**Why SQLite over PostgreSQL/DynamoDB:**  
The workload is single-writer, read-heavy, and local. SQLite requires no server process, no connection pooling, no credential management, and no monthly cost. WAL mode enables concurrent reads during ingestion. The 281 TB theoretical limit far exceeds projected needs. If multi-user access becomes necessary, the schema is standard SQL and can migrate to PostgreSQL without DDL changes.

**Why AWS CLI over boto3 for S3:**  
The backup script needs exactly three operations: upload, list, download. The AWS CLI handles these with subprocess calls, avoiding a boto3 dependency, its transitive dependency tree, and the associated supply chain surface. For a script that runs once per day, the subprocess overhead is negligible.

**Why Gunicorn with 2 workers:**  
Each worker handles one request at a time. Matplotlib is not thread-safe, so `preload_app=True` with sync workers is the correct model. Two workers provide basic concurrency (one can render a plot while the other serves a cached page) without exceeding the 2 GB RAM of a t3.small.

## 6. Infrastructure Architecture

### 6.1 Deployment Topology

```
                              Internet
                                 │
                            ┌────┴────┐
                            │ GoDaddy │
                            │   DNS   │  A: prabhusadasivam.com → Elastic IP
                            └────┬────┘  CNAME: www → prabhusadasivam.com
                                 │
                    ┌────────────┴────────────┐
                    │    AWS EC2 t3.small     │
                    │    Amazon Linux 2023    │
                    │    Elastic IP attached  │
                    │                         │
                    │  ┌────────────────────┐ │
                    │  │      Nginx         │ │
                    │  │  :80 → 301 HTTPS   │ │
                    │  │  :443 → TLS term   │ │
                    │  │  proxy_pass :8000  │ │
                    │  │  security headers  │ │
                    │  │  dotfile deny      │ │
                    │  └─────────┬──────────┘ │
                    │            │            │
                    │  ┌─────────┴──────────┐ │
                    │  │    Gunicorn        │ │
                    │  │  127.0.0.1:8000    │ │
                    │  │  2 sync workers    │ │
                    │  │  systemd managed   │ │
                    │  └─────────┬──────────┘ │
                    │            │            │
                    │  ┌─────────┴──────────┐ │
                    │  │  Flask Application │ │
                    │  │  (deep_space_portal)│ │
                    │  │  12 page routes    │ │
                    │  │  7 API endpoints   │ │
                    │  │  2 utility routes  │ │
                    │  └────────────────────┘ │
                    │                         │
                    └──────────┬──────────────┘
                               │
                    ┌──────────┴───────────────┐
                    │        AWS S3            │
                    │  db-backups/ (versioned) │
                    └──────────────────────────┘
```

### 6.2 Network Security

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | SSH | Operator IP only | Deployment and maintenance |
| 80 | HTTP | 0.0.0.0/0 | Redirect to HTTPS |
| 443 | HTTPS | 0.0.0.0/0 | Application traffic |
| 8000 | HTTP | 127.0.0.1 only | Gunicorn (not internet-exposed) |

### 6.3 Nginx Hardening

```
# Security headers on every response
X-Frame-Options:           DENY
X-Content-Type-Options:    nosniff
Referrer-Policy:           strict-origin-when-cross-origin

# Deny access to dotfiles (.git, .env, etc.)
location ~ /\. { deny all; }

# Proxy configuration — loopback only
proxy_pass http://127.0.0.1:8000;
```

### 6.4 Process Lifecycle

```
                    Boot
                      │
                      ▼
              systemd starts
         deep_space_portal.service
                      │
                      ▼
              Gunicorn spawns
              2 Flask workers
                      │
              ┌───────┴───────┐
              │               │
           Worker 1        Worker 2
              │               │
              ▼               ▼
         Serve requests  Serve requests
              │
              │ ← Process crash
              ▼
        systemd detects
        exit code ≠ 0
              │
              ▼
        Restart=always
        RestartSec=3
              │
              ▼
        Gunicorn respawns
```

## 7. Application Architecture

### 7.1 Request Flow

```
Browser GET /trajectory
         │
         ▼
     Nginx (TLS termination, security headers)
         │
         ▼
     Gunicorn → Flask route handler
         │
         ├── render_template("trajectory.html")
         │       ├── nav_caret=True (dropdown nav config)
         │       ├── page-specific meta tags (SEO)
         │       └── Template extends base layout
         │
         └── Template includes <script> that calls /api/trajectory
                    │
                    ▼
              Flask API handler
                    │
                    ├── Try: JPL HORIZONS query (real data)
                    │         │
                    │         ├── Success → matplotlib plot → base64 PNG
                    │         └── Failure ──┐
                    │                       │
                    ├── Fallback: synthetic trajectory model
                    │         │
                    │         └── matplotlib plot → base64 PNG
                    │
                    └── Return JSON:
                          {
                            "plot": "data:image/png;base64,...",
                            "events": [...],
                            "galactic_coords": {...},
                            "data_source": "jpl_horizons" | "synthetic"
                          }
```

### 7.2 Rendering Strategy

All visualization follows a consistent **server-side rendering pipeline**:

1. **Data acquisition** — Call external API or generate synthetic data
2. **Scientific computation** — NumPy/SciPy processing (filtering, FFT, ridge detection)
3. **Plot generation** — Matplotlib with `Agg` backend (no display server required)
4. **Encoding** — `io.BytesIO` → base64 string
5. **Transport** — JSON response with embedded base64 PNG
6. **Display** — Jinja2 template sets `<img src="{{ plot }}">` or JavaScript `img.src = data.plot`

This approach guarantees:
- **Identical rendering** across all browsers and devices
- **No client-side JavaScript libraries** for charting
- **SEO-friendly** — content is in the initial HTML response
- **Cacheable** — API responses can be cached at any layer

### 7.3 Caching Architecture

| Layer | Strategy | TTL | Scope |
|-------|----------|-----|-------|
| Space Intelligence APIs | In-memory Python dict | 15 minutes | Per-worker process |
| Stale cache fallback | Return last successful response on API failure | Until next success | Per-worker process |
| Browser | Standard HTTP caching headers via Nginx | Nginx defaults | Per-client |

**Design decision:** No external cache (Redis, Memcached) is used. The in-memory approach is sufficient for single-instance deployment and eliminates an infrastructure dependency. If scaling to multiple instances, a shared cache layer would be introduced.

### 7.4 Template Architecture

All 11 HTML templates share:
- Dark mission-control theme (`#0c0c0c → #1a1a2e → #16213e`)
- 3D glassmorphic navigation bar with split-button dropdowns
- SEO meta tags (title, description, Open Graph, Twitter Cards)
- Consistent `<header>` → `<main>` → journey navigation → `<footer>` structure

Pages are connected through a **sequential journey navigation**:

```
Facts → Trajectory → Plasma Waves → Density → Magnetometer → 3I/ATLAS
```

Each page includes "Previous" / "Next" links, creating a guided research narrative through the data.

## 8. Data Architecture

### 8.1 Data Domains

The platform processes data across five analytical domains:

| Domain | Data Nature | Volume Characteristic | Primary Source |
|--------|------------|----------------------|---------------|
| **Voyager 1 Telemetry** | Time-series instrument readings | Sparse (daily/hourly resolution from 164 AU) | NASA SPDF, PDS, JPL HORIZONS |
| **3I/ATLAS Tracking** | Positional ephemerides + archival observations | Batch (periodic notebook runs) | JPL HORIZONS, MAST, MPC |
| **Black Hole Simulation** | Physical constants + derived quantities | Static (recomputed on demand) | Planck 2018 parameters |
| **Space Intelligence** | NEO approaches + solar activity | Streaming-like (15-min refresh) | NASA NeoWs, DONKI, NOAA SWPC |
| **Research Insights** | Cross-project findings and hypotheses | Append-only (human-authored) | Manual entry |

### 8.2 Unified Database Schema

The analytics database consolidates all domains into 15 tables with consistent design patterns:

```
┌──────────────────────────────────────────────────────────────────┐
│                     deep_space_research.db                       │
│                                                                  │
│  VOYAGER 1 (5 tables)          3I/ATLAS (4 tables)               │
│  ┌────────────────────┐        ┌────────────────────┐            │
│  │ magnetic_field     │        │ ephemerides        │            │
│  │ plasma_wave        │        │ mast_observations  │            │
│  │ electron_density   │        │ orbital_elements   │            │
│  │ trajectory         │        │ datasets           │            │
│  │ events             │        └────────────────────┘            │
│  └────────────────────┘                                          │
│                                                                  │
│  BLACK HOLE (1 table)          SPACE INTEL (2 tables)            │
│  ┌────────────────────┐        ┌────────────────────┐            │
│  │ simulations        │        │ neos               │            │
│  └────────────────────┘        │ solar              │            │
│                                └────────────────────┘            │
│                                                                  │
│  METADATA (3 tables)                                             │
│  ┌────────────────────┐                                          │
│  │ research_insights  │  ← cross-project analytical findings     │
│  │ ingestion_log      │  ← every data load audited               │
│  │ s3_backup_log      │  ← every backup audited                  │
│  └────────────────────┘                                          │
└──────────────────────────────────────────────────────────────────┘
```

### 8.3 Schema Design Invariants

Every data table enforces these invariants:

| Invariant | Implementation | Purpose |
|-----------|----------------|---------|
| **Temporal key** | `timestamp_utc TEXT NOT NULL` (ISO 8601) | Range queries via string comparison |
| **Provenance** | `source TEXT DEFAULT '<origin>'` | Distinguish real vs. synthetic vs. derived data |
| **Audit timestamp** | `ingested_at TEXT DEFAULT (datetime('now'))` | Track when data entered the system, independent of observation time |
| **Indexed access** | B-tree index on primary timestamp column | Sub-millisecond range scans on time-series data |
| **Parameterized writes** | All SQL uses `?` placeholders | Prevent injection regardless of data content |

### 8.4 Data Lineage

```
NASA SPDF → voyager1_magneticfield_nTS_analysis.py → /api/magnetometer → JSON
                                                   ↘
                                                    → init_db.py → voyager1_magnetic_field table
                                                                              ↓
                                                                   s3_backup.py → S3

JPL HORIZONS → astroquery → /api/trajectory → JSON
             → astroquery → 3I_ATLAS_research_notebook.ipynb → ephemerides.csv
                                                              → init_db.py → atlas_3i_ephemerides table
```

Every data point can be traced from its NASA/JPL origin through the ingestion pipeline to the database row, identified by the `source` column.

## 9. API Design & Contract

### 9.1 API Inventory

| Endpoint | Method | Parameters | Response Shape |
|----------|--------|-----------|---------------|
| `/api/trajectory` | GET | — | `{ plot, events[], galactic_coords, data_source }` |
| `/api/position` | GET | — | `{ plot, distance_au, coordinates, data_source }` |
| `/api/magnetometer` | GET | `?days=` | `{ plot, statistics{}, data_source }` |
| `/api/plasma` | GET | `?hours=&freq_min=&freq_max=` | `{ spectrogram, spectrum, time_series, statistics }` |
| `/api/density` | GET | `?hours=` | `{ process_plot, nasa_plot, statistics }` |
| `/api/space-intelligence` | GET | — | `{ neos[], flares[], cmes[], storms[], kp_index, forecast[], highlights[] }` |
| `/api/status` | GET | — | `{ status, cdflib, data_sources{} }` |

### 9.2 Response Contract

All plot-bearing endpoints follow a consistent contract:

```json
{
  "plot": "data:image/png;base64,...",     // Always present
  "data_source": "jpl_horizons|synthetic", // Always present — transparency
  "statistics": { ... },                    // Domain-specific metrics
  "events": [ ... ]                         // Optional: notable data points
}
```

The `data_source` field is critical to architectural integrity: it tells the consumer whether they are viewing real NASA data or a synthetic approximation. This transparency extends the **provenance principle** from the database layer to the API layer.

### 9.3 Error Handling Contract

API endpoints never return HTTP 5xx. The degradation hierarchy is:

1. **Real data** (preferred) — external API succeeded
2. **Cached data** — external API failed, in-memory cache is fresh (< 15 min)
3. **Stale cache** — external API failed, cache is stale but usable
4. **Synthetic data** — no cache available; generate mathematically plausible data
5. **Empty response with explanation** — only if generation itself fails (extremely rare)

---

## 10. Cross-Project Integration Strategy

### 10.1 Integration Architecture

The five projects are loosely coupled through four integration mechanisms:

```
┌──────────────┐    File System     ┌──────────────┐
│  3I/ATLAS    │ ──── CSVs/JSONs ──►│  deep_space  │
│  Research    │                     │      _db    │
└──────┬───────┘                     └─────────────┘
       │                                    ▲
       │ PNGs to Images/                    │ CSVs/JSONs
       ▼                                    │
┌──────────────┐                     ┌──────┴───────┐
│  Voyager 1   │ ◄── imports ───────│  Deep Space   │
│  (science)   │                     │  Portal       │
└──────────────┘                     └──────────────┘
       │                                    │
       │                                    │ Serves all pages under one domain
       ▼                                    ▼
  Analysis outputs              prabhusadasivam.com
```

| Mechanism | Pattern | Example |
|-----------|---------|---------|
| **File-system sharing** | Sibling directories under `C:\Deep-Space-Research\` | `init_db.py` reads `../3I-Atlas-Research/ephemerides.csv` |
| **Python path import** | Portal adds `../voyager1_project` to `sys.path` | `from voyager1_magneticfield_nTS_analysis import fetch_ephemeris` |
| **Presentation integration** | Portal Flask renders templates for all projects | `/atlas`, `/blackhole`, `/mars` pages in portal app |
| **Analytical integration** | `research_insights` table links findings across domains | "Voyager 1 measures the interstellar medium that 3I/ATLAS traveled through" |

### 10.2 Integration Design Rationale

Projects are deliberately **not microservices**. A monolithic Flask application (the portal) serves all pages because:

- There is one operator, one deployment target, one domain
- Cross-project pages share navigation, styling, and SEO configuration
- The complexity cost of inter-service communication exceeds the benefit at this scale
- Adding a new research project is a single Flask route + template — no new infrastructure

The key architectural improvement is that **science modules are now decoupled from presentation**. Voyager 1 analysis scripts can be used as CLI tools, imported into Jupyter notebooks, or called by the portal — without carrying Flask/Gunicorn dependencies.

This will be revisited if the platform requires multi-team development or independent scaling (see §17).

## 11. Resilience & Graceful Degradation

### 11.1 Failure Mode Analysis

| Failure | Detection | Recovery | User Impact |
|---------|-----------|----------|-------------|
| **NASA API timeout** | `requests.Timeout` / `astroquery` exception | Synthetic data generator | Page renders with approximated data; `data_source: synthetic` |
| **NASA API rate limit** | HTTP 429 | 15-min in-memory cache serves stale data | Transparent — data is at most 15 min old |
| **Flask worker crash** | systemd detects exit code ≠ 0 | `Restart=always`, `RestartSec=3` | < 3 seconds of unavailability |
| **EC2 instance reboot** | systemd `WantedBy=multi-user.target` | Auto-start on boot | Minutes of unavailability |
| **Database corruption** | `PRAGMA integrity_check` failure | `python s3_backup.py restore` | Database queries fail until restored (web app is unaffected — it doesn't read the DB) |
| **S3 backup deletion** | Missing object on `aws s3 ls` | S3 versioning recovers previous version | No user impact |
| **Let's Encrypt renewal failure** | Certbot logs / browser TLS error | Manual `certbot renew` | HTTPS certificate warning |
| **Disk full** | Write failure | WAL checkpoint + cleanup | Ingestion/backup fails; web app continues serving |

### 11.2 Synthetic Data Architecture

The synthetic data generators are not test mocks — they are mathematically grounded models:

| Generator | Model | Accuracy |
|-----------|-------|----------|
| Trajectory | Voyager 1 velocity (17 km/s) extrapolated from last known position | < 1% distance error verified against JPL HORIZONS |
| Magnetometer | Gaussian noise around 0.1 nT baseline (interstellar medium conditions) | Physically plausible range |
| Plasma wave | Multi-frequency synthetic spectrogram with realistic power-law spectrum | Structurally accurate; not observation data |
| Electron density | Derived from synthetic plasma frequency via $n_e = (\varepsilon_0 m_e / e^2)(2\pi f_{pe})^2$ | Formula-exact; input is synthetic |

### 11.3 Resilience Principle

> **The platform renders every page, every time.** No combination of external failures produces a user-facing error. The quality of data may degrade (real → cached → synthetic), but the experience never breaks.

## 12. Security Architecture

### 12.1 Defense in Depth

```
Layer 1: Network
├── Security group: SSH restricted to operator IP
├── HTTP/HTTPS open (required for public website)
└── Gunicorn bound to 127.0.0.1 only

Layer 2: TLS
├── Let's Encrypt certificate (auto-renewal)
├── HTTP → HTTPS redirect (Nginx)
└── HSTS implied by redirect

Layer 3: Nginx
├── X-Frame-Options: DENY
├── X-Content-Type-Options: nosniff
├── Referrer-Policy: strict-origin-when-cross-origin
├── Dotfile access denied (blocks .git, .env)
└── /api/ disallowed in robots.txt

Layer 4: Application
├── Flask debug mode off by default (env-var gated)
├── SECRET_KEY via environment variable (secure random fallback)
├── flask-limiter: 10 req/min on all /api/* endpoints
├── Path traversal blocked: rejects '..' in image filenames
├── SRI integrity hashes on all CDN resources (KaTeX)
├── No user input to SQL queries (read-only web interface)
├── Parameterized SQL in all ingestion scripts
└── NASA API key via environment variable

Layer 5: Data
├── SQLite WAL mode (crash consistency)
├── Source provenance on every row
├── .gitignore excludes .db files and .env
└── No PII in any data table

Layer 6: Cloud
├── S3 bucket: all public access blocked
├── S3 versioning: protects against deletion
├── S3 SSE-S3: encryption at rest
├── IAM: scoped credentials recommended
└── AWS CLI: HTTPS enforced for all S3 operations
```

### 12.2 Secrets Inventory

| Secret | Location | In Source Control? |
|--------|----------|:-----------------:|
| AWS Access Key / Secret Key | `~/.aws/credentials` | No |
| Flask SECRET_KEY | Environment variable on EC2 | No |
| NASA API Key | `NASA_API_KEY` env var | No |
| SSH private key | `~/voyager1-deploy.pem` (local) | No |
| S3 bucket name | `S3_BACKUP_BUCKET` env var | No |

**No secrets exist in any committed file** across all four repositories.

### 12.3 STRIDE Threat Model

A complete STRIDE analysis is documented in [docs/security-threat-model.md](security-threat-model.md), covering:
- 14 identified threats across Spoofing, Tampering, Repudiation, Information Disclosure, DoS, and Elevation of Privilege
- Trust boundary diagram with 5 boundaries
- Asset inventory with CIA ratings
- Attack surface assessment
- Incident response playbooks

---

## 13. Scalability & Growth Strategy

### 13.1 Current Capacity

| Dimension | Current | Comfortable Ceiling |
|-----------|---------|-------------------|
| Concurrent users | ~5–10 (2 Gunicorn workers) | ~50 with 4 workers |
| Database rows | 86 | 10 million+ (SQLite with indexes) |
| Database size | 116 KB | 1 GB+ |
| S3 backup cost | < $0.01/mo | < $1/mo at 10 GB |
| Page load time | 2–5 sec (API-dependent) | Cacheable to < 1 sec |

### 13.2 Scaling Triggers & Responses

| Trigger | Threshold | Response |
|---------|-----------|----------|
| Concurrent users > 50 | Gunicorn worker saturation | Increase workers (up to CPU count); add response caching |
| Concurrent users > 200 | EC2 t3.small limit | Upgrade instance type; add CloudFront CDN for static assets |
| Concurrent users > 1000 | Single-instance limit | Add ALB + multiple EC2 instances; externalize cache to ElastiCache |
| Database > 1 GB | SQLite performance risk | Evaluate DuckDB (analytical) or PostgreSQL RDS (multi-user) |
| Multiple contributors | Concurrent write contention | Migrate to PostgreSQL; add application-level auth |
| Multiple research projects > 6 | Template/route sprawl | Extract shared framework; consider project-specific Flask Blueprints |

### 13.3 What Will NOT Change

These are architectural invariants that hold regardless of scale:

- **Server-side plot rendering** — matplotlib's scientific fidelity is not replaceable by JavaScript charting
- **Data provenance on every row** — `source` and `ingested_at` columns are non-negotiable
- **Graceful degradation** — synthetic fallback remains the failure strategy
- **Standard SQL** — no ORM, no SQLite-specific syntax, migration-ready at all times

## 14. Operational Excellence

### 14.1 Deployment Model

| Aspect | Current State | Target State |
|--------|--------------|-------------|
| Deployment method | `git pull` + `systemctl restart` via SSH | GitHub Actions → EC2 deploy |
| Rollback | `git revert` + `systemctl restart` | Automated rollback on health check failure |
| Health check | Manual `curl` / browser | `/api/status` endpoint (exists); automated monitoring pending |
| Log access | `journalctl -u voyager1` on EC2 | CloudWatch Logs agent |
| Uptime monitoring | Manual | External ping service (UptimeRobot / AWS Route 53 health check) |

### 14.2 Database Operations

| Operation | Command | Frequency |
|-----------|---------|-----------|
| Full init | `python init_db.py` | On schema change |
| Re-ingest | `python init_db.py --ingest-only` | When source data updates |
| Schema update | `python init_db.py --schema-only` | On table additions |
| Backup | `python s3_backup.py backup` | After each ingestion (manual; daily cron recommended) |
| Restore | `python s3_backup.py restore` | On corruption or data loss |
| Audit query | `SELECT * FROM ingestion_log ORDER BY ingested_at DESC` | Ad-hoc |

### 14.3 Observability

| Signal | Current | Gap |
|--------|---------|-----|
| Application logs | stdout → journalctl | No centralized log aggregation |
| Error tracking | Log inspection | No alerting on exceptions |
| API latency | Not measured | Add request timing middleware |
| Uptime | Not monitored | Add external health check |
| Data freshness | `ingested_at` column queryable | No automated staleness alerts |

## 15. Risks, Constraints & Trade-Offs

### 15.1 Architectural Trade-Offs

| Decision | What We Gain | What We Accept |
|----------|-------------|---------------|
| Server-side rendering | SEO, simplicity, no JS build chain | No client-side interactivity on plots |
| Single EC2 instance | Simplicity, low cost | Single point of failure for compute |
| SQLite over PostgreSQL | Zero cost, zero ops, portable | Single writer, no concurrent access |
| Monolithic Flask app | One deploy, shared navigation | All projects coupled in one process |
| Synthetic fallback | Pages always render | Users may see approximated data |
| Manual deployment | No CI/CD infrastructure to maintain | Human error risk; slower deploy cycle |
| 2 Gunicorn workers | Fits t3.small memory | Limited concurrent request handling |

### 15.2 Technical Debt Register

| Item | Severity | Effort | Impact if Unaddressed |
|------|:--------:|:------:|----------------------|
| No CI/CD pipeline | Medium | Medium | Manual deploys remain error-prone |
| No automated testing for Flask routes | Medium | Medium | Regressions detected only in production |
| No uptime monitoring | Medium | Low | Outages detected by manual observation |
| No centralized logging | Low | Medium | Debugging requires SSH to EC2 |
| Root AWS credentials in use | **High** | Low | Over-privileged access; security risk |
| No database encryption at rest | Low | Low | Acceptable — no PII or classified data |

### 15.3 Constraints

| Constraint | Source | Impact |
|-----------|--------|--------|
| NASA API rate limits | External policy | Drives caching strategy (15-min TTL) |
| Matplotlib not thread-safe | Library limitation | Mandates sync Gunicorn workers |
| SQLite single-writer | Engine limitation | Prevents concurrent ingestion processes |
| EC2 t3.small 2 GB RAM | Instance type | Limits Gunicorn workers and in-memory data |
| No PII in scope | Data classification | Simplifies security requirements significantly |

## 16. Roadmap & Evolution Path

### Phase 1 — Foundation (Complete)

- [x] Flask web application with 11 pages and 7 API endpoints
- [x] Real-time NASA/JPL data integration with synthetic fallback
- [x] 3I/ATLAS Jupyter research pipeline
- [x] Black hole bouncing cosmology simulation
- [x] Unified SQLite analytics database (15 tables)
- [x] S3 backup with versioning and audit logging
- [x] EC2 deployment with Nginx, Gunicorn, HTTPS, systemd
- [x] Security threat model and architecture documentation

### Phase 2 — Operational Maturity

- [ ] Automated backup schedule (cron/Task Scheduler)
- [ ] CI/CD pipeline (GitHub Actions → EC2)
- [ ] Uptime monitoring (Route 53 health check or UptimeRobot)
- [ ] Replace root AWS credentials with scoped IAM user
- [ ] Flask route integration tests

### Phase 3 — Data Pipeline Automation

- [ ] Scheduled ingestion from Flask `/api/*` endpoints into database
- [ ] Space intelligence data persistence (NEOs, solar events)
- [ ] Staleness detection and alerting on aged data
- [ ] Data quality dashboards in Jupyter

### Phase 4 — Analytics & Insights

- [ ] Parquet export for S3/Athena serverless queries
- [ ] Cross-project anomaly detection (magnetic field × solar activity)
- [ ] Research insight timeline visualization
- [ ] Streamlit or Jupyter dashboard for interactive analysis

### Phase 5 — Scale (If Warranted)

- [ ] CloudFront CDN for static assets and plot caching
- [ ] PostgreSQL migration for multi-user access
- [ ] Flask Blueprints for project-specific modules
- [ ] Multi-AZ deployment for high availability

## 17. Appendix — Reference

### A. Repository Map

| Repository | URL | Branch |
|-----------|-----|--------|
| Deep Space Portal | `github.com/PSadasivam/deep-space-portal` | `main` |
| Voyager 1 Analysis | `github.com/PSadasivam/voyager1-analysis` | `main` |
| 3I/ATLAS Research | `github.com/PSadasivam/3I-ATLAS-research` | `main` |
| Black Hole Simulation | `github.com/PSadasivam/universe-inside-blackhole` | `main` |
| Unified Analytics DB | `github.com/PSadasivam/deep-space-db` | `main` |

### B. External API Reference

| API | Endpoint | Data | Auth |
|-----|----------|------|------|
| JPL HORIZONS | `astroquery.jplhorizons` | Positions, velocities, ephemerides | None |
| NASA SPDF | `spdf.gsfc.nasa.gov` | Magnetometer CDF/CSV files | None |
| NASA PDS PPI | `pds-ppi.igpp.ucla.edu` | Plasma wave CDF files | None |
| NASA NeoWs | `api.nasa.gov/neo/rest/v1/feed` | Near-Earth objects | API key |
| NASA DONKI | `api.nasa.gov/DONKI/{FLR,CME,GST}` | Solar flares, CMEs, storms | API key |
| NOAA SWPC | `services.swpc.noaa.gov/products/` | Kp index, forecast | None |
| MAST (STScI) | `astroquery.mast.Observations` | HST/JWST archive metadata | None |
| MPC | Local `3I_mpc_orb.json` | Orbital elements | N/A |

### C. Key Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `deep_space_portal.nginx.conf` | `deep_space_portal/` | Nginx reverse proxy + security headers |
| `voyager1.service` | `/etc/systemd/system/` (EC2) | systemd service definition |
| `requirements.txt` | `deep_space_portal/` | Web + science dependencies |
| `requirements.txt` | `voyager1_project/` | Science-only dependencies |
| `schema.sql` | `deep_space_db/` | Database DDL |
| `.gitignore` | `deep_space_db/` | Excludes .db, WAL, .env |

### D. Related Documentation

| Document | Location | Scope |
|----------|----------|-------|
| Database Architecture | `deep_space_db/docs/database-architecture.md` | Schema design, ingestion, queries, scalability |
| Security Threat Model | `voyager1_project/docs/security-threat-model.md` | STRIDE analysis, controls, incident response |
| AWS Deployment Guide | `deep_space_portal/docs/aws-deployment.md` | EC2 setup, Nginx, Certbot, systemd |
| Getting Started | `voyager1_project/docs/getting-started.md` | Local development setup |
