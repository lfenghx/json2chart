from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
import colorsys

def auto_detect_keys(data_list: list) -> tuple:
    """自动检测数据中的名称字段和值字段"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    # 获取第一个数据项的键值对
    sample = data_list[0]
    
    # 候选名称字段（字符串类型）
    name_candidates = [k for k, v in sample.items() if isinstance(v, str)]
    
    # 候选值字段（数值类型）
    value_candidates = [k for k, v in sample.items() if isinstance(v, (int, float))]
    
    # 验证是否找到合适的字段
    if not name_candidates:
        raise ValueError("数据中不包含字符串类型的字段，无法确定名称字段")
    if not value_candidates:
        raise ValueError("数据中不包含数值类型的字段，无法确定值字段")
    
    # 优先选择可能的字段名（按常见名称排序）
    common_name_keys = ["name", "device_id", "id", "product", "label"]
    common_value_keys = ["value", "efficiency", "sales", "count", "amount"]
    
    # 尝试找到最匹配的名称字段
    name_key = next((k for k in common_name_keys if k in name_candidates), name_candidates[0])
    
    # 尝试找到最匹配的值字段
    value_key = next((k for k in common_value_keys if k in value_candidates), value_candidates[0])
    
    return name_key, value_key

def generate_colors(num_colors):
    """
    动态生成指定数量的鲜艳颜色
    :param num_colors: 所需颜色的数量
    :return: 颜色列表
    """
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        # 提高饱和度和亮度以生成更鲜艳的颜色
        rgb = colorsys.hsv_to_rgb(hue, 0.9, 0.95)
        colors.append('#%02x%02x%02x' % tuple(int(c * 255) for c in rgb))
    return colors

def generate_echarts_pie(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None
) -> str:
    """生成通用 ECharts 饼图配置，支持自动推断字段和多维数据"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    if not name_key:
        name_key, _ = auto_detect_keys(data_list)
    
    if not value_keys:
        _, value_key = auto_detect_keys(data_list)
        value_keys = [value_key]
    
    if series_names is None:
        series_names = [f"{value_key}分布" for value_key in value_keys]
    
    # 验证字段存在
    for value_key in value_keys:
        if value_key not in data_list[0] or name_key not in data_list[0]:
            raise KeyError(f"数据中未找到推断的字段: '{value_key}' 或 '{name_key}'")
    
    all_echarts_data = []
    for value_key in value_keys:
        echarts_data = [
            {"value": item[value_key], "name": item[name_key]}
            for item in data_list
        ]
        all_echarts_data.append(echarts_data)
    
    # 自动生成标题
    if not title:
        unit = ""
        sample_value = data_list[0][value_keys[0]]
        if isinstance(sample_value, float):
            unit = "%"
        title = f"{name_key} {', '.join(value_keys)}分布{unit}饼图"
    
    configs = []
    for i, echarts_data in enumerate(all_echarts_data):
        color_list = generate_colors(len(data_list))
        config = {
            "animation": True,
            "animationDuration": 1000,
            "animationEasing": "cubicOut",
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "trigger": "item",
                "formatter": f"{{a}}<br/>{{b}}: {{c}}{unit} ({{d}}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "15%",
                "top": "center",
                "title": {"text": series_names[i], "show": True},
                "data": [item[name_key] for item in data_list]
            },
            "series": [
                {
                    "name": series_names[i],
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "avoidLabelOverlap": False,
                    "itemStyle": {
                        "borderRadius": 10,
                        "borderColor": "#fff",
                        "borderWidth": 2
                    },
                    "label": {
                        "show": False,
                        "position": "center",
                    },
                    "emphasis": {
                        "label": {
                            "show": True,
                            "fontSize": "18",
                            "fontWeight": "bold"
                        }
                    },
                    "labelLine": {
                        "show": False
                    },
                    "data": echarts_data
                }
            ],
            "color": color_list
        }
        configs.append(config)
    
    return json.dumps(configs, indent=4, ensure_ascii=False)

