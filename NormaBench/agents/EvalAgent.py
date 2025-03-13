from agents.SameMeaningEvaluatorAgent import SameMeaningEvaluatorAgent

class EvalAgent:
    @classmethod
    def create(cls, metric_type: str):
        print(metric_type)
        if metric_type == "SameMeaning":
            return SameMeaningEvaluatorAgent()
        # 添加更多任务类型...
        raise ValueError(f"Unsupported metric type: {metric_type}")
