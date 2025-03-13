from agents.ImplicitTaskAgent import ImplicitTaskAgent
from agents.RandomMathTaskAgent import RandomMathTaskAgent

class TaskAgent:
    @classmethod
    def create(cls, task_type: str):
        print(task_type)
        if task_type == "ImplicitTask":
            return ImplicitTaskAgent()
        elif task_type == "RandomMathTask":
            return RandomMathTaskAgent()
        # 添加更多任务类型...
        raise ValueError(f"Unsupported task type: {task_type}")
