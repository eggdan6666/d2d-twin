# -*- coding: utf-8 -*-
"""Datasheet 下载清单：每条记录含候选 URL 列表，按顺序尝试。
来源均为厂商官网公开 Datasheet（计划书 4.2 / 5.2 节）。"""

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# ---------------- 厂商 URL 模板 ----------------
TI = lambda p, cat: {
    "part": p, "manufacturer": "TI", "category": cat,
    "urls": [f"https://www.ti.com/lit/ds/symlink/{p.lower()}.pdf",
             f"https://www.ti.com/lit/gpn/{p.upper()}"]}

ST = lambda p, cat: {
    "part": p, "manufacturer": "ST", "category": cat,
    "urls": [f"https://www.st.com/resource/en/datasheet/{p.lower()}.pdf"]}

ONS = lambda p, cat: {
    "part": p, "manufacturer": "onsemi", "category": cat,
    "urls": [f"https://www.onsemi.com/download/data-sheet/pdf/{p.lower()}-d.pdf",
             f"https://www.onsemi.com/pdf/datasheet/{p.lower()}-d.pdf"]}

NXP = lambda p, cat: {
    "part": p, "manufacturer": "NXP", "category": cat,
    "urls": [f"https://www.nxp.com/docs/en/data-sheet/{p.lower()}.pdf"]}

ADI = lambda p, cat: {
    "part": p, "manufacturer": "ADI", "category": cat,
    "urls": [f"https://www.analog.com/media/en/technical-documentation/data-sheets/{p.lower()}.pdf"]}

ESP = lambda p, f, cat: {
    "part": p, "manufacturer": "Espressif", "category": cat,
    "urls": [f"https://www.espressif.com/sites/default/files/documentation/{f}_datasheet_en.pdf"]}

MPS = lambda p, cat: {
    "part": p, "manufacturer": "MPS", "category": cat,
    "urls": [f"https://ae-mpsai-storage.oss-cn-shenzhen.aliyuncs.com/media/{p.lower()}.pdf",
             f"https://www.monolithicpower.com/en/documentview/productdocument/index/version/2/type/datasheet/lang/en/sku/{p}/"]}

PI = lambda p, f, cat: {
    "part": p, "manufacturer": "PowerIntegrations", "category": cat,
    "urls": [f"https://www.power.com/sites/default/files/documents/{f}.pdf",
             f"https://www.power.com/sites/default/files/documents/{p.lower()}.pdf"]}

ENTRIES = []

# ============ 1. 反激/AC-DC 电源（负责人实际项目方向，优先级最高） ============
FLYBACK = "flyback_power"
ENTRIES += [
    TI(p, FLYBACK) for p in [
        "UCC28740", "UCC28742", "UCC28780", "UCC28782", "UCC28760",
        "UCC28600", "UCC28610", "UCC28056", "UCC28070", "UCC28152",
        "UCC28950", "UCC28951", "UCC25224", "UCC24612", "UCC24610",
        "LM5020", "LM5023", "LM5024", "LM5025", "LM5030", "LM5035",
        "LM5038", "LM5138", "LM5180", "LM5181", "LM51805", "LM5576Q",
        "TPS23756", "TPS23758", "UCC23303", "UCC23513", "UCC23514",
        "UCC21520", "UCC21530", "UCC27524", "UCC27211", "UCC21732",
        "LM5113", "LM5109", "LM5106", "LM5104", "LMG4010", "LMG1020",
        "SG3525", "TL594", "UCC28C40", "UCC28C43", "UCC28C44", "UCC28C51",
    ]
] + [
    PI(p, f, FLYBACK) for p, f in [
        ("TNY274-280", "tny274-280"), ("TNY278", "tny274-280"),
        ("LNK364", "lnk364"), ("LNK3602", "lnk3602-3606"),
        ("LNK3606", "lnk3602-3606"), ("LNK520", "lnk520"),
        ("LNK564", "linkswitch-lt"), ("RDK-206", "rdk-206"),
    ]
] + [
    ST(p, FLYBACK) for p in ["l6599", "l6562", "l4981", "l6564", "viper27",
                             "viper37", "viper16l", "stnrgu01"]
] + [
    ONS(p, FLYBACK) for p in ["uc3842", "uc3843", "uc3844", "uc3845",
                              "ncp1200", "ncp1565", "a6263", "mc34167"]
]

