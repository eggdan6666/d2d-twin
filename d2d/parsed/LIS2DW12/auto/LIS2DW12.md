# MEMS digital output motion sensor: high-performance ultralow-power 3-axis "femto" accelerometer

![](images/4b516199f7f1a488825715fc9bbbc98a2fd5cb4c055f52869af67ce8ac62012f.jpg)

LGA-12L 2.0 x 2.0 x 0.7 (max) mm

<table><tr><td>Product status link</td></tr><tr><td>LIS2DW12</td></tr></table>

<table><tr><td rowspan=1 colspan=2>Product summary</td></tr><tr><td rowspan=1 colspan=1>Order code</td><td rowspan=1 colspan=1>LIS2DW12TR</td></tr><tr><td rowspan=1 colspan=1>Temperature range[c]</td><td rowspan=1 colspan=1>-40 to +85</td></tr><tr><td rowspan=1 colspan=1>Package</td><td rowspan=1 colspan=1>LGA-12</td></tr><tr><td rowspan=1 colspan=1>Packing</td><td rowspan=1 colspan=1>Tape and reel</td></tr></table>

<table><tr><td>Product resources</td></tr><tr><td>AN5038 (device application note)</td></tr><tr><td>TN0018 (design and soldering)</td></tr></table>

![](images/d82aa427da994715085436b7745412a36158a15989ea4dd24e146fcf9dca0a06.jpg)

# Features

Ultralow power consumption: 50 nA in power-down mode, below $1 \mu \mathsf { A }$ in active   
low-power mode   
Very low noise: down to 1.3 mg RMS in low-power mode   
Multiple operating modes with multiple bandwidths   
Android stationary detection, motion detection   
Supply voltage, 1.62 V to $3 . 6 \lor$   
Independent I/O supply   
±2g/±4g/±8g/±16g full scale   
High-speed I²C/SPl digital output interface   
Single data conversion on demand   
16-bit data output   
Embedded temperature sensor   
Self-test   
32-level FIFO   
10000 g high shock survivability   
ECOPACK and RoHS compliant

# Applications

Motion detection for wearables   
Gesture recognition and gaming   
Motion-activated functions and user interfaces   
Display orientation   
Tap/double-tap recognition   
Free-fall detection   
Smart power saving for handheld devices   
Hearing aids   
Portable healthcare devices   
Wireless sensor nodes   
Motion-enabled metering devices

# Description

The LIS2DW12 is an ultralow-power high-performance 3-axis linear accelerometer belonging to the “femto" family, which leverages on the robust and mature manufacturing processes already used for the production of micromachined accelerometers.

The device has user-selectable full scales of $\pm 2 g / \pm 4 g / \pm 8 g / \pm 1 6 g$ and can measure accelerations with output data rates from $1 . 6 \mathsf { H z }$ to $1 6 0 0 \mathsf { H z }$

The LIS2DW12 has an integrated 32-level first-in,first-out (FIFO) buffer allowing the user to store data in order to limit intervention by the host processor.

The embedded self-test capability allows the user to check the functioning of the sensor in the final application.

The device has a dedicated internal engine to process motion and acceleration detection including free-fal, wakeup,highly configurable single/double-taprecognition,activity/inactivity,stationary/motion detection,portrait/ landscape detection,and 6D/4D orientation.

The LIS2DW12 is available in a smallthin plastic,land grid array (LGA) package and it is guaranteed to operate over an extended temperature range from $\scriptscriptstyle - 4 0 ^ { \circ } \mathsf { C }$ to $+ 8 5 ^ { \circ } \mathsf { C }$ ：

# Block diagram and pin description

# 1.1

# Block diagram

![](images/322d40736ec636454fa9e633e6c7b6900afdc98fbcf4ee46fc1d23e93085852f.jpg)  
Figure 1. Block diagram

<table><tr><td></td><td></td><td></td><td></td><td>32 Level</td><td>CONTROL LOGIC</td><td>INT1</td></tr><tr><td rowspan="2">SELF TEST</td><td rowspan="2">REFERENCE</td><td rowspan="2">TRIMMING CIRCUITS</td><td rowspan="2">CLOCK</td><td rowspan="2">FIFO</td><td rowspan="2">&amp; INTERRUPT GEN.</td><td>INT2</td></tr><tr><td></td></tr></table>

# 1.2 Pin description

![](images/e9ee67ad18aec7791e5b2e01da44ac2f0b9b81877128ccddcc5bdf6ca1d13c23.jpg)  
Figure 2. Pin connections

![](images/f9d20cdf4d107e4c166cfce94413cbe470c58934025c7fa4d800bac13f1a934d.jpg)

Table 1. Pin description   

<table><tr><td rowspan=1 colspan=1> Pin#</td><td rowspan=1 colspan=1>Name</td><td rowspan=1 colspan=1>Function</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>SCLSPC</td><td rowspan=1 colspan=1>I²C serial clock (SCL)SPl serial port clock (SPC)</td></tr><tr><td rowspan=1 colspan=1>2(1)</td><td rowspan=1 colspan=1>CS</td><td rowspan=1 colspan=1>Enable SPIβC/SPI mode selection(1: SPl idle mode / FC communication enabled;0: SPl communication mode /I²C disabled)</td></tr><tr><td rowspan=1 colspan=1>3(1)</td><td rowspan=1 colspan=1>SDOSAO</td><td rowspan=1 colspan=1> SPl serial data output (SDO)lC less significant bit of the device address (SA0)</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>SDASDISDO</td><td rowspan=1 colspan=1>PC serial data (SDA)SPl serial data input (SDI)3-wire interface serial data output (SDO)</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>NC</td><td rowspan=1 colspan=1> Internally not connected. Can be tied to VDD,VDDIO,or GND.</td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>GND</td><td rowspan=1 colspan=1>0 V supply</td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>RES</td><td rowspan=1 colspan=1>Connect to GND</td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>GND</td><td rowspan=1 colspan=1>0 V supply</td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>VDD</td><td rowspan=1 colspan=1>Power supply</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>VDD_IO</td><td rowspan=1 colspan=1>Power supply for I/O pins</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>INT2</td><td rowspan=1 colspan=1>Interrupt pin 2. Clock input when selected in single data conversion on demand.</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>INT1</td><td rowspan=1 colspan=1> Interrupt pin 1</td></tr></table>

1. SDO/SA0 and CS pins are internaly pulledup. Referto Table 2.Iternal pullup values (typ.)forSDO/SA0and CS pins for the internal pull-up values (typ).

Table 2. Internal pull-up values (typ.) for SDO/SA0 and CS pins   

<table><tr><td rowspan="2">Vdd_io</td><td colspan="2">Resistor value for SDO/SA0 and CS pins</td></tr><tr><td></td><td>Typ. (kΩ)</td></tr><tr><td>1.7V</td><td></td><td>54.4</td></tr><tr><td>1.8V</td><td></td><td>49.2</td></tr><tr><td>2.5V</td><td>30.4</td><td></td></tr><tr><td>3.6V</td><td></td><td>20.4</td></tr></table>

# 2 Mechanical and electrical specifications

# 2.1 Mechanical characteristics

$@ \lor { \mathsf { d d } } = 1 . 8 \lor$ ${ \mathsf { T } } = 2 5 ^ { \circ } { \mathsf { C } }$ unless otherwise noted. The product is factory calibrated at $1 . 8 \lor .$ The operational power supply range is from $1 . 6 2 \mathrm { V }$ to $3 . 6 \lor .$

Table 3. Mechanical characteristics   

<table><tr><td rowspan=1 colspan=1>Symbol</td><td rowspan=1 colspan=2>Parameter</td><td rowspan=1 colspan=1>Test conditions</td><td rowspan=1 colspan=1>Min.</td><td rowspan=1 colspan=1>Typ.(1)</td><td rowspan=1 colspan=1>Max.</td><td rowspan=1 colspan=1>Unit</td></tr><tr><td rowspan=4 colspan=1>FS</td><td rowspan=4 colspan=2>Measurement range</td><td rowspan=4 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>±2</td><td rowspan=1 colspan=1></td><td rowspan=4 colspan=1>g</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>±8</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>±16</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=3 colspan=1></td><td rowspan=3 colspan=2></td><td rowspan=1 colspan=1>@ FS ±2 g in high-performance mode and allow-powermodes except low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.244</td><td rowspan=1 colspan=1></td><td rowspan=8 colspan=1> mg/digit</td></tr><tr><td rowspan=1 colspan=1>@ FS ±4 g in high-performance mode and allow-powermodes except low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.488</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>@ FS ±8 g in high-performance mode and allow-powermodes except low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.976</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=5 colspan=1>So</td><td rowspan=5 colspan=2>Sensitivity</td><td rowspan=1 colspan=1>@ FS ±16 g in high-performance mode and alow- power modes except low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.952</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>@ FS ±2 g in low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.976</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>@ FS ±4 g in low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.952</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>@ FS ±8 g in low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>3.904</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>@ FS ±16 g in low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>7.808</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>An</td><td rowspan=1 colspan=2>Noise density- high-performancemode(2)</td><td rowspan=1 colspan=1>@FS ±2 g</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>ug/Hz</td></tr><tr><td rowspan=4 colspan=1>RMS</td><td rowspan=4 colspan=2>RMS noise - low-power modes(3)@FS ±2 g</td><td rowspan=1 colspan=1>Low-power mode 4</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.3</td><td rowspan=1 colspan=1></td><td rowspan=4 colspan=1>mg(RMS)</td></tr><tr><td rowspan=1 colspan=1>Low-power mode 3</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.8</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Low-power mode 2</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2.4</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Low-power mode 1</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>TyOff</td><td rowspan=1 colspan=2>Zero-g level offset accuracy(4)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>±20</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>mg</td></tr><tr><td rowspan=1 colspan=1>TCO</td><td rowspan=1 colspan=2> Zero-g offset change vs. temperature</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>±0.2</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>mg/℃</td></tr><tr><td rowspan=1 colspan=1>TCS</td><td rowspan=1 colspan=2> Sensitivity change vs. temperature</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>%/℃</td></tr><tr><td rowspan=1 colspan=1>ST</td><td rowspan=1 colspan=2>Self-test positive difference</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>70</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1500</td><td rowspan=1 colspan=1>mg</td></tr></table>

1. Typical specifications are not guaranteed. 2. Noise density is the same forall ODRs. Low-noise seting enabled. 3. RMS noise is the same for al ODRs. Low-noise setting enabled. 4. Values after factory calibration test and trimming.

# 2.2 Electrical characteristics

$\textcircled { \scshape A } \lor \mathsf { d } \mathsf { d } = 1 . 8 \ : \mathsf { V }$ ${ \mathsf { T } } = 2 5 ^ { \circ } { \mathsf { C } }$ unless otherwise noted. The product is factory calibrated at $1 . 8 \lor .$ The operational power supply range is from $1 . 6 2 \mathrm { V }$ to $3 . 6 \lor .$

Table 4. Electrical characteristics   

<table><tr><td rowspan=1 colspan=1>Symbol</td><td rowspan=1 colspan=1> Parameter</td><td rowspan=1 colspan=1>Test conditions</td><td rowspan=1 colspan=1>Min.</td><td rowspan=1 colspan=1>Typ.(11)</td><td rowspan=1 colspan=1>Max.</td><td rowspan=1 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>Vdd</td><td rowspan=1 colspan=1>Supply voltage</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.62</td><td rowspan=1 colspan=1>1.8</td><td rowspan=1 colspan=1>3.6</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>Vdd_i0</td><td rowspan=1 colspan=1>I/O pins supply voltage(2)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.62</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>Vdd+0.1</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>IddHR</td><td rowspan=1 colspan=1>Supply current in high-performance mode(3)</td><td rowspan=1 colspan=1>@ ODR range12.5 Hz - 1600 Hz, 14-bit</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>UA</td></tr><tr><td rowspan=4 colspan=1>IddLP</td><td rowspan=4 colspan=1>Supply current in low-power mode(4)</td><td rowspan=1 colspan=1>ODR 100 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1></td><td rowspan=4 colspan=1>uA</td></tr><tr><td rowspan=1 colspan=1>ODR 50 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>ODR 12.5 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>ODR 1.6 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.38</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Idd_PD</td><td rowspan=1 colspan=1> Supply current in power-down</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>nA</td></tr><tr><td rowspan=1 colspan=1>VIH</td><td rowspan=1 colspan=1>Digital high-level input voltage</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.7*Vdd_IO</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>VIL</td><td rowspan=1 colspan=1>Digital low-level input voltage</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.3*Vdd_IO</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>VoH</td><td rowspan=1 colspan=1>Digital high-level output voltage</td><td rowspan=1 colspan=1>loH = 4 mA(5)</td><td rowspan=1 colspan=1>Vdd_iO - 0.2</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>VoL</td><td rowspan=1 colspan=1>Digital low-level output voltage</td><td rowspan=1 colspan=1>loL = 4 mA(5)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.2</td><td rowspan=1 colspan=1>V</td></tr></table>

1. Typical specifications are not guaranteed. 2.Itisposibletoremove VddmaintainingVdIOwithoutblockingthcommunicationbusses.Inthisconditionthemeasurementcainis powered off. 3． Low-noise setting disabled. 4.Low-power mode 1. Low-noise setting disabled. 5 $4 m A$ is themaximumdrivingcapability,thatis,the maximumDCcurrentthatcanbesourced/sunkbythedigitalpadinorderto guarantee thecorrectdigitaloutput voltage levels $V _ { O H }$ and $V _ { O L }$

# 2.3 Temperature sensor characteristics

$\textcircled { \scshape A } { \sf d } = 1 . 8 \lor$ ${ \mathsf { T } } = 2 5 ^ { \circ } { \mathsf { C } }$ unless otherwise noted

Table 5. Temperature sensor characteristics   

<table><tr><td rowspan=1 colspan=1>Symbol</td><td rowspan=1 colspan=1>Parameter</td><td rowspan=1 colspan=1>Min.</td><td rowspan=1 colspan=1>Typ. (1)</td><td rowspan=1 colspan=1>Max.</td><td rowspan=1 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>Top</td><td rowspan=1 colspan=1> Operating temperature range</td><td rowspan=1 colspan=1>-40</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>+85</td><td rowspan=1 colspan=1>℃</td></tr><tr><td rowspan=1 colspan=1>Toff</td><td rowspan=1 colspan=1>Temperature offset(2)</td><td rowspan=1 colspan=1>-15</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>+15</td><td rowspan=1 colspan=1>℃C</td></tr><tr><td rowspan=2 colspan=1>TSDr</td><td rowspan=2 colspan=1>Temperature sensor output change vs. temperature</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1（3）</td><td rowspan=1 colspan=1></td><td rowspan=2 colspan=1>LSB/C</td></tr><tr><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>16（4)</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=4 colspan=1>TODR</td><td rowspan=1 colspan=1>Temperature refresh rate in high-performance mode for all ODRsor in low-power modes for ODRs equal to 200/100/50 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1></td><td rowspan=4 colspan=1>Hz</td></tr><tr><td rowspan=1 colspan=1>Temperature refresh rate in low-power modes for ODR equal to 25 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Temperature refresh rate in low-power modes for ODR equal to 12.5 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>12.5</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Temperature refresh rate in low-power modes for ODR equal to 1.6 Hz</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.6</td><td rowspan=1 colspan=1></td></tr></table>

1. Typical specifications are not guaranteed. 2. The output of the temperature sensor is O LSB (typ.) at $\boldsymbol { 2 5 ^ { \circ } C }$ 3．8-bit resolution. 4．12-bit resolution.

# 2.4

# Communication interface characteristics

# 2.4.1

# SPl - serial peripheral interface

Subject to general operating conditions for Vdd and Top.

Table 6. SPl slave timing values   

