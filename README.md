
<p align="center">
  <img src="https://placehold.co/200x200/6C63FF/white?text=DRO" width="120" alt="DRO Logo">
</p>

<h1 align="center">🚀 DRO — Agentic Commerce Engine</h1>

<p align="center">
  <strong>AI-Powered Dropshipping Automation Platform</strong><br>
  <em>From product research to campaign launch in under 24 hours</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-2.0.0-6C63FF?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10%2B-4ECDC4?style=for-the-badge" alt="Python">
  <img src="https://img.shields.io/badge/license-Enterprise-FF6B6B?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/AI-Claude%20%7C%20GPT--4-FFD93D?style=for-the-badge" alt="AI">
</p>

---

## 🌟 The Power of Agentic Commerce

**DRO** is a commercial-grade, AI-driven dropshipping automation engine. It transforms the traditional 2-week store launch process into a **24-hour fully automated pipeline**.

Instead of manually researching products, writing copy, designing images, and setting up ads—DRO's AI agents handle the entire workflow:

| Traditional | With DRO |
|-------------|----------|
| 2-3 weeks to launch | **< 24 hours** |
| $2,000-5,000 in freelancer costs | **$0 (AI-powered)** |
| 5-10 different tools | **1 unified platform** |
| Manual research & testing | **AI-optimized strategy** |
| Generic store templates | **Cloned success architecture** |

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DRO Agentic Commerce Engine              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Market   │  │  Store   │  │ Creative │  │  Image   │  │
│  │Intelligence│  │Operations│  │  Studio  │  │   Lab    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │         │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  │
│  │   Ad     │  │  Launch  │  │  License │  │   AI    │  │
│  │ Factory  │  │  Center  │  │Security  │  │ Services│  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            AI Service Layer (Claude / GPT-4)          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Secure Licensing & HWID Binding            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | Windows 10 / macOS 12 / Ubuntu 20.04 | Windows 11 / macOS 14 |
| **Python** | 3.10+ | 3.12 |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 500 MB | 1 GB |
| **Internet** | Broadband | Broadband |
| **API Keys** | — | OpenAI or Claude |

---

## ⚡ Quick-Start Installation

### 1. Install Python

<details>
<summary><strong>Windows</strong></summary>

```powershell
# Download and install Python 3.12
winget install Python.Python.3.12

# Or download from: https://www.python.org/downloads/
# ✓ Check "Add Python to PATH" during installation
```
</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
# Using Homebrew
brew install python@3.12

# Or download from: https://www.python.org/downloads/
```
</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
```
</details>

### 2. Download DRO

```bash
# Clone or download the package
git clone https://github.com/your-org/dro-commerce.git
cd dro-commerce
```

### 3. Setup Environment

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 4. Configure API Keys

Edit the `.env` file with your credentials:

```env
# Required for AI features (at least one)
OPENAI_API_KEY=sk-your-key-here
CLAUDE_API_KEY=sk-ant-your-key-here

# Optional: for payment processing
STRIPE_SECRET_KEY=sk_live_your_key
```

### 5. Launch DRO

```bash
# Option A: Start the API server
python main.py server
# → API: http://localhost:8000
# → Docs: http://localhost:8000/docs

# Option B: Start the Streamlit Dashboard
python main.py dashboard
# → Dashboard: http://localhost:8501

# Option C: Run diagnostics
python main.py doctor
```

---

## 🎮 Dashboard Guide

### Tab 1: Market Intelligence 🔍
- Search winning products by category & price
- View competitor store data (traffic, revenue)
- AI-powered product scoring & recommendations

### Tab 2: Store Operations 🛒
- Enter any competitor URL for real-time analysis
- View store architecture (sections, design elements)
- Generate white-label clone with your branding

### Tab 3: Creative Studio ✍️
- AI-generated product copy (headlines, features, testimonials)
- 3 ad script variations per product
- Customizable tone (luxury, professional, youthful)

### Tab 4: Image Lab 🎨
- 16-image generation plan per product
- AI-generated image prompts for DALL-E / Midjourney
- Section-specific images (hero, before/after, bundles)

