# HD-Agent 第二阶段本地环境部署报告

日期：2026-10-03 ｜ 机器：RTX 3050 Ti Laptop 4GB ｜ Ollama v0.35.1

## 六步状态表

| 步骤 | 内容 | 状态 | 关键数据 |
|---|---|---|---|
| 1 | 安装包校验 | ✅ | `_setup/OllamaSetup.exe` 存在，1,580,352,416 字节，与目标完全一致（下载于前次会话，本次无需重下） |
| 2 | 静默安装 + 服务 | ✅ | `%LOCALAPPDATA%\Programs\Ollama\ollama.exe` 就位；安装约1分钟完成；API `/api/version` 返回 0.35.1；ollama app 开机常驻，无需手动 serve |
| 3 | 拉取模型 | ✅ | `qwen2.5:3b-instruct` 1.9GB（约4分钟，峰值 9MB/s）；`qwen2.5:7b-instruct-q4_K_M` 4.7GB（约8分钟）；均一次成功，无重试 |
| 4 | 推理冒烟测试 | ✅ | 见下表 |
| 5 | Embedding | ✅ | `BAAI/bge-small-zh-v1.5` 命中本地缓存，`encode(['测试'])` → shape **(1, 512)**，加载+推理共 8.0s（CPU torch 2.14.1+cpu，sentence-transformers 6.1.0） |
| 6 | LongMemEval-S | ✅ | `data/eval/longmemeval_s.json` 278MB，验证为合法 JSON：**500 条**样本，字段 question_id / question_type / question / answer / question_date / haystack_dates / haystack_session_ids / haystack_sessions / answer_session_ids |

## 步骤4 冒烟测试明细

问题：`What is the absolute maximum input voltage of LM2596? keep answer under 20 words`

| 模型 | 首答耗时 | 冷启动 eval rate | 热态 eval rate | prompt eval | 加载方式 | 显存 | 答案正误 |
|---|---|---|---|---|---|---|---|
| qwen2.5:3b-instruct | 59.4s（含27.4s引擎冷初始化） | 1.52 tok/s | **57.51 tok/s** | 热态 4.13→缓存命中50/51 | **100% GPU** | 3002/4096 MiB | ❌ 答 37V |
| qwen2.5:7b-instruct-q4_K_M | 7.5s（load 仅5.9s） | **15.18 tok/s** | — | 102.21 tok/s | **55% CPU / 45% GPU 分层** | 3131/4096 MiB | ✅ 答 40V |

结论：
- 3b 首次 1.52 tok/s 是引擎冷启动+与 7b 拉取并发所致的一次性开销；热态 57.5 tok/s 完全满足主力问答。
- 7b-q4 在 4GB 显存上自动 CPU/GPU 分层（权重 5.1GB > 4GB），15 tok/s 可用于复核轨，冷启动仅需 ~7.5s。
- 两模型同时驻留显存不可行（3002+3131>4096），混合推理需轮换加载；`OLLAMA_KEEP_ALIVE` 建议设 2~5 分钟平衡切换开销。
- 冒烟中 3b 答错（37V）、7b 答对（40V），恰好印证"3b 主力 + 7b 复核"双轨设计的必要性。

## 步骤5 缓存路径

模型本地缓存：`C:\Users\ZhuanZ\.cache\huggingface\hub\models--BAAI--bge-small-zh-v1.5`（离线可用，无需 HF_ENDPOINT；设置后仅作更新兜底）。

## 步骤6 数据来源备注

GitHub 仓库实际作者为 **xiaowu0162**（非任务书写的 xiaoxi1027，且其 GitHub 仓库 data/ 已不含大文件）。
实际下载源（HuggingFace hf-mirror，LFS 裸文件、无扩展名）：
`https://hf-mirror.com/datasets/xiaowu0162/longmemeval/resolve/main/longmemeval_s`
备用：入口 `https://hf-mirror.com/api/datasets/xiaowu0162/longmemeval/tree/main`（同数据集另有 longmemeval_oracle 15MB、longmemeval_m 2.7GB）。jsDelivr 路径 `xiaoxi1027/LongMemEval@main/data/longmemeval_s.json` 已失效。

## 遗留问题清单

1. corpus/ 与 rag/ 代码未做任何改动（符合要求）；rag/embed.py 接 Ollama 向量后端（`RAG_EMBED_MODEL`）尚未联调。
2. 3b 冒烟答案错误（37V）：为无检索上下文的裸模型记忆问答，属预期；接入 BM25+向量检索后需重测。
3. bge 模型当前在 CPU 上运行（torch 为 cpu 版）；语料 456 篇全量重建索引若耗时过长，可考虑装 CUDA 版 torch。
4. 显存不足以双模型常驻，编排层需处理 3b↔7b 换入换出延迟（冷启动 3b 约 27s / 7b 约 6s）。
5. 临时文件 `_setup/smoke_3b.txt`、`_setup/smoke_7b_cold.txt` 为测试原始输出，可留作凭证或删除。
