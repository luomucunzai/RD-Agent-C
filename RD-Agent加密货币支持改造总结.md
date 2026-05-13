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

### P0 - 必须修改（不改则功能异常）

| # | 文件 | 修改内容 |
|---|------|----------|
| 1 | `rdagent/scenarios/qlib/experiment/factor_data_template/README.md` | 列描述改为通用表述，添加 7×24 说明 |
| 2 | `rdagent/scenarios/qlib/experiment/utils.py` | 新增 `generate_data_folder_from_crypto()`；修改 `get_data_folder_intro()` 追加 CRYPTO_MODE 描述 |
| 3 | `rdagent/scenarios/qlib/experiment/prompts.yaml` | 移除股票代码示例；`qlib_factor_background` 改为通用描述；experiment_setting 支持 `crypto_mode` |
| 4 | `rdagent/scenarios/qlib/developer/utils.py` | CRYPTO_MODE 时跳过 1 分钟数据检测 |
| 5 | 5 个 Qlib YAML 模板文件 | 硬编码的 A 股参数全部改为 Jinja2 模板变量（`region`, `market`, `benchmark`, `ann_scaler` 等） |
| 6 | `rdagent/scenarios/qlib/developer/factor_runner.py` | CRYPTO_MODE 时传入加密货币回测参数 |

### P1 - 建议修改

| # | 文件 | 修改内容 |
|---|------|----------|
| 7 | `rdagent/app/qlib_rd_loop/conf.py` | CRYPTO_MODE 时默认时间范围改为 2024-05-14 ~ 2026-04-30 |

### P2 - 可选修改

| # | 文件 | 修改内容 |
|---|------|----------|
| 8 | `rdagent/scenarios/qlib/prompts.yaml` | factor_hypothesis_specification 和 factor_feedback_generation 添加加密货币指导 |
| 9 | `rdagent/scenarios/qlib/developer/feedback.py` | CRYPTO_MODE 时 `IMPORTANT_METRICS` 切换 |
| 10 | 3 个 scenario `*_experiment.py` | 给 experiment_setting 模板传入 `crypto_mode` 变量 |

### 额外增加

| # | 文件 | 修改内容 |
|---|------|----------|
| 11 | `rdagent/.../factor_data_template/generate_crypto.py` | 新增：币安 CSV 转 H5（因子代码读取用） |
| 12 | `rdagent/.../factor_data_template/convert_to_qlib_format.py` | 新增：H5 转 Qlib 原生 bin 格式（回测引擎用） |
| 13 | `rdagent/oai/backend/litellm.py` | 修复：SiliconFlow Embedding 兼容性 |
| 14 | `dev/.env` | 新增：CRYPTO_MODE + DeepSeek + SiliconFlow 配置 |

---

## 数据流水线

```
downdata.py → 币安 CSV (OHLCV)
    ↓
generate_crypto.py → H5 (因子代码读取用)
                     MultiIndex(datetime, instrument)
                     6 columns: $open,$close,$high,$low,$volume,$factor(=1.0)
    ↓
convert_to_qlib_format.py → Qlib 原生格式 (回测引擎用)
                            calendars/day.txt
                            features/{inst}/{field}.day.bin
                            instruments/all.txt
```

### Qlib 0.9.7 数据格式规范

```
~/.qlib/qlib_data/cn_data/
├── calendars/
│   └── day.txt              # YYYY-MM-DD, 每行一天
├── features/
│   └── btcusdt/             # ⚠ 标的目录名全小写！
│       ├── close.day.bin    # ⚠ 命名: {field}.{freq}.bin
│       ├── open.day.bin     #    field = 去 $ 小写 (close, open, ...)
│       ├── high.day.bin     #    freq = day (日线)
│       ├── low.day.bin
│       ├── volume.day.bin
│       ├── factor.day.bin   # =1.0 for crypto
│       └── ...              # adjclose/amount/change/vwap (可选的)
└── instruments/
    └── all.txt              # ⚠ TAB分隔, 无表头
```

