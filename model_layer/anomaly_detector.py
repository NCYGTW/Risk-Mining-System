#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型层 - 无监督异常检测器
功能：使用多种无监督算法检测异常
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
import logging

logger = logging.getLogger('AnomalyDetector')

class AnomalyDetector:
    """无监督异常检测器"""
    
    def __init__(self, config: Dict):
        """初始化异常检测器"""
        self.config = config
        self.models = {
            'isolation_forest': IsolationForest(
                n_estimators=config.get('if_n_estimators', 100),
                contamination=config.get('contamination', 0.1),
                random_state=config.get('random_state', 42)
            ),
            'lof': LocalOutlierFactor(
                n_neighbors=config.get('lof_n_neighbors', 20),
                contamination=config.get('contamination', 0.1)
            ),
            'one_class_svm': OneClassSVM(
                kernel=config.get('svm_kernel', 'rbf'),
                nu=config.get('svm_nu', 0.1)
            )
        }
    
    def detect_anomalies(self, data: pd.DataFrame) -> Dict[str, float]:
        """检测异常并生成异常分数
        
        Args:
            data: 处理后的数据
        
        Returns:
            Dict[str, float]: 公司名称到异常分数的映射
        """
        logger.info("开始异常检测")
        
        # 准备特征数据
        feature_columns = [col for col in data.columns if col != '行业' and pd.api.types.is_numeric_dtype(data[col])]
        X = data[feature_columns].values
        
        # 存储每个模型的结果
        model_scores = {}
        
        # Isolation Forest
        try:
            if_scores = self.models['isolation_forest'].fit(X).score_samples(X)
            # 转换为0-1的分数
            model_scores['isolation_forest'] = (if_scores.max() - if_scores) / (if_scores.max() - if_scores.min())
        except Exception as e:
            logger.error(f"Isolation Forest异常: {str(e)}")
        
        # Local Outlier Factor
        try:
            lof_scores = self.models['lof'].fit(X).negative_outlier_factor_
            # 转换为0-1的分数
            model_scores['lof'] = (lof_scores.max() - lof_scores) / (lof_scores.max() - lof_scores.min())
        except Exception as e:
            logger.error(f"Local Outlier Factor异常: {str(e)}")
        
        # One-Class SVM
        try:
            svm_scores = self.models['one_class_svm'].fit(X).decision_function(X)
            # 转换为0-1的分数
            model_scores['one_class_svm'] = (svm_scores.max() - svm_scores) / (svm_scores.max() - svm_scores.min())
        except Exception as e:
            logger.error(f"One-Class SVM异常: {str(e)}")
        
        # 综合异常分数（简单平均）
        anomaly_scores = {}
        companies = data.index.tolist()
        
        for i, company in enumerate(companies):
            scores = [model_scores[model][i] for model in model_scores if i < len(model_scores[model])]
            if scores:
                anomaly_scores[company] = float(np.mean(scores))
            else:
                anomaly_scores[company] = 0.0
        
        logger.info(f"异常检测完成，共{len(anomaly_scores)}家公司获得异常分数")
        
        return anomaly_scores