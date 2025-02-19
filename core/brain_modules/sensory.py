import torch
from transformers import AutoProcessor, AutoModel
from config.neuro_config import SENSORY_CONFIG

class MultimodalProcessor:
    """多模态感知处理模块 (联合视觉皮层与体感皮层功能)"""
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained(SENSORY_CONFIG["processor"])
        self.model = AutoModel.from_pretrained(SENSORY_CONFIG["model"])
        self.fusion_layer = torch.nn.Linear(768*3, 512)  # 三模态融合
    
    def process(self, inputs):
        # 多模态特征提取
        visual_feats = self._process_vision(inputs["vision"])
        tactile_feats = self._process_tactile(inputs["tactile"])
        auditory_feats = self._process_auditory(inputs["auditory"])
        
        # 特征融合 (参考顶叶联合区功能)
        fused = torch.cat([visual_feats, tactile_feats, auditory_feats], dim=-1)
        return self.fusion_layer(fused)
    
    def _process_vision(self, images):
        return self.model(**self.processor(images=images, return_tensors="pt")).last_hidden_state.mean(dim=1)
    
    def _process_tactile(self, sensor_data):
        return torch.nn.functional.normalize(torch.tensor(sensor_data))
    
    def _process_auditory(self, audio_wave):
        return self.model(audio_input=audio_wave).mean(dim=1)