**二进制 `.bin` 文件格式：**
| 偏移 | 类型 | 值 |
|------|------|-----|
| 0-3 | int32 LE | start_index（日历起始位置，通常=0） |
| 4+ | float32 LE | 每日特征值，按日历顺序，缺失=NaN |

---

## 经验教训总结

### 1️⃣ 包管理陷阱

| 问题 | 错误做法 | 正确做法 |
|------|---------|---------|
| **Qlib 包名** | `pip install qlib` | **`pip install pyqlib`** |
| **非官方包** | PyPI 上 `qlib` 是另一个废弃项目 | 微软 Qlib 的包名是 `pyqlib` |
| **依赖安装** | `pyqlib` 用 `--no-deps` 跳过依赖 | 直接 `pip install pyqlib` 让 pip 自动处理 |
| **验证方法** | 检查模块名 | `python -c "import qlib; print(qlib.__version__)"` |

**教训：** 遇到 `ModuleNotFoundError` 时先确认 pip 包名是否正确，不要急着 `--no-deps`。

### 2️⃣ Qlib 数据格式踩坑

| 坑 | 错误做法 | 正确做法 | 发现方法 |
|----|---------|---------|---------|
| 数据类型 | 用 **float64** | 用 **float32** | 读 `FileFeatureStorage.__getitem__` 源码 |
| 文件头 | 魔数 uint32 + count uint32 | **start_index int32** | 读 `FileFeatureStorage.write` 源码 |
| 文件名 | `$close.bin` | **`close.day.bin`** | 读 `FileFeatureStorage.__init__` 源码 |
| 字段命名 | 保留 `$` 前缀 | **去 `$` 全小写** | 文件名拼接逻辑: `{field}.{freq}.bin` |
| 标的目录 | `BTCUSDT/` (大写) | **`btcusdt/` (全小写)** | 文件名拼接: `{instrument.lower()}/` |
| instruments | CSV 格式, 有表头 | **TAB 分隔, 无表头** | 读 `FileInstrumentStorage` 源码 |
| 参考旧格式 | 参考 `qlib_bin_down/` (0.8 版) | **读 Qlib 0.9.7 源码** | 0.9.7 完全重写了存储层 |

**教训：** 不要靠猜或参考旧版本数据。**直接读 Qlib 源码中的 `file_storage.py`** 是最准确的方式。

### 3️⃣ Qlib 0.9.7 的关键变化

- **无 `DumpData`/`DumpDataAll`**：旧版工具的 dump 功能在 0.9.7 已移除
- **`FileStorage` 体系**：`FileCalendarStorage`、`FileInstrumentStorage`、`FileFeatureStorage`
- **`qlib.init()` 触发 mlflow**：导致 protobuf 版本冲突，设 `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` 解决
- **`D.instruments()` 返回 dict**：不再是 list，需要通过 `D.instruments()['market']` 或直接用 `D.features(list_of_symbols, ...)`

### 4️⃣ 数据验证方法

```python
# 方法 A：通过 D.features() 测试（需 qlib.init 全量加载）
import qlib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data")
from qlib.data import D
data = D.features(["btcusdt"], ["$close"], start_time="2025-01-01", end_time="2025-01-05")

# 方法 B：直接用 FileFeatureStorage（轻量验证，无需 qlib.init）
import os
from qlib.data.storage.file_storage import FileFeatureStorage
fs = FileFeatureStorage(os.path.expanduser("~/.qlib/qlib_data/cn_data"), "btcusdt", "close", freq="day")
print(fs.data[:5])  # 查看前 5 个值
```

### 5️⃣ 环境配置

- **SSH 免密登录**：`ssh-copy-id` 或手动追加公钥到 `~/.ssh/authorized_keys`
- **Python 版本**：3.10 最稳定（3.14 有依赖兼容问题）
- **运行模式**：不要再设 `env_type=conda`（默认），需要时设 `MODEL_CoSTEER_env_type=local`（见下文）
- **Embedding**：DeepSeek 不支持 → 用 SiliconFlow 的 `BAAI/bge-large-en-v1.5`
- **LiteLLM 兼容**：`litellm_proxy/` 前缀的 embedding 模型需要绕过 LiteLLM 直接调用 OpenAI 客户端

