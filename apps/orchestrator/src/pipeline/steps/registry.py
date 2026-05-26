from pathlib import Path

from src.api.validators import safe_page_segment
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
from src.pipeline.workspace import (
    backend_dir as ws_backend_dir,
    frontend_admin_dir as ws_frontend_admin_dir,
    frontend_app_dir as ws_frontend_app_dir,
    java_sources_dir as ws_java_sources_dir,
)

STEP_DEFINITIONS: list[tuple[int, str]] = [
    (1, "spec_load"),
    (2, "spec_verify"),
    (3, "api_contract"),
    (4, "react_generation"),
    (5, "java_generation"),
    (6, "java_test"),
    (7, "integration"),
    (8, "equivalence_check"),
    (9, "complete"),
]


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

    def __init__(self, mcp_server_path: Path, mcp_python_path: str = "python3"):
        self.mcp_server_path = mcp_server_path
        self.mcp_python_path = mcp_python_path

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None:
            return StepResult(success=False, error="No spec in context")

        worker = MCPWorker(
            mcp_server_path=self.mcp_server_path,
            python_path=self.mcp_python_path,
        )
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
                cache_creation_tokens=result.cache_creation_tokens,
                cache_read_tokens=result.cache_read_tokens,
                cost=result.cost,
                duration_ms=result.duration_ms,
            )
        return StepResult(
            success=False,
            error=result.error,
            model_used="haiku",
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            cost=result.cost,
            duration_ms=result.duration_ms,
        )


class Step4ReactGen(BaseStep):
    name = "react_generation"
    step_number = 4

    def __init__(
        self,
        output_base: Path,
        frontend_dir: Path | None = None,
        screenshots_dir: Path | None = None,
        *,
        default_project_root: Path | None = None,
        dev_port: int = 3100,
        dev_startup_timeout_s: int = 30,
        ssim_threshold: float = 0.85,
        diff_threshold_pct: float = 15.0,
        strict_visual_gate: bool = True,
    ):
        self.output_base = output_base
        self.frontend_dir = frontend_dir
        self.screenshots_dir = screenshots_dir
        self.default_project_root = default_project_root or output_base.parent.parent.parent.parent
        self.dev_port = dev_port
        self.dev_startup_timeout_s = dev_startup_timeout_s
        self.ssim_threshold = ssim_threshold
        self.diff_threshold_pct = diff_threshold_pct
        self.strict_visual_gate = strict_visual_gate

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None or context.api_contract is None:
            return StepResult(success=False, error="Missing spec or api_contract in context")

        page_id = safe_page_segment(context.page_id)
        if context.workspace_root is not None:
            output_dir = ws_frontend_admin_dir(context, self.default_project_root) / page_id.replace(".", "/")
        else:
            output_dir = self.output_base / page_id.replace(".", "/")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find original screenshot
        screenshot_path = None
        if self.screenshots_dir:
            # Try both naming conventions: dot-separated and underscore-separated
            candidates = []
            for folder_name in [page_id.replace(".", "_"), page_id]:
                page_screenshots = self.screenshots_dir / folder_name
                candidates.extend([
                    page_screenshots / "original.png",
                    page_screenshots / "full_page.png",
                    page_screenshots / "step3_ambassador.png",
                ])
            for c in candidates:
                if c.exists():
                    screenshot_path = c
                    break

        if self.strict_visual_gate and (screenshot_path is None or not screenshot_path.exists()):
            return StepResult(
                success=False,
                error="Visual gate is strict but no baseline screenshot was found",
            )

        result = await generate_react(
            spec=context.spec,
            api_contract=context.api_contract,
            output_dir=output_dir,
            screenshot_path=screenshot_path,
        )

        if not result.success:
            return StepResult(
                success=False,
                error=result.error,
                model_used="sonnet",
                cost=result.cost,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cache_creation_tokens=result.cache_creation_tokens,
                cache_read_tokens=result.cache_read_tokens,
                duration_ms=result.duration_ms,
            )

        # Visual verification
        visual_artifacts: dict[str, object] = {"files": result.files_created}
        if screenshot_path and screenshot_path.exists():
            try:
                if context.workspace_root is not None:
                    frontend_dir = ws_frontend_app_dir(context, self.default_project_root)
                else:
                    frontend_dir = self.frontend_dir or self.output_base.parent.parent.parent.parent
                page_route = "/admin/" + context.page_id.replace(".", "/")
                passed, comparison, react_shot = await verify_visual_similarity(
                    original_screenshot=screenshot_path,
                    react_project_dir=frontend_dir,
                    page_route=page_route,
                    port=self.dev_port,
                    startup_timeout_s=self.dev_startup_timeout_s,
                    ssim_threshold=self.ssim_threshold,
                    diff_threshold_pct=self.diff_threshold_pct,
                )
                result.visual_diff_percent = comparison.diff_percent
                visual_artifacts.update(
                    {
                        "visual_diff": comparison.diff_percent,
                        "visual_ssim": comparison.ssim,
                    }
                )

                from src.api.ws.events import event_bus
                event_bus.emit("pipeline:visual_diff", {
                    "page_id": context.page_id,
                    "diff_percent": comparison.diff_percent,
                    "ssim": comparison.ssim,
                    "passed": passed,
                })

                if not passed:
                    return StepResult(
                        success=False,
                        error=(
                            f"Visual gate failed: ssim={comparison.ssim} "
                            f"(threshold {self.ssim_threshold}), "
                            f"diff={comparison.diff_percent}% (threshold {self.diff_threshold_pct}%)"
                        ),
                        artifacts=visual_artifacts,
                        model_used="sonnet",
                        cost=result.cost,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        cache_creation_tokens=result.cache_creation_tokens,
                        cache_read_tokens=result.cache_read_tokens,
                        duration_ms=result.duration_ms,
                    )
            except Exception as e:
                # Visual check failed but files were generated — pass with warning
                from src.api.ws.events import event_bus
                event_bus.emit("pipeline:visual_diff_skipped", {
                    "page_id": context.page_id,
                    "reason": str(e)[:100],
                })
                if self.strict_visual_gate:
                    return StepResult(
                        success=False,
                        error=f"Visual verification error: {str(e)[:200]}",
                        artifacts=visual_artifacts,
                        model_used="sonnet",
                        cost=result.cost,
                        input_tokens=result.input_tokens,
                        output_tokens=result.output_tokens,
                        cache_creation_tokens=result.cache_creation_tokens,
                        cache_read_tokens=result.cache_read_tokens,
                        duration_ms=result.duration_ms,
                    )
                visual_artifacts["visual_check_error"] = str(e)[:200]

        else:
            visual_artifacts["visual_diff"] = result.visual_diff_percent

        return StepResult(
            success=True,
            artifacts=visual_artifacts,
            model_used="sonnet",
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )


class Step5JavaGen(BaseStep):
    name = "java_generation"
    step_number = 5

    def __init__(self, output_base: Path, *, default_project_root: Path | None = None):
        self.output_base = output_base
        self.default_project_root = default_project_root or output_base.parent.parent.parent.parent.parent

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None or context.api_contract is None:
            return StepResult(success=False, error="Missing spec or api_contract in context")

        page_id = safe_page_segment(context.page_id)
        if context.workspace_root is not None:
            output_dir = ws_java_sources_dir(context, self.default_project_root) / page_id.replace(".", "/")
        else:
            output_dir = self.output_base / page_id.replace(".", "/")
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
                cost=result.cost,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cache_creation_tokens=result.cache_creation_tokens,
                cache_read_tokens=result.cache_read_tokens,
                duration_ms=result.duration_ms,
            )
        return StepResult(
            success=False,
            error=result.error,
            model_used="sonnet",
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )


class Step6JavaTest(BaseStep):
    name = "java_test"
    step_number = 6

    def __init__(
        self,
        output_base: Path,
        *,
        default_project_root: Path | None = None,
        strict_infra_failures: bool = True,
    ):
        self.output_base = output_base
        self.default_project_root = default_project_root or output_base
        self.strict_infra_failures = strict_infra_failures

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None:
            return StepResult(success=False, error="Missing spec in context")

        page_id = safe_page_segment(context.page_id)
        java_files = context.generated_files.get("java_generation", [])
        if context.workspace_root is not None:
            output_dir = ws_backend_dir(context, self.default_project_root)
        else:
            output_dir = self.output_base

        result = await generate_java_tests(
            spec=context.spec,
            java_files=java_files,
            output_dir=output_dir,
        )
        artifacts = {
            "files": result.test_files,
            "tests_passed": result.tests_passed,
            "tests_failed": result.tests_failed,
        }
        if result.warning:
            artifacts["warning"] = result.warning
            if self.strict_infra_failures:
                return StepResult(
                    success=False,
                    artifacts=artifacts,
                    error=f"Java test infrastructure failure: {result.warning}",
                    duration_ms=result.duration_ms,
                )
        if result.success:
            return StepResult(
                success=True,
                artifacts=artifacts,
                duration_ms=result.duration_ms,
            )
        return StepResult(
            success=False,
            artifacts=artifacts,
            error=result.error,
            duration_ms=result.duration_ms,
        )


