# SCNet 批处理迁移：待环境证据

操作任务 ID：D2D-HPC-RECOVERY-20261012。

已知：Qwen-3B 与 DeepSeek-6.7B 各 240 个样本已拉回本地。Qwen-14B 最后确认完成 6/20；Notebook SSH 当前无响应。14B 的真实完成数量仍未知，不能按 6/20 直接重跑。

下一步：先运行 `scnet_batch_preflight.sh` 的只读诊断，返回作业日志。此脚本不下载模型、不启动推理、不修改旧评测结果。HPC 上 `/public/home/lct3086708928` 与 Notebook 中 `/root/private_data` 的映射尚需核实；原容器的 `/opt/conda` 不保证在 HPC 作业环境存在。

诊断返回后：先下载全部旧 Qwen-14B JSON，检查每颗是否包含 seed 1、2、3 各 4 个样本以及完整结果字段；冻结完整结果。若存在半颗结果，保存为不可变历史分片。现有 gen_code.py 不支持按样本断点续跑，不能用文件大小判断完成，更不能直接覆盖半颗 JSON。为缺失样本续跑时需保持每个 seed 的原生成顺序和 RNG 消耗，并核验提示词、IR、harness、模型以及运行环境；环境变更必须记录在新 manifest，不能默认认为与 Notebook 同环境。

## 可复制操作陪伴提示词

请协助 D2D-Twin 的操作任务 D2D-HPC-RECOVERY-20261012。Notebook 免费额度已用完，用户只能使用 SCNet HPC 作业。请每次只指导一个步骤。第一步运行提供的 scnet_batch_preflight.sh 只读诊断，界面不同则依据截图调整。不要索取密码、验证码、私钥或 token。不要下载大模型，不要覆盖现有 JSON，不要把调度完成当成实验成功。收集 stdout、stderr、作业 ID、数据目录、Python/容器/module 信息；确认返回日志真实存在后提供返回卡。

## 操作返回卡

- 操作任务 ID：D2D-HPC-RECOVERY-20261012
- 作业 ID：待提供
- 运行状态：待提供
- stdout/stderr：待提供
- d2d 与 models 目录：待核验
- Python/容器/模块：待核验
- Qwen-14B 结果文件：待核验
- 是否启动推理：否（此步骤只读）
