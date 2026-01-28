## AI Intelligent Chart Generation Tool (json2chart)

**Author:** lfenghx
**Version:** 1.2.0
**Type:** tool

### Description

json2chart is an intelligent JSON data visualization tool that can automatically convert JSON format data into various types of interactive charts. The tool adopts LLM intelligent analysis technology to automatically identify data structures and recommend the best visualization solutions.
![alt text](_assets/1.image.png)

Video tutorial: https://www.bilibili.com/video/BV1qj1CB8Enz

### Core Features

#### Intelligent Data Analysis and Field Recognition

- Automatically detect category fields and value fields in JSON data
- Intelligently analyze data structure through large models and recommend the best chart type
- Support automatically generating appropriate chart titles and data series names
- Provide automatic fallback mechanism when field detection fails

#### Multiple Chart Type Support

- **Pie Chart**: Suitable for displaying proportional distribution data
- **Bar Chart**: Suitable for comparing numerical sizes of different categories
- **Line Chart**: Suitable for displaying data trends over time or other continuous variables
- **Radar Chart**: Suitable for multi-dimensional data comparison analysis (requires at least 3 numerical fields)
- **Funnel Chart**: Suitable for displaying process conversion rate data
- **Scatter Chart**: Suitable for analyzing correlations between two numerical indicators

#### Advanced Features

- **Data Grouping Support**: Can display multi-series charts grouped by specified fields
- **Custom Color Scheme**: Support adjusting the saturation and brightness of chart colors
- **Intelligent Data Type Conversion**: Automatically attempt to convert relevant fields to appropriate numerical types
- **Automatic Error Handling**: Provide friendly error prompts and exception handling mechanisms
- **Multiple Data Format Support**: Accept JSON object arrays or JSON string formats

### Technical Features

- Generate interactive chart configurations based on ECharts
- Integrate large model analysis capabilities to improve the intelligence of chart generation
- Use pandas for data processing and analysis
- Adopt modular design, each chart type is independently implemented for easy expansion
- Support streaming output of chart configuration results

### Typical Application Scenarios

- Automatic visualization of data analysis reports
- Business indicator monitoring dashboard generation
- Quick display of statistical data
- Data exploration and pattern discovery
- Real-time visualization of API response data

### Input Format

One-dimensional data
[
{
"设备编号": "CNC1",
"效率": 76.0
},
{
"设备编号": "CNC2",
"效率": 77.0
}
]
![alt text](_assets/2.一维数据.png)

Two-dimensional data
[
{
"姓名": "张三",
"月份": "1 月",
"迟到次数": 2,
"迟到总时间": 5
},
{
"姓名": "张三",
"月份": "2 月",
"迟到次数": 3,
"迟到总时间": 7
}
]
![alt text](_assets/3.二维数据.png)

Three-dimensional data
[
{
"姓名": "张三",
"迟到次数": 14,
"旷工天数": 15,
"早退次数": 1
},
{
"姓名": "李四",
"迟到次数": 2,
"旷工天数": 14,
"早退次数": 3
}
]
![alt text](_assets/4.三维数据.png)

