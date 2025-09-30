#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估与选择层 - 规则评估器
功能：评估规则质量并选择最优规则集
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger('RuleEvaluator')

class RuleEvaluator:
    """规则评估器"""
    
    def __init__(self, config: Dict):
        """初始化规则评估器"""
        self.config = config
        # 评估指标权重
        self.metric_weights = {
            'coverage': 0.2,
            'anomaly_lift': 0.3,
            'stability': 0.2,
            'specificity': 0.2,
            'consistency': 0.1
        }
    
    def evaluate_and_select_rules(self, compiled_rules: List[Dict], data: pd.DataFrame, 
                                 anomaly_scores: Dict) -> List[Dict]:
        """评估并选择规则
        
        Args:
            compiled_rules: 编译后的规则列表
            data: 数据
            anomaly_scores: 异常分数
        
        Returns:
            List[Dict]: 选择的规则列表
        """
        logger.info(f"开始评估规则，共{len(compiled_rules)}条规则")
        
        # 为每条规则计算评估指标
        evaluated_rules = []
        for rule in compiled_rules:
            try:
                metrics = self._calculate_rule_metrics(rule, data, anomaly_scores)
                rule_with_metrics = rule.copy()
                rule_with_metrics['metrics'] = metrics
                evaluated_rules.append(rule_with_metrics)
            except Exception as e:
                logger.error(f"评估规则{rule.get('id', '未知ID')}失败: {str(e)}")
        
        # 计算综合评分
        for rule in evaluated_rules:
            rule['overall_score'] = self._calculate_overall_score(rule['metrics'])
        
        # 按综合评分排序
        evaluated_rules.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # 选择最优规则集
        selected_rules = self._select_optimal_rules(evaluated_rules)
        
        logger.info(f"规则评估完成，共选择{len(selected_rules)}条规则")
        
        return selected_rules
    
    def _calculate_rule_metrics(self, rule: Dict, data: pd.DataFrame, 
                               anomaly_scores: Dict) -> Dict:
        """计算规则的评估指标"""
        metrics = {}
        
        # 计算覆盖率
        coverage = self._calculate_coverage(rule, data)
        metrics['coverage'] = coverage
        
        # 计算异常分数提升
        anomaly_lift = self._calculate_anomaly_lift(rule, data, anomaly_scores)
        metrics['anomaly_lift'] = anomaly_lift
        
        # 计算稳定性（这里使用简化版本）
        stability = self._calculate_stability(rule, data)
        metrics['stability'] = stability
        
        # 计算特异性（这里使用简化版本）
        specificity = self._calculate_specificity(rule)
        metrics['specificity'] = specificity
        
        # 计算行业一致性（这里使用简化版本）
        consistency = self._calculate_industry_consistency(rule, data)
        metrics['consistency'] = consistency
        
        return metrics
    
    def _calculate_coverage(self, rule: Dict, data: pd.DataFrame) -> float:
        """计算规则覆盖率"""
        # 获取执行函数
        execute_func = rule.get('execute_function')
        if not execute_func:
            return 0.0
        
        # 统计命中的公司数量
        hit_count = 0
        total_count = len(data)
        
        for company_name, row in data.iterrows():
            # 准备数据
            row_dict = row.to_dict()
            # 添加公司名称
            row_dict['company_name'] = company_name
            
            # 执行规则
            if execute_func(row_dict):
                hit_count += 1
        
        # 计算覆盖率
        coverage = hit_count / total_count if total_count > 0 else 0.0
        
        return coverage
    
    def _calculate_anomaly_lift(self, rule: Dict, data: pd.DataFrame, 
                               anomaly_scores: Dict) -> float:
        """计算异常分数提升"""
        # 获取执行函数
        execute_func = rule.get('execute_function')
        if not execute_func:
            return 1.0
        
        # 统计命中公司的异常分数
        hit_scores = []
        all_scores = list(anomaly_scores.values())
        
        for company_name, row in data.iterrows():
            row_dict = row.to_dict()
            row_dict['company_name'] = company_name
            
            if execute_func(row_dict) and company_name in anomaly_scores:
                hit_scores.append(anomaly_scores[company_name])
        
        # 计算提升
        if not hit_scores or not all_scores:
            return 1.0
        
        hit_mean = np.mean(hit_scores)
        all_mean = np.mean(all_scores)
        
        lift = hit_mean / all_mean if all_mean > 0 else 1.0
        
        return lift
    
    def _calculate_stability(self, rule: Dict, data: pd.DataFrame) -> float:
        """计算规则稳定性（简化实现）"""
        # 在实际应用中，这里应该使用跨期数据计算稳定性
        # 这里返回一个默认值，表示稳定性良好
        return 0.8
    
    def _calculate_specificity(self, rule: Dict) -> float:
        """计算规则特异性（简化实现）"""
        # 在实际应用中，这里应该计算与其他规则的重叠度
        # 这里返回一个默认值，表示特异性良好
        return 0.7
    
    def _calculate_industry_consistency(self, rule: Dict, data: pd.DataFrame) -> float:
        """计算行业一致性（简化实现）"""
        # 在实际应用中，这里应该计算规则在不同行业的表现一致性
        # 这里返回一个默认值，表示行业一致性良好
        return 0.6
    
    def _calculate_overall_score(self, metrics: Dict) -> float:
        """计算综合评分"""
        overall_score = 0.0
        
        for metric_name, weight in self.metric_weights.items():
            if metric_name in metrics:
                # 归一化指标值（这里使用简化的归一化）
                value = metrics[metric_name]
                # 确保值在0-1之间
                normalized_value = max(0.0, min(1.0, value))
                overall_score += normalized_value * weight
        
        return overall_score
    
    def _select_optimal_rules(self, evaluated_rules: List[Dict]) -> List[Dict]:
        """选择最优规则集"""
        # 按综合评分选择前N条规则
        top_n = self.config.get('top_n_rules', 10)
        selected_rules = evaluated_rules[:top_n]
        
        # 过滤覆盖率过高或过低的规则
        min_coverage = self.config.get('min_coverage', 0.02)
        max_coverage = self.config.get('max_coverage', 0.08)
        
        filtered_rules = []
        for rule in selected_rules:
            coverage = rule['metrics'].get('coverage', 0.0)
            if min_coverage <= coverage <= max_coverage:
                filtered_rules.append(rule)
        
        return filtered_rules