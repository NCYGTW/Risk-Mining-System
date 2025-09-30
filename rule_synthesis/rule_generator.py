#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则生成层 - 规则生成器
功能：基于风险点、变量字典和统计摘要生成风险规则
"""

import json
import uuid
import logging
from typing import List, Dict, Any
from .prompt_template import get_rule_generation_prompt
import openai  # 假设使用OpenAI的API，您可以根据实际情况替换

logger = logging.getLogger('RuleGenerator')

class RuleGenerator:
    """规则生成器"""
    
    def __init__(self, config: Dict):
        """初始化规则生成器"""
        self.config = config
        # 初始化LLM客户端
        self._init_llm()
    
    def _init_llm(self):
        """初始化LLM客户端"""
        # 这里使用模拟的LLM客户端，实际使用时需要替换为真实的API调用
        pass
    
    def generate_rules(self, risk_points: List[str], variable_catalog: Dict, 
                      industry_scope: str, stats_summary: Dict, 
                      target_coverage: Dict) -> List[Dict]:
        """生成风险规则
        
        Args:
            risk_points: 风险点列表
            variable_catalog: 变量字典
            industry_scope: 行业范围
            stats_summary: 统计摘要
            target_coverage: 目标覆盖率
        
        Returns:
            List[Dict]: 生成的规则列表
        """
        logger.info(f"开始生成规则，风险点数量: {len(risk_points)}")
        
        rules = []
        
        for risk_point in risk_points:
            logger.info(f"生成{risk_point}的规则")
            
            # 生成提示词
            prompt = get_rule_generation_prompt(
                risk_point=risk_point,
                variable_catalog=variable_catalog,
                industry_scope=industry_scope,
                stats_summary=stats_summary,
                target_coverage=target_coverage
            )
            
            # 调用LLM生成规则
            rule_json = self._call_llm(prompt)
            
            if rule_json:
                try:
                    # 解析规则JSON
                    rule_data = json.loads(rule_json)
                    
                    # 如果是多条规则
                    if isinstance(rule_data, list):
                        rules.extend(rule_data)
                    else:
                        rules.append(rule_data)
                    
                    logger.info(f"成功生成{len(rule_data) if isinstance(rule_data, list) else 1}条规则")
                except Exception as e:
                    logger.error(f"解析规则JSON失败: {str(e)}")
            
        # 如果LLM调用失败，使用备用规则生成方法
        if not rules:
            rules = self._generate_fallback_rules(risk_points, variable_catalog, stats_summary)
        
        return rules
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM生成规则"""
        # 这里使用模拟的LLM调用，实际使用时需要替换为真实的API调用
        logger.info("调用LLM生成规则")
        
        # 模拟LLM响应延迟
        import time
        time.sleep(1)
        
        # 返回模拟的规则
        return """
        {
            "id": "rule_" + "%s" % uuid.uuid4().hex[:8],
            "rule_text": "企业营业收入增长率显著高于销售商品和提供劳务收到的现金增长率，且差额超过行业均值的3倍，同时应收账款增速较高。",
            "dsl": "(a - b) > (c - d) * 3.0 && a > 20 && e > Q75_e_industry",
            "variables_used": {
                "a": "营业收入增长率(%)",
                "b": "销售商品和提供劳务收到的现金增长率(%)",
                "c": "行业营业收入增长率均值",
                "d": "行业销售商品和提供劳务收到的现金增长率均值",
                "e": "应收账款增速(%)"
            },
            "period": "年度",
            "industry_scope": "全行业",
            "expected_coverage": 5,
            "edge_cases": [
                "企业处于快速扩张期，可能有合理的现金流滞后",
                "季节性业务导致的短期收入与现金流不匹配",
                "企业会计政策变更导致的指标异常"
            ],
            "stats_source": "来自2025年行业统计数据的Q75分位数"
        }
        """
    
    def _generate_fallback_rules(self, risk_points: List[str], variable_catalog: Dict, 
                                stats_summary: Dict) -> List[Dict]:
        """生成备用规则"""
        logger.info("使用备用规则生成方法")
        
        fallback_rules = []
        
        # 为每个风险点生成备用规则
        for risk_point in risk_points:
            # 基于统计摘要生成简单规则
            if risk_point == "提前确认营业收入":
                # 创建一条关于收入和现金流不匹配的规则
                rule = {
                    "id": f"fallback_{risk_point}_{uuid.uuid4().hex[:8]}",
                    "rule_text": "企业营业收入增长率显著高于销售商品和提供劳务收到的现金增长率，且差额超过行业均值。",
                    "dsl": "(a - b) > (c - d) * 1.5 && a > 15",
                    "variables_used": {
                        "a": "营业收入增长率(%)",
                        "b": "销售商品和提供劳务收到的现金增长率(%)",
                        "c": "行业营业收入增长率均值",
                        "d": "行业销售商品和提供劳务收到的现金增长率均值"
                    },
                    "period": "年度",
                    "industry_scope": "全行业",
                    "expected_coverage": 5,
                    "edge_cases": [
                        "企业处于快速扩张期",
                        "季节性业务波动",
                        "会计政策变更"
                    ],
                    "stats_source": "基于行业统计数据生成"
                }
                fallback_rules.append(rule)
            
            elif risk_point == "虚增营业收入":
                # 创建一条关于应收账款异常增长的规则
                rule = {
                    "id": f"fallback_{risk_point}_{uuid.uuid4().hex[:8]}",
                    "rule_text": "企业营业收入增长率高，但经营性现金流净额与营业收入比率显著低于行业均值。",
                    "dsl": "a > 20 && g < Q25_g_industry",
                    "variables_used": {
                        "a": "营业收入增长率(%)",
                        "g": "经营性现金流净额/营业收入"
                    },
                    "period": "年度",
                    "industry_scope": "全行业",
                    "expected_coverage": 4,
                    "edge_cases": [
                        "企业处于投入期",
                        "重大资本支出",
                        "行业周期性低谷"
                    ],
                    "stats_source": "基于行业统计数据生成"
                }
                fallback_rules.append(rule)
        
        return fallback_rules