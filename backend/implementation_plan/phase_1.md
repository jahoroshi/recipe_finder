## Phase 1: Project Setup and Infrastructure (Week 1)

### 1.1 Dependencies

**Installed Dependencies:**
```
all required dependencies are installed:

annotated-types==0.7.0
anyio==4.11.0
cachetools==6.2.1
certifi==2025.10.5
charset-normalizer==3.4.3
click==8.3.0
fastapi==0.119.0
filetype==1.2.0
google-ai-generativelanguage==0.7.0
google-api-core==2.26.0
google-auth==2.41.1
google-genai==1.43.0
googleapis-common-protos==1.70.0
greenlet==3.2.4
grpcio==1.75.1
grpcio-status==1.75.1
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
iniconfig==2.1.0
jsonpatch==1.33
jsonpointer==3.0.0
langchain-core==0.3.79
langchain-google-genai==2.1.12
langgraph==0.6.10
langgraph-checkpoint==2.1.2
langgraph-prebuilt==0.6.4
langgraph-sdk==0.2.9
langsmith==0.4.34
numpy==2.3.3
orjson==3.11.3
ormsgpack==1.11.0
packaging==25.0
pgvector==0.4.1
pluggy==1.6.0
proto-plus==1.26.1
protobuf==6.32.1
psycopg2-binary==2.9.11
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.12.0
pydantic_core==2.41.1
Pygments==2.19.2
pytest==8.4.2
pytest-asyncio==1.2.0
python-dotenv==1.1.1
PyYAML==6.0.3
requests==2.32.5
requests-toolbelt==1.0.0
rsa==4.9.1
sniffio==1.3.1
SQLAlchemy==2.0.44
starlette==0.48.0
tenacity==9.1.2
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.5.0
uvicorn==0.37.0
websockets==15.0.1
xxhash==3.6.0
zstandard==0.25.0
```

### 1.2 Database Infrastructure

**PostgreSQL URI:**
```
postgresql://postgres:postgres@localhost:5438/recipes
```

**Redis URI:**
```
redis://localhost:6381
```

### 1.3 Configuration Management

**Create Configuration Module:**
- Implement `Settings` class with Pydantic BaseSettings
- Set up environment variable validation
- All required credentials and settings are stored in `/home/jahoroshi/PycharmProjects/TestTaskClaude/.env`

**Key Configurations:**
- Database connection strings with async support
- Redis connection parameters
- Gemini API credentials
- Logging configuration

**Critical Implementation Rule - Environment File Loading:**

Use absolute paths for `.env` file resolution to ensure configuration works across different execution contexts (terminal, IDE, debugger, CI/CD):

```python
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Compute absolute path to .env file
    _project_root = Path(__file__).resolve().parent.parent.parent
    _env_file = _project_root / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_env_file),  # Use absolute path, not ".env"
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ... field definitions
```

**Rationale:** Relative paths like `".env"` fail when the working directory differs from the project root (e.g., running from PyCharm debugger, Docker, or subdirectories).

**Additional Requirements:**
- Create `run_server.py` entry point script with proper `sys.path` setup
- Include `.env.example` with all required variables documented
- Add early validation with clear error messages for missing environment variables

---

## Post-Implementation:

### 1. Write unit tests AND RUN created tests(!!!)
Verify implemented logic functionality:
- Configuration and environment variables loading tests
- PostgreSQL and Redis connection tests
- Gemini API integration tests

### 2. Update Claude.md
Add to documentation:
- List of implemented components
- Architectural decisions made
- Implementation details
- Known issues and TODOs



---