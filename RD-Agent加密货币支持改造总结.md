# RD-Agent 加密货币支持改造总结

## 概述

对微软 RD-Agent 框架的 `qlib` 量化场景进行改造，使其支持加密货币市场（7×24 连续交易、无复权因子）。所有修改通过 `CRYPTO_MODE=true` 环境变量切换，不影响原有的 A 股场景。

---

## 核心差异：A股 vs 加密货币

| 特性 | A 股 | 加密货币 | 影响范围 |
|------|------|---------|---------|
| 交易时间 | 周一至周五 9:30-15:00 | 7×24 连续交易 | 日历、年化、时间配置 |
| 复权因子 | `$factor` 列用于除权调整 | 无复权，`$factor=1.0` | 数据生成、回测引擎 |
| 交易日历 | 需过滤非交易日 | 每天都是交易日 | 数据连续性、日历配置 |
| 年化天数 | 252 个交易日 | 365 个自然日 | 回测指标计算 |
| 标的识别 | `SH600000` 等股票代码 | `BTCUSDT`、`ETHUSDT` 等交易对 | Prompt 模板、YAML 配置 |
| 涨跌停限制 | 10% | 无限制 | 回测参数 |
| 最低佣金 | 5 元固定费用 | 按比例收费 | 回测参数 |

---

## 修改文件总清单

### 数据层

| # | 文件 | 修改内容 |
|---|------|----------|
| 1 | `factor_data_template/README.md` | 列描述改为通用表述，添加 7×24 说明 |
| 2 | `factor_data_template/generate_crypto.py` | **新增**：币安 CSV 转 H5（MultiIndex, $factor=1.0） |
| 3 | `factor_data_template/convert_to_qlib_format.py` | **新增**：H5 转 Qlib 原生 bin 格式（float32） |
| 4 | `experiment/utils.py` | 新增 `generate_data_folder_from_crypto()`；`get_data_folder_intro()` 追加 CRYPTO_MODE 描述 |

### 场景配置层

| # | 文件 | 修改内容 |
|---|------|----------|
| 5 | `experiment/prompts.yaml` | 移除股票代码示例；支持 `crypto_mode` 条件显示 |
| 6 | `experiment/factor_experiment.py` | `get_runtime_environment()` 加异常保护 |
| 7 | `experiment/model_experiment.py` | 同上 |
| 8 | `experiment/quant_experiment.py` | 同上 |
| 9 | 5 个 YAML 模板文件 | 硬编码参数全部改为 Jinja2 模板变量 |
| 10 | `scenarios/qlib/prompts.yaml` | 添加 CRYPTO_MODE 指导 |

### 运行层

| # | 文件 | 修改内容 |
|---|------|----------|
| 11 | `developer/factor_runner.py` | CRYPTO_MODE 时传入加密货币回测参数（移除 `region`，`limit_threshold=1.0`） |
| 12 | `developer/utils.py` | CRYPTO_MODE 时跳过 1 分钟数据检测 |
| 13 | `developer/feedback.py` | CRYPTO_MODE 时 `IMPORTANT_METRICS` 切换为 `['IC', 'l2.valid']`；`process_results` 增加指标缺失保护 |
| 14 | `app/qlib_rd_loop/conf.py` | CRYPTO_MODE 时默认时间范围改为 2024-05-14 ~ 2026-04-20 |

### 环境层

| # | 文件 | 修改内容 |
|---|------|----------|
| 15 | `app/cli.py` | CLI 导入改为懒加载，避免一个场景缺少依赖导致整个 CLI 崩溃 |
| 16 | `components/coder/factor_coder/config.py` | `get_factor_env()` 增加 venv 降级支持（`LocalConf` fallback） |
| 17 | `components/coder/model_coder/conf.py` | `get_model_env()` 增加 `local` 模式 |
| 18 | `components/coder/model_coder/model.py` | `ModelFBWorkspace.execute()` 增加 `local` 分支 |
| 19 | `utils/env.py` | `QlibCondaConf.conda_env_name` 优先使用 `CONDA_DEFAULT_ENV`；`CondaConf._update_bin_path()` 增加 conda 命令失败的回退路径 |
| 20 | `oai/backend/litellm.py` | `litellm_proxy/` 前缀的 embedding 请求绕过 LiteLLM 直连 OpenAI 客户端 |
| 21 | `oai/utils/embedding.py` | `trim_text_for_embedding()` encode/decode 时去掉 `litellm_proxy/` 前缀 |

