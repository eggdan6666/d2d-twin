# 主审分组来源签审

已逐项登记六芯片129字段、903个维度；出处为本地原始厂商PDF。关键位图已另行渲染核对。状态/输出RO权限、复位读回与运行中不变分别记录；not used的TYPE标签与功能定义分别记录。

新增差异包括TMP100 OS极性和分辨率、TMP102动态OS/AL及EM格式、TMP1075动作前置条件/模式写清/unused策略、TMP126单寄存器无auto-increment读清及跨TEMP清DR/模式副作用、BMP280模式和XLSB文字、Bosch动态状态及写入commit。见findings.json和fields.json。

TMP1075 DIEID访问内部冲突及BME封面/正文版本差异保持未解决；不称官方勘误。无模型运行、无参考测试准入、无实物测量。下一步：在新输入候选与新harness兑现条件后重新冻结。
