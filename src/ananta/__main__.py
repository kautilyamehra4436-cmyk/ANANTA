"""Run a local smoke test: python -m ananta."""
from .controller import AnantaController
from .models import Claim, TaskRequest


def main():
    engine = AnantaController()
    result = engine.process(
        TaskRequest("ANANTA core smoke test", task_id="smoke-001"),
        [Claim("The system does not claim consciousness.")],
    )
    print(result)
    print({"audit_events": len(engine.audit())})


if __name__ == "__main__":
    main()