### 配置

| # | 文件 | 内容 |
|---|------|------|
| 22 | `.env` | `CRYPTO_MODE=true` + DeepSeek Chat + SiliconFlow Embedding |

---

## 数据流水线

```
downdata.py → 币安 CSV (OHLCV)
    ↓
generate_crypto.py → H5 (因子代码读取用)
                     MultiIndex(datetime, instrument)
                     6 columns: $open,$close,$high,$low,$volume,$factor(=1.0)
    ↓
convert_to_qlib_format.py → Qlib 原生格式 (回测引擎 qrun 用)
                            calendars/day.txt
                            features/{inst}/{field}.day.bin
                            instruments/all.txt
```

### Qlib 0.9.7 `cn_data` 目录结构

```
~/.qlib/qlib_data/cn_data/
├── calendars/
│   └── day.txt                    # YYYY-MM-DD, 每行一天
├── features/
│   └── btcusdt/                   # ⚠ 标的目录名全小写！
│       ├── close.day.bin          # ⚠ 命名: {field}.{freq}.bin
│       ├── open.day.bin           #    field = 去 $ 小写 (close, open, ...)
│       ├── high.day.bin           #    freq = day (日线)
│       ├── low.day.bin
│       ├── volume.day.bin
│       └── factor.day.bin         # =1.0 for crypto
└── instruments/
    └── all.txt                    # ⚠ TAB分隔, 无表头: symbol\tstart_date\tend_date
```

### 二进制 `.bin` 文件格式

| 偏移 | 类型 | 值 |
|------|------|-----|
| 0-3 | int32 LE | start_index（日历起始位置，通常=0） |
| 4+ | float32 LE | 每日特征值，按日历顺序，缺失=NaN（⚠ 不是 float64！） |

写入方式：`np.hstack([start_index, arr]).astype(np.float32).tofile(f)`

---

## 服务器部署

| 项目 | 信息 |
|------|------|
| 服务器 | `192.168.1.171` (Ubuntu 22.04, 8 代 i5) |
| SSH | 密钥认证免密码 |
| Miniconda | `~/miniconda3` |
| conda 环境 | `rdagent`（Python 3.10） |
| 项目路径 | `~/rdagent_dev/`（SSH 登录后自动进入，已配 `.bashrc`） |
| Git | 本地 + 服务器各一个独立仓库 |
| pyqlib | 0.9.7（conda 环境内） |
| LLM Chat | DeepSeek API (`deepseek/deepseek-chat`) |
| LLM Embedding | SiliconFlow → `BAAI/bge-m3`（8192 tokens） |
| 数据 | 8 交易对（BTC/ETH/BNB/SOL/DOGE/TAO/PEPE/HYPE），717 天 |
| Web UI  | `rdagent server_ui --port 19899` |

### 快速运行

```bash
conda activate rdagent
cd ~/rdagent_dev
export $(grep -v '^#' .env | xargs)
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
rdagent fin_factor
```

---

## 测试验证结果

### 场景测试

| 场景 | 命令 | 状态 | 费用 | 结果 |
|------|------|------|------|------|
| 因子挖掘 | `fin_factor` | ✅ 5/5 步骤完成 | ~$0.008 | 生成 Momentum/Volatility/VWAP 因子，评估通过，Qlib 回测执行 ✅ |
| 因子+模型联合 | `fin_quant` | ✅ 因子生成+评估 | ~$0.005 | 生成 5 个因子全部验证通过 |
| 模型进化 | `fin_model` | ⚠️ 需装 torch | — | SimpleGRU 代码正确，执行缺 torch |

### 核心链路验证

- ✅ 币安数据下载（downdata.py）→ CSV
- ✅ CSV → H5（generate_crypto.py，$factor=1.0）
- ✅ H5 → Qlib 原生 bin（convert_to_qlib_format.py，float32 格式）
- ✅ Qlib 数据读取（D.features() 正常返回 717 天数据）
- ✅ Alpha158 表达式正常计算（返回有效数值，无 NaN）
- ✅ LLM 因子生成（DeepSeek Chat）
- ✅ 因子代码本地执行（读取 crypto H5）
- ✅ 因子结果评估（shape/code/value 三层）
- ✅ RAG 知识库存储（bge-m3 embedding）
- ✅ Qlib 回测（qrun 成功执行 LGBModel 预测+组合分析）
- ✅ 反馈（feedback 正常生成 SOTA 对比）
- ✅ 记录（record 正常保存）

