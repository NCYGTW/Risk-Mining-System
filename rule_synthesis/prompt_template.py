#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则生成层 - 提示词模板
功能：提供LLM生成规则的提示词模板
"""

from typing import Dict, Any

def get_rule_generation_prompt(risk_point: str, variable_catalog: Dict, 
                              industry_scope: str, stats_summary: Dict, 
                              target_coverage: Dict) -> str:
    """获取规则生成的提示词
    
    Args:
        risk_point: 风险点
        variable_catalog: 变量字典
        industry_scope: 行业范围
        stats_summary: 统计摘要
        target_coverage: 目标覆盖率
    
    Returns:
        str: 提示词
    """
    
    # 格式化变量字典
    formatted_variables = "\n".join([f"{key} = {value}" for key, value in variable_catalog.items()])
    
    # 格式化统计摘要
    overall_stats = stats_summary.get('overall', {})
    formatted_stats = "\n".join([
        f"{key}: 均值={stats.get('mean', 0)}, 标准差={stats.get('std', 0)}, "
        f"Q25={stats.get('Q25', 0)}, Q50={stats.get('Q50', 0)}, Q75={stats.get('Q75', 0)}, "
        f"IQR={stats.get('IQR', 0)}, MAD={stats.get('MAD', 0)}"
        for key, stats in overall_stats.items()
    ])
    
    # 构建提示词
    prompt = f"""角色：你是审计与财务风控专家，擅长从稳健统计中设定阈值并写成可执行规则。

输入：
- 风险点：{risk_point}
- 变量字典：
{formatted_variables}
- 行业/规模口径：{industry_scope}
- 统计摘要：
{formatted_stats}
- 约束：命中率在{target_coverage.get('low', 2)}-{target_coverage.get('high', 8)}%；避免除零；标注周期（YoY/MoM/TTM）。

任务：
1）给出一条或多条简洁、可落地的自然语言判断规则（必须包含具体阈值与对比基准）。
2）为每条规则提供严格的JSON，含：id、rule_text、dsl、variables_used、period、industry_scope、expected_coverage。
3）给出3个"容易误判的边界条件"。

输出：仅返回JSON，符合以下数据格式：
{{
    "id": "规则唯一ID",
    "rule_text": "自然语言描述的规则",
    "dsl": "DSL布尔表达式",
    "variables_used": {{"变量名": "变量描述"}},
    "period": "周期",
    "industry_scope": "行业范围",
    "expected_coverage": "预期覆盖率(%)",
    "edge_cases": ["边界条件1", "边界条件2", "边界条件3"],
    "stats_source": "阈值来源的统计数据说明"
}}"""
    
    return prompt