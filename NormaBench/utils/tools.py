import json
from utils.utils import State

def save_state(state: State, task_name: str):
    # 将state保存为json文件，并且将当前运行的task添加到已完成列表
    with open(f"state_{task_name}.json", "w") as f:
        json.dump(state.collected_results[task_name], f)
    # 将当前任务添加到已完成列表
    state.completed_tasks.append(task_name)
    print("state saved. task: {}".format(task_name))
