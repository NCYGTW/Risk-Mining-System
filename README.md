# RiskminingSystem

## 无监督风险模型挖掘系统

RiskminingSystem 是一个基于无监督学习的风险挖掘系统，旨在从年报等财务数据中自动识别异常公司并生成可解释的风险规则。系统采用多层架构设计，整合数据预处理、异常检测、规则生成、规则编译与评估等模块。

## 架构概览

系统采用分层架构模式，主要包含以下组件：

- **`main.py`**: 系统主入口，包含 `RiskMiningSystem` 主类，负责协调各模块执行完整的风险挖掘流程
- **`data_layer/data_processor.py`**: 数据层，包含 `DataProcessor` 类，负责数据预处理、特征提取和统计摘要生成
- **`model_layer/anomaly_detector.py`**: 模型层，包含 `AnomalyDetector` 类，集成了多种无监督异常检测算法（Isolation Forest、Local Outlier Factor、One-Class SVM）
- **`rule_synthesis/rule_generator.py`**: 规则合成层，包含 `RuleGenerator` 类，负责基于异常检测结果生成风险规则（待实现）
- **`rule_compile/rule_compiler.py`**: 规则编译层，包含 `RuleCompiler` 类，负责规则校验与编译（待实现）
- **`autoeval/evaluator.py`**: 自动评估层，包含 `RuleEvaluator` 类，负责规则质量评估与选择
- **`utils/config_manager.py`**: 工具层，配置管理器（待实现）
- **`RiskAnalysisSystem/`**: 风险分析子系统，包含多个智能体（Agent）

## 核心组件

### 数据处理器 (`DataProcessor`)
- `process_data()`: 数据处理主函数，返回处理后的数据和统计摘要
- `_clean_data()`: 数据清洗功能，处理缺失值
- `_extract_features()`: 特征提取，计算财务指标差异、经营效率特征、异常波动性特征等
- `_calculate_statistics()`: 计算整体和分行业的统计量

### 异常检测器 (`AnomalyDetector`)
- `detect_anomalies()`: 异常检测主函数，返回公司名称到异常分数的映射
- 集成算法：
  - Isolation Forest (`isolation_forest`)
  - Local Outlier Factor (`lof`)
  - One-Class SVM (`one_class_svm`)

### 规则评估器 (`RuleEvaluator`)
- `evaluate_and_select_rules()`: 评估并选择规则的主函数
- `_calculate_rule_metrics()`: 计算规则评估指标
- 评估指标：
  - 覆盖率 (`coverage`)
  - 异常分数提升 (`anomaly_lift`)
  - 稳定性 (`stability`)
  - 特异性 (`specificity`)
  - 行业一致性 (`consistency`)

## 工作流程

1. **数据处理阶段**: `RiskMiningSystem.run_pipeline()` 调用 `DataProcessor.process_data()` 进行数据预处理与特征提取
2. **异常检测阶段**: 调用 `AnomalyDetector.detect_anomalies()` 识别异常公司
3. **规则生成阶段**: 调用 `RuleGenerator.generate_rules()` 基于风险点和变量目录生成规则
4. **规则编译阶段**: 通过 `RuleCompiler.validate_rule()` 和 `compile_rule()` 验证和编译规则
5. **规则评估阶段**: 使用 `RuleEvaluator.evaluate_and_select_rules()` 评估规则质量并选择最优规则集
6. **结果保存**: 保存选择的规则到 `output/rules/selected_rules.json`

## 依赖项

- `pandas>=1.5.0` - 数据操作
- `numpy>=1.23.0` - 数值计算
- `scikit-learn>=1.2.0` - 机器学习算法
- `openai>=1.0.0` - LLM 接口
- `matplotlib>=3.7.0` - 可视化
- `seaborn>=0.12.0` - 统计可视化

## 使用方法

```bash
python main.py
```

## 配置参数

系统支持以下主要配置参数（通过 `ConfigManager` 管理）：
- `data_path`: 输入数据路径
- `contamination`: 异常比例参数
- `if_n_estimators`: Isolation Forest 的估计器数量
- `lof_n_neighbors`: LOF 的邻居数量
- `top_n_rules`: 选择的规则数量
- `min_coverage` / `max_coverage`: 规则覆盖率范围

## 风险分析子系统

`RiskAnalysisSystem/` 目录包含基于多智能体的分析系统：
- `RiskFormulaParserAgent`: 风险公式解析智能体
- `DataValidationAgent`: 数据验证智能体
- `ReportGenerationAgent`: 报告生成智能体
- `ForumEngine`: 论坛引擎监控器

## 待完成模块

- `rule_generator.py`: 规则生成模块
- `rule_compiler.py`: 规则编译模块
- `config_manager.py`: 配置管理模块

## 评估指标

系统实现了多维度规则评估框架，包含：
- **覆盖率 (Coverage)**: 规则命中的公司比例
- **异常提升度 (Anomaly Lift)**: 命中公司的平均异常分数与总体平均异常分数的比率
- **稳定性 (Stability)**: 规则在时间维度上的稳定性
- **特异性 (Specificity)**: 规则与其他规则的区分度
- **行业一致性 (Industry Consistency)**: 规则在不同行业中的表现一致性

## 输出格式

最终输出保存为 JSON 格式，包含选择的规则及其相关指标：
```json
{
  "id": "rule_id",
  "execute_function": "lambda function",
  "metrics": {
    "coverage": 0.05,
    "anomaly_lift": 2.3,
    "stability": 0.8,
    "specificity": 0.7,
    "consistency": 0.6
  },
  "overall_score": 0.75
}
```

## 许可证

[待添加]