# ============ 2. DC-DC / PMIC / 线性稳压器 ============
POWER_MGMT = "power_management"
ENTRIES += [
    TI(p, POWER_MGMT) for p in [
        "LM2596", "LM2576", "LM2577", "LM1084", "LM1117", "LM317", "LM337",
        "TPS5430", "TPS5431", "TPS5433", "TPS5435", "TPS5436", "TPS5450",
        "TPS5456", "TPS5460", "TPS5462", "TPS5490", "TPS54360", "TPS54368",
        "TPS561201", "TPS562201", "TPS563201", "TPS62A01", "TPS62A02",
        "TPS62203", "TPS63000", "TPS63020", "TPS63070", "TPS7A02", "TPS7A05",
        "TPS7A20", "TPS7A45", "TPS7A4700", "TPS7A49", "TPS7A83", "TPS7A84",
        "LP5907", "LP5902", "LM4040", "REF3033", "REF3425", "LM73220",
        "TPS2051B", "TPS2052B", "LM5050", "LM66100", "LM74700", "LM74700Q1",
        "TPS564201", "TPS563200", "TPS62L01", "TPS567208", "LM5145", "LM5146",
        "LM5164", "LM5166", "LM76002", "LM76003",
    ]
] + [
    ST(p, POWER_MGMT) for p in ["ld1117", "ld1086", "l4940", "ld39080", "stmps225"]
] + [
    MPS(p, POWER_MGMT) for p in ["MP1584", "MP2315", "MP2359", "MP8751",
                                 "MP1482", "MP2482", "MP8741", "MP3424"]
]

# ============ 3. 传感器（MPU6050 等为计划书指定器件） ============
SENSOR = "sensor"
ENTRIES += [
    {"part": "MPU6050", "manufacturer": "InvenSense", "category": SENSOR,
     "urls": ["https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf",
              "https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6050-Datasheet1.pdf"]},
    {"part": "MPU9250", "manufacturer": "InvenSense", "category": SENSOR,
     "urls": ["https://invensense.tdk.com/wp-content/uploads/2015/02/DS-MPU9250-rev1-1.pdf"]},
    {"part": "ICM20948", "manufacturer": "InvenSense", "category": SENSOR,
     "urls": ["https://invensense.tdk.com/wp-content/uploads/2015/02/DS-000159-ICM-20948-v1.3.pdf"]},
    {"part": "BME280", "manufacturer": "Bosch", "category": SENSOR,
     "urls": ["https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf"]},
    {"part": "BMP280", "manufacturer": "Bosch", "category": SENSOR,
     "urls": ["https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds001.pdf",
              "https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp280-ds005.pdf"]},
    {"part": "BNO055", "manufacturer": "Bosch", "category": SENSOR,
     "urls": ["https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bno055-ds00j.pdf"]},
    {"part": "LSM6DSO", "manufacturer": "ST", "category": SENSOR,
     "urls": ["https://www.st.com/resource/en/datasheet/lsm6dso.pdf"]},
    {"part": "LSM6DSL", "manufacturer": "ST", "category": SENSOR,
     "urls": ["https://www.st.com/resource/en/datasheet/lsm6dsl.pdf"]},
    {"part": "IIS3DWC", "manufacturer": "ST", "category": SENSOR,
     "urls": ["https://www.st.com/resource/en/datasheet/iis3dwc.pdf"]},
    {"part": "LIS3DH", "manufacturer": "ST", "category": SENSOR,
     "urls": ["https://www.st.com/resource/en/datasheet/lis3dh.pdf"]},
] + [
    TI(p, SENSOR) for p in ["LM35", "TMP36", "TMP102", "LM75B", "AMC1301",
                            "AMC1311", "AMC1200", "ADS1115", "ADS1118",
                            "ADS1220", "ADS1256", "INA128", "INA180", "INA219",
                            "TL431", "TL432"]
]