def generate_echarts_bar(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None
) -> str:
    """生成通用 ECharts 柱状图配置，支持自动推断字段和多维数据"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    if not name_key:
        name_key, _ = auto_detect_keys(data_list)
    
    if not value_keys:
        _, value_key = auto_detect_keys(data_list)
        value_keys = [value_key]
    
    if series_names is None:
        series_names = [f"{value_key}分布" for value_key in value_keys]
    
    # 验证字段存在
    for value_key in value_keys:
        if value_key not in data_list[0] or name_key not in data_list[0]:
            raise KeyError(f"数据中未找到推断的字段: '{value_key}' 或 '{name_key}'")
    
    x_axis_data = [item[name_key] for item in data_list]
    series_data_list = []
    for value_key in value_keys:
        series_data = [item[value_key] for item in data_list]
        series_data_list.append(series_data)
    
    # 自动生成标题
    if not title:
        unit = ""
        sample_value = data_list[0][value_keys[0]]
        if isinstance(sample_value, float):
            unit = "%"
        title = f"{name_key} {', '.join(value_keys)}分布{unit}柱状图"
    
    # 处理单位
    unit = ""
    first_item_value = data_list[0][value_keys[0]]
    if isinstance(first_item_value, float):
        unit = "%"
    
    # 动态生成颜色列表
    color_list = generate_colors(len(value_keys))  # 关键修改点1

    # 处理单位（移动到tooltip配置前）
    unit = ""
    if value_keys:
        first_item_value = data_list[0][value_keys[0]]
        if isinstance(first_item_value, float):
            unit = "%"

    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a}<br/>{b}: {c}" + unit,
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "xAxis": {
            "type": "category",
            "data": x_axis_data,
            "axisTick": {
                "alignWithLabel": True
            },
            "axisLabel": {
                "rotate": 45,
                "interval": 0
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        },
        "yAxis": {
            "type": "value",
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        },
        "legend": {  # 新增图例配置
            "data": series_names,
            "left": "center",
            "bottom": "0%",
            "textStyle": {
                    "fontSize": 12
                }
        },
        "series": []
    }
    
    for i, series_data in enumerate(series_data_list):
        series_config = {
            "name": series_names[i],
            "type": "bar",
            "data": series_data,
            "itemStyle": {
                "color": color_list[i],
                "barBorderRadius": [5, 5, 0, 0],
                "shadowBlur": 10,
                "shadowColor": 'rgba(0, 0, 0, 0.3)'
            }
        }
        config["series"].append(series_config)
    
    return json.dumps(config, indent=4, ensure_ascii=False)

def generate_echarts_line(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None
) -> str:
    """生成通用 ECharts 折线图配置，支持自动推断字段和多维数据"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    if not name_key:
        name_key, _ = auto_detect_keys(data_list)
    
    if not value_keys:
        _, value_key = auto_detect_keys(data_list)
        value_keys = [value_key]
    
    if series_names is None:
        series_names = [f"{value_key}分布" for value_key in value_keys]
    
    # 验证字段存在
    for value_key in value_keys:
        if value_key not in data_list[0] or name_key not in data_list[0]:
            raise KeyError(f"数据中未找到推断的字段: '{value_key}' 或 '{name_key}'")
    
    x_axis_data = [item[name_key] for item in data_list]
    series_data_list = []
    for value_key in value_keys:
        series_data = [item[value_key] for item in data_list]
        series_data_list.append(series_data)
    
    # 自动生成标题
    if not title:
        unit = ""
        sample_value = data_list[0][value_keys[0]]
        if isinstance(sample_value, float):
            unit = "%"
        title = f"{name_key} {', '.join(value_keys)}分布{unit}折线图"
    
    # 处理单位
    unit = ""
    first_item_value = data_list[0][value_keys[0]]
    if isinstance(first_item_value, float):
        unit = "%"
    # 动态生成颜色列表（按系列数量生成）
    color_list = generate_colors(len(value_keys))  # 关键修改点1
    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a}<br/>{b}: {c}" + unit,
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "xAxis": {
            "type": "category",
            "data": x_axis_data,
            "axisTick": {
                "alignWithLabel": True
            },
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        },
        "yAxis": {
            "type": "value",
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        },
        "legend": {  # 新增图例配置
            "data": series_names,
            "left": "center",
            "bottom": "10%",
            "textStyle": {
                "fontSize": 12
            }
        },
        "series": []
    }
    
    for i, series_data in enumerate(series_data_list):
        series_config = {
            "name": series_names[i],
            "type": "line",
            "data": series_data,
            "smooth": True,
            "lineStyle": {
                "width": 2,
                "color": color_list[i]
            },
            "itemStyle": {
                "color": color_list[i]
            },
            "symbol": 'circle',
            "symbolSize": 8
        }
        config["series"].append(series_config)
    
    return json.dumps(config, indent=4, ensure_ascii=False)

class Json2chartTool(Tool):
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        chart_type = tool_parameters.get("chart_type", "饼状图")
        chart_data = tool_parameters.get("chart_data", [])
        chart_title = tool_parameters.get("chart_title", "图表")
        value_keys = tool_parameters.get("value_keys", None)
        series_names = tool_parameters.get("series_names", None)
        try:
            data_list = json.loads(chart_data)
            # 解析 value_keys
            if value_keys:
                value_keys = json.loads(value_keys.replace("'", "\""))
            # 解析 series_names
            if series_names:
                series_names = json.loads(series_names.replace("'", "\""))

            if chart_type == "饼状图":
                echarts_config = generate_echarts_pie(data_list, title=chart_title, value_keys=value_keys, series_names=series_names)
            elif chart_type == "柱状图":
                echarts_config = generate_echarts_bar(data_list, title=chart_title, value_keys=value_keys, series_names=series_names)
            elif chart_type == "折线图":
                echarts_config = generate_echarts_line(data_list, title=chart_title, value_keys=value_keys, series_names=series_names)
            else:
                raise ValueError(f"不支持的图表类型: {chart_type}")

            yield self.create_text_message(f"```echarts\n{echarts_config}\n```")

        except Exception as e:
            yield self.create_text_message(f"生成失败！错误信息: {str(e)}")