Multi-dimensional line data
[
{"成绩月份": "2024-09", "课程编号": "002", "成绩": 80.0},
{"成绩月份": "2024-09", "课程编号": "003", "成绩": 83.0},
{"成绩月份": "2024-09", "课程编号": "004", "成绩": 83.0},
{"成绩月份": "2024-09", "课程编号": "006", "成绩": 75.0},
{"成绩月份": "2024-09", "课程编号": "008", "成绩": 68.0},
{"成绩月份": "2024-09", "课程编号": "010", "成绩": 80.0},
{"成绩月份": "2024-09", "课程编号": "013", "成绩": 40.0},
{"成绩月份": "2024-09", "课程编号": "103", "成绩": 89.0},
{"成绩月份": "2024-10", "课程编号": "002", "成绩": 83.0},
{"成绩月份": "2024-10", "课程编号": "003", "成绩": 94.0},
{"成绩月份": "2024-10", "课程编号": "004", "成绩": 80.5},
{"成绩月份": "2024-10", "课程编号": "006", "成绩": 77.0},
{"成绩月份": "2024-10", "课程编号": "008", "成绩": 70.0},
{"成绩月份": "2024-10", "课程编号": "010", "成绩": 81.0},
{"成绩月份": "2024-10", "课程编号": "013", "成绩": 37.0},
{"成绩月份": "2024-10", "课程编号": "103", "成绩": 89.0},
{"成绩月份": "2024-11", "课程编号": "002", "成绩": 93.5},
{"成绩月份": "2024-11", "课程编号": "003", "成绩": 89.0},
{"成绩月份": "2024-11", "课程编号": "004", "成绩": 87.0},
{"成绩月份": "2024-11", "课程编号": "006", "成绩": 80.0},
{"成绩月份": "2024-11", "课程编号": "008", "成绩": 72.0},
{"成绩月份": "2024-11", "课程编号": "010", "成绩": 81.0},
{"成绩月份": "2024-11", "课程编号": "013", "成绩": 32.0},
{"成绩月份": "2024-11", "课程编号": "103", "成绩": 89.0},
{"成绩月份": "2024-12", "课程编号": "002", "成绩": 80.0},
{"成绩月份": "2024-12", "课程编号": "006", "成绩": 85.0},
{"成绩月份": "2025-01", "课程编号": "002", "成绩": 94.0},
{"成绩月份": "2025-01", "课程编号": "003", "成绩": 88.0},
{"成绩月份": "2025-01", "课程编号": "004", "成绩": 95.0},
{"成绩月份": "2025-01", "课程编号": "010", "成绩": 82.0},
{"成绩月份": "2025-01", "课程编号": "013", "成绩": 31.0},
{"成绩月份": "2025-01", "课程编号": "103", "成绩": 89.0}
]
![alt text](_assets/5.多维折线数据.png)

Radar chart
[
{
"产品": "产品 A",
"质量": 85,
"价格": 90,
"服务": 75,
"创新": 95,
"知名度": 80
},
{
"产品": "产品 B",
"质量": 92,
"价格": 83,
"服务": 88,
"创新": 85,
"知名度": 90
},
{
"产品": "产品 C",
"质量": 78,
"价格": 95,
"服务": 82,
"创新": 70,
"知名度": 75
}
]
![alt text](_assets/6.雷达图数据.png)

Funnel chart
[
{
"阶段": "浏览产品",
"用户数": 10000
},
{
"阶段": "加入购物车",
"用户数": 5000
},
{
"阶段": "提交订单",
"用户数": 3000
},
{
"阶段": "完成支付",
"用户数": 2000
},
{
"阶段": "确认收货",
"用户数": 1800
}
]
![alt text](_assets/7.漏斗图数据.png)

Scatter chart
[
{
"产品名称": "智能手机 A",
"价格(元)": 5999,
"月销量(台)": 12000,
"品牌": "品牌 X"
},
{
"产品名称": "智能手机 B",
"价格(元)": 4599,
"月销量(台)": 18000,
"品牌": "品牌 X"
},
{
"产品名称": "智能手机 C",
"价格(元)": 3999,
"月销量(台)": 25000,
"品牌": "品牌 Y"
},
{
"产品名称": "智能手机 D",
"价格(元)": 2999,
"月销量(台)": 32000,
"品牌": "品牌 Y"
},
{
"产品名称": "智能手机 E",
"价格(元)": 1999,
"月销量(台)": 45000,
"品牌": "品牌 Z"
},
{
"产品名称": "智能手机 F",
"价格(元)": 6999,
"月销量(台)": 8000,
"品牌": "品牌 X"
}
]
![alt text](_assets/8.散点图数据.png)

### Output Format

The tool outputs standard ECharts configuration strings, which can be directly rendered into interactive charts in ECharts-supported environments.

Plugin GitHub repository: https://github.com/lfenghx/json2chart

### Contact the author

Email: 550916599@qq.com
WeChat: lfeng2529230
github: lfenghx
