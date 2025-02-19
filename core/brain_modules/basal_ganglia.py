# import torch

# class BasalGangliaSelector:
#     """行为选择器 (实现概率性动作选择)"""
#     def __init__(self):
#         self.dopamine_level = 0.5  # 多巴胺水平模拟
        
#     def select_action(self, proposals):
#         probs = torch.softmax(torch.tensor([p['priority'] for p in proposals]), dim=0)
#         chosen_idx = torch.multinomial(probs, 1).item()
#         self._update_dopamine(reward=proposals[chosen_idx]['expected_reward'])
#         return proposals[chosen_idx]
    
#     def _update_dopamine(self, reward):
#         self.dopamine_level += 0.1 * (reward - self.dopamine_level)