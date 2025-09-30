#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据层 - 数据处理与统计摘要模块
功能：对原始的年报数据进行预处理，并生成统计摘要
目前各函数的代码都是示例代码，需要根据原始数据文件进行修改

"""

import os
import json
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging

def setup_logger():
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

setup_logger()
logger = logging.getLogger('DataProcessor')

class DataProcessor:
    """数据处理器"""
    
    def __init__(self, config: Dict):
        """初始化数据处理器"""
        self.config = config
        #数据文件的路径，此处为实例，后续需要修改
        self.data_path = config.get('data_path', 'data/sample_data.json')   
        
    def process_data(self) -> Tuple[pd.DataFrame, Dict]:
        """处理数据并生成统计摘要
        
        Returns:
            Tuple[pd.DataFrame, Dict]: 处理后的数据和统计摘要
        """
        logger.info(f"从{self.data_path}加载数据")
        
        # 加载数据
        data = self._load_data()
        
        # 数据清洗
        cleaned_data = self._clean_data(data)
        
        # 特征提取
        feature_data = self._extract_features(cleaned_data)
        
        # 计算统计摘要
        stats_summary = self._calculate_statistics(feature_data)
        
        logger.info(f"数据处理完成，共{len(feature_data)}条记录，生成了{len(feature_data.columns) - len(cleaned_data.columns)}个新特征")
        
        return feature_data, stats_summary
    
    def _load_data(self) -> Dict:
        """加载原始数据"""
        if not os.path.exists(self.data_path):
            logger.error(f"原始数据文件不存在: {self.data_path}")
            raise FileNotFoundError(f"原始数据文件不存在: {self.data_path}")
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载原始数据失败: {str(e)}")
            raise RuntimeError(f"加载原始数据失败: {str(e)}")
    
    def _clean_data(self, raw_data: Dict) -> pd.DataFrame:
        """清洗数据"""
        # 转换为DataFrame
        companies_data = raw_data.get('data', {})
        df = pd.DataFrame.from_dict(companies_data, orient='index')
        
        # 处理缺失值
        df = df.fillna(df.mean())
        
        return df
    
    def _extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """从原始数据中提取特征，用于异常检测
        
        Args:
            data: 清洗后的原始数据
            
        Returns:
            pd.DataFrame: 包含提取特征的数据
        """
        logger.info("开始提取特征")
        
        # 创建数据副本以避免修改原始数据
        feature_data = data.copy()
        
        # 1. 财务指标差异特征
        # 收入与现金流差异（虚增收入风险指标）
        if '营业收入增长率' in data.columns and '销售商品和提供劳务收到的现金增长率' in data.columns:
            feature_data['收入现金差异率'] = data['营业收入增长率'] - data['销售商品和提供劳务收到的现金增长率']
        
        # 应收账款与收入增长不匹配（提前确认收入风险指标）
        if '应收账款增速' in data.columns and '营业收入增长率' in data.columns:
            feature_data['应收收入比率'] = data['应收账款增速'] / (data['营业收入增长率'] + 1e-8)  # 加小值避免除零
        
        # 2. 经营效率特征
        # 现金流覆盖比率
        if '经营性现金流净额/营业收入' in data.columns:
            # 转换为正向指标，值越高风险越低
            feature_data['现金流覆盖度'] = data['经营性现金流净额/营业收入'] * -1
        
        # 3. 异常波动性特征
        # 计算各财务指标的相对波动性（需要时间序列数据）
        # 这里使用行业内相对位置作为替代
        if '行业' in data.columns:
            # 按行业分组计算各指标的Z-score
            for col in data.columns:
                if col != '行业' and pd.api.types.is_numeric_dtype(data[col]):
                    # 计算每个公司在行业内的Z-score
                    feature_data[f'{col}_行业Z值'] = data.groupby('行业')[col].transform(
                        lambda x: (x - x.mean()) / (x.std() + 1e-8)
                    )
        
        # 4. 综合风险指数（简单平均多个风险相关指标）
        risk_indicators = []
        if '收入现金差异率' in feature_data.columns:
            risk_indicators.append('收入现金差异率')
        if '应收收入比率' in feature_data.columns:
            risk_indicators.append('应收收入比率')
        if '现金流覆盖度' in feature_data.columns:
            risk_indicators.append('现金流覆盖度')
        
        # 添加标准化后的行业Z值到风险指标
        for col in feature_data.columns:
            if '_行业Z值' in col:
                risk_indicators.append(col)
        
        if risk_indicators:
            # 标准化各风险指标并计算平均风险分数
            normalized_risks = []
            for indicator in risk_indicators:
                # 简单归一化到0-1范围
                min_val = feature_data[indicator].min()
                max_val = feature_data[indicator].max()
                if max_val > min_val:  # 避免除零
                    normalized = (feature_data[indicator] - min_val) / (max_val - min_val)
                else:
                    normalized = pd.Series(0, index=feature_data.index)
                normalized_risks.append(normalized)
            
            feature_data['综合风险指数'] = sum(normalized_risks) / len(normalized_risks)
        
        logger.info(f"特征提取完成，共生成{len(feature_data.columns) - len(data.columns)}个新特征")
        
        return feature_data
    
    def _calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """计算统计摘要"""
        stats_summary = {}
        
        # 计算整体统计量
        overall_stats = {}
        for column in data.columns:
            if column != '行业' and pd.api.types.is_numeric_dtype(data[column]):
                series = data[column]
                overall_stats[column] = {
                    'mean': float(series.mean()),
                    'std': float(series.std()),
                    'min': float(series.min()),
                    'max': float(series.max()),
                    'Q25': float(series.quantile(0.25)),
                    'Q50': float(series.quantile(0.5)),
                    'Q75': float(series.quantile(0.75)),
                    'IQR': float(series.quantile(0.75) - series.quantile(0.25)),
                    'MAD': float(series.mad())
                }
        
        stats_summary['overall'] = overall_stats
        
        # 分行业计算统计量
        if '行业' in data.columns:
            industry_stats = {}
            for industry in data['行业'].unique():
                industry_data = data[data['行业'] == industry]
                industry_stats[industry] = {}
                for column in industry_data.columns:
                    if column != '行业' and pd.api.types.is_numeric_dtype(industry_data[column]):
                        series = industry_data[column]
                        industry_stats[industry][column] = {
                            'mean': float(series.mean()),
                            'std': float(series.std()),
                            'min': float(series.min()),
                            'max': float(series.max()),
                            'Q25': float(series.quantile(0.25)),
                            'Q50': float(series.quantile(0.5)),
                            'Q75': float(series.quantile(0.75)),
                            'IQR': float(series.quantile(0.75) - series.quantile(0.25)),
                            'MAD': float(series.mad())
                        }
            
            stats_summary['industry'] = industry_stats
        
        return stats_summary