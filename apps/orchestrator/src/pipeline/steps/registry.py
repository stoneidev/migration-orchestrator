from pathlib import Path

from src.pipeline.engine import BaseStep, StepResult, StepContext
from src.pipeline.steps.step1_spec_load import load_spec
from src.pipeline.steps.step2_spec_verify import verify_spec
from src.pipeline.steps.step3_api_contract import generate_api_contract
from src.pipeline.steps.step4_react_gen import generate_react
from src.pipeline.steps.step5_java_gen import generate_java
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
                model_used="sonnet",
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cost=0.0,
            )
        return StepResult(success=False, error=result.error)


class Step4ReactGen(BaseStep):
    name = "react_generation"
    step_number = 4

    def __init__(self, output_base: Path):
        self.output_base = output_base

    async def execute(self, context: StepContext) -> StepResult:
        if context.spec is None or context.api_contract is None:
            return StepResult(success=False, error="Missing spec or api_contract in context")

        output_dir = self.output_base / context.page_id.replace(".", "/")
        output_dir.mkdir(parents=True, exist_ok=True)

        result = await generate_react(
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


def create_pipeline_steps(settings: Settings) -> list[BaseStep]:
    return [
        Step1SpecLoad(specs_dir=settings.specs_dir),
        Step2SpecVerify(mcp_server_path=settings.mcp_server_path),
        Step3ApiContract(),
        Step4ReactGen(output_base=Path("apps/frontend/src/app/admin")),
        Step5JavaGen(output_base=Path("apps/backend/src/main/java")),
    ]
