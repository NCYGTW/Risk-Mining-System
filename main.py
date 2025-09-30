#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
无监督风险模型挖掘系统主入口
功能：整合各模块，提供完整的风险挖掘流程
"""

import os
import sys
import logging
from pathlib import Path

# 设置日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("riskmining.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RiskMiningSystem')

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from data_layer.data_processor import DataProcessor
from model_layer.anomaly_detector import AnomalyDetector
from rule_synthesis.rule_generator import RuleGenerator
from rule_compile.rule_compiler import RuleCompiler
from autoeval.evaluator import RuleEvaluator
from utils.config_manager import ConfigManager

class RiskMiningSystem:
    """无监督风险模型挖掘系统主类"""
    
    def __init__(self, config_path=None):
        """初始化系统"""
        logger.info("启动无监督风险模型挖掘系统")
        
        # 加载配置
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # 初始化各层模块
        self.data_processor = DataProcessor(self.config)
        self.anomaly_detector = AnomalyDetector(self.config)
        self.rule_generator = RuleGenerator(self.config)
        self.rule_compiler = RuleCompiler(self.config)
        self.rule_evaluator = RuleEvaluator(self.config)
        
        logger.info("系统初始化完成")
    
    def run_pipeline(self):
        """运行完整的风险挖掘流程"""
        logger.info("开始运行风险挖掘流程")
        
        try:
            # 1. 数据处理与特征提取
            logger.info("阶段1: 数据处理与特征提取")
            data, stats_summary = self.data_processor.process_data()
            
            # 2. 异常检测
            logger.info("阶段2: 异常检测")
            anomaly_scores = self.anomaly_detector.detect_anomalies(data)
            
            # 3. 规则生成
            logger.info("阶段3: 规则生成")
            rules = self.rule_generator.generate_rules(
                risk_points=self.config['risk_points'],
                variable_catalog=self.config['variable_catalog'],
                industry_scope=self.config['industry_scope'],
                stats_summary=stats_summary,
                target_coverage=self.config['target_coverage']
            )
            
            # 4. 规则编译与校验
            logger.info("阶段4: 规则编译与校验")
            compiled_rules = []
            for rule in rules:
                if self.rule_compiler.validate_rule(rule):
                    compiled_rule = self.rule_compiler.compile_rule(rule)
                    compiled_rules.append(compiled_rule)
            
            # 5. 规则评估与选择
            logger.info("阶段5: 规则评估与选择")
            selected_rules = self.rule_evaluator.evaluate_and_select_rules(
                compiled_rules, data, anomaly_scores
            )
            
            # 6. 保存结果
            logger.info("阶段6: 保存结果")
            self._save_results(selected_rules)
            
            logger.info("风险挖掘流程完成")
            return selected_rules
            
        except Exception as e:
            logger.error(f"流程运行失败: {str(e)}")
            raise
    
    def _save_results(self, selected_rules):
        """保存选择的规则到知识库"""
        # 实现规则保存逻辑
        output_path = self.config.get('output_path', 'output/rules')
        os.makedirs(output_path, exist_ok=True)
        
        import json
        with open(os.path.join(output_path, 'selected_rules.json'), 'w', encoding='utf-8') as f:
            json.dump(selected_rules, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存{len(selected_rules)}条规则到{output_path}")

if __name__ == "__main__":
    """主入口"""
    try:
        # 创建系统实例
        system = RiskMiningSystem()
        
        # 运行完整流程
        selected_rules = system.run_pipeline()
        
        # 输出结果摘要
        print(f"\n=== 风险挖掘系统运行完成 ===")
        print(f"成功生成并选择了 {len(selected_rules)} 条风险规则")
        
    except Exception as e:
        print(f"系统运行失败: {str(e)}")
        sys.exit(1)