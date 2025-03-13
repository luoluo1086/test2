import os
import requests
from utils.utils import State

class Testee:
    @classmethod
    def create(cls, testee_type: str, testee_name: str):
        if testee_type == "LLM":
            return LLMTestee(testee_name)
        elif testee_type == "Math":
            return MathTestee(testee_name)
        # 添加更多子类...
        raise ValueError(f"Unsupported testee type: {testee_type}")

class LLMTestee:
    def __init__(self, name):
        self.__task_name__ = name
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
    
    def set_task_name(self, name):
        self.__task_name__ = name
        print("Testee name set to: " + self.__task_name__)
    
    def run(self, state: State) -> State:
        print("## testee: {} ##".format(self.__task_name__))
        input = state.task_states[self.__task_name__]["current_case"]["input"]
        print("input: {}".format(input))
        output = "test"
        state.task_states[self.__task_name__]["model_output"] = output
        return state
    

class MathTestee:
    def __init__(self, name):
        self.__task_name__ = name

    def set_task_name(self, name):
        self.__task_name__ = name
        print("Testee name set to: " + self.__name__)

    def run(self, state: State) -> State:
        print("## testee: {} ##".format(self.__task_name__))
        input = state.task_states[self.__task_name__]["current_case"]["input"]
        # 示例：简单数学计算
        output = str(eval(input))
        state.task_states[self.__task_name__]["model_output"] = output
        return state