<table><tr><td rowspan=2 colspan=1>Symbol</td><td rowspan=2 colspan=1> Parameter</td><td rowspan=1 colspan=2>Value (1)</td><td rowspan=2 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>Min</td><td rowspan=1 colspan=1>Max</td></tr><tr><td rowspan=1 colspan=1>tc(SPC)</td><td rowspan=1 colspan=1>SPI clock cycle</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>fc(SPC)</td><td rowspan=1 colspan=1>SPI clock frequency</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>MHz</td></tr><tr><td rowspan=1 colspan=1>tsu(CS)</td><td rowspan=1 colspan=1>CS setup time</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1></td><td rowspan=7 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>th(CS)</td><td rowspan=1 colspan=1>CS hold time</td><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tsu(SI)</td><td rowspan=1 colspan=1>SDl input setup time</td><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>th(SI)</td><td rowspan=1 colspan=1>SDI input hold time</td><td rowspan=1 colspan=1>15</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tv(sO）</td><td rowspan=1 colspan=1> SDO valid output time</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>50</td></tr><tr><td rowspan=1 colspan=1>th(so）</td><td rowspan=1 colspan=1>SDO output hold time</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tdis(So)</td><td rowspan=1 colspan=1>SDO output disable time</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>50</td></tr></table>

1.10 MHz clock frequency for SPl with both 4 and 3 wires,based on characterization results, not tested in production.

![](images/0239598161f47cee905c965efd33782d5b1ca0b95f8998bdd02791497d424372.jpg)  
Figure 3. SPl slave timing diagram

Note:

Measurement points are done at 0.3·Vdd_IO and 0.7·Vdd_IO for both input and output ports.

# 2.4.2

# I²C - inter-lC control interface

Subject to general operating conditions for Vdd and Top.

Table 7. ²C slave timing values   

<table><tr><td rowspan=2 colspan=1> Symbol</td><td rowspan=2 colspan=1>Parameter</td><td rowspan=1 colspan=2>PC standard mode(1)</td><td rowspan=1 colspan=2> IC fast mode(1)</td><td rowspan=2 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>Min</td><td rowspan=1 colspan=1>Max</td><td rowspan=1 colspan=1>Min</td><td rowspan=1 colspan=1>Max</td></tr><tr><td rowspan=1 colspan=1>f(SCL)</td><td rowspan=1 colspan=1>SCL clock frequency</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>400</td><td rowspan=1 colspan=1> kHz</td></tr><tr><td rowspan=1 colspan=1>tw(SCLL)</td><td rowspan=1 colspan=1>SCL clock low time</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.3</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>us</td></tr><tr><td rowspan=1 colspan=1>tW(SCLH)</td><td rowspan=1 colspan=1>SCL clock high time</td><td rowspan=1 colspan=1>4.0</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1> tsu(SDA)</td><td rowspan=1 colspan=1>SDA setup time</td><td rowspan=1 colspan=1>250</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>th(SDA)</td><td rowspan=1 colspan=1>SDA data hold time</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>3.45</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.9</td><td rowspan=1 colspan=1>us</td></tr><tr><td rowspan=1 colspan=1>th(ST)</td><td rowspan=1 colspan=1>START condition hold time</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1></td><td rowspan=4 colspan=1>us</td></tr><tr><td rowspan=1 colspan=1>tsu(SR)</td><td rowspan=1 colspan=1>Repeated START condition setup time</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tsu(SP)</td><td rowspan=1 colspan=1> STOP condition setup time</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tw(SP:SR)</td><td rowspan=1 colspan=1>Bus free time between STOP and START condition</td><td rowspan=1 colspan=1>4.7</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1.3</td><td rowspan=1 colspan=1></td></tr></table>

1．Data based on standard I²C protocol requirement, not tested in production.

![](images/0890a08b8e25168572e9f955e098155f80e8ffa80a4bc36c54347b6feb984793.jpg)  
Figure 4. IC slave timing diagram

Note:

Measurement points are done at 0.3·Vdd_IO and 0.7·Vdd_IO for both ports.

Table 8. I²C high-speed mode specifications at 1 MHz and 3.4 MHz   

<table><tr><td rowspan=19 colspan=1>ModeFast mode plus(1)</td><td rowspan=1 colspan=1>Symbol</td><td rowspan=1 colspan=1> Parameter</td><td rowspan=1 colspan=1>Min</td><td rowspan=1 colspan=1>Max</td><td rowspan=1 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>fscL</td><td rowspan=1 colspan=1>SCL clock frequency</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>MHz</td></tr><tr><td rowspan=1 colspan=1>tHD;STA</td><td rowspan=1 colspan=1>Hold time (repeated) START condition</td><td rowspan=1 colspan=1>260</td><td rowspan=1 colspan=1>、</td><td rowspan=11 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>tLow</td><td rowspan=1 colspan=1>Low period of the SCL clock</td><td rowspan=1 colspan=1>500</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tHIGH</td><td rowspan=1 colspan=1>High period of the SCL clock</td><td rowspan=1 colspan=1>260</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>tSU;STA</td><td rowspan=1 colspan=1>Setup time for a repeated START condition</td><td rowspan=1 colspan=1>260</td><td rowspan=1 colspan=1>、</td></tr><tr><td rowspan=1 colspan=1>tHD:DAT</td><td rowspan=1 colspan=1>Data hold time</td><td rowspan=1 colspan=1>。</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>tsU:DAT</td><td rowspan=1 colspan=1>Data setup time</td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>trDA</td><td rowspan=1 colspan=1>Rise time of SDA signal</td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1>120</td></tr><tr><td rowspan=1 colspan=1>tfDA</td><td rowspan=1 colspan=1>Falltime of SDA signal</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>120</td></tr><tr><td rowspan=1 colspan=1>trcL</td><td rowspan=1 colspan=1> Rise time of SCL signal</td><td rowspan=1 colspan=1>20*Vdd/5.5</td><td rowspan=1 colspan=1>120</td></tr><tr><td rowspan=1 colspan=1>trcL</td><td rowspan=1 colspan=1>Falltime of SCL signal</td><td rowspan=1 colspan=1>20*Vdd/5.5</td><td rowspan=1 colspan=1>120</td></tr><tr><td rowspan=1 colspan=1> tsU:STO</td><td rowspan=1 colspan=1> Setup time for STOP condition</td><td rowspan=1 colspan=1>260</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>Cb</td><td rowspan=1 colspan=1>Capacitive load for each bus line</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>550</td><td rowspan=1 colspan=1>pF</td></tr><tr><td rowspan=1 colspan=1>tvD;DAT</td><td rowspan=1 colspan=1>Data valid time</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1>450</td><td rowspan=1 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>tvD:ACK</td><td rowspan=1 colspan=1>Data valid acknowledge time</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1>450</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>VnL</td><td rowspan=1 colspan=1>Noise margin at low level</td><td rowspan=1 colspan=1>0.1Vdd</td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>VnH</td><td rowspan=1 colspan=1>Noise margin at high level</td><td rowspan=1 colspan=1>0.2Vdd</td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tsp</td><td rowspan=1 colspan=1>Pulse width of spikes that must be suppressed by the input filter</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1>ns</td></tr><tr><td rowspan=16 colspan=1>High-speed mode(1)</td><td rowspan=1 colspan=1>fsCLH</td><td rowspan=1 colspan=1>SCLH clock frequency</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>3.4</td><td rowspan=1 colspan=1>MHz</td></tr><tr><td rowspan=1 colspan=1>tsU;STA</td><td rowspan=1 colspan=1>Setup time for a repeated START condition</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1>：</td><td rowspan=12 colspan=1>ns</td></tr><tr><td rowspan=1 colspan=1>tHD;STA</td><td rowspan=1 colspan=1>Hold time (repeated) START condition</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>tLow</td><td rowspan=1 colspan=1>Low period of the SCLH clock</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>tHIGH</td><td rowspan=1 colspan=1>High period of the SCLHclock</td><td rowspan=1 colspan=1>60</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>tSU:DAT</td><td rowspan=1 colspan=1>Data setup time</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>tHD;DAT</td><td rowspan=1 colspan=1>Data hold time</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>70</td></tr><tr><td rowspan=1 colspan=1>trcL</td><td rowspan=1 colspan=1>Rise time of SCLH signal</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>40</td></tr><tr><td rowspan=1 colspan=1>trCL1</td><td rowspan=1 colspan=1>Rise time of SCLH signal after a repeated START condition and after anacknowledge bit</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>80</td></tr><tr><td rowspan=1 colspan=1>tfCL</td><td rowspan=1 colspan=1>Falltime of SCLH signal</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>40</td></tr><tr><td rowspan=1 colspan=1>trDA</td><td rowspan=1 colspan=1>Rise time of SDAH signal</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>80</td></tr><tr><td rowspan=1 colspan=1>tfDA</td><td rowspan=1 colspan=1>Fall time of SDAH signal</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>80</td></tr><tr><td rowspan=1 colspan=1>tsU;STO</td><td rowspan=1 colspan=1>Setup time for STOP condition</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1>：</td></tr><tr><td rowspan=1 colspan=1>Cb</td><td rowspan=1 colspan=1>Capacitive load for each bus line</td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>pF</td></tr><tr><td rowspan=1 colspan=1>VnH</td><td rowspan=1 colspan=1>Noise margin at high level</td><td rowspan=1 colspan=1>0.2Vdd</td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>tsp</td><td rowspan=1 colspan=1>Pulse width of spikes that must be suppressed by the input filter</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>ns</td></tr></table>

# 2.5

# Absolute maximum ratings

Stresses above those listed as “absolute maximum ratings"may cause permanent damage to the device. This is a stress rating only and functional operation of the device under these conditions is not implied.Exposure to maximum rating conditions for extended periods may affect device reliability.

Table 9. Absolute maximum ratings   

<table><tr><td rowspan=1 colspan=1>Symbol</td><td rowspan=1 colspan=1>Ratings</td><td rowspan=1 colspan=1>Maximum value</td><td rowspan=1 colspan=1>Unit</td></tr><tr><td rowspan=1 colspan=1>Vdd</td><td rowspan=1 colspan=1>Supply voltage</td><td rowspan=1 colspan=1>-0.3 to 4.8</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>Vdd_IO</td><td rowspan=1 colspan=1>I/O pins supply voltage</td><td rowspan=1 colspan=1>-0.3 to 4.8</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=1 colspan=1>Vin</td><td rowspan=1 colspan=1>Input voltage on any control pin(CS, SCL/SPC, SDA/SDI/SDO, SDO/SA0)</td><td rowspan=1 colspan=1>-0.3 to Vdd_iO +0.3</td><td rowspan=1 colspan=1>V</td></tr><tr><td rowspan=2 colspan=1>Apow</td><td rowspan=2 colspan=1>Acceleration (any axis, powered, Vdd = 1.8 V)</td><td rowspan=1 colspan=1>3000 g for 0.5 ms</td><td rowspan=1 colspan=1>g</td></tr><tr><td rowspan=1 colspan=1> 10000g for 0.2 ms</td><td rowspan=1 colspan=1>g</td></tr><tr><td rowspan=2 colspan=1>AUNP</td><td rowspan=2 colspan=1>Acceleration (any axis, unpowered)</td><td rowspan=1 colspan=1> 3000 g for 0.5 ms</td><td rowspan=1 colspan=1>g</td></tr><tr><td rowspan=1 colspan=1>10000 g for 0.2 ms</td><td rowspan=1 colspan=1>g</td></tr><tr><td rowspan=1 colspan=1>TOP</td><td rowspan=1 colspan=1>Operating temperature range</td><td rowspan=1 colspan=1>-40 to +85</td><td rowspan=1 colspan=1>℃</td></tr><tr><td rowspan=1 colspan=1>TSTG</td><td rowspan=1 colspan=1> Storage temperature range</td><td rowspan=1 colspan=1>-40 to +125</td><td rowspan=1 colspan=1>℃</td></tr><tr><td rowspan=1 colspan=1>ESD</td><td rowspan=1 colspan=1>Electrostatic discharge protection</td><td rowspan=1 colspan=1>2 (HBM)</td><td rowspan=1 colspan=1>kv</td></tr></table>

# Note:

Supply voltage on any pin should never exceed $4 . 8 ~ V .$

This device is sensitive to mechanical shock, improper handling can cause permanent damage to the part.

![](images/ca1f5f7208798d1d85f3708bffaf707df11b79bc799ec927f5933bd224706082.jpg)

This device is sensitive to electrostatic discharge (ESD),improper handling can cause permanent damage to the part.

# 3 Terminology and functionality

# 3.1

# Terminology

# 3.1.1

# Sensitivity

Sensitivity describes the gain of the sensor and can be determined by applying 1 $g$ acceleration to it. As the sensor can measure DC accelerations this can be done easily by pointing the axis of interest towards the center of the Earth, noting the output value,rotating the sensor by 180 degrees (pointing to the sky)and noting the output value again. By doing so, $\pm 1 ~ g$ acceleration is applied to the sensor. Subtracting the larger output value fromthe smaler one,and dividing the result by 2,leads to the actual sensitivity of the sensor.This value changes very little over temperature and time. The sensitivity tolerance describes the range of sensitivities of a large population of sensors.

# 3.1.2 Zero-g level offset

Zero-g level ofset describes the deviation of an actual output signal from the ideal output signalif no acceleration is present. A sensor in a steady state on a horizontal surface measures $_ { 0 \ g }$ on the $\mathsf { X } .$ -axis and $_ { 0 \ g }$ on the Y-axis whereas the Z-axis measures $1 g$ .The output is ideally in the middle of the dynamic range of the sensor (content of OUTregisters O0h,data expressed as two's complement number).A deviation from the ideal value in this case is called zero $\cdot g$ level offset. Ofset is to some extent a result of stress to the MEMS sensor and therefore the ofset can slightly change after mounting the sensor onto a printed circuit board or exposing it to extensive mechanical stress. Offset changes little over temperature,see “Zero-g level ofset change vs. temperature".

# 3.2

# Functionality

# 3.2.1

# Operating mode

Two sets of operating modes have been designed to offer the customer a broad choice of noise/power consumption combinations:

Low-noise disabled (see Table 10. Operating modes - low-noise seting disabled) Low-noise enabled (see Table 11. Operating modes - low-noise seting enabled)

Writing the LOW_NOlSE bit in CTRL6 (25h) selects the operating mode (low-noise).

One high-performance mode: focus on low noise Four low-power modes: trade-off between noise and power consumption

These operating modes are selected by writing the MODE[1:0] and LP_MODE[1:0] bits in CTRL1 (20h).

Table 10. Operating modes - low-noise setting disabled   

<table><tr><td rowspan=1 colspan=2>Parameter</td><td rowspan=1 colspan=1> High-performancemode</td><td rowspan=1 colspan=1>Low-powermode 4</td><td rowspan=1 colspan=1>Low-powermode3</td><td rowspan=1 colspan=1>Low-powermode2</td><td rowspan=1 colspan=1>Low-powermode1</td></tr><tr><td rowspan=1 colspan=2>Resolution [bit]</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>12-bit</td></tr><tr><td rowspan=1 colspan=2>ODR[Hz]</td><td rowspan=1 colspan=1>12.5 - 1600</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td></tr><tr><td rowspan=1 colspan=2>BW [Hz]</td><td rowspan=1 colspan=1>ODR/2 (N/A for1600 Hz),ODR/4, ODR/10,ODR/20</td><td rowspan=1 colspan=1>180ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>360 ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>720ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>3200ODR/4,ODR/10,ODR/20</td></tr><tr><td rowspan=1 colspan=2>Noise density [ug/√Hz]@FS = ±2 g, ODR = 200 Hz</td><td rowspan=1 colspan=1>110</td><td rowspan=1 colspan=1>160</td><td rowspan=1 colspan=1>210</td><td rowspan=1 colspan=1>300</td><td rowspan=1 colspan=1>550</td></tr><tr><td rowspan=7 colspan=1> Supply current [μA]@Vdd=1.8 V</td><td rowspan=1 colspan=1>ODR = 1.6 Hz</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1>0.65</td><td rowspan=1 colspan=1>0.55</td><td rowspan=1 colspan=1>0.45</td><td rowspan=1 colspan=1>0.38</td></tr><tr><td rowspan=1 colspan=1>ODR = 12.5 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>2.5</td><td rowspan=1 colspan=1>1.6</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>ODR = 25 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>8.5</td><td rowspan=1 colspan=1>4.5</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>1.5</td></tr><tr><td rowspan=1 colspan=1>= 50 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>16</td><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>5.5</td><td rowspan=1 colspan=1>3</td></tr><tr><td rowspan=1 colspan=1>ODR = 100 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>32</td><td rowspan=1 colspan=1>17.5</td><td rowspan=1 colspan=1>10.5</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>ODR = 200 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>63</td><td rowspan=1 colspan=1>34.5</td><td rowspan=1 colspan=1>20.5</td><td rowspan=1 colspan=1>10</td></tr><tr><td rowspan=1 colspan=1>ODR = 400,800,1600 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>=</td><td rowspan=1 colspan=1>=</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1>=</td></tr></table>

Table 11. Operating modes - low-noise setting enabled   

<table><tr><td rowspan=1 colspan=2>Parameter</td><td rowspan=1 colspan=1> High-performancemode</td><td rowspan=1 colspan=1>Low-powermode 4</td><td rowspan=1 colspan=1>Low-powermode3</td><td rowspan=1 colspan=1>Low-powermode2</td><td rowspan=1 colspan=1>Low-powermode 1</td></tr><tr><td rowspan=1 colspan=2>Resolution [bit]</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>14-bit</td><td rowspan=1 colspan=1>12-bit</td></tr><tr><td rowspan=1 colspan=2>ODR[Hz]</td><td rowspan=1 colspan=1>12.5- 1600</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td><td rowspan=1 colspan=1>1.6 - 200</td></tr><tr><td rowspan=1 colspan=2>BW [Hz]</td><td rowspan=1 colspan=1>ODR/2 (N/A for 1600Hz)，ODR/4, ODR/10,ODR/20</td><td rowspan=1 colspan=1>180ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>360ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>720ODR/4,ODR/10,ODR/20</td><td rowspan=1 colspan=1>3200ODR/4,ODR/10,ODR/20</td></tr><tr><td rowspan=1 colspan=2>Noise density [ug/√Hz]@FS = ±2 g, ODR = 200 Hz</td><td rowspan=1 colspan=1>90</td><td rowspan=1 colspan=1>130</td><td rowspan=1 colspan=1>180</td><td rowspan=1 colspan=1>240</td><td rowspan=1 colspan=1>450</td></tr><tr><td rowspan=7 colspan=1> Supply current [uA]@Vdd=1.8 V</td><td rowspan=1 colspan=1>ODR = 1.6 Hz</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1>0.7</td><td rowspan=1 colspan=1>0.6</td><td rowspan=1 colspan=1>0.5</td><td rowspan=1 colspan=1>0.4</td></tr><tr><td rowspan=1 colspan=1>ODR = 12.5 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>1.1</td></tr><tr><td rowspan=1 colspan=1>ODR = 25 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>3.5</td><td rowspan=1 colspan=1>2</td></tr><tr><td rowspan=1 colspan=1>ODR = 50 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>3.5</td></tr><tr><td rowspan=1 colspan=1>ODR = 100 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>39</td><td rowspan=1 colspan=1>21.5</td><td rowspan=1 colspan=1>13</td><td rowspan=1 colspan=1>6</td></tr><tr><td rowspan=1 colspan=1>ODR = 200 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>77</td><td rowspan=1 colspan=1>42</td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1>12</td></tr><tr><td rowspan=1 colspan=1>ODR = 400,800,1600 Hz</td><td rowspan=1 colspan=1>120</td><td rowspan=1 colspan=1>=</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>=</td><td rowspan=1 colspan=1>=</td></tr></table>

# 3.2.2

# Single data conversion on-demand mode

The device features a single data conversion on-demand mode thatis valid forboth sets of operating modes (lownoise disabled or enabled)in the four low-power modes.This mode is enabled by writing the MODE[1:0]bits to 10 in CTRL1 (20h). Low power modes are selected by writing the LP_MODE[1:0] bits in CTRL1 (20h).

The trigger for output data generation can be managed through the IC/SPl or by applying a clock signal on the INT2 pin acting here as an input by writing the SLP_MODE_ SEL bit in CTRL3 (22h):

When SLP_MODE_SEL $= 0$ ,output data generation is triggered by the clock signal on the INT2 pin (see Figure 5. Single data conversion on-demand functionality).   
When SLP_MODE $. { \mathsf { S E L } } = 1$ , output data generation starts when the SLP_MODE_1 bit is set to 1 logic through the IC/SPI. When XL data are available in the registers,this bit is automatically set to O and the device is ready for another triggered session.

)utput data are generated according to the selected low-power mode.

When output data is saved in an output register or FIFO,the device goes to power-down mode and waits for a new trigger.

All ODRs in the range from 0 to up to $2 0 0 ~ \mathsf { H z }$ are supported due to the INT2 clock input.   
A DRDY signal or FIFO flags are available on the INT1 pin.   
Power consumption is the same as that of standard low-power modes for the same ODR.

![](images/5240126eda7a595b8c7e161b23cc331737415e17d0e1431787fa3c57f5b07322.jpg)  
Figure 5. Single data conversion on-demand functionality

At the end of turn-on time T_on,the DRDY interrupt is activated,output data are available to be read and the device goes into power-down. T_on values depend on the low-power mode as follows:

T_on (typ.) $=$

. 1.20 ms for low-power mode 1   
1.70 ms for low-power mode 2   
2.30 ms for low-power mode 3   
3.55 ms for low-power mode 4

# 3.2.3

# Self-test

The self-test alows checking the sensorfunctionality without moving it.The self-test function is off when the selftest bits (ST)are programmed to O0. When the self-test bits are changed,an actuation force is applied to the sensor, simulating a definite input acceleration. In this case,the sensor outputs exhibit a change in their DC levels,whichare related to the selected fullscale through the device sensitivity.When theself-test is activated, the device output level is given by the algebraic sum ofthe signals produced by the acceleration acting on the sensor and by the electrostatic test-force.If the output signals change within the amplitude specified in Table 3.Mechanical characteristics,then the sensor is working properly and the parameters of the interface chip are within the defined specifications.

# 3.2.4

# Activity/lnactivity, Android stationary/motion-detection functions

The activity/inactivity function recognizes the device's sleep state and allows reducing system power consumption.

When the activity/inactivity function is activated by seting the INTERRUPTS_ENABLE bitin CTRL7(3Fh)and the SLEEP_ON bit in WAKE_UP_THS (34h), the LIS2DW12 automatically goes to $1 2 . 5 \mathsf { H z }$ ODR in the low-power mode previously selected by the LP_MODE[1:0] bits in CTRL1 (20h)if the sleep state condition is detected and wakes up as soon as the interrupt event has been detected, increasing the output data rate and bandwidth.

With this feature the system may be eficiently switched from low-power mode to ful performance depending on user-selectable positioning and acceleration events, thus ensuring power saving and flexibility.

The Android stationary/motion detection function only recognizes the device's sleep state.

When the Android stationary/motion-detection function is activated by seting the STATIONARY bit in WAKE_UP_DUR (35h),the LIS2DW12 detects acceleration below afixed threshold but does notchange either ODR or operating mode (high-performance mode or low-power mode) after sleep state detection.

The activity/inactivity recognition function can use the high-pass filter or the ofset outputs,this choice can be made through the USR_OFF_ON_OUT bit in CTRL7 (3Fh).

If the device is in sleep (inactivity/stationary) mode, when at least one of the axes exceeds the threshold in WAKE_UP_THS (34h), the device goes into a sleep-to-wake state (as wake-up).

For the activity/inactivity function,the device,in a wake-up state, returns to the operating mode (HPor LP)and ODR before sleep state detection.

Activity/inactivityAndroidstationary/motion-detection thresholdanddurationcanbeconfigured inthefolowing control registers:

WAKE_UP_THS (34h) WAKE_UP_DUR (35h)

# High tap/double-tap user configurability

The device embeds the possibility to select the following parameters:

single axis or multiple axes in TAP_THS_Z (32h)   
axis priority in TAP_THS_Y (31h)   
threshold value of each axis in TAP_THS_X (30h), TAP_THS_Y (31h),and TAP_THS_Z (32h)   
max time threshold between two consecutive taps for double-tap recognition, min time threshold between   
two consecutive taps to detect a new tap event in INT_DUR (33h)

# 3.2.6 Offset management

The user can manage the ofset in the output or for wake-up detection using dedicated embedded hardware (see Section 5.1: Block diagram of filters).

# 3.3

# Sensing element

A proprietary process is used to create a surface micromachined accelerometer. The technology allows procesing suspended slicon structures,which are attached to the substrate in a few points caled anchors and are free to move in the direction of the sensed acceleration. In order to be compatible with the traditional packaging techniques,a cap is placed on top of the sensing element to avoid blocking the moving parts during the molding phase of the plastic encapsulation. When an acceleration is applied to the sensor, the proof mass displaces from its nominal position,causing an imbalance in the capacitive half-bridge.This imbalance is measured using charge integration in response to a voltage pulse applied to the capacitor.

At steady-state the nominal value of the capacitors are afew pF and when an acceleration is applied, the maximum variation of the capacitive load is in the fF range.

# 3.4 IC interface

The complete measurement chain is composed of a low-noise capacitive amplifier, which converts the capacitive unbalancing of the MEMS sensor into an analog voltage using an analog-to-digital converter.

The acceleration data may be accessed through an C/SPl interface thus making the device particularly suitable for direct interfacing with a microcontroller.

The LIS2DW12 features a data-ready signal, which indicates when a new set of measured acceleration data is available, thus simplifying data synchronization in the digital system that uses the device.

# 3.5 Factory calibration

The IC interface is factory-calibrated for sensitivity (So) and zero- $\mathfrak { g }$ level offset.

The trim values are stored inside the device in nonvolatile memory. Anytime the device is turned on,the trimming parameters are downloaded into the registers to be used during active operation.This allows using the device without further calibration.If an accidental write occurs in the registers where trimming parameters are stored,the BOOT bit in CTRL2 (21h) can help to retrieve the correct trimming parameters from nonvolatile memory without the need to switch on/offthe device.This bit is automatically reset at the end of the download operation.Setting this bit has no impact on the control registers.

# 3.6

# Temperature senso

The temperature is available in OUT_T_L (ODh), OUT_T_H(OEh)stored as two's complement data,left-justified in 12-bit mode and in OUT_T (26h) stored as two's complement data, left-justified in 8-bit mode.

Refer to Table 5. Temperature sensor characteristics for the conversion factor.

# 4 Application hints

![](images/17daca870f4270ee7862e4aab2713cebaa1faa9503436517443615b714fc4e7c.jpg)  
Figure 6. LIS2DW12 electrical connections (top view)

The device core is supplied through the Vdd line while the I/O pads are supplied through the Vdd_IO line. Power supply decoupling capacitors (100 nF ceramic, $1 0 \mu \mathsf { F }$ aluminum) should be placed as near as possible to pin 9 of the device (common design practice).

All the voltage and ground supplies must be present at the same time to have proper behavior of the IC (refer to Figure 6.LIS2DW12 electrical connections (top view).It is possible to remove Vdd while maintaining Vdd_lO without blocking the communication bus,in this condition the measurement chain is powered off.

The functionality of the device and the measured acceleration data are selectable and accessible through the l²C or SPl interfaces. When using the $1 ^ { 2 } \mathsf { C }$ ,CS must be tied high (i.e. connected to Vdd_lO).

The functions,the threshold and the timing of the twointerrupt pins (INT1 and INT2)can be completely programmed by the user through the I²C/SPl interface.

Table 12. Internal pin status   

<table><tr><td rowspan=1 colspan=1>Pin#</td><td rowspan=1 colspan=1>Name</td><td rowspan=1 colspan=1>Function</td><td rowspan=1 colspan=1>Pin status</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>SCLSPC</td><td rowspan=1 colspan=1>I²C serial clock (SCL)SPl serial port clock (SPC)</td><td rowspan=1 colspan=1>Default: open drain</td></tr><tr><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>CS</td><td rowspan=1 colspan=1>Enable SPI|C/SPI mode selection1: SPl idle mode / IC communication enabled0: SPI communication mode / IC disabled</td><td rowspan=1 colspan=1>Default: input with internal pul-up(1)</td></tr><tr><td rowspan=1 colspan=1>3</td><td rowspan=1 colspan=1>SDOSAO</td><td rowspan=1 colspan=1>Serial data output (SDO)PC less significant bit of the device address (SA0)</td><td rowspan=1 colspan=1>Default: input with internal pull-up</td></tr><tr><td rowspan=1 colspan=1>4</td><td rowspan=1 colspan=1>SDASDISDO</td><td rowspan=1 colspan=1>IPC serial data (SDA)SPl serial data input (SDI)3-wire interface serial data output (SDO)</td><td rowspan=1 colspan=1>Default: (SDA) input open drain</td></tr><tr><td rowspan=1 colspan=1>5</td><td rowspan=1 colspan=1>NC</td><td rowspan=1 colspan=1> Internally not connected. Can be tied to VDD, VDDIO,or GND.</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>6</td><td rowspan=1 colspan=1>GND</td><td rowspan=1 colspan=1>0 V supply</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>7</td><td rowspan=1 colspan=1>RES</td><td rowspan=1 colspan=1>Connect to GND</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>8</td><td rowspan=1 colspan=1>GND</td><td rowspan=1 colspan=1>o V supply</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>9</td><td rowspan=1 colspan=1>VDD</td><td rowspan=1 colspan=1>Power supply</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>VDD_IO</td><td rowspan=1 colspan=1>Power supply for I/O pins</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>INT2</td><td rowspan=1 colspan=1> Interrupt pin 2. Clock input when selected in single data conversion on-demand.</td><td rowspan=1 colspan=1>Default: push-pull output forced to Gnd</td></tr><tr><td rowspan=1 colspan=1>12</td><td rowspan=1 colspan=1>INT1</td><td rowspan=1 colspan=1>Interrupt pin 1</td><td rowspan=1 colspan=1>Default: push-pull output forced to Gnd</td></tr></table>

1. In order to disable the internal pull-up on the CS pin, write 1 to the CS_PU_DISC bit in CTRL2 (21h).

# 5 Digital main blocks

# 5.1 Block diagram of filters

![](images/91f5db365793e682e6d5ab03180e04076fe0f8305a7b290023f046183c423c40.jpg)  
Figure 7. Accelerometer chain

Referring to Figure 7. Accelerometer chain, the first block is the low-pass filter 1 (LPF1) whose behavior is a function of the actual ODR and mode selected in CTRL1 (20h). The signal is then downsampled and can be either directly sent to the output registers orto the low-pass filter 2 (LPF2)or high-passfilter (HP) using the BW_FILT[1:0] bits and FDS bit in CTRL6 (25h).

In the low-pass path,it is possible to apply a user ofset determined by the X_OFS_USR (3Ch),Y_OFS_USR (3Dh),Z_OFS_USR (3Eh) register values and the USR_OFF_W bit in CTRL7 (3Fh)and send the result to the output using the USR_OFF_ON_OUT bit in CTRL7 (3Fh).

In the high-pass path,it is possible to use the high-pass filter reference mode (HP)using the HP_REF_MODE bit in CTRL7 (3Fh).

# 5.2

# Data stabilization time vs. ODR/device setting

Some data samples need to be discarded when changing the ODR in HP mode with ODR/2 bandwidth selection.   
The table below provides the number of samples to be discarded in order to obtain valid usable data.

Table 13. Number of samples to be discarded   

<table><tr><td rowspan=1 colspan=3>MODE[1:0] inCTRL1 (20h)</td><td rowspan=1 colspan=1>ODR [Hz]</td><td rowspan=1 colspan=1>BW_FILT[1:0] inCTRL6 (25h)</td><td rowspan=1 colspan=1> Samples to be discarded</td></tr><tr><td rowspan=1 colspan=3>00</td><td rowspan=1 colspan=1>-</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0</td></tr><tr><td rowspan=9 colspan=3>01</td><td rowspan=1 colspan=1>12.5</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0</td></tr><tr><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0</td></tr><tr><td rowspan=1 colspan=1>50</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>0</td></tr><tr><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=2></td><td rowspan=1 colspan=1>200</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=2></td><td rowspan=2 colspan=1></td><td rowspan=2 colspan=1>400</td><td rowspan=2 colspan=1></td><td rowspan=2 colspan=1>1</td></tr><tr><td rowspan=1 colspan=2></td></tr><tr><td rowspan=1 colspan=2></td><td rowspan=1 colspan=1>800</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>1</td></tr><tr><td rowspan=1 colspan=1>1600</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>2</td></tr></table>

# 5.3 FIFO

The LIS2DW12 embeds 32 slots of 14-bit data FIFO for each of the three output channels,X,Y,and Z of the acceleration data.This alows consistent power saving for the system,since the host processor does not need to continuously polldata from the sensor,but it can wake up only when needed and burst the significant data out from the FIFO.

The internal FlFO allows collecting 32 samples (14-bit size data) for each axis.

When the FIFO mode is other than bypass,reading the output registers (28h to 2Dh) returns the oldest FIFO sample set. In order to minimize communication between the master and slave, the address read may be automaticall incremented by the device by setting the IF_ADD_INC bit of CTRL2 (21h)to 1. The device rolls back to $_ { 0 \times 2 8 }$ when register $\scriptstyle 0 \times 2 0$ is reached.

This buffer can work according to the following five different modes:

+ Bypass mode FIFO mode Continuous-to-FIFO Bypass-to-continuous Continuous

Each mode is selected by the FMode[2:0] bits in the FIFO_CTRL (2Eh) register.

Programmable FIFO threshold is selected in FIFO_CTRL (2Eh). Status and FIFO overrun events are available in the FIFO_SAMPLES (2Fh)register and can be used to generate dedicated interupts on the INT1 and INT2 pins using the CTRL4_INT1_PAD_CTRL (23h) and CTRL5_INT2_PAD_CTRL (24h) registers.

FIFO_SAMPLES (2Fh)(FIFO_FTH)goes to 1 when the number of unread samples FIFO_SAMPLES (2Fh) (Dif[5:0]) is greater than or equal to FTH[4:0] in FIFO_CTRL (2Eh).

=TH[4:0] is equal to 0, FIFO_SAMPLES (2Fh) (FIFO_FTH) goes to 0.

FIFO_SAMPLES (2Fh) (FIFO_OVR) is equal to 1 if a FIFO slot is overwritten

FIFO_SAMPLES (2Fh)(Dif[5:0]) contains stored data levels of unread samples.When Dif[5:0] is equal to D00000, FIFO is empty.When Dif[5:0] is equal to 100000, FIFO is full and the unread samples are 32.

To guarantee the corect acquisition of data during the switching into and out of FIFO,the first sample acquired must be discarded.

When the FIFOthreshold statusflag isO logic,FIFOfiling is lower than the threshold level and when 1 logic, FIFO filling is equal to or higher than the threshold level.

# 5.3.1 Bypass mode

In bypass mode (FIFO_CTRL (2Eh) (FMode $[ 2 ; 0 ] ) = 0 0 0$ ), the FIFO is not operational, no data is collected in FIFO memory,and it remains empty with the only actual sample available in the output registers.

Bypass mode is also used to reset the FIFO when in FIFO mode

For each channel,only the first address is used. When new data is available,the old data is overwriten.

# 5.3.2 FIFO mode

In FIFO mode (FIFO_CTRL (2Eh)(FMode [2:0])= 001) data from the X,Y,and Z channels are stored in the FIFO until it is full when 32 unread samples are stored in memory, data collecting is stopped.

To reset the FIFO content, bypass mode should be written in the FIFO_CTRL (2Eh)register,setting the FMODE [2:0] bits to O00.After this reset command,it is possible to restart FIFOmode, writing the value 001 in FIFO_CTRL (2Eh)(FMODE [2:0]).

The FIFO buffer can memorize 32 slots of X, Y, and Z data.

# 5.3.3 Continuous mode

Continuous mode (FIFO_CTRL (2Eh) (FMode[2:0] $=$ 110) provides a continuous FIFO update: when 32 unread samples are stored in memory,as new data arrives the oldest data is discarded and overwritten bythe newer.

A FIFO threshold flag FIFO_SAMPLES (2Fh)(FIFO_FTH)is asserted when the number of unread samples in FIFO is greater than or equal to (FIFO_CTRL (2Eh)FTH[4:0]).

It is possible to route FIFO_SAMPLES (2Fh)(FTH)to the INT1 pin by writing the INT1_FTHbit to 1 in register CTRL4_INT1_PAD_CTRL (23h) or to the INT2 pin by writing the INT2_FTH bit to 1 in register CTRL5_INT2_PAD_CTRL (24h).

If an overrun occurs,the oldest sample in FIFO is overwriten and the FIFO_OVR flag in FIFO_SAMPLES (2Fh) is asserted.

In order toempty the FIFO before it is fu,t is also possible topullfrom FIFO the number of unread samples available in FIFO_SAMPLES (2Fh) (DIif[5:0]).

# 5.3.4 Continuous-to-FIFO mode

In continuous-to-FIFO mode FIFO_CTRL (2Eh)(FMode $[ 2 ; 0 ] = 0 1 1$ ), FIFO operates in continuous mode and FIFO mode starts upon an internal trigger event. When the FiFOis full,data colecting is stopped.The trigger could be a single or double tap,wake-up,free-fal,6D interrupt,orany combination of these events,，but every interrupthas to be routed to the corresponding pad to be used as a trigger.

![](images/ab8aad7232771bf3c592339843e19730d9ccf63132c62d56c303c9c631f78325.jpg)  
Figure 8. Continuous-to-FIFO mode

![](images/c166fe1c199f0256d5a6a3a97d48b20f31605f332f7cbf1f44c9cc0e3872e8a2.jpg)  
Figure 9. Trigger event to FIFO for continuous-to-FIFO mode

# 5.3.5 Bypass-to-continuous mode

In bypass-to-continuous mode (FIFO_CTRL (2Eh)(FMode $[ 2 ; 0 ] = 1 0 0$ ), datameasurement storage inside FIFO starts incontinuous mode upon an internal trigger event,then the sample that follws the trigger is available in FIFO.The trigger could be a single or double tap, wake-up,free-fal, 6D interupt, orany combination of these events, but every interrupt has to be routed to the corresponding pad to be used as a trigger.

![](images/c263df4b59108ee1d885f988f46bb817d10d52400ebb1fb27f7d4c5d76d57a04.jpg)  
Figure 10. Bypass-to-continuous mode   
Trigger event

![](images/c358e1e294913a2097c1e09b69853a873bfc65f6f504f47ea8f0e9d3a7584a5c.jpg)  
Figure 11. Trigger event to FlFO for bypass-to-continuous mode

# 6 Digital interfaces

The registers embedded inside the LIS2DW12 may be accessed through both the $1 ^ { 2 } \mathsf { C }$ and SPl serial interfaces.   
The latter may be software configured to operate either in 3-wire or 4-wire interface mode.

The serial interfaces are mapped to the same pins.To select/exploit the I²C interface, the CS line must be tied high (that is,connected to Vdd_iO).

Table 14. Serial interface pin description   

<table><tr><td> Pin name</td><td>Pin description</td></tr><tr><td rowspan="3">CS</td><td>Enable SPI</td></tr><tr><td>I²C/SPI mode selection</td></tr><tr><td>(1: SPl idle mode / I²C communication enabled; 0: SPl communication mode / I²C disabled)</td></tr><tr><td>SCL SPC</td><td>I²C serial clock (SCL)</td></tr><tr><td rowspan="3">SDA SDI</td><td>SPI serial port clock (SPC)</td></tr><tr><td>I²C serial data (SDA)</td></tr><tr><td> SPl serial data input (SDI)</td></tr><tr><td>SDO</td><td> 3-wire interface serial data output (SDO)</td></tr><tr><td>SAO</td><td>I²C address selection (SA0)</td></tr><tr><td>SDO</td><td> SPI serial data output (SDO)</td></tr></table>

# 6.1

# ²C serial interface

The LIS2DW12 $1 ^ { 2 } \mathsf { C }$ is a bus slave. The $1 ^ { 2 } \mathsf { C }$ is employed to write data into registers whose content can also be read back.

The relevant I²C terminology is given in the table below.

Table 15. IC terminology   

<table><tr><td rowspan=1 colspan=1>Term</td><td rowspan=1 colspan=1>Description</td></tr><tr><td rowspan=1 colspan=1>Transmitter</td><td rowspan=1 colspan=1>The device that sends data to the bus</td></tr><tr><td rowspan=1 colspan=1>Receiver</td><td rowspan=1 colspan=1>The device that receives data from the bus</td></tr><tr><td rowspan=1 colspan=1>Master</td><td rowspan=1 colspan=1>The device that initiates a transfer, generates clock signals,and terminates a transfer</td></tr><tr><td rowspan=1 colspan=1>Slave</td><td rowspan=1 colspan=1>The device addressed by the master</td></tr></table>

There are two signals associated with the $1 ^ { 2 } \mathsf { C }$ bus: the serial clock line (SCL) and the serial data line (SDA). The latter is a bidirectional line used for sending and receiving the data to/from the interface. Both the lines must be connected to Vdd_IO through an external pull-up resistor. When the bus is free,both the lines are high.

The $\mathsf { I } ^ { 2 } \mathsf { C }$ interface supports fast mode ( $4 0 0 ~ \mathsf { k H z }$ ） ${ } ^ { 1 2 } \mathrm { C }$ standards as well as normal mode.   
In order to disable the $1 ^ { 2 } \mathsf { C }$ block, CTRL2 (21h) (I2C_DISABLE) $= 1$ must be set.

# 6.1.1 l²C operation

The transaction on the bus is started through a start (ST) signal. A start condition is defined as a high to low transition on the dataline while the SCLlineis held high. Afterthis has been transmited bythe master,the bus is considered busy.The next byte of data transmitted after the start condition containsthe address of the slave in the first7 bits andthe eighth bit tells whether the master is receiving data from the slave or transmitting data to the slave.When an address is sent, each device in the system compares the first seven bits after a start condition with its address. If they match, the device considers itself addressed by the master.

The slave address (SAD)associated to the LIS2DW12 is O01100xb where the x bit is modified by the SA0/SDO pin in order to modify the device address.If the SA0/SDO pin is connected to the supply voltage,the address is 0011001b,otherwise if the SA0/SDO pin is connected to ground, the address is O01100ob.This solution permits to connect and address two different accelerometers to the same $1 ^ { 2 } \mathrm { C }$ lines.

Data transfer with acknowledge is mandatory.The transmiter must release the SDA line during the acknowledge pulse.The receiver must then pullthe data line low so that it remains stable low during the high period of the acknowledge clock pulse. Areceiver that has been addressed is obliged to generate an acknowledge after each byte of data received.

The C embedded inside the LIS2DW12 behaves like a slave device and the folowing protocol must be adhered to.After the start condition (ST), a slave address is sent. Once a slave acknowledge (SAK) has been returned,an 8-bit subaddress (SUB) is transmited: the 7LSb represents the actual register address while the CTRL2 (21h) (IF_ADD_INC) bit defines the address increment.

The slave address is completed with a read/write bit. If the bit is 1 (read),a repeated start (SR) condition must be issued after the two subaddress bytes.If the bit is O(write) the master transmits to the slave with direction unchanged. Table 16 explains how the SAD+read/write bit pattern is composed, listing al the possible configurations.

Table 16. SAD+read/write patterns   

<table><tr><td rowspan=1 colspan=1>Command</td><td rowspan=1 colspan=1>SAD[6:1]</td><td rowspan=1 colspan=1>SAD[0] = SA0</td><td rowspan=1 colspan=1>R/W</td><td rowspan=1 colspan=1>SAD+R/W</td></tr><tr><td rowspan=1 colspan=1>Read</td><td rowspan=1 colspan=1>001100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>00110001 (31h)</td></tr><tr><td rowspan=1 colspan=1>Write</td><td rowspan=1 colspan=1>001100</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>00110000 (30h)</td></tr><tr><td rowspan=1 colspan=1>Read</td><td rowspan=1 colspan=1>001100</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>00110011 (33h)</td></tr><tr><td rowspan=1 colspan=1>Write</td><td rowspan=1 colspan=1>001100</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>00110010 (32h)</td></tr></table>

Table 17. Transfer when master is writing one byte to slave   

<table><tr><td rowspan=1 colspan=1>Master</td><td rowspan=1 colspan=1>ST</td><td rowspan=1 colspan=1> SAD + W</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SUB</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SP</td></tr><tr><td rowspan=1 colspan=1>Slave</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td></tr></table>

Table 18. Transfer when master is writing multiple bytes to slave   

<table><tr><td rowspan=1 colspan=1>Master</td><td rowspan=1 colspan=1>ST</td><td rowspan=1 colspan=1> SAD + W</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SUB</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SP</td></tr><tr><td rowspan=1 colspan=1>Slave</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td></tr></table>

# Table 19. Transfer when master is receiving (reading) one byte of data from slave

<table><tr><td rowspan=1 colspan=1>Master</td><td rowspan=1 colspan=1>ST</td><td rowspan=1 colspan=1> SAD + W</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SUB</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SR</td><td rowspan=1 colspan=1>SAD + R</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>NMAK</td><td rowspan=1 colspan=1>SP</td></tr><tr><td rowspan=1 colspan=1>Slave</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

Table 20. Transfer when master is receiving (reading) multiple bytes of data from slave   

<table><tr><td rowspan=1 colspan=1>Master</td><td rowspan=1 colspan=1>ST</td><td rowspan=1 colspan=1> SAD+W</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SUB</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SR</td><td rowspan=1 colspan=1>SAD+R</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>MAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>MAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>NMAK</td><td rowspan=1 colspan=1>SP</td></tr><tr><td rowspan=1 colspan=1>Slave</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>SAK</td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>DATA</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1></td></tr></table>

Data are transmited in byte format (DATA). Each data transfer contains 8 bits.The number of bytes transferred per transfer is unlimited.Data is transfered with the most significant bit (MSb)first.If a receiver cannot receive another complete byte of data untilit has performed some other function,it can hold the clock line,SCL low to force the transmiter into a wait state. Data transfer only continues when the receiver is readyfor another byte and releases the data line.Ifa slave receiver does not acknowledge the slave address (that is,itis not able to receive because itis performing some real-time function)the dataline must be left high by the slave.The master can then aborthetransfer.Alowto high transition on the SDAline while the SCLlineis high is defined as astop condition. Each data transfer must be terminated by the generation of a stop (SP) condition.

In the presented communication format MAK is master acknowledge and NMAK is no master acknowledge.

# 6.2

# SPl bus interface

The LIS2DW12 SPl is a bus slave. The SPl allows writing to and reading from the registers of the device.   
The serial interface interacts with the application using four wires: CS, SPC, SDl, and SDO.

![](images/4bd772a140457fe89a2c6c15379fab152daf1936140c8d65f9923c12c60c1d3e.jpg)  
Figure 12. Read and write protocol

CS enables the serial port and it is controled by the SPl master.It goes low at the start of the transmission and goes back high at the end. SPC is the serial port clock and it is controlled by the SPl master.It is stopped high when CS is high (no transmission). SDl and SDO are respectively the serial port data input and output. Those lines are driven at the falling edge of SPC and should be captured at the rising edge of SPC.

Both the read register and write register commands are completed in 16 clock pulses or in multiples of 8 in case of multiple read/write bytes. Bit duration is the time between two faling edges of SPC.The first bit (bit O)starts al thefirst fallng edge of SPC afterthe fallng edge of CS while the last bit (bit 15,bit 23,..)starts ate last falling edge of SPC just before the rising edge of Cs.

bit 0: RW bit. When O, the data DI(7:0)is writen into the device.When 1,the data DO(7:0)from the device is read. In the latter case, the chip drives SDO at the start of bit 8.

bit 1-7: address AD(6:0). This is the address field of the indexed register.

bit 8-15: data Dl(7:O) (write mode). This is the data that is written into the device (MSb first).

3-15: data DO(7:O) (read mode). This is the data that is read from the device (MSb first).

In multiple read/write commands,additional blcks of 8 clock periods are added. When the CTRL2 (21h) (IF_ADD_INC)bit is 0,the address used to read/write data remains the same for every block. When the CTRL2 (21h) (IF_ADD_INC) bit is 1, the address used to read/write data is increased at every block.

The function and the behavior of SDl and SDO remain unchanged.

# 6.2.1 SPI read

![](images/5f182eff240c42abaa73ccdf861de6e9b0c849f196f261547fcec155e63157fd.jpg)  
Figure 13. SPl read protocol

The SPl read command is performed with 16 clock pulses.A multiple byte read command is performed by adding blocks of 8 clock pulses to the previous one.

bit 0: READ bit. The value is 1.   
bit 1-7: address AD(6:O). This is the address field of the indexed register.   
bit 8-15: data DO(7:O) (read mode). This is the data that is read from the device (MSb first).   
bit 16-. : data DO(..-8). Additional data in multiple byte reads.

![](images/b2ee25937100494985fd620c000473ab3e71a8dc2adc8f5182e787f2df1b3e98.jpg)  
Figure 14. Multiple byte SPl read protocol (2-byte example)

# 6.2.2 SPl write

![](images/5ddb70d7e6446504bcc26dd5af96e024d23f9f4e40a17903f9327ea8e40e4c3b.jpg)  
Figure 15. SPl write protocol

The SPl write command is performed with 16 clock pulses.A multiple byte write command is performed by adding blocks of 8 clock pulses to the previous one.

bit O: WRITE bit. The value is 0.   
bit 1 -7: address AD(6:0). This is the address field of the indexed register.   
bit 8-15: data Dl(7:O) (write mode). This is the data that is written inside the device (MSb first).   
bit 16-. : data Dl(..-8). Additional data in multiple byte writes.

![](images/f4f5fcf377bc256fa20029b23051d8fe635d70ebae504e07f29ed9b21c6b5d97.jpg)  
Figure 16. Multiple byte SPl write protocol (2-byte example)

# 6.2.3 SPl read in 3-wire mode

3-wire mode is entered by setting the CTRL2 (21h)(SIM) bit equal to 1 (SPI serial interface mode selection).

![](images/6f2a3428700129706f14555539b8f6717ec8d62a90683e6ab443119622564553.jpg)  
Figure 17. SPl read protocol in 3-wire mode

The SPl read command is performed with 16 clock pulses: bit O: READ bit. The value is 1.   
bit 1-7: address AD(6:O). This is the address field of the indexed register.   
bit 8-15: data DO(7:0)(read mode). This is the data that is read from the device (MSb first).   
A multiple read command is also available in 3-wire mode.

# 7 Register mapping

The table given below provides a list of the 8-bit registers embedded in the device and the coresponding addresses.

Table 21. Register map   

<table><tr><td rowspan=2 colspan=1>Name</td><td rowspan=2 colspan=2> Type(1)</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=2>Register address</td><td rowspan=2 colspan=1> Default</td></tr><tr><td rowspan=1 colspan=1>Hex</td><td rowspan=1 colspan=1>Binary</td><td></td></tr><tr><td rowspan=1 colspan=1>OUT_T_L</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>0D</td><td rowspan=1 colspan=1>00001101</td><td rowspan=1 colspan=1>00000000</td><td rowspan=2 colspan=1>Temp sensor output</td></tr><tr><td rowspan=1 colspan=1>OUT_T_H</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>0E</td><td rowspan=1 colspan=1>00001110</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>WHO_AM_I</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>0F</td><td rowspan=1 colspan=1>0000111</td><td rowspan=1 colspan=1>01000100</td><td rowspan=1 colspan=1>Who am I ID</td></tr><tr><td rowspan=1 colspan=1>RESERVED</td><td rowspan=1 colspan=2>，</td><td rowspan=1 colspan=1>10-1F</td><td rowspan=1 colspan=1></td><td rowspan=1 colspan=1>：</td><td rowspan=1 colspan=1>RESERVED</td></tr><tr><td rowspan=1 colspan=1>CTRL1</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>20</td><td rowspan=1 colspan=1>00100000</td><td rowspan=1 colspan=1>00000000</td><td rowspan=6 colspan=1>Control registers</td></tr><tr><td rowspan=1 colspan=1>CTRL2</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>21</td><td rowspan=1 colspan=1>00100001</td><td rowspan=1 colspan=1>00000100</td></tr><tr><td rowspan=1 colspan=1>CTRL3</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>22</td><td rowspan=1 colspan=1>00100010</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>CTRL4_INT1_PAD_CTRL</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>23</td><td rowspan=1 colspan=1>00100011</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>CTRL5_INT2_PAD_CTRL</td><td rowspan=1 colspan=2>RW</td><td rowspan=1 colspan=1>24</td><td rowspan=1 colspan=1>00100100</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>CTRL6</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>25</td><td rowspan=1 colspan=1>00100101</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>OUT_T</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>26</td><td rowspan=1 colspan=1>00100110</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Temp sensor output</td></tr><tr><td rowspan=1 colspan=1>STATUS</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>27</td><td rowspan=1 colspan=1>00100111</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Status data register</td></tr><tr><td rowspan=1 colspan=1>OUT_X_L</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>28</td><td rowspan=1 colspan=1>00101000</td><td rowspan=1 colspan=1>00000000</td><td rowspan=6 colspan=1> Output registers</td></tr><tr><td rowspan=1 colspan=1>OUT_X_H</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>29</td><td rowspan=1 colspan=1>00101001</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>OUT_Y_L</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>2A</td><td rowspan=1 colspan=1>00101010</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>OUT_Y_H</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>2B</td><td rowspan=1 colspan=1>00101011</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>OUT_Z_L</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>2C</td><td rowspan=1 colspan=1>00101100</td><td rowspan=1 colspan=1>0000000</td></tr><tr><td rowspan=1 colspan=1>OUT_Z_H</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>2D</td><td rowspan=1 colspan=1>00101101</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>FIFO_CTRL</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>2E</td><td rowspan=1 colspan=1>00101110</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>FIFO control register</td></tr><tr><td rowspan=1 colspan=1>FIFO_SAMPLES</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>2F</td><td rowspan=1 colspan=1>00101111</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Unread samples stored in FIFO</td></tr><tr><td rowspan=1 colspan=1>TAP_THS_X</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>30</td><td rowspan=1 colspan=1>00110000</td><td rowspan=1 colspan=1>00000000</td><td rowspan=3 colspan=1>Tap thresholds</td></tr><tr><td rowspan=1 colspan=1>TAP_THS_Y</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>31</td><td rowspan=1 colspan=1>00110001</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>TAP_THS_Z</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>32</td><td rowspan=1 colspan=1>00110010</td><td rowspan=1 colspan=1>00000000</td></tr><tr><td rowspan=1 colspan=1>INT_DUR</td><td rowspan=1 colspan=2>RMW</td><td rowspan=1 colspan=1>33</td><td rowspan=1 colspan=1>00110011</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Interrupt duration</td></tr><tr><td rowspan=1 colspan=1>WAKE_UP_THS</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>34</td><td rowspan=1 colspan=1>00110100</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Tap/double-tap selection,inactity enable,wake-up threshold</td></tr><tr><td rowspan=1 colspan=1>WAKE_UP_DUR</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>35</td><td rowspan=1 colspan=1>00110101</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Wake-up duration</td></tr><tr><td rowspan=1 colspan=1>FREE_FALL</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>36</td><td rowspan=1 colspan=1>00110110</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Free-fall configuration</td></tr><tr><td rowspan=1 colspan=1>STATUS_DUP</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>37</td><td rowspan=1 colspan=1>00110111</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Status register</td></tr><tr><td rowspan=1 colspan=1>WAKE_UP_SRC</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>38</td><td rowspan=1 colspan=1>00111000</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Wake-up source</td></tr><tr><td rowspan=1 colspan=1>TAP_SRC</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>39</td><td rowspan=1 colspan=1>00111001</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1>Tap source</td></tr><tr><td rowspan=1 colspan=1>SIXD_SRC</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>3A</td><td rowspan=1 colspan=1>00111010</td><td rowspan=1 colspan=1>0000000</td><td rowspan=1 colspan=1>6D source</td></tr><tr><td rowspan=1 colspan=1>ALL_INT_SRC</td><td rowspan=1 colspan=2>R</td><td rowspan=1 colspan=1>3B</td><td rowspan=1 colspan=1>00111011</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>X_OFS_USR</td><td rowspan=1 colspan=2>R/W</td><td rowspan=1 colspan=1>3C</td><td rowspan=1 colspan=1>00111100</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1></td></tr></table>

<table><tr><td rowspan=2 colspan=1>Name</td><td rowspan=2 colspan=1>Type(1)</td><td rowspan=1 colspan=2>Register address</td><td rowspan=2 colspan=1>Default</td><td rowspan=2 colspan=1>Comment</td></tr><tr><td rowspan=1 colspan=1>Hex</td><td rowspan=1 colspan=1>Binary</td></tr><tr><td rowspan=1 colspan=1>Y_OFS_USR</td><td rowspan=1 colspan=1>R/W</td><td rowspan=1 colspan=1>3D</td><td rowspan=1 colspan=1>00111110</td><td rowspan=1 colspan=1>0000000</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>Z_OFS_USR</td><td rowspan=1 colspan=1>R/W</td><td rowspan=1 colspan=1>3E</td><td rowspan=1 colspan=1>00000100</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1></td></tr><tr><td rowspan=1 colspan=1>CTRL7</td><td rowspan=1 colspan=1>RW</td><td rowspan=1 colspan=1>3F</td><td rowspan=1 colspan=1>00000100</td><td rowspan=1 colspan=1>00000000</td><td rowspan=1 colspan=1></td></tr></table>

1. $R =$ read-only register, $R W =$ readable/writable register

Registers marked as Reserved must not be changed. Writing to those registers may cause permanent damage to the device.

The content of the registers that are loaded at boot should not be changed.They contain the factory calibration values. Their content is automatically restored when the device is powered up.

# 8 Register description

# 8.1

# OUT_T_L (ODh)

Temperature output register in 12-bit resolution (R)

Table 22. OUT_T_L register   

<table><tr><td rowspan=1 colspan=1>TEMP3</td><td rowspan=1 colspan=1>TEMP2</td><td rowspan=1 colspan=1>TEMP1</td><td rowspan=1 colspan=1>TEMPO</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

Table 23. OUT_T_L register description   

<table><tr><td>TEMP[3:0]</td><td>The 8 least significant bits of the temperature sensor output. 0 LSB = 25°C. Sensitivity = 16 LSB/C.</td></tr><tr><td></td><td>Together with OUT_T_H (OEh),it forms the output value expressed as a 16-bit word in two&#x27;s complement</td></tr></table>

# 8.2

# OUT_T_H (OEh)

Temperature output register in 12-bit resolution (R)

Table 24. OUT_T_H register   

<table><tr><td rowspan=1 colspan=1>TEMP11</td><td rowspan=1 colspan=1>TEMP10</td><td rowspan=1 colspan=1>TEMP9</td><td rowspan=1 colspan=1>TEMP8</td><td rowspan=1 colspan=1>TEMP7</td><td rowspan=1 colspan=1>TEMP6</td><td rowspan=1 colspan=1>TEMP5</td><td rowspan=1 colspan=1>TEMP4</td></tr></table>

Table 25. OUT_T_H register description   

<table><tr><td>TEMP[11:4]</td><td>The 8 most significant bits of the temperature sensor output. 0 LSB = 25°C. Sensitivity = 16 LSB/C. Together with OUT_T_L (ODh), it forms the output value expressed as a 16-bit word in two&#x27;s complement</td></tr></table>

# 8.3

# WHO_AM_I (0Fh)

Who_AM_I register (R). This register is a read-only register. Its value is fixed at 44h.

Table 26. WHO_AM_I register default values   

<table><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

# 8.4

# CTRL1 (20h)

Control register 1 (R/W)

Table 27. Control register 1   

<table><tr><td rowspan=1 colspan=1>ODR3</td><td rowspan=1 colspan=1>ODR2</td><td rowspan=1 colspan=1>ODR1</td><td rowspan=1 colspan=1>ODRO</td><td rowspan=1 colspan=1>MODE1</td><td rowspan=1 colspan=1>MODEO</td><td rowspan=1 colspan=1>LP_MODE1</td><td rowspan=1 colspan=1>LP_MODE0</td></tr></table>

Table 28. Control register 1 description   

<table><tr><td rowspan=1 colspan=1>ODR[3:0]</td><td rowspan=1 colspan=1> Output data rate and mode selection (see Table 29. Data rate configuration)</td></tr><tr><td rowspan=1 colspan=1>MODE[1:0]</td><td rowspan=1 colspan=1> Mode selection (see Table 30. Mode selection)</td></tr><tr><td rowspan=1 colspan=1>LP_MODE[1:0]</td><td rowspan=1 colspan=1>Low-power mode selection (see Table 31. Low-power mode selection)</td></tr></table>

ODR[3:0]is used to setthe powermode and ODR selection.The following table lists the bitsetings for powerdown mode and each available frequency.

Table 29. Data rate configuration   

<table><tr><td rowspan=1 colspan=1>ODR[3:0]</td><td rowspan=1 colspan=1> Power mode / data rate configuration</td></tr><tr><td rowspan=1 colspan=1>0000</td><td rowspan=1 colspan=1>Power-down</td></tr><tr><td rowspan=1 colspan=1>0001</td><td rowspan=1 colspan=1>High-performance /low-power mode 12.5 /1.6 Hz</td></tr><tr><td rowspan=1 colspan=1>0010</td><td rowspan=1 colspan=1>High-performance /low-power mode 12.5 Hz</td></tr><tr><td rowspan=1 colspan=1>0011</td><td rowspan=1 colspan=1>High-performance /low-power mode 25 Hz</td></tr><tr><td rowspan=1 colspan=1>0100</td><td rowspan=1 colspan=1>High-performance /low-power mode 50 Hz</td></tr><tr><td rowspan=1 colspan=1>0101</td><td rowspan=1 colspan=1>High-performance /low-power mode 100 Hz</td></tr><tr><td rowspan=1 colspan=1>0110</td><td rowspan=1 colspan=1>High-performance /low-power mode 200 Hz</td></tr><tr><td rowspan=1 colspan=1>0111</td><td rowspan=1 colspan=1> High-performance /low-power mode 400 /200 Hz</td></tr><tr><td rowspan=1 colspan=1>1000</td><td rowspan=1 colspan=1>High-performance /low-power mode 80o / 200 Hz</td></tr><tr><td rowspan=1 colspan=1>1001</td><td rowspan=1 colspan=1>High-performance /low-power mode 1600 / 200 Hz</td></tr></table>

Table 30. Mode selection   

<table><tr><td rowspan=1 colspan=1>MODE[1:0]</td><td rowspan=1 colspan=1> Mode and resolution</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>Low-power mode (12/14-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>High-performance mode (14-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>Single data conversion on-demand mode (12/14-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>11</td><td></td></tr></table>

Table 31. Low-power mode selection   

<table><tr><td rowspan=1 colspan=1>LP_MODE[1:0]</td><td rowspan=1 colspan=1>Power mode and resolution</td></tr><tr><td rowspan=1 colspan=1>00</td><td rowspan=1 colspan=1>Low-power mode 1 (12-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>Low-power mode 2 (14-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>Low-power mode 3 (14-bit resolution)</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>Low-power mode 4 (14-bit resolution)</td></tr></table>

# 8.5

# CTRL2 (21h)

Control register 2 (R/W)

Table 32. Control register 2   

<table><tr><td rowspan=1 colspan=1>BOOT</td><td rowspan=1 colspan=1>SOFTRESET</td><td rowspan=1 colspan=1>0(1)</td><td rowspan=1 colspan=1>CS_PU_DISC</td><td rowspan=1 colspan=1>BDU</td><td rowspan=1 colspan=1>IF_ADD_INC</td><td rowspan=1 colspan=1>12C_DISABLE</td><td rowspan=1 colspan=1>SIM</td></tr></table>

1．This bit must be set to O for the correct operation of the device.

<table><tr><td rowspan=1 colspan=1>BOOT</td><td rowspan=1 colspan=1>Boot enables retrieving the correct trimming parameters from nonvolatile memory into registers wheretrimming parameters are stored.Once the operation is over, this bit automatically returns to 0.Default value: 0 (0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>SOFT_RESET</td><td rowspan=1 colspan=1> Soft reset acts as reset for all control registers, then goes to 0.Default value: 0 (0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>CS_PU_DISC</td><td rowspan=1 colspan=1>Disconnect CS pull-up. Default value: 0(0: pull-up connected to CS pin;1: pull-up disconnected to CS pin)</td></tr><tr><td rowspan=1 colspan=1>BDU</td><td rowspan=1 colspan=1>Block data update. Default value: 0(0: continuous update; 1: output registers not updated until MSB and LSB read)</td></tr><tr><td rowspan=1 colspan=1>IF_ADD_INC</td><td rowspan=1 colspan=1>Register address automaticall incremented during multiple byte access with a serial interface (I²C or SPl).Default value: 1(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>I2C_DISABLE</td><td rowspan=1 colspan=1>Disable l²C communication protocol. Default value: 0(0: SPl and I²C interfaces enabled; 1: IC mode disabled)</td></tr><tr><td rowspan=1 colspan=1>SIM</td><td rowspan=1 colspan=1>SPl serial interface mode selection. Default value: 0(0: 4-wire interface; 1: 3-wire interface)</td></tr></table>

The BDU bit is used to inhibit the update ofthe output registers until both upperand lower register parts are read. In default mode $\left( \mathsf { B D U } = 0 \right)$ ) the output register values are updated continuously. When the BDU is activated $( \mathsf { B D U } = 1$ ), the content of the output registers is not updated until both MSB and LSB are read which avoids reading values related to different sample times.

# 8.6

# CTRL3 (22h)

Control register 3 (R/W)

Table 33. Control register 3   

<table><tr><td rowspan=1 colspan=1>ST2</td><td rowspan=1 colspan=1>ST1</td><td rowspan=1 colspan=1>PP_OD</td><td rowspan=1 colspan=1>LIR</td><td rowspan=1 colspan=1>H_LACTIVE</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>SLP_MODE_SEL</td><td rowspan=1 colspan=1>SLP_MODE_1</td></tr></table>

Table 34. Control register 3 description   

<table><tr><td rowspan=1 colspan=1>ST[2:1]</td><td rowspan=1 colspan=1>Enables self-test. Default value: 00(00: self-test disabled; other: see Table 35. Self-test mode selection)</td></tr><tr><td rowspan=1 colspan=1>PP_OD</td><td rowspan=1 colspan=1>Push-pull/open-drain selection on interrupt pad. Default value: 0(0: push-pull; 1: open-drain)</td></tr><tr><td rowspan=1 colspan=1>LIR</td><td rowspan=1 colspan=1>Latched interrupt. Switches between latched (1 logic)and pulsed (0 logic) mode for function source signalsand interrupts routed to pins (wake-up, single/double-tap). Default value: 0(0: interrupt request not latched; 1: interrupt request latched)</td></tr><tr><td rowspan=1 colspan=1>H_LACTIVE</td><td rowspan=1 colspan=1>Interrupt active high, low. Default value: 0(0: active high; 1: active low)</td></tr><tr><td rowspan=1 colspan=1>SLP_MODE_SEL</td><td rowspan=1 colspan=1>Single data conversion on demand mode selection:(0: enabled with external trigger on INT2;1: enabled by IC/SPI writing SLP_MODE_1 to 1)</td></tr><tr><td rowspan=1 colspan=1>SLP_MODE_1</td><td rowspan=1 colspan=1>Single data conversion on-demand mode enable.When SLP_MODE_SEL= 1 and this bit is set to 1 logic, single data conversion on-demand mode starts.When accelerometer data are available in the registers,this bit is set to O automatically and the device is ready for another triggered session.</td></tr></table>

Table 35. Self-test mode selection   

<table><tr><td rowspan=1 colspan=1>ST2</td><td rowspan=1 colspan=1>ST1</td><td rowspan=1 colspan=1> Self-test mode</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>Normal mode</td></tr><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>Positive sign self-test</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>Negative sign self-test</td></tr><tr><td rowspan=1 colspan=1>1</td><td rowspan=1 colspan=1>1</td><td></td></tr></table>

# 8.7

# CTRL4_INT1_PAD_CTRL (23h)

Control register 4 (R/W)

Table 36. Control register 4   

<table><tr><td rowspan=1 colspan=1>INT1_6D</td><td rowspan=1 colspan=1>INT1SINGLE_TAP</td><td rowspan=1 colspan=1>INT1_WU</td><td rowspan=1 colspan=1>INT1_FF</td><td rowspan=1 colspan=1>INT1_TAP</td><td rowspan=1 colspan=1>INT1DIFF5</td><td rowspan=1 colspan=1>INT1FTH</td><td rowspan=1 colspan=1>INT1DRDY</td></tr></table>

Table 37. Control register 4 description   

<table><tr><td rowspan=1 colspan=1>INT1_6D</td><td rowspan=1 colspan=1>6D recognition is routed to INT1 pad. Default: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_SINGLE_TAP</td><td rowspan=1 colspan=1>Single-tap recognition is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_WU</td><td rowspan=1 colspan=1>Wake-up recognition is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_FF</td><td rowspan=1 colspan=1>Free-fal recognition is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_TAP</td><td rowspan=1 colspan=1>Double-tap recognition is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_DIFF5</td><td rowspan=1 colspan=1>FIFO fullrecognition is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_FTH</td><td rowspan=1 colspan=1>FIFO threshold interrupt is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT1_DRDY</td><td rowspan=1 colspan=1>Data-ready is routed to INT1 pad. Default value: 0(0: disabled; 1: enabled)</td></tr></table>

# 8.8

# CTRL5_INT2_PAD_CTRL (24h)

Control register 5 (R/W)

Table 38. Control register 5   

<table><tr><td rowspan=1 colspan=1>INT2_SLEEP_STATE</td><td rowspan=1 colspan=1>INT2SLEEP_CHG</td><td rowspan=1 colspan=1>INT2BOOT</td><td rowspan=1 colspan=1>INT2_DRDY_T</td><td rowspan=1 colspan=1>INT2_OVR</td><td rowspan=1 colspan=1>INT2DIFF5</td><td rowspan=1 colspan=1>INT2FTH</td><td rowspan=1 colspan=1>INT2DRDY</td></tr></table>

Table 39. Control register 5 description   

<table><tr><td rowspan=1 colspan=1>INT2_SLEEP_STATE</td><td rowspan=1 colspan=1>Enables routing SLEEP_STATE to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_SLEEP_CHG</td><td rowspan=1 colspan=1>Sleep change status routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_BOOT</td><td rowspan=1 colspan=1>Boot state routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_DRDY_T</td><td rowspan=1 colspan=1>Temperature data-ready is routed to INT2. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_OVR</td><td rowspan=1 colspan=1>FIFO overrun interrupt is routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_DIFF5</td><td rowspan=1 colspan=1>FIFO full recognition is routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_FTH</td><td rowspan=1 colspan=1>FIFO threshold interrupt is routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>INT2_DRDY</td><td rowspan=1 colspan=1>Data-ready is routed to INT2 pad. Default value: 0(0: disabled; 1: enabled)</td></tr></table>

# 8.9

# CTRL6 (25h)

Control register 6 (R/W)

Table 40. Control register 6   

<table><tr><td rowspan=1 colspan=1>BW_FILT1</td><td rowspan=1 colspan=1>BW_FILT0</td><td rowspan=1 colspan=1>FS1</td><td rowspan=1 colspan=1>FSO</td><td rowspan=1 colspan=1>FDS</td><td rowspan=1 colspan=1>LOWNOISE</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

<table><tr><td>BW_FILT[1:0]</td><td>Bandwidth selection (see Table 41. Digital filtering cutof selection)</td></tr><tr><td>FS[1:0]</td><td>Full-scale selection (see Table 42. Full-scale selection)</td></tr><tr><td rowspan="2">FDS</td><td>Filtered data type selection. Default value: 0</td></tr><tr><td>(0: low-pass filter path selected;</td></tr><tr><td rowspan="2">LOW_NOISE</td><td>1: high-pass filter path selected)</td></tr><tr><td>Low-noise configuration.</td></tr><tr><td></td><td>(0: disabled; 1: enabled)</td></tr></table>

Table 41. Digital filtering cutoff selection   

<table><tr><td rowspan=1 colspan=1>BW_FILT[1:0]</td><td rowspan=1 colspan=1>Bandwidth selection</td></tr><tr><td rowspan=1 colspan=1>00</td><td rowspan=1 colspan=1> ODR/2 (up to ODR = 800 Hz, 400 Hz when ODR = 1600 Hz)</td></tr><tr><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>ODR/4 (HP/LP)</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>ODR/10 (HP/LP)</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>ODR/20 (HP/LP)</td></tr></table>

Table 42. Full-scale selection   

<table><tr><td rowspan=1 colspan=1>FS[1:0]</td><td rowspan=1 colspan=1>Full-scale selection</td></tr><tr><td rowspan=1 colspan=1>00</td><td rowspan=1 colspan=1>+2g</td></tr><tr><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1>±4g</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>±8g</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>±16g</td></tr></table>

# 8.10 OUT_T (26h)

Temperature output register in 8-bit resolution (R)

Table 43. OUT_T register   

<table><tr><td rowspan=1 colspan=1>TEMP7</td><td rowspan=1 colspan=1>TEMP6</td><td rowspan=1 colspan=1>TEMP5</td><td rowspan=1 colspan=1>TEMP4</td><td rowspan=1 colspan=1>TEMP3</td><td rowspan=1 colspan=1>TEMP2</td><td rowspan=1 colspan=1>TEMP1</td><td rowspan=1 colspan=1>TEMPO</td></tr></table>

Table 44. OUT_T register description   

<table><tr><td rowspan="3">TEMP[7:0]</td><td>Temperature sensor output data.</td></tr><tr><td>The value is expressed as two&#x27;s complement sign. Sensitivity= 1C/LSB</td></tr><tr><td>0 LSB represents T= 25°C ambient.</td></tr></table>

# 8.11

#

# STATUS (27h)

Status register (R)

Table 45. STATUS register   

<table><tr><td rowspan=1 colspan=1>FIFO_THS</td><td rowspan=1 colspan=1>WU_IA</td><td rowspan=1 colspan=1>SLEEP_STATE</td><td rowspan=1 colspan=1>DOUBLETAP</td><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>DRDY</td></tr></table>

Table 46. STATUS register description   

<table><tr><td rowspan=1 colspan=1>FIFO_THS</td><td rowspan=1 colspan=1> FIFO threshold status flag(0: FIFOfiling is lower than threshold level; 1: FIFO filing is equal toor higher than the threshold level.)</td></tr><tr><td rowspan=1 colspan=1>WU_IA</td><td rowspan=1 colspan=1>Wake-up event detection status(0: wake-up event not detected; 1: wake-up event detected)</td></tr><tr><td rowspan=1 colspan=1>SLEEP_STATE</td><td rowspan=1 colspan=1>Sleep event status.(0: sleep event not detected; 1: sleep event detected)</td></tr><tr><td rowspan=1 colspan=1>DOUBLE_TAP</td><td rowspan=1 colspan=1>Double-tap event status(0: double-tap event not detected; 1: double-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1>Single-tap event status(0: single-tap event not detected; 1: single-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>Source of change in position portrait/landscape/face-up/face-down(0: no event detected; 1: a change in position detected)</td></tr><tr><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>Free-fall event detection status(0: free-fall event not detected; 1: free-fall event detected)</td></tr><tr><td rowspan=1 colspan=1>DRDY</td><td rowspan=1 colspan=1>Data-ready status(0: not ready; 1: X-, Y- and Z-axis new data available)</td></tr></table>

# 3.12 OUT_X_L (28h)

X-axis LSB output register (R)

Table 47. OUT_X_L register   

<table><tr><td rowspan=1 colspan=1>X_L7</td><td rowspan=1 colspan=1>X_L6</td><td rowspan=1 colspan=1>X_L5</td><td rowspan=1 colspan=1>X_L4</td><td rowspan=1 colspan=1>X_L3(1)</td><td rowspan=1 colspan=1>X_L2(1)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

1． If low-power mode 1 is enabled, this bit is set to 0.

The 8 least significant bits of linear acceleration sensor $\mathsf { X }$ axis output. Together with the OUT_X_H (29h) register, it forms the output value expressed as a 16-bit word in two's complement.

# 8.13

# OUT_X_H (29h)

X-axis MSB output register (R)

Table 48. OUT_X_H register   

<table><tr><td rowspan=1 colspan=1>X_H7</td><td rowspan=1 colspan=1>X_H6</td><td rowspan=1 colspan=1>X_H5</td><td rowspan=1 colspan=1>X_H4</td><td rowspan=1 colspan=1>X_H3</td><td rowspan=1 colspan=1>X_H2</td><td rowspan=1 colspan=1>X_H1</td><td rowspan=1 colspan=1>X_H0</td></tr></table>

The 8 most significant bits of linear acceleration sensor $\mathsf { X } .$ axis output. Together with the OUT_X_L (28h) register, it forms the output value expressed as a 16-bit word in two's complement.

# 8.14

# OUT_Y_L (2Ah)

Y-axis LSB output register (R)

Table 49. OUT_Y_L register   

<table><tr><td rowspan=1 colspan=1>Y_L7</td><td rowspan=1 colspan=1>Y_L6</td><td rowspan=1 colspan=1>Y_L5</td><td rowspan=1 colspan=1>Y_L4</td><td rowspan=1 colspan=1>Y L3(1)</td><td rowspan=1 colspan=1>Y_L2(1)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

1． If low-power mode 1 is enabled, this bit is set to 0.

The 8 least significant bits of linear acceleration sensor Y-axis output. Together with the OUT_Y_H(2Bh)register, it forms the output value expressed as a 16-bit word in two's complement.

# }.15

# OUT_Y_H (2Bh)

Y-axis MSB output register (R)

Table 50. OUT_Y_H register   

<table><tr><td rowspan=1 colspan=1>Y_H7</td><td rowspan=1 colspan=1>Y_H6</td><td rowspan=1 colspan=1>Y_H5</td><td rowspan=1 colspan=1>Y_H4</td><td rowspan=1 colspan=1>Y_H3</td><td rowspan=1 colspan=1>Y_H2</td><td rowspan=1 colspan=1>Y_H1</td><td rowspan=1 colspan=1>Y_H0</td></tr></table>

The 8 most significant bits oflinear acceleration sensor Y-axis output. Together with the OUT_Y_L (2Ah)register, it forms the output value expressed as a 16-bit word in two's complement.

# 3.16 OUT_Z_L (2Ch)

Z-axis LSB output register (R)

Table 51. OUT_Z_L register   

<table><tr><td rowspan=1 colspan=1>Z_L7</td><td rowspan=1 colspan=1>Z_L6</td><td rowspan=1 colspan=1>Z_L5</td><td rowspan=1 colspan=1>Z_L4</td><td rowspan=1 colspan=1>Z_L3(1)</td><td rowspan=1 colspan=1>ZL2(1)</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td></tr></table>

1． If low-power mode 1 is enabled, this bit is set to 0.

The8 least significant bits of linear acceleration sensor Z-axis output. Together with the OUT_Z_H (2Dh register, it forms the output value expressed as a 16-bit word in two's complement.

# 8.17

# OUT_Z_H (2Dh)

Z-axis MSB output register (R)

Table 52. OUT_Z_H register   

<table><tr><td rowspan=1 colspan=1>Z_H7</td><td rowspan=1 colspan=1>Z_H6</td><td rowspan=1 colspan=1>Z_H5</td><td rowspan=1 colspan=1>Z_H4</td><td rowspan=1 colspan=1>Z_H3</td><td rowspan=1 colspan=1>Z_H2</td><td rowspan=1 colspan=1>Z_H1</td><td rowspan=1 colspan=1>Z_HO</td></tr></table>

The 8 most significant bits oflinear acceleration sensor Z-axis output. Together with the OUT_Z_L (2Ch)register, it forms the output value expressed as a 16-bit word in two's complement.

# 8.18

# FIFO_CTRL (2Eh

FIFO control register (R/W)

Table 53. FIFO_CTRL register   

<table><tr><td rowspan=1 colspan=1>FMode2</td><td rowspan=1 colspan=1>FMode1</td><td rowspan=1 colspan=1>FMode0</td><td rowspan=1 colspan=1>FTH4</td><td rowspan=1 colspan=1>FTH3</td><td rowspan=1 colspan=1>FTH2</td><td rowspan=1 colspan=1>FTH1</td><td rowspan=1 colspan=1>FTHO</td></tr></table>

Table 54. FIFO_CTRL register description   

<table><tr><td>FMode[2:0]</td><td>FIFO mode selection bits. Default: O00. For further details,refer to Table 55.FIFO mode selection.</td></tr><tr><td>FTH[4:0]</td><td>FIFO threshold level seting</td></tr></table>

Table 55. FlFO mode selection   

<table><tr><td rowspan=1 colspan=1>FMode[2:0]</td><td rowspan=1 colspan=1> Mode description</td></tr><tr><td rowspan=1 colspan=1>000</td><td rowspan=1 colspan=1>Bypass mode: FIFO turned off</td></tr><tr><td rowspan=1 colspan=1>001</td><td rowspan=1 colspan=1>FIFO mode: stops collecting data when FIFO is full</td></tr><tr><td rowspan=1 colspan=1>010</td><td rowspan=1 colspan=1>Reserved</td></tr><tr><td rowspan=1 colspan=1>011</td><td rowspan=1 colspan=1>Continuous-to-FIFO: stream mode until trigger is deasserted, then FIFO mode</td></tr><tr><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>Bypass-to-continuous: bypass mode until trigger is deasserted, then FIFO mode</td></tr><tr><td rowspan=1 colspan=1>101</td><td rowspan=1 colspan=1>Reserved</td></tr><tr><td rowspan=1 colspan=1>110</td><td rowspan=1 colspan=1> Continuous mode: If the FIFO is full the new sample overwrites the older sample.</td></tr><tr><td rowspan=1 colspan=1>111</td><td rowspan=1 colspan=1>Reserved</td></tr></table>

# 8.19 FIFO_SAMPLES (2Fh)

FIFO_SAMPLES control register (R)

Table 56. FIFO_SAMPLES register   

<table><tr><td rowspan=1 colspan=1>FIFO_FTH</td><td rowspan=1 colspan=1>FIFO_OVR</td><td rowspan=1 colspan=1>Diff5</td><td rowspan=1 colspan=1>Diff4</td><td rowspan=1 colspan=1>Diff3</td><td rowspan=1 colspan=1>Diff2</td><td rowspan=1 colspan=1>Diff1</td><td rowspan=1 colspan=1>Diffo</td></tr></table>

Table 57. FIFO_SAMPLES register description   

<table><tr><td>FIFO_FTH</td><td>FIFO threshold status flag (0: FIFO filling is lower than threshold level;</td></tr><tr><td>FIFO_OVR</td><td>1: FIFO filing is equal to or higher than the threshold level.) FIFO overrun status</td></tr><tr><td></td><td>(0: FIFO is not completely filled; 1: FIFO is completely filled and at least one sample has been overwritten)</td></tr><tr><td>Di[5:0]</td><td>Represents the number of unread samples stored in FIFO. (000000 = FIFO empty; 100000 = FIFO full, 32 unread samples).</td></tr></table>

# 8.20

# TAP_THS_X (30h)

Enables 4D configuration and configures TAP threshold (R/W)

Table 58. TAP_THS_X register   

<table><tr><td rowspan=1 colspan=1>4D_EN</td><td rowspan=1 colspan=1>6D_THS1</td><td rowspan=1 colspan=1>6D_THS0</td><td rowspan=1 colspan=1>TAPTHSX_4</td><td rowspan=1 colspan=1>TAP_THSX_3</td><td rowspan=1 colspan=1>TAPTHSX_2</td><td rowspan=1 colspan=1>TAPTHSX_1</td><td rowspan=1 colspan=1>TAPTHSX_0</td></tr></table>

# Table 59. TAP_THS_X register description

<table><tr><td rowspan=1 colspan=1>4D_EN</td><td rowspan=1 colspan=1>Enables 4D detection portrait/landscape position(0: no position detected;1: portrait/landscape detection and face-up/face-down position enabled).</td></tr><tr><td rowspan=1 colspan=1>6D_THS[1:0]</td><td rowspan=1 colspan=1>Thresholds for 4D/6D function @ FS = ±2 g (refer to Table 60. 4D/6D threshold setting FS @ ±2 g)</td></tr><tr><td rowspan=1 colspan=1>TAP_THSX_[4:0]</td><td rowspan=1 colspan=1>Threshold for TAP recognition @ FS = ±2 g on X direction</td></tr></table>

Table 60. 4D/6D threshold setting FS $@$ ±2 g   

<table><tr><td rowspan=1 colspan=1>6D_THS[1:0]</td><td rowspan=1 colspan=1>Threshold decoding (degrees)</td></tr><tr><td rowspan=1 colspan=1>00</td><td rowspan=1 colspan=1>6 (80 degrees)</td></tr><tr><td rowspan=1 colspan=1>01</td><td rowspan=1 colspan=1> 11 (70 degrees)</td></tr><tr><td rowspan=1 colspan=1>10</td><td rowspan=1 colspan=1>16 (60 degrees)</td></tr><tr><td rowspan=1 colspan=1>11</td><td rowspan=1 colspan=1>21 (50 degrees)</td></tr></table>

# 8.21 TAP_THS_Y (31h)

Table 61. TAP_THS_Y register   

<table><tr><td rowspan=1 colspan=1>TAPPRIOR_2</td><td rowspan=1 colspan=1>TAPPRIOR_1</td><td rowspan=1 colspan=1>TAPPRIOR_0</td><td rowspan=1 colspan=1>TAPTHSY_4</td><td rowspan=1 colspan=1>TAPTHSY_3</td><td rowspan=1 colspan=1>TAPTHSY_2</td><td rowspan=1 colspan=1>TAPTHSY_1</td><td rowspan=1 colspan=1>TAPTHSY_0</td></tr></table>

Table 62. TAP_THS_Y register description   

<table><tr><td>TAP_PRIOR_[2:0]</td><td>Selection of priority axis for tap detection (see Table 63. Selection of axis priority for tap detection)</td></tr><tr><td>TAP_THSY_[4:0]</td><td>Threshold for tap recognition @ FS = ±2 g on Y direction</td></tr></table>

Table 63. Selection of axis priority for tap detection   

<table><tr><td rowspan=1 colspan=1>TAP_PRIOR_[2:0]</td><td rowspan=1 colspan=1>Max priority</td><td rowspan=1 colspan=1>Mid priority</td><td rowspan=1 colspan=1>Min priority</td></tr><tr><td rowspan=1 colspan=1>000</td><td rowspan=1 colspan=1>×</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>Z</td></tr><tr><td rowspan=1 colspan=1>001</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>×</td><td rowspan=1 colspan=1>Z</td></tr><tr><td rowspan=1 colspan=1>010</td><td rowspan=1 colspan=1>X</td><td rowspan=1 colspan=1>Z</td><td rowspan=1 colspan=1>Y</td></tr><tr><td rowspan=1 colspan=1>011</td><td rowspan=1 colspan=1>Z</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>×</td></tr><tr><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>X</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>Z</td></tr><tr><td rowspan=1 colspan=1>101</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>Z</td><td rowspan=1 colspan=1>×</td></tr><tr><td rowspan=1 colspan=1>110</td><td rowspan=1 colspan=1>Z</td><td rowspan=1 colspan=1>X</td><td rowspan=1 colspan=1>Y</td></tr><tr><td rowspan=1 colspan=1>111</td><td rowspan=1 colspan=1>Z</td><td rowspan=1 colspan=1>Y</td><td rowspan=1 colspan=1>×</td></tr></table>

# 8.22

# TAP_THS_Z (32h)

Table 64. TAP_THS_Z register   

<table><tr><td rowspan=1 colspan=1>TAP_XEN</td><td rowspan=1 colspan=1>TAP_YEN</td><td rowspan=1 colspan=1>TAP_Z_EN</td><td rowspan=1 colspan=1>TAPTHSZ_4</td><td rowspan=1 colspan=1>TAPTHSZ_3</td><td rowspan=1 colspan=1>TAPTHSZ_2</td><td rowspan=1 colspan=1>TAP_THSZ_1</td><td rowspan=1 colspan=1>TAPTHSZ_0</td></tr></table>

Table 65. TAP_THS_Z register description   

<table><tr><td rowspan=1 colspan=1>TAP_X_EN</td><td rowspan=1 colspan=1>Enables X direction in tap recognition(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>TAP_Y_EN</td><td rowspan=1 colspan=1>Enables Y direction in tap recognition(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>TAP_Z_EN</td><td rowspan=1 colspan=1>Enables Z direction in tap recognition(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>TAP_THSZ_[4:0]</td><td rowspan=1 colspan=1>Threshold for tap recognition @ FS = ±2 g on Z direction</td></tr></table>

# 8.23

# INT_DUR (33h)

Interrupt duration register (R/W)

Table 66. INT_DUR register   

<table><tr><td rowspan=1 colspan=1>LATENCY3</td><td rowspan=1 colspan=1>LATENCY2</td><td rowspan=1 colspan=1>LATENCY1</td><td rowspan=1 colspan=1>LATENCYO</td><td rowspan=1 colspan=1>QUIET1</td><td rowspan=1 colspan=1>QUIETO</td><td rowspan=1 colspan=1>SHOCK1</td><td rowspan=1 colspan=1>SHOCKO</td></tr></table>

Table 67. INT_DUR register description   

<table><tr><td rowspan=1 colspan=1>LATENCY[3:0]</td><td rowspan=1 colspan=1>Duration of maximum time gap for double-tap recognition. When double-tap recognition is enabled, thisregister expresses the maximum time between two successive detected taps to determine a double-tap event.Default value is LATENCY[3:0] = 0000 (which is 16 * 1/ODR)1 LSB = 32 * 1/ODR</td></tr><tr><td rowspan=1 colspan=1>QUIET[1:0]</td><td rowspan=1 colspan=1>Expected quiet time aftera tap detection: this register represents the time after the first detected tap n whichthere must not be any overthreshold event.Default value is QUIET[1:0] = 00 (which is 2 * 1/ODR)1 LSB = 4 * 1/ODR</td></tr><tr><td rowspan=1 colspan=1>SHOCK[1:0]</td><td rowspan=1 colspan=1>Maximum duration of overthreshold event: this register represents the maximum time of an overthresholdsignal detection to be recognized as a tap event.Default value is SHOCK[1:0] = 00 (which is 4 * 1/ODR)1 LSB = 8 *1/ODR</td></tr></table>

# 8.24

# WAKE_UP_THS (34h)

Wake-up threshold register (R/W)

Table 68. WAKE_UP_THS register   

<table><tr><td rowspan=1 colspan=1>SINGLEDOUBLE_TAP</td><td rowspan=1 colspan=1>SLEEP_ON</td><td rowspan=1 colspan=1>WK_THS5</td><td rowspan=1 colspan=1>WK_THS4</td><td rowspan=1 colspan=1>WK_THS3</td><td rowspan=1 colspan=1>WK_THS 2</td><td rowspan=1 colspan=1>WK_THS 1</td><td rowspan=1 colspan=1>WK_THS 0</td></tr></table>

Table 69. WAKE_UP_THS register description   

<table><tr><td rowspan=1 colspan=1>SINGLE_DOUBLE_TAP</td><td rowspan=1 colspan=1>Enables single/double-tap event. Default value: 0(0: only single-tap event is enabled; 1: single and double-tap events are enabled)</td></tr><tr><td rowspan=1 colspan=1>SLEEP_ON</td><td rowspan=1 colspan=1>Enables sleep (inactivity). Default value: 0(0: sleep disabled; 1: sleep enabled)</td></tr><tr><td rowspan=1 colspan=1>WK_THS[5:0]</td><td rowspan=1 colspan=1>Wake-up threshold, 6-bit unsigned 1 LSB = 1/64 of FS. Default value: 000000</td></tr></table>

# 8.25 WAKE_UP_DUR (35h)

Wake--up and sleep duration configuration register (R/W)

Table 70. WAKE_UP_DUR register   

<table><tr><td rowspan=1 colspan=1>FF_DUR5</td><td rowspan=1 colspan=1>WAKEDUR1</td><td rowspan=1 colspan=1>WAKE_DURO</td><td rowspan=1 colspan=1>STATIONARY</td><td rowspan=1 colspan=1>SLEEP_DUR3</td><td rowspan=1 colspan=1>SLEEP_DUR2</td><td rowspan=1 colspan=1>SLEEP_DUR1</td><td rowspan=1 colspan=1>SLEEP_DUR0</td></tr></table>

Table 71. WAKE_UP_DUR register description   

<table><tr><td rowspan=1 colspan=1>FF_DUR5</td><td rowspan=1 colspan=1>Free-fall duration. In conjunction with FF_DUR [4:0] bit in the FREE_FALL (36h)register.1 LSB = 1* 1/ODR</td></tr><tr><td rowspan=1 colspan=1>WAKE_DUR[1:0]</td><td rowspan=1 colspan=1>Wake-up duration. 1 LSB = 1 *1/ODR</td></tr><tr><td rowspan=1 colspan=1>STATIONARY</td><td rowspan=1 colspan=1>Enables stationary detection / motion detection with no automatic ODR change when detecting stationary stateDefault value: 0(0: disabled; 1: enabled)</td></tr><tr><td rowspan=1 colspan=1>SLEEP_DUR[3:0]</td><td rowspan=1 colspan=1>Duration to go in sleep modeDefault value is SLEEP_ DUR[3:0] = 0000 (which is 16 * 1/ODR).1 LSB= 512* 1/ODR</td></tr></table>

# 8.26

# FREE_FALL (36h)

Free-fall duration and threshold configuration register (R/W)

Table 72. FREE_FALL register   

<table><tr><td rowspan=1 colspan=1>FF_DUR4</td><td rowspan=1 colspan=1>FF_DUR3</td><td rowspan=1 colspan=1>FF_DUR2</td><td rowspan=1 colspan=1>FF_DUR1</td><td rowspan=1 colspan=1>FF_DUR0</td><td rowspan=1 colspan=1>FF_THS2</td><td rowspan=1 colspan=1>FF_THS1</td><td rowspan=1 colspan=1>FF_THS0</td></tr></table>

Table 73. FREE_FALL register description   

<table><tr><td>FF_DUR [4:0]</td><td>Free-fall duration.In conjunction with FF_DUR5 bit in the WAKE_UP_DUR (35h) register. 1 LSB= 1 * 1/ODR</td></tr><tr><td>FF_THS [2:0]</td><td>Free-fal threshold @ FS = ±2 g (refer to Table 74. FREE_FALL threshold decoding @ ± 2 g FS)</td></tr></table>

Table 74. FREE_FALL threshold decoding $@ \pm z g F s$   

<table><tr><td rowspan=1 colspan=1>FF_THS[2:0]</td><td rowspan=1 colspan=1>Threshold decoding (LSB)</td></tr><tr><td rowspan=1 colspan=1>000</td><td rowspan=1 colspan=1>5</td></tr><tr><td rowspan=1 colspan=1>001</td><td rowspan=1 colspan=1>7</td></tr><tr><td rowspan=1 colspan=1>010</td><td rowspan=1 colspan=1>8</td></tr><tr><td rowspan=1 colspan=1>011</td><td rowspan=1 colspan=1>10</td></tr><tr><td rowspan=1 colspan=1>100</td><td rowspan=1 colspan=1>11</td></tr><tr><td rowspan=1 colspan=1>101</td><td rowspan=1 colspan=1>13</td></tr><tr><td rowspan=1 colspan=1>110</td><td rowspan=1 colspan=1>15</td></tr><tr><td rowspan=1 colspan=1>111</td><td rowspan=1 colspan=1>16</td></tr></table>

# 8.27 STATUS_DUP (37h)

Event detection status register (R)

Table 75. STATUS_DUP register   

<table><tr><td rowspan=1 colspan=1>OVR</td><td rowspan=1 colspan=1>DRDY_T</td><td rowspan=1 colspan=1>SLEEPSTATE_IA</td><td rowspan=1 colspan=1>DOUBLETAP</td><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>DRDY</td></tr></table>

Table 76. STATUS_DUP register description   

<table><tr><td rowspan=1 colspan=1>OVR</td><td rowspan=1 colspan=1>FIFO overrun status flag(0: FIFO is not completely filled;1: FIFO is completely filld and at least one sample has been overwritten)</td></tr><tr><td rowspan=1 colspan=1>DRDY_T</td><td rowspan=1 colspan=1>Temperature status(0: data not available; 1: a new set of data is available)</td></tr><tr><td rowspan=1 colspan=1>SLEEP_STATE_IA</td><td rowspan=1 colspan=1>Sleep event status(0: Sleep event not detected; 1: Sleep event detected)</td></tr><tr><td rowspan=1 colspan=1>DOUBLE_TAP</td><td rowspan=1 colspan=1>Double-tap event status(0: Double-tap event not detected; 1: Double-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1>Single-tap event status(0: Single-tap event not detected; 1: Single-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>Source of change in position portrait/landscape/face-up/face-down(0: no event detected; 1: a change in position is detected)</td></tr><tr><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>Free-fall event detection status(0: free-fall event not detected; 1: free-fall event detected)</td></tr><tr><td rowspan=1 colspan=1>DRDY</td><td rowspan=1 colspan=1>Data-ready status(0: not ready; 1: X-, Y-,and Z-axis new data available)</td></tr></table>

# 8.28 WAKE_UP_SRC (38h)

Wake-up source register (R)

Table 77. WAKE_UP_SRC register   

<table><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>SLEEPSTATEIA</td><td rowspan=1 colspan=1>WU_IA</td><td rowspan=1 colspan=1>X_WU</td><td rowspan=1 colspan=1>Y_WU</td><td rowspan=1 colspan=1>Z_WU</td></tr></table>

Table 78. WAKE_UP_SRC register description   

<table><tr><td>FF_IA</td><td>Free-fall event detection status (0: FF event not detected; 1: FF event detected)</td></tr><tr><td>SLEEP_STATE IA</td><td>Sleep event status</td></tr><tr><td></td><td>(0: sleep event not detected; 1: sleep event detected)</td></tr><tr><td>WU_IA</td><td>Wake-up event detection status (0: wake-up event not detected; 1: wake-up event is detected)</td></tr><tr><td rowspan="2">X_WU</td><td>Wake-up event detection status on X-axis</td></tr><tr><td>(0: wake-up event on X not detected; 1: wake-up event on X-axis is detected)</td></tr><tr><td>Y_WU</td><td>Wake-up event detection status on Y-axis</td></tr><tr><td rowspan="2"></td><td>(0: wake-up event on Y not detected; 1: wake-up event on Y-axis is detected)</td></tr><tr><td>Wake-up event detection status on Z-axis</td></tr><tr><td>Z_WU</td><td>(0: wake-up event on Z not detected; 1: wake-up event on Z-axis is detected)</td></tr></table>

# 8.29

# TAP_SRC (39h)

Tap source register (R)

Table 79. TAP_SRC register   

<table><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>TAP_IA</td><td rowspan=1 colspan=1>SINGLETAP</td><td rowspan=1 colspan=1>DOUBLETAP</td><td rowspan=1 colspan=1>TAP_SIGN</td><td rowspan=1 colspan=1>X_TAP</td><td rowspan=1 colspan=1>Y_TAP</td><td rowspan=1 colspan=1>Z_TAP</td></tr></table>

Table 80. TAP_SRC register description   

<table><tr><td rowspan=1 colspan=1>TAP_IA</td><td rowspan=1 colspan=1>Tap event status(0: tap event not detected; 1: tap event detected)</td></tr><tr><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1> Single-tap event status(0: single-tap event not detected; 1: single-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>DOUBLE_TAP</td><td rowspan=1 colspan=1> Double-tap event status(0: double-tap event not detected; 1: double-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>TAP_SIGN</td><td rowspan=1 colspan=1>Sign of acceleration detected by tap event(0: positive sign of acceleration detected; 1: negative sign of acceleration detected)</td></tr><tr><td rowspan=1 colspan=1>X_TAP</td><td rowspan=1 colspan=1>Tap event detection status on X-axis(0: tap event on X not detected; 1: tap event on X-axis is detected)</td></tr><tr><td rowspan=1 colspan=1>Y_TAP</td><td rowspan=1 colspan=1>Tap event detection status on Y-axis(0: tap event on Y not detected; 1: tap event on Y-axis is detected)</td></tr><tr><td rowspan=1 colspan=1>Z_TAP</td><td rowspan=1 colspan=1>Tap event detection status on Z-axis(0: tap event on Z not detected; 1: tap event on Z-axis is detected)</td></tr></table>

# 8.30 SIXD_SRC (3Ah)

6D source register (R)

Table 81. SIXD_SRC register   

<table><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>ZH</td><td rowspan=1 colspan=1>ZL</td><td rowspan=1 colspan=1>YH</td><td rowspan=1 colspan=1>YL</td><td rowspan=1 colspan=1>XH</td><td rowspan=1 colspan=1>XL</td></tr></table>

Table 82. SIXD_SRC register description   

<table><tr><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1> Source of change in position portrait/landscape/face-up/face-down(0: no event detected; 1: a change in position is detected)</td></tr><tr><td rowspan=1 colspan=1>ZH</td><td rowspan=1 colspan=1> ZH over threshold(0: ZH does not exceed the threshold; 1: ZH is over the threshold)</td></tr><tr><td rowspan=1 colspan=1>ZL</td><td rowspan=1 colspan=1> ZL over threshold(0: ZL does not exceed the threshold; 1: ZL is over the threshold)</td></tr><tr><td rowspan=1 colspan=1>YH</td><td rowspan=1 colspan=1>YH over threshold(0: YH does not exceed the threshold; 1: YH is over the threshold)</td></tr><tr><td rowspan=1 colspan=1>YL</td><td rowspan=1 colspan=1>YL over threshold(0: YL does not exceed the threshold; 1: YL is over the threshold)</td></tr><tr><td rowspan=1 colspan=1>XH</td><td rowspan=1 colspan=1>XH over threshold(0: XH does not exceed the threshold; 1: XH is over the threshold)</td></tr><tr><td rowspan=1 colspan=1>XL</td><td rowspan=1 colspan=1>XL over threshold(0: XL does not exceed the threshold; 1: XL is over the threshold)</td></tr></table>

# 8.31 ALL_INT_SRC (3Bh)

Reading this register, allrelated interrupt function flags routed to the INT pads are reset simultaneously.

Table 83. ALL_INT_SRC register   

<table><tr><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>0</td><td rowspan=1 colspan=1>SLEEPCHANGE_IA</td><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>DOUBLETAP</td><td rowspan=1 colspan=1>SINGLETAP</td><td rowspan=1 colspan=1>WU_IA</td><td rowspan=1 colspan=1>FF_IA</td></tr></table>

Table 84. ALL_INT_SRC register description   

<table><tr><td rowspan=1 colspan=1>SLEEP_CHANGE_IA</td><td rowspan=1 colspan=1> Sleep change status(0: sleep change not detected; 1: sleep change detected)</td></tr><tr><td rowspan=1 colspan=1>6D_IA</td><td rowspan=1 colspan=1>Source of change in position portrait/landscape/face-up/face-down(0: no event detected; 1: a change in position detected)</td></tr><tr><td rowspan=1 colspan=1>DOUBLE_TAP</td><td rowspan=1 colspan=1>Double-tap event status(0: double-tap event not detected; 1: double-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>SINGLE_TAP</td><td rowspan=1 colspan=1>Single-tap event status(0: single-tap event not detected; 1: single-tap event detected)</td></tr><tr><td rowspan=1 colspan=1>WU_IA</td><td rowspan=1 colspan=1>Wake-up event detection status(0: wake-up event not detected; 1: wake-up event detected)</td></tr><tr><td rowspan=1 colspan=1>FF_IA</td><td rowspan=1 colspan=1>Free-fall event detection status.(0: free-fall event not detected; 1: free-fall event detected)</td></tr></table>

# 8.32 X_OFS_USR (3Ch)

# Table 85. X_OFS_USR register

<table><tr><td rowspan=1 colspan=1>X_OFSUSR_7</td><td rowspan=1 colspan=1>X_OFSUSR_6</td><td rowspan=1 colspan=1>X_OFSUSR_5</td><td rowspan=1 colspan=1>X_OFSUSR_4</td><td rowspan=1 colspan=1>X_OFSUSR_3</td><td rowspan=1 colspan=1>X_OFSUSR_2</td><td rowspan=1 colspan=1>X_OFSUSR_1</td><td rowspan=1 colspan=1>X_OFSUSR_0</td></tr></table>

Table 86. X_OFS_USR register description   

<table><tr><td>X_OFS_USR_[7:0]</td><td></td></tr></table>

# 8.33

# Y_OFS_USR (3Dh)

# Table 87. Y_OFS_USR register

<table><tr><td rowspan=1 colspan=1>Y_OFS_USR_7</td><td rowspan=1 colspan=1>Y_OFSUSR_6</td><td rowspan=1 colspan=1>Y_OFS_USR_5</td><td rowspan=1 colspan=1>Y_OFSUSR_4</td><td rowspan=1 colspan=1>Y_OFSUSR_3</td><td rowspan=1 colspan=1>Y_OFSUSR_2</td><td rowspan=1 colspan=1>Y_OFS_USR_1</td><td rowspan=1 colspan=1>Y_OFS_USR_0</td></tr></table>

Table 88. Y_OFS_USR register description   

<table><tr><td>Y_OFS_USR_[7:0]</td><td>Two&#x27;s comple</td></tr></table>

# 8.34

# Z_OFS_USR (3Eh)

# Table 89. Z_OFS_USR register

<table><tr><td rowspan=1 colspan=1>Z_OFS_USR_7</td><td rowspan=1 colspan=1>Z_OFS_USR_6</td><td rowspan=1 colspan=1>Z_OFSUSR_5</td><td rowspan=1 colspan=1>Z_OFS_USR_4</td><td rowspan=1 colspan=1>Z_OFS_USR_3</td><td rowspan=1 colspan=1>Z_OFS_USR_2</td><td rowspan=1 colspan=1>Z_OFS_USR_1</td><td rowspan=1 colspan=1>Z_OFS_USR_0</td></tr></table>

Table 90. Z_OFS_USR register description   

<table><tr><td>Z_OFS_USR_[7:0]</td><td>Two&#x27;s complement user offset value on Z-axis data,used for wake-up function</td></tr></table>

# 8.35 CTRL7 (3Fh)

Table 91. CTRL7 register   

<table><tr><td rowspan=1 colspan=1>DRDYPULSED</td><td rowspan=1 colspan=1>INT2_ON_INT1</td><td rowspan=1 colspan=1>INTERRUPTS_ENABLE</td><td rowspan=1 colspan=1>USR_OFF_ON_OUT</td><td rowspan=1 colspan=1>USR_OFF_ON_WU</td><td rowspan=1 colspan=1>USR_OFF_W</td><td rowspan=1 colspan=1>HP_REF_MODE</td><td rowspan=1 colspan=1>LPASS_ON6D</td></tr></table>

Table 92. CTRL7 register description   

<table><tr><td rowspan=1 colspan=1>DRDY_PULSED</td><td rowspan=1 colspan=1> Switches between latched and pulsed mode for data ready interrupt(0: latched mode is used; 1: pulsed mode enabled for data-ready)</td></tr><tr><td rowspan=1 colspan=1>INT2_ON_INT1</td><td rowspan=1 colspan=1> Signal routing(1: all signals available only on INT2 are routed to INT1)</td></tr><tr><td rowspan=1 colspan=1>INTERRUPTS_ENABLE</td><td rowspan=1 colspan=1>Enables interrupts</td></tr><tr><td rowspan=1 colspan=1>USR_OFF_ON_OUT</td><td rowspan=1 colspan=1>Enables application of user offset value in accelerometer output data registersFDS bit in CTRL6 (25h) must be set to 0 logic (low-pass path selected).</td></tr><tr><td rowspan=1 colspan=1>USR_OFF_ON_WU</td><td rowspan=1 colspan=1>Enables application of user ofset value on accelerometer data for wake-up function only</td></tr><tr><td rowspan=1 colspan=1>USR_OFF_W</td><td rowspan=1 colspan=1>Selects the weight of the user ofset words specified by X_OFS_USR_[7:0], Y_OFS_USR_[7:0],and Z_OFS_USR_[7:0] bits(0: 977 μg/LSB; 1: 15.6 mg/LSB)</td></tr><tr><td rowspan=1 colspan=1>HP_REF_MODE</td><td rowspan=1 colspan=1>Enables high-pass filter reference mode(0: high-pass filter reference mode disabled (default);1: high-pass filter reference mode enabled)</td></tr><tr><td rowspan=1 colspan=1>LPASS_ON6D</td><td rowspan=1 colspan=1>(0: ODR/2 low-passfiltered data sent to 6D interupt function (default);1: LPF2 output data sent to 6D interrupt function)</td></tr></table>

# 9 Package information

To meet environmental requirements, ST offers these devices in diferent grades of ECOPACK packages, depending on their level of environmental compliance.ECOPACK specifications,grade definitions,and product status are available at: www.st.com. ECOPACK is an ST trademark.

# Soldering information

The LGA package is compliant with the ECOPACK and RoHS standard.   
It is qualified for soldering heat resistance according to JEDEC J-STD-020.   
For land patern and soldering recommendations, consult technical note TNo018 available on www.st.com.

# 9.2

# LGA-12L package information

![](images/828c4f487f17e51efcc708b269c9f0a8a83b48f8b9c6cbb7377fbc40fef2678a.jpg)  
Figure 18. LGA-12L $\mathbf { 2 . 0 \times 2 . 0 \times 0 . 7 \ m m }$ package outline and mechanical data

Dimensions are in millimeter unless otherwise specified. General Tolerance is $+ / - 0 . 1 5 \mathsf { m m }$ unless otherwise specified.

# OUTERDIMENSIONS

<table><tr><td rowspan=1 colspan=1>ITEM</td><td rowspan=1 colspan=1>DIMENSION[mm]</td><td rowspan=1 colspan=1>TOLERANCE[mm]</td></tr><tr><td rowspan=1 colspan=1>Length[L]</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>±0.1</td></tr><tr><td rowspan=1 colspan=1>Width[W]</td><td rowspan=1 colspan=1>2</td><td rowspan=1 colspan=1>±0.1</td></tr><tr><td rowspan=1 colspan=1>Height [H]</td><td rowspan=1 colspan=1>0.7MAX</td><td rowspan=1 colspan=1>/</td></tr></table>

# 9.3 LGA-12L packing information

![](images/f2a4bfa1b04026ba779e0e79af9b1afd376f1f06cb3104db82ecd7e3f2daf382.jpg)  
Figure 19. Carrier tape information for LGA-12L package   
NOTES: 1 10SPROCKETHOLEFITCHCUMULATIVETOLERANCE±0.2 2. POCKETPOSITIONRELATIVETOSPROCKETHOLEMEASUREDASTRUEPOSITIONOFPOCKET,NOT POCKET HOLE. 3 AOANDBOARECALCULATEDONAPLANEAIADISTANCE“R'ABOVETHEBOTTOMOFTHEPOCKET

![](images/6ef69826400a496a1585077464d721b21ffcc1acf8d3b622c2edf2a05d634bb9.jpg)  
Figure 20. LGA-12L package orientation in carrier tape

# Revision history

Table 93. Document revision history   

<table><tr><td>Date</td><td>Revision</td><td>Changes</td></tr><tr><td>10-Feb-2017</td><td>1</td><td>Initial release</td></tr><tr><td rowspan="3">13-Apr-2017</td><td rowspan="3">2</td><td>Updated Applications and Figure 7: Accelerometer chain</td></tr><tr><td>Added Section 3.2.4: Activity/lnactivity, Android stationary/motion-detection functions</td></tr><tr><td>Renamed registers 3Ch, 3Dh, 3Eh,3Fh</td></tr><tr><td>15-Jun-2017</td><td>3</td><td>Added bullet concerning Android to Features</td></tr><tr><td rowspan="5">12-Sep-2017</td><td rowspan="5">4</td><td>Document status promoted to “production data&quot;</td></tr><tr><td>Updated Description</td></tr><tr><td>Updated Section 3.2.4: Activity/lnactivity, Android stationary/motion-detection functions</td></tr><tr><td>Added bit 7 to CTRL5_INT2_PAD_CTRL (24h)</td></tr><tr><td>Added bit 4 to WAKE_UP_DUR (35h)</td></tr><tr><td>01-Oct-2018</td><td>5</td><td>Added product label indicating participation in ST&#x27;s sustainable technology program</td></tr><tr><td rowspan="3">06-Nov-2018</td><td rowspan="3">6</td><td>Updated Section 3.2.4 Activity/lnactivity, Android stationary/motion-detection functions</td></tr><tr><td>Updated Figure 6. LIS2DW12 electrical connections (top view) Added Section 9.3 LGA-12 packing information</td></tr><tr><td>Updated Figure 19. Carrier tape information for LGA-12 package</td></tr><tr><td>03-May-2019</td><td>7</td><td>Updated OUT_T_L (ODh)and OUT_T_H (0Eh)</td></tr><tr><td>02-Jul-2019</td><td>8</td><td> Updated product summary</td></tr><tr><td rowspan="4">17-Sep-2024</td><td rowspan="4">9</td><td></td></tr><tr><td>Added quick links to product resources</td></tr><tr><td>Updated ViH and ViL in Table 4. Electrical characteristics as wellas Notes below Figure 3.SPl slave timing diagram and Figure 4. I²C slave timing diagram</td></tr><tr><td> Minor textual updates</td></tr></table>

# Contents

# 1 Block diagram and pin description.

1.1 Block diagram 3   
1.2 Pin description. 4

# Mechanical and electrical specifications . 6

2.1 Mechanical characteristics . .6   
2.2 Electrical characteristics . 7   
2.3 Temperature sensor characteristics 8   
2.4 Communication interface characteristics .9   
2.4.1 SPl - serial peripheral interface . 9   
2.4.2 I²C - inter-lC control interface 10

# 2.5 Absolute maximum ratings. 12

# Terminology and functionality .13

# 3.1 Terminology 13

3.1.1 Sensitivity 13   
3.1.2 Zero-g level offset . 13

# 3.2 Functionality. 14

3.2.1 Operating modes 14   
3.2.2 Single data conversion on-demand mode . 16   
3.2.3 Self-test. 16   
3.2.4 Activity/Inactivity, Android stationary/motion-detection functions . 17   
3.2.5 High tap/double-tap user configurability 17   
3.2.6 Offset management. 17

# Sensing element . 18

3.4 IC interface. 18   
3.5 Factory calibration.. 18   
3.6 Temperature sensor 18

# Application hints .19

# Digital main blocks .21

5.1 Block diagram of filters . .21   
5.2 Data stabilization time vs. ODR/device setting .22

# 5.3 FIFO .23

5.3.1 Bypass mode 24  
5.3.2 FIFO mode 24  
5.3.3 Continuous mode 24  
5.3.4 Continuous-to-FIFO mode.. .25

# 5.3.5 Bypass-to-continuous mode 26

# igital interfaces .27

# 6.1 ²C serial interface. 27

6.1.1 I²C operation . 28

# 6.2 SPI bus interface. .29

6.2.1 SPI read 30   
6.2.2 SPI write 31   
6.2.3 SPl read in 3-wire mode 32   
Register mapping.... ..33   
Register description ..35   
8.1 OUT_T_L (ODh).. . .35   
8.2 OUT_T_H (0Eh) .35   
8.3 WHO_AM_I (0Fh). . .35   
8.4 CTRL1 (20h) ..36   
8.5 CTRL2 (21h) ..37   
8.6 CTRL3 (22h) ..38   
8.7 CTRL4_INT1_PAD_CTRL (23h). ..39   
8.8 CTRL5_INT2_PAD_CTRL (24h). .40   
8.9 CTRL6 (25h) . .41   
8.10 OUT_T (26h).. .42   
8.11 STATUS (27h) . .42   
8.12 OUT_X_L (28h). .43   
8.13 OUT_X_H (29h) .43   
8.14 OUT_Y_L (2Ah). .43   
8.15 OUT_Y_H (2Bh) .43   
8.16 OUT_Z_L (2Ch).. .44   
8.17 OUT_Z_H (2Dh) .44   
8.18 FIFO_CTRL (2Eh). .44   
8.19 FIFO_SAMPLES (2Fh). .45   
8.20 TAP_THS_X (30h) .45   
8.21 TAP_THS_Y (31h) .46   
8.22 TAP_THS_Z (32h). .46   
8.23 INT_DUR (33h) . .47   
8.24 WAKE_UP_THS (34h) .47   
8.25 WAKE_UP_DUR (35h). .48   
8.26 FREE_FALL (36h).. .48   
8.27 STATUS_DUP (37h). .49   
8.28 WAKE_UP_SRC (38h). .50   
8.29 TAP_SRC (39h)... . .51   
8.30 SIXD_SRC (3Ah). .52   
8.31 ALL_INT_SRC (3Bh) .53   
8.32 X_OFS_USR (3Ch). .54   
8.33 Y_OFS_USR (3Dh). .54   
8.34 Z_OFS_USR (3Eh). .54   
8.35 CTRL7 (3Fh) . .55

# Package information. .56

9.1 Soldering information .56   
9.2 LGA-12L package information . .56   
9.3 LGA-12L packing information .57

# Revision history .58

# List of tables

#

Table 1. Pin description.. 4   
Table 2. Internal pull-up values (typ.) for SDO/SA0 and CS pins. 5   
Table 3. Mechanical characteristics 6   
Table 4. Electrical characteristics 7   
Table 5. Temperature sensor characteristics 8   
Table 6. SPl slave timing values. 9   
Table 7. $1 ^ { 2 } \mathrm { C }$ slave timing values . 10   
Table 8. βC high-speed mode specifications at 1 MHz and 3.4 MHz. 11   
Table 9. Absolute maximum ratings .. 12   
Table 10. Operating modes - low-noise setting disabled 14   
Table 11. Operating modes - low-noise setting enabled 15   
Table 12. Internal pin status 20   
Table 13. Number of samples to be discarded 22   
Table 14. Serial interface pin description. 27   
Table 15. IC terminology 27   
Table 16. SAD+read/write patterns. 28   
Table 17. Transfer when master is writing one byte to slave. 28   
Table 18. Transfer when master is writing multiple bytes to slave 28   
Table 19. Transfer when master is receiving (reading) one byte of data from slave . 28   
Table 20. Transfer when master is receiving (reading) multiple bytes of data from slave 28   
Table 21. Register map. 33   
Table 22. OUT_T_L register 35   
Table 23. OUT_T_L register description 35   
Table 24. OUT_T_Hregister 35   
Table 25. OUT_T_H register description 35   
Table 26. WHO_AM_I register default values. 35   
Table 27. Control register 1 . 36   
Table 28. Control register 1 description. 36   
Table 29. Data rate configuration. 36   
Table 30. Mode selection 36   
Table 31. Low-power mode selection 36   
Table 32. Control register 2 . 37   
Table 33. Control register 3 . 38   
Table 34. Control register 3 description. 38   
Table 35. Self-test mode selection 38   
Table 36. Control register 4．. 39   
Table 37. Control register 4 description . 39   
Table 38. Control register 5 . 40   
Table 39. Control register 5 description 40   
Table 40. Control register 6 . 41   
Table 41. Digital filtering cutoff selection 41   
Table 42. Full-scale selection. 41   
Table 43. OUT_T register 42   
Table 44. OUT_T register description 42   
Table 45. STATUS register 42   
Table 46. STATUS register description 42   
Table 47. OUT_X_L register 43   
Table 48. OUT_X_H register . 43   
Table 49. OUT_Y_L register 43   
Table 50. OUT_Y_Hregister 43   
Table 51. OUT_Z_L register 44   
Table 52. OUT_Z_H register . 44   
Table 53. FIFO_CTRL register. 44   
Table 54. FIFO_CTRL register description.. 44   
Table 55. FIFO mode selection 44   
Table 56. FIFO_SAMPLES register 45   
Table 57. FIFO_SAMPLES register description 45   
Table 58. TAP_THS_X register 45   
Table 59. TAP_THS_X register description 45   
Table 60. 4D/6D threshold setting FS $@ { \pm } 2 ~ g$ 45   
Table 61. TAP_THS_Y register 46   
Table 62. TAP_THS_Y register description 46   
Table 63. Selection of axis priority for tap detection 46   
Table 64. TAP_THS_Z register 46   
Table 65. TAP_THS_Z register description 46   
Table 66. INT_DUR register 47   
Table 67. INT_DUR register description 47   
Table 68. WAKE_UP_THS register. 47   
Table 69. WAKE_UP_THS register description 47   
Table 70. WAKE_UP_DUR register 48   
Table 71. WAKE_UP_DUR register description 48   
Table 72. FREE_FALL register 48   
Table 73. FREE_FALL register description 48   
Table 74. FREE_FALL threshold decoding $@ \pm 2 g$ FS 48   
Table 75. STATUS_DUP register . 49   
Table 76. STATUS_DUP register description . 49   
Table 77. WAKE_UP_SRC register 50   
Table 78. WAKE_UP_SRC register description 50   
Table 79. TAP_SRC register . 51   
Table 80. TAP_SRC register description . 51   
Table 81. SIXD_SRC register 52   
Table 82. SIXD_SRC register description 52   
Table 83. ALL_INT_SRC register.. 53   
Table 84. ALL_INT_SRC register description. 53   
Table 85. X_OFS_USR register . 54   
Table 86. X_OFS_USR register description. 54   
Table 87. Y_OFS_USR register. 54   
Table 88. Y_OFS_USR register description. 54   
Table 89. Z_OFS_USR register 54   
Table 90. Z_OFS_USR register description. 54   
Table 91. CTRL7 register 55   
Table 92. CTRL7 register description 55   
Table 93. Document revision history. 58

# List of figures

Figure 1. Block diagram 3   
Figure 2. Pin connections 4   
Figure 3. SPl slave timing diagram 9   
Figure 4. C slave timing diagram 10   
Figure 5. Single data conversion on-demand functionality 16   
Figure 6. LIS2DW12 electrical connections (top view). 19   
Figure 7. Accelerometer chain 21   
Figure 8. Continuous-to-FIFO mode 25   
Figure 9. Trigger event to FIFO for continuous-to-FIFO mode. 25   
Figure 10. Bypass-to-continuous mode . 26   
Figure 11. Trigger event to FIFO for bypass-to-continuous mode 26   
Figure 12. Read and write protocol . 29   
Figure 13. SPl read protocol 30   
Figure 14. Multiple byte SPI read protocol (2-byte example). 30   
Figure 15. SPl write protocol 31   
Figure 16. Multiple byte SPl write protocol (2-byte example) 31   
Figure 17. SPl read protocol in 3-wire mode 32   
Figure 18. LGA-12L $2 . 0 \times 2 . 0 \times 0 . 7$ mm package outline and mechanical data 56   
Figure 19. Carrier tape information for LGA-12L package 57   
Figure 20. LGA-12L package orientation in carier tape . 57

# IMPORTANT NOTICE-READ CAREFULLY

Scroelectdtt productsandrueatottrcsedeeeantfotidctsec products are sold pursuantto ST's terms and conditions of salein place at the time of order acknowledgment.

Purchasersarepofteecefctsdsuisaeif purchasers' products.

No license,express or implied,to any intellectual property right is granted by ST herein.

ResaleofSTproductswithprovisionsdiferentfromtheinformationsetforthhereinshallvoidanywarrantygrantedySTforsuchproduct.

STandtheearkfdialatodeaertpct are the property of their respective owners.

Information in this documentsupersedes andreplaces information previouslysuplied inany priorversions ofthisdocument.

$\circledcirc$ 2024 STMicroelectronics -All rights reserved