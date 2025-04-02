import numpy as np
import math

class Sampling:
    def __init__(self):
        pass
    
    def pareto_sample(self, data_list, sample_count=None, sample_rate=None):
        """
        根据帕累托分布进行采样
        
        参数:
        data_list: 输入的包含字典的列表，每个字典中包含'confidence'键
        sample_count: 采样数量（优先级高于sample_rate）
        sample_rate: 采样率（当sample_count为None时使用）
        
        返回:
        采样后的列表
        """
        if not data_list:
            return []
        
        # 计算采样数量
        if sample_count is not None:
            sample_size = min(sample_count, len(data_list))
        elif sample_rate is not None:
            sample_size = max(1, min(math.ceil(len(data_list) * sample_rate), len(data_list)))
        else:
            raise ValueError("必须提供采样数量(sample_count)或采样率(sample_rate)")
        
        # 提取confidence值并计算权重
        confidences = [item.get('confidence', 0.5) for item in data_list]
        
        # 根据confidence值计算权重（confidence越小，权重越大）
        # 使用1 / confidence作为权重，但要避免除以零
        weights = [1 / (c + 1e-9) for c in confidences]
        
        # 归一化权重
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # 生成帕累托分布的样本索引
        # 帕累托分布的形状参数alpha设置为1
        alpha = 1
        # 使用权重作为概率分布
        indices = np.random.choice(
            len(data_list), 
            size=sample_size, 
            replace=False, 
            p=weights
        )
        
        # 返回采样后的数据
        return [data_list[i] for i in indices]

if __name__ == "__main__":
    # 示例数据
    data = [
        {'id': 1, 'confidence': 0.1},
        {'id': 2, 'confidence': 0.3},
        {'id': 3, 'confidence': 0.5},
        {'id': 4, 'confidence': 0.7},
        {'id': 5, 'confidence': 0.9}
    ]
    
    sampler = Sampling()
    
    # 采样3个对象
    sampled_data = sampler.pareto_sample(data, sample_count=3)
    print("采样结果:", sampled_data)
    
    # 采样50%的对象
    sampled_data_rate = sampler.pareto_sample(data, sample_rate=0.5)
    print("按采样率采样结果:", sampled_data_rate)