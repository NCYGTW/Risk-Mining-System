#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具模块 - 配置管理器
功能：管理系统配置
"""

import os
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('ConfigManager')

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，如果不提供则使用默认配置
        """
        self.config_path = config_path or 'config/config.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        # 如果配置文件存在，加载配置
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"从{self.config_path}加载配置成功")
                return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        
        # 如果配置文件不存在或加载失败，使用默认配置
        logger.warning(f"配置文件不存在或加载失败，使用默认配置")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        default_config = {
            # 系统配置
            'output_path': 'output/rules',
            'log_level': 'INFO',
            'random_state': 42,
            
            # 数据配置
            'data_path': 'data/sample_data.json',
            
            # 风险点配置
            'risk_points': [
                "提前确认营业收入",
                "虚增营业收入"
            ],
            
            # 变量字典
            'variable_catalog': {
                'a': '营业收入增长率(%)',
                'b': '销售商品和提供劳务收到的现金增长率(%)',
                'c': '行业营业收入增长率分位(Q75)',
                'd': '行业现金收入同比增速分位(Q75)',
                'e': '应收账款增速(%)',
                'f': '存货周转天数',
                'g': '经营性现金流净额/营业收入'
            },
            
            # 行业范围
            'industry_scope': '全行业',
            
            # 目标覆盖率
            'target_coverage': {
                'low': 2,
                'high': 8
            },
            
            # 异常检测配置
            'contamination': 0.1,
            'if_n_estimators': 100,
            'lof_n_neighbors': 20,
            'svm_kernel': 'rbf',
            'svm_nu': 0.1,
            
            # 规则评估配置
            'top_n_rules': 10,
            'min_coverage': 0.02,
            'max_coverage': 0.08
        }
        
        # 如果配置文件不存在，保存默认配置
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def get_config(self) -> Dict:
        """获取配置
        
        Returns:
            Dict: 配置字典
        """
        return self.config
    
    def update_config(self, new_config: Dict) -> None:
        """更新配置
        
        Args:
            new_config: 新的配置字典
        """
        self.config.update(new_config)
        
        # 保存更新后的配置
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已更新并保存到{self.config_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")