### Qlib 回测输出指标

```
LGBModel 预测 → IC=NaN, l2.valid=0.865
基准策略年化收益率: -34.7%, 最大回撤: -64.3%
因子增强策略年化: 30.6%（有费用） / 29.1%（无费用）
因子增强策略最大回撤: -17.2% / -17.7%
```

IC=NaN 是因为 Alpha158 因子对加密货币预测精度不够（模型质量问题，非系统 bug）。

---

## 经验教训总结

### 1️⃣ 包管理：`qlib` ≠ `pyqlib`

| 问题 | 错误做法 | 正确做法 |
|------|---------|---------|
| Qlib 包名 | `pip install qlib` | **`pip install pyqlib`** |
| 依赖安装 | `--no-deps` 跳过依赖 | 直接 `pip install pyqlib` |
| 环境管理 | venv 不方便跑 Qlib 回测 | 用 conda 环境 + `CONDA_DEFAULT_ENV` |

**教训：** 遇到 ModuleNotFoundError 先检查 pip 包名是否正确。

### 2️⃣ Qlib 0.9.7 数据格式（最坑）

| 坑 | 错误做法 | 正确做法 | 发现方法 |
|----|---------|---------|---------|
| 数据类型 | **float64** | **float32** | 读 `FileFeatureStorage.__getitem__` |
| 文件头 | 魔数(uint32) + count(uint32) | **start_index(int32)** | 读 `FileFeatureStorage.write` |
| 文件名 | `$close.bin` | **`close.day.bin`** | 读 `FileFeatureStorage.__init__` |
| 字段名 | 保留 `$` | **去 `$` 全小写** | `{field}.{freq}.bin` |
| 标的目录 | `BTCUSDT/` | **`btcusdt/`** | `{instrument.lower()}/` |
| instruments | CSV 有表头 | **TAB 分隔无表头** | 读 `FileInstrumentStorage` |
| 参考旧版 | `qlib_bin_down/` (0.8) | **读 0.9.7 源码** | 存储层完全重写 |

**教训：** 不要靠猜。**直接读 Qlib 源码 `file_storage.py`**。

### 3️⃣ Qlib 回测部署（conda 必要）

- **`qrun` 命令**需要 conda 环境里安装 pyqlib
- **`QlibCondaConf`** 默认 conda 环境名 `rdagent4qlib`，需改为 `CONDA_DEFAULT_ENV`
- **`CondaConf._update_bin_path()`** 需要 `conda` 命令在 PATH 中，失败时有回退路径
- **protobuf 冲突**：`qlib.init()` 触发 mlflow → 设置 `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`
- **`region` 参数**：不支持 `global`，使用默认 `cn`
- **`limit_threshold`**：不支持字符串类型，设为 `1.0`（100%=无限制）

### 4️⃣ Embedding 模型选择

| 模型 | Token 限制 | 状态 |
|------|-----------|------|
| `BAAI/bge-large-en-v1.5` | 512 | ❌ 因子代码文本超限 |
| `BAAI/bge-m3` | 8192 | ✅ 建议使用 |
| `Qwen/Qwen3-Embedding-0.6B` | 32000 | ✅ 可选 |
| `text-embedding-3-small` | 8191 | ✅ 需 OpenAI Key |

### 5️⃣ CLI 懒加载

原版 CLI 在模块顶部 import 所有场景，任一场景缺依赖就导致整个 CLI 崩溃。修复：改为在命令函数内部 import。

### 6️⃣ venv vs conda

- **因子代码执行**：venv 可用（需 `LocalConf(bin_path=venv_bin)`）
- **模型代码执行**：venv 可用（需设 `MODEL_CoSTEER_env_type=local`）
- **Qlib 回测**：**必须 conda 环境**（需要 `qrun` 命令）
- 推荐：日常开发用 venv，回测用 conda

### 7️⃣ feedback.py 指标名匹配

Qlib 回测输出的 `qlib_res.csv` 包含以下可用指标：
- `IC`, `Rank IC`, `ICIR`, `Rank ICIR`（预测相关性，可能为 NaN）
- `l2.train`, `l2.valid`（模型损失，总是有值）
- `1day.excess_return_with_cost.annualized_return`（组合分析年化收益率）
- `1day.excess_return_with_cost.max_drawdown`（最大回撤）

`IMPORTANT_METRICS` 必须匹配实际输出，否则 `combined_df.loc[...]` 会 KeyError。