# ============ 4. 存储（W25Q64 为计划书指定器件） ============
MEMORY = "memory"
ENTRIES += [
    {"part": "W25Q64", "manufacturer": "Winbond", "category": MEMORY,
     "urls": ["https://www.winbond.com/resource-files/w25q64jv%20revk%2005112022%20online.pdf",
              "https://www.winbond.com/resource-files/w25q64fv%20revc%2002282017%20online.pdf"]},
    {"part": "W25Q128", "manufacturer": "Winbond", "category": MEMORY,
     "urls": ["https://www.winbond.com/resource-files/w25q128jv%20revi%2007242017%20online.pdf",
              "https://www.winbond.com/resource-files/w25q128jv%20revk%2005112022%20online.pdf"]},
    {"part": "W25Q32", "manufacturer": "Winbond", "category": MEMORY,
     "urls": ["https://www.winbond.com/resource-files/w25q32jv%20revg%2003272018%20plus.pdf"]},
    {"part": "GD25Q64", "manufacturer": "GigaDevice", "category": MEMORY,
     "urls": ["https://www.gigadevice.com/datasheet/gd25q64e/"]},
    {"part": "MX25L64", "manufacturer": "Macronix", "category": MEMORY,
     "urls": ["https://www.macronix.com/Lists/Datasheet/Attachments/7544/MX25L6406E,%203V,%2064Mb,%20v1.0.pdf"]},
] + [
    ST(p, MEMORY) for p in ["m24c02-f", "m24c64-w"]
] + [
    {"part": "AT24C02C", "manufacturer": "Microchip", "category": MEMORY,
     "urls": ["https://ww1.microchip.com/downloads/aemacman/documents/Product_LineDocuments/memory/pdfs/20006028D.pdf",
              "https://ww1.microchip.com/downloads/en/DeviceDoc/20006028D.pdf"]},
    {"part": "AT25SL32", "manufacturer": "Microchip", "category": MEMORY,
     "urls": ["https://ww1.microchip.com/downloads/en/DeviceDoc/20005953B.pdf"]},
    {"part": "IS25LP064", "manufacturer": "ISSI", "category": MEMORY,
     "urls": ["https://www.issi.com/WW/pdf/25LP-WP064.pdf"]},
]

# ============ 5. 无线/蜂窝模组（EC600M 为计划书指定器件） ============
RF_MODULE = "wireless_module"
ENTRIES += [
    {"part": "EC600M-CN", "manufacturer": "Quectel", "category": RF_MODULE,
     "urls": ["https://www.quectel.com/wp-content/uploads/2022/04/Quectel_EC600M_CN_LTE_Standard_Module_Datasheet_V1.1.pdf",
              "https://developer.aliyun.com/topic/download?id=4858"]},
    {"part": "EC800M-CN", "manufacturer": "Quectel", "category": RF_MODULE,
     "urls": ["https://www.quectel.com/wp-content/uploads/2022/04/Quectel_EC800M_CN_LTE_Standard_Module_Datasheet_Datasheet.pdf"]},
    {"part": "BG96", "manufacturer": "Quectel", "category": RF_MODULE,
     "urls": ["https://www.quectel.com/wp-content/uploads/2021/06/Quectel_BG96_LTE_CAT_M1NB2_GNSS_Standard_Module_Datasheet_V1.3.pdf"]},
    {"part": "EG25-G", "manufacturer": "Quectel", "category": RF_MODULE,
     "urls": ["https://www.quectel.com/wp-content/uploads/2021/09/Quectel_EG25-G_LTE_Standard_Modules_Datasheet_V1.4.pdf"]},
    ESP("ESP32", "esp32", RF_MODULE),
    ESP("ESP32-S3", "esp32-s3", RF_MODULE),
    ESP("ESP32-C3", "esp32-c3", RF_MODULE),
    ESP("ESP32-C6", "esp32-c6", RF_MODULE),
    {"part": "nRF52832", "manufacturer": "Nordic", "category": RF_MODULE,
     "urls": ["https://www.nordicsemi.com/-/media/Software-and-other-downloads/Product-Datasheets/nRF52832_PS_v17.pdf"]},
    {"part": "NRF24L01+", "manufacturer": "Nordic", "category": RF_MODULE,
     "urls": ["https://www.nordicsemi.com/-/media/Software-and-other-downloads/Product-Datasheets/nRF24L01ProductBriefcopy1pdf.pdf"]},
    {"part": "SI4730", "manufacturer": "Skyworks", "category": RF_MODULE,
     "urls": ["https://www.skyworksinc.com/-/media/SkyWorks/Documents/Products/1701-1800/Si4730_Datasheet.pdf"]},
]

