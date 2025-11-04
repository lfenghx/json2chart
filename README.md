## AI Intelligent Chart Generation Tool (json2chart)

**Author:** lfenghx
**Version:** 1.2.0
**Type:** tool

### Description

json2chart is an intelligent JSON data visualization tool that can automatically convert JSON format data into various types of interactive charts. The tool adopts LLM intelligent analysis technology to automatically identify data structures and recommend the best visualization solutions.
![alt text](1.image.png)

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

### Output Format

The tool outputs standard ECharts configuration strings, which can be directly rendered into interactive charts in ECharts-supported environments.

Plugin GitHub repository: https://github.com/lfenghx/json2chart

Contact the author:
Email: 550916599@qq.com
WeChat: lfeng2529230
github: lfenghx
