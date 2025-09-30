#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则编译层 - 规则编译器
功能：解析和验证DSL规则
"""

import re
import ast
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger('RuleCompiler')

class RuleCompiler:
    """规则编译器"""
    
    def __init__(self, config: Dict):
        """初始化规则编译器"""
        self.config = config
        # 允许的操作符
        self.allowed_operators = {
            '+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=', '&&', '||', '!', '(', ')'
        }
        # 允许的函数
        self.allowed_functions = {'abs', 'max', 'min'}
    
    def validate_rule(self, rule: Dict) -> bool:
        """验证规则是否有效
        
        Args:
            rule: 规则字典
        
        Returns:
            bool: 规则是否有效
        """
        logger.info(f"验证规则: {rule.get('id', '未知ID')}")
        
        # 检查必要字段
        required_fields = ['id', 'rule_text', 'dsl', 'variables_used', 'period', 'industry_scope']
        for field in required_fields:
            if field not in rule:
                logger.error(f"缺少必要字段: {field}")
                return False
        
        # 验证DSL语法
        if not self._validate_dsl_syntax(rule['dsl']):
            logger.error(f"DSL语法验证失败")
            return False
        
        # 验证变量引用
        if not self._validate_variable_references(rule['dsl'], rule['variables_used']):
            logger.error(f"变量引用验证失败")
            return False
        
        # 检查除零风险
        if self._has_division_by_zero_risk(rule['dsl']):
            logger.warning(f"规则存在除零风险")
            # 这里可以选择返回False或仅警告
        
        logger.info(f"规则验证通过")
        return True
    
    def _validate_dsl_syntax(self, dsl: str) -> bool:
        """验证DSL语法"""
        try:
            # 替换逻辑操作符为Python语法
            python_expr = dsl.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
            
            # 检查表达式是否有效
            ast.parse(python_expr)
            
            # 检查是否只使用了允许的操作符
            # 这里可以添加更复杂的操作符检查
            
            return True
        except SyntaxError as e:
            logger.error(f"DSL语法错误: {str(e)}")
            return False
    
    def _validate_variable_references(self, dsl: str, variables_used: Dict) -> bool:
        """验证变量引用是否有效"""
        # 提取DSL中的所有变量引用
        # 这是一个简化的实现，实际可能需要更复杂的解析
        var_pattern = re.compile(r'\b([a-zA-Z_]\w*)\b')
        matches = var_pattern.findall(dsl)
        
        # 过滤掉操作符和函数名
        keywords = {'and', 'or', 'not', 'True', 'False', 'abs', 'max', 'min'}
        variables_in_dsl = {var for var in matches if var not in keywords and var not in self.allowed_functions}
        
        # 检查是否所有引用的变量都在variables_used中定义
        for var in variables_in_dsl:
            # 处理Q25, Q75等特殊变量
            if var.startswith('Q') and '_' in var:
                # Q25_g_industry 类似的变量可以跳过具体验证
                continue
            if var not in variables_used:
                logger.error(f"引用了未定义的变量: {var}")
                return False
        
        return True
    
    def _has_division_by_zero_risk(self, dsl: str) -> bool:
        """检查是否存在除零风险"""
        # 简化的检查逻辑
        if '/' in dsl:
            # 检查是否有直接除以零的情况
            if '/0' in dsl or '/ 0' in dsl:
                return True
            # 更复杂的检查可以分析除数表达式
        
        return False
    
    def compile_rule(self, rule: Dict) -> Dict:
        """编译规则为可执行形式
        
        Args:
            rule: 规则字典
        
        Returns:
            Dict: 编译后的规则
        """
        logger.info(f"编译规则: {rule.get('id', '未知ID')}")
        
        # 创建编译后的规则副本
        compiled_rule = rule.copy()
        
        # 生成可执行的Python表达式
        python_expr = self._translate_to_python(rule['dsl'])
        compiled_rule['python_expression'] = python_expr
        
        # 生成执行函数
        compiled_rule['execute_function'] = self._create_execution_function(python_expr, rule['variables_used'])
        
        logger.info(f"规则编译完成")
        return compiled_rule
    
    def _translate_to_python(self, dsl: str) -> str:
        """将DSL转换为Python表达式"""
        # 替换逻辑操作符
        python_expr = dsl.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
        
        # 这里可以添加更多转换逻辑
        
        return python_expr
    
    def _create_execution_function(self, python_expr: str, variables_used: Dict) -> callable:
        """创建执行规则的函数"""
        # 构建函数代码
        func_code = f"""
        def execute_rule(data):
            try:
                # 确保所有需要的变量都在数据中
                for var_name, var_desc in variables_used.items():
                    if var_name not in data:
                        # 处理Q分位数变量
                        if var_name.startswith('Q') and '_' in var_name:
                            # 这里可以添加Q分位数变量的处理逻辑
                            pass
                        else:
                            return False
                
                # 执行表达式
                return bool({python_expr})
            except Exception as e:
                # 记录错误但不中断流程
                logger.error(f"执行规则时出错: {{str(e)}}")
                return False
        """
        
        # 创建函数对象
        namespace = {}
        exec(func_code, namespace)
        
        return namespace['execute_rule']