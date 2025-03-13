from utils.utils import State

class SameMeaningEvaluatorAgent:
    def __init__(self):
        self.__task_name__ = None
    
    def set_task_name(self, task_name):
        self.__task_name__ = task_name

    def evaluate(self, state: State) -> State:
        print("## evaluating {} ##".format(self.__task_name__))
        print(state)
        expected = state.task_states[self.__task_name__]["current_case"]["expected"]
        actual = state.task_states[self.__task_name__]["model_output"]
        state.task_states[self.__task_name__]["evaluation_result"] = {
            "match": expected.strip() == actual.strip(),
            "reason": None
        }

        # 如果collected_results中没有该任务的结果，则添加一个空list
        if self.__task_name__ not in state.collected_results:
            state.collected_results[self.__task_name__] = []
        # 将本次结果添加到collected_results中
        state.collected_results[self.__task_name__].append(state.task_states[self.__task_name__])
        return state