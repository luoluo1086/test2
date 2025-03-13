from utils.utils import State
import json
import time

class ImplicitTaskAgent:
    def __init__(self, file_path = "data/implicit_task.json"):
        self.__name__ = "ImplicitTask"
        self.current_case = 0
        self.max_cases = 2
        self.test_cases = self.get_test_cases(file_path)
    
    def get_next_case(self, state: State) -> State:
        print("## task: {} ##".format(self.__name__))
        # 根据current_case，确定输出哪个case，并放入TaskState中返回，如果已运行所有case，则current_case为None
        if self.current_case < self.max_cases:
            state.task_states[self.__name__]["current_case"] = self.test_cases[self.current_case]
            self.current_case += 1
            state.task_states[self.__name__]["remaining"] = self.max_cases - self.current_case
        else:
            # 所有问题生成完毕，打印等待信号
            print(f"{self.__name__}: All cases generated. Waiting for signal...")
            while True:
                time.sleep(1)  # 等待1秒
        print(state)
        return state
    
    def get_test_cases(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            test_cases = data["task"]["test_cases"]
        return test_cases

        
        