class Step7Integration(BaseStep):
    name = "integration"
    step_number = 7

    def __init__(
        self,
        frontend_base: Path,
        backend_dir: Path | None = None,
        *,
        default_project_root: Path | None = None,
    ):
        self.frontend_base = frontend_base
        self.backend_dir = backend_dir
        self.default_project_root = default_project_root or frontend_base.parent.parent.parent.parent

    async def execute(self, context: StepContext) -> StepResult:
        page_id = safe_page_segment(context.page_id)
        if context.workspace_root is not None:
            frontend_dir = ws_frontend_admin_dir(context, self.default_project_root) / page_id.replace(".", "/")
            backend = ws_backend_dir(context, self.default_project_root)
        else:
            frontend_dir = self.frontend_base / page_id.replace(".", "/")
            backend = self.backend_dir

        if not frontend_dir.exists():
            return StepResult(success=False, error=f"Frontend dir not found: {frontend_dir}")

        result = await integrate_frontend_backend(
            spec=context.spec,
            api_contract=context.api_contract,
            frontend_dir=frontend_dir,
            backend_dir=backend,
        )

        if result.success:
            return StepResult(
                success=True,
                artifacts={"files_modified": result.files_modified, "report": result.report},
                model_used="sonnet",
                cost=result.cost,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cache_creation_tokens=result.cache_creation_tokens,
                cache_read_tokens=result.cache_read_tokens,
                duration_ms=result.duration_ms,
            )
        return StepResult(
            success=False,
            error=result.error,
            model_used="sonnet",
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )


class Step8Equivalence(BaseStep):
    name = "equivalence_check"
    step_number = 8

    def __init__(
        self,
        mcp_server_path: Path,
        backend_root: Path | None = None,
        *,
        default_project_root: Path | None = None,
    ):
        self.mcp_server_path = mcp_server_path
        self.backend_root = backend_root
        self.default_project_root = default_project_root or backend_root

    async def execute(self, context: StepContext) -> StepResult:
        java_files = context.generated_files.get("java_generation", [])
        if context.workspace_root is not None:
            search_roots = [ws_backend_dir(context, self.default_project_root)]
        elif self.backend_root:
            search_roots = [self.backend_root]
        else:
            search_roots = None
        result = await check_equivalence(
            spec=context.spec,
            java_files=java_files,
            search_roots=search_roots,
        )
        return StepResult(
            success=result.success,
            artifacts={
                "covered": result.covered,
                "missing": result.missing,
                "extra": result.extra,
                "endpoints": result.endpoints,
            },
            error=None if result.success else f"Missing operations: {result.missing}",
        )


class Step9Complete(BaseStep):
    name = "complete"
    step_number = 9

    async def execute(self, context: StepContext) -> StepResult:
        result = await complete_migration(page_id=context.page_id)
        return StepResult(success=result.success, artifacts={"message": result.message})


def create_pipeline_steps(settings: Settings) -> list[BaseStep]:
    project_root = settings.project_root
    return [
        Step1SpecLoad(specs_dir=settings.specs_dir),
        Step2SpecVerify(
            mcp_server_path=settings.mcp_server_path,
            mcp_python_path=settings.mcp_python_path,
        ),
        Step3ApiContract(),
        Step4ReactGen(
            output_base=project_root / "apps" / "frontend" / "src" / "app" / "admin",
            frontend_dir=project_root / "apps" / "frontend",
            screenshots_dir=project_root / "screenshots",
            default_project_root=project_root,
            dev_port=settings.frontend_dev_port,
            dev_startup_timeout_s=settings.frontend_dev_startup_timeout_s,
            ssim_threshold=settings.visual_ssim_threshold,
            diff_threshold_pct=settings.visual_diff_threshold_pct,
            strict_visual_gate=settings.strict_visual_gate,
        ),
        Step5JavaGen(
            output_base=project_root / "apps" / "backend" / "src" / "main" / "java",
            default_project_root=project_root,
        ),
        Step6JavaTest(
            output_base=project_root / "apps" / "backend",
            default_project_root=project_root,
            strict_infra_failures=settings.strict_java_test,
        ),
        Step7Integration(
            frontend_base=project_root / "apps" / "frontend" / "src" / "app" / "admin",
            backend_dir=project_root / "apps" / "backend",
            default_project_root=project_root,
        ),
        Step8Equivalence(
            mcp_server_path=settings.mcp_server_path,
            backend_root=project_root / "apps" / "backend",
            default_project_root=project_root,
        ),
        Step9Complete(),
    ]
