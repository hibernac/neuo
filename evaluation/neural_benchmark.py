class NeuralBenchmark:
    """神经科学启发的评估指标"""
    METRICS = {
        'decision_quality': {
            'weight': 0.4,
            'fn': lambda x: x['confidence'] * x['speed']
        },
        'collaboration_efficiency': {
            'weight': 0.3,
            'fn': self._calc_turn_efficiency
        },
        'neurological_plausibility': {
            'weight': 0.3,
            'fn': self._brain_region_activation
        }
    }
    
    def evaluate(self, episode_log):
        """多维度评估（参考STARK和CollabLLM评估协议）"""
        scores = {}
        for metric, params in self.METRICS.items():
            scores[metric] = params['fn'](episode_log) * params['weight']
        return sum(scores.values())