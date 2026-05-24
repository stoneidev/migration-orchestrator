import asyncio
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.workers.claude_cli import ClaudeCLIWorker
from src.api.ws.events import event_bus

router = APIRouter()

_init_status = {"frontend": "idle", "backend": "idle"}


FRONTEND_PROMPT = """Create a Next.js 15 project scaffold with the following requirements:

## Structure (Feature-Sliced Design)
```
src/
├── app/                    ← Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   └── admin/             ← Admin pages will be generated here
├── features/              ← FSD features (business logic per page)
├── entities/              ← FSD entities (shared domain models)
├── shared/
│   ├── ui/                ← shadcn/ui components
│   ├── api/               ← TanStack Query hooks + axios client
│   ├── lib/               ← Zustand stores, utilities
│   └── config/            ← Environment config
└── widgets/               ← FSD widgets (composite UI blocks)
```

## Tech Stack
- Next.js 15 with App Router
- TypeScript strict mode
- Tailwind CSS + shadcn/ui (install via npx shadcn@latest init)
- TanStack Query v5 for API calls
- Zustand for client state
- React Hook Form + Zod for forms
- Pretendard font (via CDN)
- Jest + React Testing Library

## Requirements
- Create package.json with all dependencies
- Create tsconfig.json (strict mode)
- Create tailwind.config.ts
- Create next.config.ts
- Create .eslintrc.json + .prettierrc
- Create jest.config.ts
- Create src/shared/api/client.ts (axios instance with base URL from env)
- Create src/shared/api/query-client.ts (TanStack QueryClient provider)
- Create src/shared/lib/store.ts (Zustand store template)
- Create src/app/layout.tsx with Pretendard font + QueryClientProvider
- Create src/app/page.tsx (placeholder)
- DO NOT install node_modules (just create config files)
- Korean language (ko) in html lang
"""

BACKEND_PROMPT = """Create a Spring Boot project scaffold with the following requirements:

## Structure (DDD/Hexagonal)
```
src/main/java/com/silicon2/admin/
├── domain/                     ← Layer별 (shared)
│   ├── model/                  ← Entity, VO
│   ├── service/                ← Domain Service
│   └── repository/             ← Repository interfaces (Port out)
├── common/                     ← 공통 모듈
│   ├── response/               ← ApiResponse wrapper
│   ├── exception/              ← GlobalExceptionHandler + error codes
│   ├── config/                 ← SecurityConfig, CorsConfig, JpaConfig
│   └── util/                   ← Pagination utilities
└── SiliconAdminApplication.java

src/main/resources/
├── application.yml
├── application-local.yml
└── db/migration/               ← Flyway (empty, migrations added per page)

src/test/java/com/silicon2/admin/
└── SiliconAdminApplicationTests.java
```

## Tech Stack
- Java 21
- Spring Boot 3.4
- Gradle (Kotlin DSL) with build.gradle.kts
- Spring Web + Spring Data JPA + Spring Validation
- Flyway for DB migration
- MySQL connector
- Lombok
- MapStruct
- SpringDoc OpenAPI (Swagger)
- JUnit 5 + Mockito + Spring Boot Test

## Requirements
- Create build.gradle.kts with all dependencies
- Create settings.gradle.kts (project name: silicon2-admin)
- Create gradle.properties (Java 21)
- Create src/main/resources/application.yml (MySQL config, Flyway, server port 8080)
- Create src/main/resources/application-local.yml (localhost MySQL)
- Create ApiResponse.java (generic wrapper: success, data, error, meta)
- Create ErrorCode.java (enum with code + message)
- Create GlobalExceptionHandler.java
- Create CorsConfig.java (allow localhost:3000)
- Create SiliconAdminApplication.java
- Create SiliconAdminApplicationTests.java
- Create an empty Flyway migration directory
- DO NOT download gradle wrapper (just create config files)
"""


async def _init_frontend(project_root: Path):
    _init_status["frontend"] = "running"
    event_bus.emit("project:init_started", {"target": "frontend"})

    frontend_dir = project_root / "apps" / "frontend"
    frontend_dir.mkdir(parents=True, exist_ok=True)

    worker = ClaudeCLIWorker()
    result = await worker.invoke(
        prompt=FRONTEND_PROMPT,
        model="sonnet",
        max_turns=20,
        cwd=frontend_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if result.success:
        _init_status["frontend"] = "complete"
        event_bus.emit("project:init_completed", {"target": "frontend", "output": result.output[:200]})
    else:
        _init_status["frontend"] = f"failed: {result.error[:100]}"
        event_bus.emit("project:init_failed", {"target": "frontend", "error": result.error[:200]})


async def _init_backend(project_root: Path):
    _init_status["backend"] = "running"
    event_bus.emit("project:init_started", {"target": "backend"})

    backend_dir = project_root / "apps" / "backend"
    backend_dir.mkdir(parents=True, exist_ok=True)

    worker = ClaudeCLIWorker()
    result = await worker.invoke(
        prompt=BACKEND_PROMPT,
        model="sonnet",
        max_turns=20,
        cwd=backend_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if result.success:
        _init_status["backend"] = "complete"
        event_bus.emit("project:init_completed", {"target": "backend", "output": result.output[:200]})
    else:
        _init_status["backend"] = f"failed: {result.error[:100]}"
        event_bus.emit("project:init_failed", {"target": "backend", "error": result.error[:200]})


class InitRequest(BaseModel):
    targets: list[str] = ["frontend", "backend"]


@router.post("/project/init", status_code=202)
async def init_project(request: InitRequest, background_tasks: BackgroundTasks):
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent

    for target in request.targets:
        if target == "frontend":
            background_tasks.add_task(_init_frontend, project_root)
        elif target == "backend":
            background_tasks.add_task(_init_backend, project_root)

    return {
        "success": True,
        "data": {"message": f"Initializing: {request.targets}", "targets": request.targets},
    }


@router.get("/project/status")
async def project_status():
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    frontend_exists = (project_root / "apps" / "frontend" / "package.json").exists()
    backend_exists = (project_root / "apps" / "backend" / "build.gradle.kts").exists()

    return {
        "success": True,
        "data": {
            "frontend": {
                "initialized": frontend_exists,
                "status": _init_status["frontend"],
            },
            "backend": {
                "initialized": backend_exists,
                "status": _init_status["backend"],
            },
        },
    }
