<div align="center">

# 🚀 JZD Content Studio

### AI-Powered Content Creation, Review & Social Publishing Platform

*A production-style, full-stack platform with a server-enforced approval workflow — from sign-up to social publishing.*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-TBD-lightgrey?style=for-the-badge)

[**Quick Start**](#-quick-start) •
[**Features**](#-key-features) •
[**Architecture**](#-architecture) •
[**API Docs**](#-api-documentation) •
[**Roadmap**](#-roadmap)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Application Workflow](#-application-workflow)
- [What's Real vs. Mocked](#-whats-real-vs-mocked)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Testing the Workflow](#-testing-the-workflow)
- [Architecture](#-architecture)
- [Configuration](#-configuration)
- [Going Live](#-going-live)
- [Extending the Platform](#-extending-the-platform)
- [Security](#-security)
- [Limitations](#-current-limitations)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 Overview

**JZD Content Studio** is a full-stack content management and publishing platform built around one complete, backend-enforced workflow:

> **Sign Up → OTP Verification → Secure Login → AI Content Generation → Admin Review → Approval / Rejection → Download → Social Publishing**

It is built with **FastAPI, SQLAlchemy, JWT authentication, role-based authorization, pluggable AI / email / publishing providers, and a browser-based frontend.**

Unlike a UI-only prototype, critical business rules live in the backend. For example, **content download is blocked at the API level until an administrator approves the content** — hiding a button in the UI cannot bypass it.

---

## ✨ Key Features

<table>
<tr>
<td width="50%" valign="top">

### 🔐 Security-First Backend
- bcrypt password hashing
- JWT authentication
- Role-based access (Admin / Editor)
- OTP account verification
- API-level download restrictions
- Backend-enforced approval workflow

</td>
<td width="50%" valign="top">

### 🤖 AI-Ready Architecture
- Provider interface for AI generation
- Works out of the box with a mock provider
- Swap in a real AI service without redesigning the app

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📧 Pluggable Email
- Console provider (default, for development)
- SMTP provider (production)
- OTP delivery abstracted behind one interface

</td>
<td width="50%" valign="top">

### 📱 Social Publishing
- Adapter / Factory-style architecture
- **LinkedIn · Facebook · Instagram · WhatsApp**
- Add new platforms without touching core logic

</td>
</tr>
</table>

### Feature Matrix

| Feature | Status | Implementation |
|---|:---:|---|
| User registration | ✅ | Real |
| OTP verification | ✅ | Real |
| Password hashing | ✅ | bcrypt |
| Authentication | ✅ | JWT |
| Role-based access | ✅ | Server-enforced |
| Admin review, approve, reject, comment | ✅ | Real |
| Download protection | ✅ | API-enforced (HTTP 403) |
| AI generation | ✅ | Provider architecture |
| Email delivery | ✅ | Provider architecture |
| Social publishing & status tracking | ✅ | Adapter architecture |
| SQLite database | ✅ | Default |
| PostgreSQL support | ✅ | Via SQLAlchemy |
| Swagger / OpenAPI docs | ✅ | Built in |
| Docker deployment | 🔜 | Ready to containerize |

---

## 🎯 Application Workflow

```mermaid
flowchart TD
    A[Create Account] --> B[OTP Verification]
    B --> C[Secure Login]
    C --> D[Generate Content with AI]
    D --> E[Submit for Admin Review]
    E --> F{Admin Decision}
    F -->|Approved| G[Download Content]
    F -->|Rejected| H[Comments / Revision]
    H --> D
    G --> I[Publish]
    I --> J[LinkedIn]
    I --> K[Facebook]
    I --> L[Instagram]
    I --> M[WhatsApp]
```

### Content State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT
    DRAFT --> PENDING_REVIEW: Submit
    PENDING_REVIEW --> APPROVED: Admin approves
    PENDING_REVIEW --> REJECTED: Admin rejects + comment
    REJECTED --> DRAFT: Revise
    APPROVED --> PUBLISHED: Publish
    PUBLISHED --> [*]
```

### Roles & Permissions

| Role | Capabilities |
|---|---|
| **User / Editor** | Generate content · View own content · Submit for review · Download approved content · Publish approved content |
| **Admin** | Review submitted content · Approve · Reject · Add comments · Control the review workflow |

---

## ⚡ What's Real vs. Mocked

The app runs with **zero API keys** by using mock providers only where external credentials are required.

| Component | Default | Production |
|---|---|---|
| 👤 Accounts | Real | No change |
| 🔑 Passwords | bcrypt | No change |
| 🎫 JWT sessions | Real | No change |
| 🛡️ Roles & permissions | Real | No change |
| 📩 OTP delivery | Console / mock | Configure SMTP |
| 🤖 AI generation | Working mock provider | Configure real AI provider |
| 📱 Social publishing | Mock pipeline | Configure platform credentials |
| 🗄️ Database | SQLite | PostgreSQL recommended |

> **Important:** mocked *external services* do not mean a mocked *workflow*. Authentication, authorization, database operations, approval rules, API permissions, content states, and publishing status flows are all implemented in the backend.

---

## 🏗️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python · FastAPI · SQLAlchemy · Pydantic · Uvicorn · bcrypt · JWT |
| **Database** | SQLite (dev) · PostgreSQL (production-ready) |
| **Frontend** | HTML5 · CSS3 · JavaScript · Fetch API |
| **Patterns** | REST API · Provider Pattern · Adapter Pattern · Factory-style registration · RBAC · Service-oriented structure |

---

## 📁 Project Structure

```text
JZD Content Studio
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── config.py
│   │   ├── providers/
│   │   │   ├── email_provider.py
│   │   │   ├── ai_provider.py
│   │   │   └── publishers.py
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── content.py
│   │       ├── admin.py
│   │       └── publish.py
│   ├── requirements.txt
│   ├── .env.example
│   └── jzd.db
├── frontend/
│   └── index.html
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10+**
- pip
- Git
- A modern web browser

> No external API key is required for the default development setup.

### 1. Clone the repository

```bash
git clone https://github.com/hadiinamdar/AI-Powered-Digital-Content-Platform.git
cd AI-Powered-Digital-Content-Platform
```

### 2. Create a virtual environment

<details open>
<summary><b>Windows</b></summary>

```bash
cd backend
python -m venv venv
venv\Scripts\activate
```
</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```
</details>

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

<details open>
<summary><b>Windows</b></summary>

```bash
copy .env.example .env
```
</details>

<details>
<summary><b>macOS / Linux</b></summary>

```bash
cp .env.example .env
```
</details>

### 5. Start the backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now available at **http://localhost:8000**

### 6. Open the frontend

Open `frontend/index.html` in your browser. It talks to `http://localhost:8000` by default — if your backend is hosted elsewhere, update `API_BASE` in `index.html`.

---

## 🧪 Testing the Workflow

| Step | Action | Expected Result |
|:---:|---|---|
| **1** | Click **Create New Account**, enter details, then **Send OTP** | OTP generated |
| **2** | Enter the OTP (shown in the backend terminal with the console provider) | Account verified |
| **3** | Sign in with your verified credentials | JWT session issued |
| **4** | Open **Generate with AI**, enter a prompt, click **Generate Content** | Content created |
| **5** | Submit the content for review | Status → `PENDING_REVIEW` |
| **6** | Use the demo review flow to sign in as the seeded admin | Admin dashboard |
| **7** | **Approve**, or **Reject** with a comment | Status updated |
| **8** | Try downloading **before** approval | `HTTP 403 Forbidden` |
| **9** | Download **after** approval | `HTTP 200 OK` |
| **10** | Click **Proceed to Publish**, choose platforms | Publishing pipeline runs |

**Example prompt:**

```text
Create a professional LinkedIn post about the benefits of artificial intelligence in modern businesses.
```

> In mock mode, the external platform response is simulated, but the internal publishing and status pipeline runs for real.

### 🛡️ Server-Side Approval Protection

```mermaid
flowchart LR
    A[Download request] --> B{Authenticated?}
    B -->|No| X1[401 Unauthorized]
    B -->|Yes| C{Owns content?}
    C -->|No| X2[403 Forbidden]
    C -->|Yes| D{Approved?}
    D -->|No| X3[403 Forbidden]
    D -->|Yes| E[200 OK — content returned]
```

Hiding the download button in the frontend does **not** bypass the rule — the backend decides.

---

## 🏛️ Architecture

### High-Level Overview

```mermaid
flowchart TD
    FE[Frontend<br/>HTML / CSS / JS] -->|REST| API[FastAPI Application]
    API --> AUTH[Auth Router]
    API --> CONTENT[Content Router]
    API --> ADMIN[Admin Router]
    API --> PUB[Publish Router]
    AUTH & CONTENT & ADMIN & PUB --> ORM[SQLAlchemy Models]
    ORM --> DB[(SQLite / PostgreSQL)]
    CONTENT --> AI[AIProvider]
    AUTH --> EMAIL[EmailProvider]
    PUB --> SOCIAL[Publishers]
    AI --> AI1[Mock / Real AI]
    EMAIL --> EM1[Console / SMTP]
    SOCIAL --> SO1[LinkedIn · Facebook · Instagram · WhatsApp]
```

### Provider Abstractions

| Provider | Default | Production |
|---|---|---|
| **AIProvider** | Mock (no API key) | Real AI API |
| **EmailProvider** | Console | SMTP |
| **Publisher** | Mock pipeline | LinkedIn / Facebook / Instagram / WhatsApp APIs |

Each provider sits behind an interface, so implementations can be replaced **without rewriting** authentication, content, admin, or database logic.

### Architecture Principles

- **Separation of concerns** — auth, content, admin, publishing, and providers are separate modules
- **Provider abstraction** — external dependencies are hidden behind interfaces
- **Adapter pattern** — every social platform implements a common publisher interface
- **Server-side authorization** — security rules are enforced by the backend, never by UI visibility
- **Configuration-driven integrations** — switch services via environment variables

---

## ⚙️ Configuration

All integrations are controlled through environment variables.

```env
# Database
DATABASE_URL=sqlite:///./jzd.db

# Providers
EMAIL_PROVIDER=console
AI_PROVIDER=mock
PUBLISH_MODE=mock
```

### Development vs. Production

| Area | Development | Production |
|---|---|---|
| Database | SQLite | PostgreSQL |
| Email | Console | SMTP |
| AI | Mock / configured provider | Production AI |
| Publishing | Mock | Platform APIs |
| Credentials | Development values | Secure secrets |
| Deployment | Local Uvicorn | Docker / Cloud |
| HTTPS | Optional locally | **Required** |
| Admin credentials | Development | Secure credentials |

> ⚠️ A development admin account may be seeded at startup. **Never use development credentials in production.**

---

## 🌐 Going Live

<details>
<summary><b>📩 Email (SMTP)</b></summary>

```env
EMAIL_PROVIDER=smtp

SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

Any SMTP-compatible provider or your own mail server will work.
</details>

<details>
<summary><b>🤖 AI</b></summary>

Configure your AI provider and credentials. The provider architecture lets you replace the model implementation independently of the rest of the app. For image generation, connect a dedicated image-generation provider.
</details>

<details>
<summary><b>📱 Social Platforms</b></summary>

Live publishing requires platform-specific developer apps, permissions, OAuth credentials, access tokens, and/or business verification. These requirements come from the platform APIs and cannot be bypassed in application code.
</details>

<details>
<summary><b>📲 WhatsApp Business Cloud API</b></summary>

```env
PUBLISH_MODE=live

WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_RECIPIENT_PHONE_NUMBER=
```

A production implementation must use the WhatsApp Business Cloud API media/message workflow and handle delivery/status callbacks where required. The app intentionally **does not** report a real WhatsApp publication when production credentials and integration are not configured.
</details>

<details>
<summary><b>🗄️ Database (PostgreSQL)</b></summary>

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE
```
</details>

<details>
<summary><b>🐳 Docker (suggested production topology)</b></summary>

```mermaid
flowchart TD
    NET[Internet] --> RP[Reverse Proxy]
    RP --> FE[Frontend]
    RP --> API[FastAPI]
    API --> PG[(PostgreSQL)]
    API --> EXT[External APIs]
    EXT --> AI[AI]
    EXT --> EM[Email]
    EXT --> SO[Social]
```
</details>

---

## 🧱 Extending the Platform

### Add a new social platform

1. Open `backend/app/providers/publishers.py`
2. Create a class implementing the publisher interface
3. Register it in the platform registry

```python
class NewPlatformPublisher(BasePublisher):
    def publish(self, content):
        ...
```

No changes are needed to authentication, content management, admin review, approval workflow, database models, or the publishing status pipeline.

---

## 🔒 Security

**Pre-deployment checklist**

- [ ] Change all development credentials
- [ ] Use strong, unique JWT secrets
- [ ] Never commit `.env` or API keys
- [ ] Keep SMTP passwords out of the repository
- [ ] Enable HTTPS
- [ ] Use a production database
- [ ] Configure secure CORS policies
- [ ] Review OAuth permissions
- [ ] Store secrets securely
- [ ] Disable debug / development settings
- [ ] Implement token expiration and rotation policies
- [ ] Set up production logging and monitoring

---

## 🚧 Current Limitations

| Area | Note |
|---|---|
| **AI** | The default provider works without a key. For real AI-generated artwork, connect a production image-generation provider. |
| **Social publishing** | Live publishing needs approved developer/business apps and valid credentials. |
| **Frontend** | Opens directly as an HTML file; serve it via a proper web server for production. |

---

## 🗺️ Roadmap

### ✅ Completed

- [x] Full-stack application structure
- [x] Registration, OTP verification, bcrypt hashing
- [x] JWT authentication & role-based authorization
- [x] AI and email provider architectures
- [x] Admin review with approve / reject / comment
- [x] Server-side download protection
- [x] Publishing pipeline with LinkedIn, Facebook, Instagram, WhatsApp adapters
- [x] Swagger API documentation

### 🔜 Planned

- [ ] Production image-generation integration
- [ ] Complete OAuth account-connection flow
- [ ] Production social publishing credentials
- [ ] PostgreSQL deployment
- [ ] Docker Compose environment
- [ ] Cloud deployment
- [ ] Background publishing workers
- [ ] Scheduled publishing
- [ ] Content analytics dashboard
- [ ] Publishing history
- [ ] Advanced admin dashboard
- [ ] Automated testing and CI/CD
- [ ] Production monitoring and observability

---

## 📚 API Documentation

With the backend running, interactive Swagger docs are available at:

**👉 http://localhost:8000/docs**

| Route group | Purpose |
|---|---|
| `/auth` | Registration, OTP, login |
| `/content` | Generate, view, submit, download content |
| `/admin` | Review, approve, reject, comment |
| `/publish` | Social publishing and status |

An OpenAPI schema is also exposed for API clients and tooling.

---

## 🤝 Contributing

Contributions are welcome!

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature

# 2. Make your changes, then commit
git add .
git commit -m "Add your feature"

# 3. Push and open a Pull Request
git push origin feature/your-feature
```

---

## 📜 License

Add your preferred license before public distribution. For proprietary or company-owned deployments, review the repository's license and contribution terms before publishing.

---

<div align="center">

### 👨‍💻 JZD Content Studio

*A full-stack AI-powered digital content creation, review, and social publishing platform.*

**Python · FastAPI · SQLAlchemy · JWT · bcrypt · SQLite · HTML · CSS · JavaScript · REST**

<br/>

### ⭐ Found this useful?

Give the repository a star and follow for updates.

**[github.com/hadiinamdar/AI-Powered-Digital-Content-Platform](https://github.com/hadiinamdar/AI-Powered-Digital-Content-Platform)**

</div>