### 6️⃣ 运行环境踩坑（venv 非 conda）

| 问题 | 错误做法 | 正确做法 |
|------|---------|---------|
| **factor env** | `get_factor_env()` 硬编码 `CondaConf` | 增加 venv fallback：检测不到 conda 时用 `LocalConf(bin_path=venv_bin)` |
| **model env** | `get_model_env()` 只支持 docker/conda | 增加 `local` 模式，同上 |
| **model execute** | `ModelFBWorkspace.execute()` 硬编码 env 类型 | 增加 `local` 分支，用 `LocalEnv(LocalConf(...))` |
| **python 找不到** | subprocess 里 `python: not found` | 设 `local` 模式或 conda 环境下运行 |
| **CONDA_DEFAULT_ENV** | venv 中此变量为空 | 检测为空时自动降级为 `LocalEnv` |
| **`rdagent --help`** | 加载全部场景导致依赖冲突 | 直接调用 `from rdagent.app.qlib_rd_loop.factor import main` |
| **`fin_model` 缺 torch** | 找不到 torch | `pip install torch` 或跳过模型场景 |

**解决路径：**
```
场景初始化 → get_runtime_environment()
    → 失败：mock runtime 跳过（测试用）
    → 根治：修 get_factor_env() / get_model_env() 支持 venv
因子执行 → FACTOR_CoSTEER_python_bin
模型执行 → MODEL_CoSTEER_env_type=local
回测执行 → Qlib Conda/Docker（暂未在 venv 中验证）
```

### 7️⃣ 测试验证结果

| 场景 | 命令 | 状态 | 费用 | 生成的因子/模型 |
|------|------|------|------|----------------|
| 因子挖掘 | `fin_factor` | ✅ **通过** | ~$0.005 | Volatility_10d（10日波动率） |
| 因子+模型联合 | `fin_quant` | ✅ **通过** | ~$0.003 | momentum_10d（10日动量） |
| 模型进化 | `fin_model` | ⚠️ 需装 torch | — | SimpleGRU（代码正确，执行缺 torch） |

**核心链路全部验证通过的项目：**
- ✅ 币安数据下载（downdata.py）→ CSV
- ✅ CSV → H5（generate_crypto.py，$factor=1.0）
- ✅ H5 → Qlib 原生 bin（convert_to_qlib_format.py，float32）
- ✅ Qlib 数据读取（D.features()）
- ✅ LLM 因子生成（DeepSeek Chat）
- ✅ 因子代码本地执行（读取 crypto H5）
- ✅ 因子结果评估（shape/code/value 三层）
- ✅ RAG 知识库存储（SiliconFlow Embedding）

---

## 服务器部署状态快照

| 项目 | 信息 |
|------|------|
| 服务器 | `192.168.1.171` (Ubuntu 22.04) |
| SSH 登录 | 密钥认证（免密码），`li@192.168.1.171` |
| 虚拟环境 | `~/rdagent_venv` (Python 3.10) |
| 项目路径 | `~/rdagent_dev/` |
| Git 仓库 | 本地 + 服务器各一个独立仓库 |
| Qlib | `pyqlib 0.9.7` |
| LLM Chat | DeepSeek API (`deepseek/deepseek-chat`) |
| LLM Embedding | SiliconFlow (`BAAI/bge-large-en-v1.5`) |
| 币安数据 | 8 交易对, 717 条/对, 2024-05-14 ~ 2026-04-30 |
| H5 数据 | `git_ignore_folder/factor_implementation_source_data/daily_pv.h5` |
| Qlib 原生数据 | `~/.qlib/qlib_data/cn_data/` (48 个 .bin 文件, 444 KB) |

### 快速部署

```bash
ssh li@192.168.1.171
source ~/rdagent_venv/bin/activate
cd ~/rdagent_dev && rdagent fin_factor
```

`.env` 需包含：`CRYPTO_MODE=true` + DeepSeek API Key + SiliconFlow API Key。