# ============ 6. TEC 驱动 / 电机与执行器驱动 ============
DRIVER = "driver_actuator"
ENTRIES += [
    {"part": "TB6612FNG", "manufacturer": "Toshiba", "category": DRIVER,
     "urls": ["https://www.toshiba.com/taec/components/Databook/Download/tbc2000_e.pdf",
              "https://datasheetspdf.com/pdf-file/920792/Toshiba/TB6612FNG/1"]},
    {"part": "DRV8833", "manufacturer": "TI", "category": DRIVER,
     "urls": ["https://www.ti.com/lit/ds/symlink/drv8833.pdf"]},
] + [
    TI(p, DRIVER) for p in ["DRV8837", "DRV8870", "DRV8871", "DRV8711",
                            "DRV8702", "DRV8825", "DRV11873",
                            "SN75441", "ULN2003A", "TPIC6B595"]
] + [
    ST(p, DRIVER) for p in ["l298", "l293d", "bts50055", "l6219ds?", "stgost12f6"]
] + [
    NXP(p, DRIVER) for p in ["74HC595", "PCA9685", "UBA2015", "TEA19162"]
]

# ============ 7. MCU（大创/求职常用型号） ============
MCU = "mcu"
ENTRIES += [
    ST(p, MCU) for p in ["stm32f103c8", "stm32f103cb", "stm32f103xb",
                         "stm32f407vg", "stm32f407ve", "stm32f411ce",
                         "stm32l476rg", "stm32g071rb", "stm32h743zi",
                         "stm32c031c6", "stm8s003f3"]
] + [
    {"part": "ATmega328P", "manufacturer": "Microchip", "category": MCU,
     "urls": ["https://ww1.microchip.com/downloads/en/DeviceDoc/ATmegaPC-DataSheet-40002090A.pdf",
              "https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf"]},
    {"part": "ATmega32u4", "manufacturer": "Microchip", "category": MCU,
     "urls": ["https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Datasheet.pdf"]},
    {"part": "PIC16F1825", "manufacturer": "Microchip", "category": MCU,
     "urls": ["https://ww1.microchip.com/downloads/en/DeviceDoc/40001413B.pdf"]},
    {"part": "SAML21", "manufacturer": "Microchip", "category": MCU,
     "urls": ["https://ww1.microchip.com/downloads/en/DeviceDoc/SAML21-Family-Datasheet-DS40002356B.pdf"]},
    {"part": "GD32F103", "manufacturer": "GigaDevice", "category": MCU,
     "urls": ["https://www.gigadevice.com/datasheet/gd32f103vk/"]},
    {"part": "CH32V303", "manufacturer": "WCH", "category": MCU,
     "urls": ["https://www.wch-ic.com/downloads/CH32V303DS0_PDF.html"]},
    {"part": "ESP8266", "manufacturer": "Espressif", "category": MCU,
     "urls": ["https://www.espressif.com/sites/default/files/documentation/4006-esp8266ex_datasheet_en.pdf",
              "https://www.espressif.com/sites/default/files/documentation/4a08-esp8266ex_datasheet_en.pdf"]},
]

