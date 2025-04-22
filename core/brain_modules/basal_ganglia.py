import numpy as np
import json
import argparse
import graphviz
import matplotlib.pyplot as plt
import networkx as nx
from typing import Callable
import sys
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/config')
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/core')
sys.path.append(r'/Users/hongjunwu/Desktop/Pj/neocortex/util')
from neuro_config import ACTION_LIST, SURFACE_LIST, OBJECT_LIST, POSSIBLE_BELIEF
from neuro_utils import query_llm

class BasalGanglia:
    # 初始化动态贝叶斯网络，接收初始概率、转移模型和发射模型作为参数
    def __init__(self):
        self.htn = {}
        self.state_scores = {}
        self.current_state = "start state"
        self.last_action = ""
        self.states = []
        self.observations = []
        self.initial_probs = {loc: 1/len(POSSIBLE_BELIEF) for loc in POSSIBLE_BELIEF}
        self.n_states = len(POSSIBLE_BELIEF)
        self.current_params = {
            'initial_probs': self.initial_probs,
            'transition_probs': np.ones((self.n_states, self.n_states)) / self.n_states,
            'emission_probs': np.ones((self.n_states, 3)) / 3
        }
        self.belief_mean = {  # Unknown initial position
            'robot': ([0.0, 0.0, 0.0]),
            'bottle': np.array([np.nan, np.nan, np.nan]),
            'book': np.array([np.nan, np.nan, np.nan]),
            'box': np.array([np.nan, np.nan, np.nan]),
            'paper': np.array([np.nan, np.nan, np.nan]),
            'cabinet': np.array([np.nan, np.nan, np.nan]),
            'apple': np.array([np.nan, np.nan, np.nan])
        }
        self.belief_covariance = {obj: np.eye(3) * 0.1 for obj in self.belief_mean}

    # 接收新的观察数据并更新状态
    def ingest_observation(self, observation: list):
        self.observations.extend(observation)
        obsv = self._transform_observations(observation)
        self._predict(self.last_action)
        self._update(obsv)
    
    def _transform_observations(self, obs_list):
        obs_dict = {}
        for item in obs_list:
            for key, value in item.items():
                processed_value = [np.nan if isinstance(v, str) and v == "nan()" else v for v in value]
                obs_dict[key] = np.array(processed_value, dtype=np.float64)
        return obs_dict
    
    def _predict(self, action=None):
        """
        Update belief_mean based on the robot's action.
        Supports actions from ACTION_LIST.
        """
        if not action:
            return
        action_parts = action.split()
        if len(action_parts) < 2:
            print("Invalid action format!")
            return

        main_action = f"{action_parts[0]} {action_parts[1]}" if action_parts[0] != "look" else action_parts[0]
        direction = action_parts[-1]
        
        # Only "move arm" actions will affect the spatial belief in this simple example
        # Other actions like "move finger" or "look" don't modify positions here
        if main_action == "move arm":
            delta = 0.1  # You can parametrize this based on task specifics
            shift = np.zeros(3)

            if direction == "forward":
                shift[1] += delta  # +y direction
            elif direction == "backward":
                shift[1] -= delta  # -y direction
            elif direction == "leftward":
                shift[0] -= delta  # -x direction
            elif direction == "rightward":
                shift[0] += delta  # +x direction
            elif direction == "upward":
                shift[2] += delta  # +z direction
            elif direction == "downward":
                shift[2] -= delta  # -z direction

            # Robot moves, so environment shifts relatively
            for obj in self.belief_mean:
                if obj != 'robot':
                    self.belief_mean[obj] -= shift

            # Update robot's internal belief of its own position
            self.belief_mean['robot'] += shift

    def _update(self, observation):
        for obj, obs_pos in observation.items():
            if not np.isnan(obs_pos).any():
                # Kalman Gain
                K = self.belief_covariance[obj] @ np.linalg.inv(self.belief_covariance[obj] + np.eye(3) * 0.05)
                # Update mean
                self.belief_mean[obj] = self.belief_mean[obj] + K @ (obs_pos - self.belief_mean[obj])
                # Update covariance
                self.belief_covariance[obj] = (np.eye(3) - K) @ self.belief_covariance[obj]
    
    def merge_htn_from_json(self, llm_response: dict):
        def extract_transitions(node, parent_state, found_current):
            for transition in node.get('transitions', []):
                action = transition['action']
                next_state = transition['next_state']['state']
                
                if parent_state not in self.htn:
                    self.htn[parent_state] = {}
                if action not in self.htn[parent_state]:
                    self.htn[parent_state][action] = []
                if next_state not in self.htn[parent_state][action]:
                    self.htn[parent_state][action].append(next_state)
                if found_current == 0:
                    self.current_state = next_state
                    found_current = 1
                extract_transitions(transition['next_state'], next_state, found_current)

        root = llm_response['next_state']
        extract_transitions(root, self.current_state, 0)
    
    def update_state_scores(self, llm_response: dict, gamma: float = 0.8):
        def traverse(node):
            state = node['state']
            new_score = node['score']
            if state in self.state_scores:
                self.state_scores[state] = gamma * self.state_scores[state] + (1 - gamma) * new_score
            else:
                self.state_scores[state] = new_score
            for transition in node.get('transitions', []):
                traverse(transition['next_state'])

        traverse(llm_response['next_state'])

    def _transition_model(self, prev_state, observations: list):
        all_obs_features = []
        for obs_dict in observations:
            for obj, coords in obs_dict.items():
                obs_features = np.array([coords[0], coords[1], coords[2]])
                all_obs_features.append(obs_features)
        
        # Calculate transition probabilities using current parameters
        transition_probs = self.current_params['transition_probs']
        emission_probs = np.mean([self._compute_emission_probability(feat) for feat in all_obs_features], axis=0)
        
        # Forward algorithm step
        predicted_state = np.dot(prev_state, transition_probs) * emission_probs
        return predicted_state / np.sum(predicted_state)  # Normalize

    def _compute_emission_probability(self, observation):
        # Compute likelihood of observation given each state
        emission_probs = np.zeros(self.n_states)
        for i in range(self.n_states):
            # Use multivariate normal distribution
            mean = self.current_params['emission_probs'][i]
            diff = observation - mean
            emission_probs[i] = np.exp(-0.5 * np.dot(diff, diff))
        return emission_probs / np.sum(emission_probs)  # Normalize

    def run_em(self, max_iter=100, tol=1e-5, llm_assist=False):
        for _ in range(max_iter):
            state_posteriors = self._e_step()
            new_params = self._m_step(state_posteriors)
            if self._check_convergence(new_params, tol):
                break
            self.current_params = new_params

    def _e_step(self):
        T = len(self.observations)
        alpha = np.zeros((T, self.n_states))
        alpha[0] = self.initial_probs
        for t in range(1, T):
            alpha[t] = self._forward_update(alpha[t-1], self.observations[t])
        return alpha / alpha.sum(axis=1, keepdims=True)

    def _forward_update(self, prev_alpha, observation):
        for obj, coords in observation.items():
            obs_features = np.array([coords[0], coords[1], coords[2]])
        emission_probs = self._compute_emission_probability(obs_features)
        return np.dot(prev_alpha, self.current_params['transition_probs']) * emission_probs

    def _m_step(self, state_posteriors):
        T = len(self.observations)
        new_transition = np.zeros((self.n_states, self.n_states))
        new_emission = np.zeros((self.n_states, 3))
        
        # Update transition probabilities
        for t in range(T-1):
            for i in range(self.n_states):
                for j in range(self.n_states):
                    new_transition[i,j] += state_posteriors[t,i] * state_posteriors[t+1,j]
        
        # Normalize transition probabilities
        row_sums = new_transition.sum(axis=1)
        new_transition = new_transition / row_sums[:, np.newaxis]
        
        # Update emission parameters
        for i in range(self.n_states):
            weighted_sum = np.zeros(3)
            weight_sum = 0
            for t in range(T):
                for obj, coords in self.observations[t].items():
                    obs = np.array([coords[0], coords[1], coords[2]])
                    weighted_sum += state_posteriors[t,i] * obs
                    weight_sum += state_posteriors[t,i]
            new_emission[i] = weighted_sum / weight_sum

        return {
            'initial_probs': state_posteriors[0],
            'transition_probs': new_transition,
            'emission_probs': new_emission
        }
    
    def visualize_htn(self, dict_data, save_path=None):
        def build_graph(G, node, parent=None, action=None):
            state_name = node["state"]
            score = node["score"]
            is_goal = node["is_goal"]
            G.add_node(state_name, score=score, is_goal=is_goal)
            if parent and action:
                G.add_edge(parent, state_name, action=action)
            for transition in node.get("transitions", []):
                build_graph(G, transition["next_state"], state_name, transition["action"])
        
        G = nx.DiGraph()
        next_state = dict_data["next_state"]
        build_graph(G, next_state)
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G)
        node_colors = ["red" if G.nodes[n]["is_goal"] else "lightblue" for n in G.nodes]
        nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=2000, edge_color="black", font_size=10, font_weight="bold")
        edge_labels = {(u, v): d["action"] for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, font_color="blue")
        if save_path:
            plt.savefig(save_path, format="png", dpi=300)
        else:
            plt.show()
        return G

    # 检查算法是否收敛
    def _check_convergence(self, new_params, tol):
        return all(np.abs(new_params[k] - self.current_params[k]).max() < tol 
                 for k in new_params.keys())