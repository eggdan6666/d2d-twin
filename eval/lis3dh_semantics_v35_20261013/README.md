# LIS3DH v3.5 有界语义验证

从项目根目录运行 `python _setup/run_lis3dh_v35.py` 生成实际见证与有界闭包；`python _setup/package_lis3dh_v35.py` 验收专家契约、复跑独立测试并更新本轮状态；`python _setup/archive_lis3dh_v35.py` 校验签审字节与档案清单。已有 Python、pytest 和本地手册足够，无需 SCNet、API 或硬件。

主接口为 `Semantics(profile='common_source')`、`write(reg,byte)`、`read(reg)`、`read_masked(reg,mask)`，事件 `qualified_sample_completed(x_word=uint16,y_word=uint16,z_word=uint16,overwritten=bool)` 和 `power_on_completed`。这些是已资格化的同步XYZ数字样本及已稳定的冷启动边界；不执行实际加速度测量、上电或ODR计时。主样本范围为全轴开启、ST0、BDU0、FIFO/滤波旁路、合法模式，overwrite由调用方明确资格化。

STATUS 默认已知掩码是 `0xFE`。XDA 位的描述缺失，不得整字节读为零；输出数据在新样本前未知。发生样本后，第一次 STATUS 或输出读取会使主范围的后续 STATUS 数值未知，因为原手册没有给出读后的清除/保留规则。mask 是观察限制，不是物理按位读取。OutsideContract 表示基准范围限制，不是芯片统一的错误响应。

`read_consumption_candidate` 使用 `sample_completed(x_word,y_word,z_word)`，明确假设每轴读取低/高两半后消费样本、清ready/overrun，组状态取ANY。这些是假设策略，不能作为厂商保证。BDU1首样本/等全部轴读取后接受下一次到达也只在候选分支中验证，不缓存或推测被拒绝的中间样本。XDA在候选分支仍未被认证。

ST00/01/10只验证合法寄存器存储；ST11无普通存储断言。非零ST的物理自检幅度、符号和2/8样本稳定时间未实现。原IR、冻结测试和历史成绩保持原样。

producer重复运行会重写耗时记录。已签审后若重跑，应依次运行 `tests/record_independent_execution.py` 和 `tests/package_code_review.py` 重新绑定输入输出，再 package/archive。