# ============ 8. 运放 / 模拟前端 ============
ANALOG = "analog_ic"
ENTRIES += [
    TI(p, ANALOG) for p in ["LM358", "LM324", "LM393", "LM2903", "TL081",
                            "TL082", "TL072", "NE5532", "NE5534", "NE555",
                            "LMC555", "OPA333", "OPA140", "OPA2134", "OPA1652",
                            "OPA827", "OPA847", "THS4001", "INA333",
                            "TLV2372", "TLV2462", "CD4051", "CD4052", "CD4053",
                            "SN74LVC1G08", "SN74AHC1G08", "SN74HC595",
                            "SN74LVC245A", "SN75176B", "SN65HVD230",
                            "TLC5940", "TLC5947",
                            "TPIC6595", "CD74HC4067"]
] + [
    ADI(p, ANALOG) for p in ["ad620", "adr020", "ad8230", "ad8232",
                             "ltc4305", "lt1024", "ad5592r", "ad8105"]
] + [
    {"part": "TLV2374", "manufacturer": "TI", "category": ANALOG,
     "urls": ["https://www.ti.com/lit/ds/symlink/tlv2374.pdf"]},
]

# ============ 9. 功率器件 / MOSFET / LED 驱动 ============
DISCRETE = "power_discrete"
ENTRIES += [
    ONS(p, DISCRETE) for p in ["irf540n", "irf9z30pbf", "nfs025n06",
                               "fdd8436", "ncp1529", "lm3410"]
] + [
    TI(p, DISCRETE) for p in ["CSD18502Q5A", "TPS92610", "TPS929120",
                              "LM3414", "LM3402", "LM3404", "TPS92598",
                              "TLV62568", "TPS92230"]
] + [
    {"part": "PT4103", "manufacturer": "BPS", "category": DISCRETE,
     "urls": ["https://www.bpths.com/api/file_down.php?name=PT4103&ext=pdf"]}
]

# ============ 10. 南芯 / 矽力杰（计划书指定厂商，官网按 ID 下载→待人工核实） ============
SILERGY = "silergy_southchip"
ENTRIES += [
    {"part": "SY8089A", "manufacturer": "Silergy", "category": SILERGY,
     "urls": ["https://www.silergy.com/download/downloadFile?id=3561&type=product&ftype=note"]},
    {"part": "SY5041", "manufacturer": "Silergy", "category": SILERGY,
     "urls": ["https://silergy.blob.core.windows.net/silergy/document/SY5041A.pdf"]},
    {"part": "SC2021A", "manufacturer": "Southchip", "category": SILERGY,
     "urls": ["https://www.southchip.com/rest/sc2021a/download?type=1"]},
    {"part": "SC3503", "manufacturer": "Southchip", "category": SILERGY,
     "urls": ["https://www.southchipsemi.com/rest/sc3503/download?type=1"]},
    {"part": "SCP1060", "manufacturer": "Southchip", "category": SILERGY,
     "urls": ["https://www.southchip.com/rest/scp1060/download?type=1"]},
]


