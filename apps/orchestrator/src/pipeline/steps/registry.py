from pathlib import Path

from src.pipeline.engine import BaseStep, StepResult, StepContext
from src.pipeline.steps.step1_spec_load import load_spec
from src.pipeline.steps.step2_spec_verify import verify_spec
from src.pipeline.steps.step3_api_contract import generate_api_contract
from src.pipeline.steps.step4_react_gen import generate_react, verify_visual_similarity
from src.pipeline.steps.step5_java_gen import generate_java
from src.pipeline.steps.step6_java_test import generate_java_tests
from src.pipeline.steps.step7_integration import integrate_frontend_backend
from src.pipeline.steps.step8_equivalence import check_equivalence
from src.pipeline.steps.step9_complete import complete_migration
from src.workers.mcp import MCPWorker
from src.config import Settings


class Step1SpecLoad(BaseStep):
    name = "spec_load"
    step_number = 1

    def __init__(self, specs_dir: Path):
        self.specs_dir = specs_dir

    async def execute(self, context: StepContext) -> StepResult:
        try:
            spec = load_spec(context.page_id, specs_dir=self.specs_dir)
            return StepResult(success=True, artifacts={"spec": spec})
        except Exception as e:
            return StepResult(success=False, error=str(e))


class Step2SpecVerify(BaseStep):
    name = "spec_verify"
    step_number = 2

    def __init__(self, mcp_server_path: Path):
        self.mcp_server_path = mcp_server_path

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None:
            return StepResult(success=False, error="No spec in context")

        worker = MCPWorker(mcp_server_path=self.mcp_server_path)
        async with worker.connect():
            result = await verify_spec(context.spec, worker)

        if result.success:
            return StepResult(success=True, artifacts={"verification": result.gaps})
        else:
            return StepResult(success=False, error=f"Gaps found: {result.gaps}")


class Step3ApiContract(BaseStep):
    name = "api_contract"
    step_number = 3

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None:
            return StepResult(success=False, error="No spec in context")

        result = await generate_api_contract(context.spec)
        if result.success:
            return StepResult(
                success=True,
                artifacts={"api_contract": result.content},
                model_used="haiku",
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cost=result.cost,
            )
        return StepResult(success=False, error=result.error)


class Step4ReactGen(BaseStep):
    name = "react_generation"
    step_number = 4

    def __init__(self, output_base: Path, frontend_dir: Path | None = None, screenshots_dir: Path | None = None):
        self.output_base = output_base
        self.frontend_dir = frontend_dir
        self.screenshots_dir = screenshots_dir

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None or context.api_contract is None:
            return StepResult(success=False, error="Missing spec or api_contract in context")

        output_dir = self.output_base / context.page_id.replace(".", "/")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find original screenshot
        screenshot_path = None
        if self.screenshots_dir:
            page_screenshots = self.screenshots_dir / context.page_id.replace(".", "_")
            candidates = [
                page_screenshots / "original.png",
                page_screenshots / "full_page.png",
                page_screenshots / "step3_ambassador.png",
            ]
            for c in candidates:
                if c.exists():
                    screenshot_path = c
                    break

        result = await generate_react(
            spec=context.spec,
            api_contract=context.api_contract,
            output_dir=output_dir,
            screenshot_path=screenshot_path,
        )

        if not result.success:
            return StepResult(success=False, error=result.error)

        # Visual verification
        if screenshot_path and screenshot_path.exists():
            try:
                frontend_dir = self.frontend_dir or self.output_base.parent.parent.parent.parent  # apps/frontend
                page_route = "/admin/" + context.page_id.replace(".", "/")
                passed, diff_pct, react_shot = await verify_visual_similarity(
                    original_screenshot=screenshot_path,
                    react_project_dir=frontend_dir,
                    page_route=page_route,
                )
                result.visual_diff_percent = diff_pct

                from src.api.ws.events import event_bus
                event_bus.emit("pipeline:visual_diff", {
                    "page_id": context.page_id,
                    "diff_percent": diff_pct,
                    "passed": passed,
                })

                if not passed:
                    return StepResult(
                        success=False,
                        error=f"Visual diff too high: {diff_pct}% (threshold: 15%)",
                        artifacts={"files": result.files_created, "visual_diff": diff_pct},
                    )
            except Exception as e:
                # Visual check failed but files were generated — pass with warning
                from src.api.ws.events import event_bus
                event_bus.emit("pipeline:visual_diff_skipped", {
                    "page_id": context.page_id,
                    "reason": str(e)[:100],
                })

        return StepResult(
            success=True,
            artifacts={"files": result.files_created, "visual_diff": result.visual_diff_percent},
            model_used="sonnet",
        )