### Tab 5: Ad Factory 📺
- Multi-angle ad creative packages
- AI Avatar script preparation (MaxFusion ready)
- Facebook ad format packaging

### Tab 6: Launch Center 🚀
- Campaign setup with interest targeting
- Budget forecasting & ROAS estimation
- A/B testing recommendations
- One-click campaign activation

### Tab 7: Settings ⚙️
- API key management (OpenAI, Claude)
- License key activation
- System diagnostics & health checks

---

## 🔐 Licensing System

DRO uses a **hardware-ID (HWID) binding** license system:

```
License Format: DRO-XXXXX-XXXXX-XXXXX-XXXXX
```

| Feature | Free Mode | Licensed |
|---------|-----------|----------|
| Product Research | ✅ | ✅ |
| Store Cloning | ✅ | ✅ |
| AI Copywriting | ❌ (Mock) | ✅ (Real AI) |
| Image Generation | ❌ (Mock) | ✅ (Real AI) |
| Ad Creation | ✅ | ✅ |
| Campaign Launch | ✅ | ✅ |
| Source Code Access | ❌ (Obfuscated) | ❌ (Obfuscated) |

**To activate:**
1. Purchase a license key
2. Go to Settings → Licensing
3. Enter your key and click "Activate"

---

## 📦 Distribution & Build

```bash
# Full build (obfuscate + package)
python build.py

# Individual steps
python build.py obfuscate    # Obfuscate only
python build.py package      # Package only
python build.py clean        # Clean build artifacts
```

The build system uses **PyArmor** for source code obfuscation:
- Protects against IP theft and unauthorized cloning
- Encrypts bytecode at runtime
- Binds execution to licensed machines
- Produces redistributable package in `dist/dro/`

---

## 🛡️ Security Features

| Feature | Implementation |
|---------|---------------|
| **License Validation** | HWID-bound encrypted keys |
| **API Key Storage** | Fernet-encrypted .env files |
| **Source Protection** | PyArmor obfuscation |
| **Request Auth** | License gate middleware |
| **CORS** | Configurable origins |
| **Audit Logging** | All API calls logged |

---

## 🧪 API Reference

Full API documentation available at `http://localhost:8000/docs` (Swagger UI).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/license/status` | GET | License validation status |
| `/api/license/activate` | POST | Activate license key |
| `/api/settings/status` | GET | System configuration status |
| `/api/settings/keys` | POST | Save API keys |
| `/api/research/search` | POST | Search winning products |
| `/api/research/analyze` | POST | Analyze specific product |
| `/api/store/analyze` | POST | Analyze competitor store |
| `/api/store/clone` | POST | Generate white-label store |
| `/api/copy/generate` | POST | Generate product copy |
| `/api/copy/ads` | POST | Generate ad scripts |
| `/api/images/generate` | POST | Generate image plan |
| `/api/ads/create` | POST | Create ad packages |
| `/api/ads/avatar` | POST | Prepare AI avatar script |
| `/api/launch/setup` | POST | Configure ad campaign |
| `/api/launch/execute` | POST | Launch ad campaign |
| `/api/launch/forecast` | POST | Estimate campaign performance |
| `/api/launch/ab-test` | GET | A/B testing recommendations |

---

## 🤝 Support

| Channel | Availability |
|---------|-------------|
| 📧 Email | support@dro-commerce.com |
| 💬 Discord | [Join our server](https://discord.gg/dro) |
| 📚 Documentation | [docs.dro-commerce.com](https://docs.dro-commerce.com) |
| 🐛 Issues | [GitHub Issues](https://github.com/your-org/dro-commerce/issues) |

---

## 📄 License

**DRO — Agentic Commerce Engine**  
Copyright © 2024 DRO Systems. All rights reserved.

This software is protected by copyright law and international treaties.  
Unauthorized reproduction or distribution is prohibited.

---

<p align="center">
  <strong>Built with ❤️ for the next generation of e-commerce entrepreneurs.</strong><br>
  <em>"The best time to start was yesterday. The next best time is now."</em>
</p>
