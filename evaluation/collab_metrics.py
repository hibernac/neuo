class CollaborativeMetrics:
    """多智能体协作评估系统"""
    METRICS = {
        'task_efficiency': {
            'weight': 0.3,
            'measure': lambda logs: sum(log['steps']) / len(log)
        },
        'knowledge_utilization': {
            'weight': 0.4,
            'measure': self._calc_knowledge_usage
        },
        'neurological_alignment': {
            'weight': 0.3,
            'measure': self._brain_activation_similarity
        }
    }
    
    def evaluate_session(self, session_log):
        scores = {}
        for metric, params in self.METRICS.items():
            scores[metric] = params['measure'](session_log) * params['weight']
        return sum(scores.values())
    
    def _calc_knowledge_usage(self, logs):
        used_knowledge = set()
        total_knowledge = self.knowledge_base.size()
        for log in logs:
            used_knowledge.update(log['knowledge_accessed'])
        return len(used_knowledge) / total_knowledge