# ============ 11. 第二轮扩充（TI 目录为主，失败自动记录） ============
EXTRA = {
 POWER_MGMT: [
  "TPS54060","TPS5410","TPS54331","TPS54340","LM2674","LM2675","LM2676","LM2678",
  "LM2734","LM27402","LM5008","LM5017","LM5018","LM5019","LM5085","LM5116","LM5117",
  "LM5143","LM5144","LM5160","LM5163","LM76102","LMR36015","LMR36506","LMR50410",
  "LMR50420","TPS62130","TPS62150","TPS62152","TPS62153","TPS62840","TPS544C20",
  "TPS546D24","TPS566248","TPS56821","TPS7A03","TPS7A10","TPS7A83001","LM2940",
  "LM2941","LP2985","TPS7B6702","REF3025","REF3030","REF3045","REF3133","REF6025",
  "LM4041","TPS22919","TPS25940","LM723","LM3409","TPS92570","TPS92615","TPS92231",
  "TPS3808","TPS3823","INA226","INA228","INA231","INA199","INA3221","LM76102",
 ],
 FLYBACK: [
  "UCC28019","UCC28910","LM5021","LM5071","TPS23754","UCC28065","UCC28070",
  "UCC21320","UCC21330","UCC27500","AMC1305","AMC3301","UCC29950","LM5170",
  "TPS55340","TPS55045","LTC4421?","UCC28080","NCP1566?",
 ],
 ANALOG: [
  "OPA192","OPA2188","OPA188","OPA1642","OPA1612","OPA1688","OPA656","OPA657",
  "OPA855","OPA2156","LMH6629","THS3201","TLV3501","TLV3502","TLV3544","LMV7219",
  "LMH7322","TXB0104","TXB0108","TXS0102E","TXS0104E","TXS0108E","SN74LVC1T45",
  "SN74LVC4245A","SN74AUP1G04","SN74AHC244","SN74LVC2G34","ISO1042","ISO7721",
  "ISO7731","ISO7741","SN65HVD75","ADS1015","ADS7052","TLV5618","DAC8563",
  "CD74HC4051","SN74HC4067","SN74LVC1G14","SN74LVC1G04",
 ],
 SENSOR: [
  "TMP117","TMP1075","TMP461","HDC2010","HDC2021","HDC2080","LMT86","AMC1210",
  "AMC1306","ADS131M02","LM94022",
 ],
 DRIVER: [
  "DRV8256","DRV8231","DRV8876","DRV8908","DRV11873","DRV8614","DRV8412?","CSD18560Q5A",
 ],
}
for _cat, _parts in EXTRA.items():
    for _p in _parts:
        ENTRIES.append(TI(_p, _cat))

ENTRIES += [ST(p, MCU) for p in ["stm32f051r8", "stm32f103c6", "stm32f405rg",
                                 "stm32l151cb", "stm32wb55rg"]]
ENTRIES += [ST(p, SENSOR) for p in ["lis2dw12", "iis328dq", "tsens?"]]
ENTRIES += [ST(p, POWER_MGMT) for p in ["tsx?", "ldo?"]]
ENTRIES += [ST(p, ANALOG) for p in ["tsu901ai8t?"]]

