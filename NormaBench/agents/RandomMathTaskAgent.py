import random
import time
from utils.utils import State

class RandomMathTaskAgent:
    def __init__(self):
        self.__name__ = "RandomMathTask"
        self.current_case = 0
        self.max_cases = 2  # 生成5个随机数学题
    
    def get_next_case(self, state: State) -> State:
        print("## task: {} ##".format(self.__name__))
        if self.current_case < self.max_cases:
            state.task_states[self.__name__]["current_case"] = self.generate_random_math_problem()
            self.current_case += 1
            state.task_states[self.__name__]["remaining"] = self.max_cases - self.current_case
        else:
            # 所有问题生成完毕，打印等待信号
            print(f"{self.__name__}: All cases generated. Waiting for signal...")
            while True:
                time.sleep(1)  # 等待1秒
        print(state)
        return state

    def generate_random_math_problem(self):
        num_a = random.randint(1, 10)
        num_b = random.randint(1, 10)
        res = num_a + num_b
        problem = {
            "input": f"{num_a}+{num_b}等于几？",
            "expected": f"{res}"
        }
        return problem