class Step5JavaGen(BaseStep):
    name = "java_generation"
    step_number = 5

    def __init__(self, output_base: Path):
        self.output_base = output_base

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None or context.api_contract is None:
            return StepResult(success=False, error="Missing spec or api_contract in context")

        output_dir = self.output_base / context.page_id.replace(".", "/")
        output_dir.mkdir(parents=True, exist_ok=True)

        result = await generate_java(
            spec=context.spec,
            api_contract=context.api_contract,
            output_dir=output_dir,
        )
        if result.success:
            return StepResult(
                success=True,
                artifacts={"files": result.files_created},
                model_used="sonnet",
            )
        return StepResult(success=False, error=result.error)


class Step6JavaTest(BaseStep):
    name = "java_test"
    step_number = 6

    def __init__(self, output_base: Path):
        self.output_base = output_base

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None:
            return StepResult(success=False, error="Missing spec in context")

        java_files = context.generated_files.get("java_generation", [])
        output_dir = self.output_base / context.page_id.replace(".", "/")
        output_dir.mkdir(parents=True, exist_ok=True)

        result = await generate_java_tests(
            spec=context.spec,
            java_files=java_files,
            output_dir=output_dir,
        )
        if result.success:
            return StepResult(success=True, artifacts={"files": result.test_files}, model_used="sonnet")
        return StepResult(success=False, error=result.error)


class Step7Integration(BaseStep):
    name = "integration"
    step_number = 7

    def __init__(self, frontend_base: Path, backend_dir: Path | None = None):
        self.frontend_base = frontend_base
        self.backend_dir = backend_dir

    async def execute(self, context: StepContext) -> StepResult:
        frontend_dir = self.frontend_base / context.page_id.replace(".", "/")

        if not frontend_dir.exists():
            return StepResult(success=False, error=f"Frontend dir not found: {frontend_dir}")

        result = await integrate_frontend_backend(
            spec=context.spec,
            api_contract=context.api_contract,
            frontend_dir=frontend_dir,
            backend_dir=self.backend_dir,
        )

        if result.success:
            return StepResult(
                success=True,
                artifacts={"files_modified": result.files_modified, "report": result.report},
                model_used="sonnet",
                cost=result.report.get("cost", 0),
                duration_ms=result.report.get("duration_ms", 0),
            )
        return StepResult(success=False, error=result.error)


class Step8Equivalence(BaseStep):
    name = "equivalence_check"
    step_number = 8

    def __init__(self, mcp_server_path: Path):
        self.mcp_server_path = mcp_server_path

    async def execute(self, context: StepContext) -> StepResult:
        java_files = context.generated_files.get("java_generation", [])
        result = await check_equivalence(
            spec=context.spec,
            java_files=java_files,
        )
        return StepResult(
            success=result.success,
            artifacts={"covered": result.covered, "missing": result.missing},
        )


class Step9Complete(BaseStep):
    name = "complete"
    step_number = 9

    async def execute(self, context: StepContext) -> StepResult:
        result = await complete_migration(page_id=context.page_id)
        return StepResult(success=result.success, artifacts={"message": result.message})


def create_pipeline_steps(settings: Settings) -> list[BaseStep]:
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    return [
        Step1SpecLoad(specs_dir=settings.specs_dir),
        Step2SpecVerify(mcp_server_path=settings.mcp_server_path),
        Step3ApiContract(),
        Step4ReactGen(
            output_base=project_root / "apps" / "frontend" / "src" / "app" / "admin",
            frontend_dir=project_root / "apps" / "frontend",
            screenshots_dir=project_root / "screenshots",
        ),
        Step5JavaGen(output_base=project_root / "apps" / "backend" / "src" / "main" / "java"),
        Step6JavaTest(output_base=project_root / "apps" / "backend"),
        Step7Integration(
            frontend_base=project_root / "apps" / "frontend" / "src" / "app" / "admin",
            backend_dir=project_root / "apps" / "backend",
        ),
        Step8Equivalence(mcp_server_path=settings.mcp_server_path),
        Step9Complete(),
    ]