# ============ 12. 第三轮扩充（冲刺 300+，TI/ST 长尾型号） ============
EXTRA3 = {
 POWER_MGMT: [
  "TPS54202M","TPS54021?","TPS54521?","TPS54202?","TPS54622?","TPS54560",
  "TPS54318?","TPS54330?","TPS54541?","TPS54542","TPS54540?","TPS54332?","TPS54342?",
  "LMR14020?","LMR16030?","LMR33630","LMR33620?","LMR33640?","LMR36520?","LMR33035?",
  "TPS62A03?","TPS62A04","TPS62850?","TPS62873?","TPS62893?","TPS62910?","TPS62A02",
  "TPS7A02","TPS7A02?","TPS7A04","TPS7A08","TPS7A14","TPS7A15","TPS7A16","TPS7A21",
  "TPS7A26","TPS7A30","TPS7A31","TPS7A33","TPS7A34","TPS7A35","TPS7A36","TPS7A37",
  "TPS7A38","TPS7A39","TPS7A4002","TPS7A41","TPS7A4101","TPS7A4118","TPS7A418",
  "TPS7A47","TPS7A48","TPS7A4901","TPS7A70","TPS7A71","TPS7A72","TPS7A73","TPS7A74",
  "TPS7A75","TPS7A76","TPS7B50","TPS7B50Q1","TPS7B87?","TPS7C40","TPS7C50?","TPS7C65?",
 ],
 ANALOG: [
  "OPA1688","OPA1698?","OPA2187","OPA2187?","OPA2322","OPA2325","OPA2326","OPA2333",
  "OPA2340","OPA2344","OPA2350","OPA2354","OPA2356","OPA2365?","OPA237?","OPA2376",
  "OPA2684","OPA2690","OPA316","OPA320","OPA322","OPA328","OPA330","OPA335","OPA340",
  "OPA344","OPA354","OPA356","OPA364","OPA365","OPA376","OPA378","OPA380","OPA4322",
  "OPA4333","OPA4340","OPA450","OPA453","OPA454","OPA462","OPA466","OPA467","OPA4727",
  "OPA4H333","OPA835","OPA836","OPA858?","OPA859?","OPA860?","OPA890","OPA891","OPA892",
  "TLV1721","TLV1722","TLV1805","TLV181?","TLV2316","TLV2322","TLV2374","TLV369","TLV6001",
  "LMH6552?","LMH6611?","LMH6624?","LMV321","LMV358","LMV711","LMV717?","SN74LV1T34",
  "TXB0102","TXU0104?","TXS0101","TXS0104","UC2844-1?","ADS1100","ADS1110","ADS1113",
  "ADS1114","ADS1116","ADS118?","ADS119?","ADS405?","ADS504?","DAC701?","DAC7311","DAC7573",
  "TLV320A?","TVP5146?","ADC121S?","ADC08D?","LMX2592","LMX2594?","LMK3C14?","CDCV300?",
 ],
 FLYBACK: [
  "UCC28056","UCC28060","UCC28061","UCC28063","UCC28064","UCC28070","UCC28075","UCC28108",
  "UCC28160","UCC28180","UCC28220","UCC28240","UCC28241?","UCC28243","UCC2946?","LMG3522?",
  "LMG3525R05?","LMG5236?","LMG5208?","UCC213130?","UCC213230?","UCC213330?","UCC213430?",
  "ISO6842?","ISO6821?","ISO6830?","ISO5852?","AMC1400?","AMC1411?","AMC1430?","AMC1480?",
  "TPS710?","TPS552?","LM5175","LM5177?","LM5200?","LM74500?","LM74502?","LMC2145?",
 ],
 SENSOR: ["TMP100","TMP101","TMP103","TMP104","TMP102A","TMP1075","TMP112","TMP124",
  "TMP126?","TMP20","TMP235?","LM35","LM50","LM74","LM73","LM75","LM83","LM92?","LM93?",
  "TMP175?","DAC081S?","ADC084S?","TPT29554?","TPS23861?","DPD14010?","HDC1080","HDC1085?"],
 DRIVER: ["DRV8874","DRV8312?","DRV8313","DRV8323?","DRV8320?","DRV8323R?","DRV835?","DRV8701",
  "DRV8713?","DRV8714?","DRV8722?","DRV8723?","DRV8725?","DRV8728?","LMD1824?","L298?","MC33926?"],
 DISCRETE: ["CSD19536?","CSD18571?","CSD18504?","CSD17555?","TPU?","LM5100","LM5101?","LM5111",
  "LM5112?","LM5115","LM5165?","LM5162?","LM51610?","LM51615?","LM7241?","LM7352?"],
}
for _cat, _parts in EXTRA3.items():
    for _p in _parts:
        ENTRIES.append(TI(_p, _cat))
# 去掉带 ? 的不确定项在 build_entries 中统一处理

ENTRIES += [ST(p, MCU) for p in ["stm32f302c8", "stm32f072c8", "stm32l073rz",
                                 "stm32u375vc", "stm32g474re", "stm32f401cc",
                                 "stm32f410rb", "stm32l432kc", "stm32wl55jc"]]
ENTRIES += [ST(p, ANALOG) for p in ["lm358", "lm324", "lm393", "tsx?", "tsb951ait?"]]
ENTRIES += [ST(p, MEMORY) for p in ["m24128-b?", "s?"]]


def build_entries():
    seen, out = set(), []
    for e in ENTRIES:
        part = e["part"].rstrip("?")
        if part.upper() in seen or not part:
            continue
        seen.add(part.upper())
        urls = [u.replace(part.lower() + "?", part.lower())
                 .replace(part + "?", part) for u in e["urls"]]
        out.append({**e, "part": part, "urls": urls})
    return out
