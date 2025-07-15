from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
import colorsys
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
import pandas as pd

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
        title = f"{name_key} {', '.join(value_keys)}分布饼图"

    legend_data = [item[name_key] for item in data_list]

    max_radius = 70  # 最大半径
    min_radius = 30   # 最小内径
    ring_width = (max_radius - min_radius) / len(all_echarts_data) if len(all_echarts_data) > 1 else 20

    # 生成颜色列表，按数据项数量生成
    color_list = generate_colors(len(data_list))

    # 构造单个配置对象
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
            "formatter": "{a}<br/>{b}: {c} ({d}%)"
        },
        "legend": {
            "type": "scroll",  # 添加滚动功能
            "orient": "horizontal",  # 水平布局
            "left": "center",
            "bottom": "0%",  # 图例放在底部
            "textStyle": {
                "fontSize": 10  # 减小字体大小
            },
            "data": legend_data
        },
        "series": [],
        "color": color_list
    }

    # 计算每个系列的半径，避免饼图重叠
    series_count = len(all_echarts_data)
    radius_step = 20 // series_count  # 根据系列数量计算半径步长

    for i, echarts_data in enumerate(all_echarts_data):
        # 外层系列用大半径，内层系列用小半径
        outer_radius = max_radius - i * ring_width
        inner_radius = max(outer_radius - ring_width, 0)

        series_config = {
            "name": series_names[i],
            "type": "pie",
            "radius": [f"{inner_radius}%", f"{outer_radius}%"],  # 调整每个系列的半径
            "avoidLabelOverlap": True,  # 开启标签重叠处理
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
            "data": [
                {
                    "value": item[value_keys[i]],
                    "name": item[name_key],
                    # 保持颜色与图例一致
                    "itemStyle": {"color": color_list[j]}
                }
                for j, item in enumerate(data_list)
            ]
        }
        config["series"].append(series_config)

    return json.dumps(config, indent=4, ensure_ascii=False)

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
        title = f"{name_key} {', '.join(value_keys)}分布柱状图"

    # 动态生成颜色列表
    color_list = generate_colors(len(value_keys))

    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a}<br/>{b}: {c}",
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
        title = f"{name_key} {', '.join(value_keys)}分布折线图"

    # 动态生成颜色列表（按系列数量生成）
    color_list = generate_colors(len(value_keys))
    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a}<br/>{b}: {c}",
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
        chart_data = tool_parameters.get("chart_data", [])
        chart_title = tool_parameters.get("chart_title")
        chart_type = tool_parameters.get("chart_type")
        model = tool_parameters.get("model")
        
        # 检查 chart_data 是否为字符串，若是则尝试解析为 JSON
        if isinstance(chart_data, str):
            try:
                chart_data = json.loads(chart_data)
            except json.JSONDecodeError:
                yield self.create_text_message("图表数据不是有效的 JSON 格式")
                return

        try:
            df = pd.DataFrame(chart_data)
            data_list = df.to_dict(orient='records')  # 将 DataFrame 转换为列表

            # 提取表头和前三行数据并转换为类似 Markdown 格式，设置 index=False 避免输出索引列
            sample_data = df.head(3).to_csv(sep='|', na_rep='nan', index=False)
            sample_markdown = '|' + sample_data.replace('\n', '\n|')

            # 调用大模型生成配置参数
            try:
                response = self.session.model.llm.invoke(
                    model_config=LLMModelConfig(
                        provider=model.get('provider'),
                        model=model.get('model'),
                        mode=model.get('mode'),
                        completion_params=model.get('completion_params'),
                    ),
                    prompt_messages=[
                        SystemPromptMessage(
                            content="""
                            你是一个专业的数据可视化专家，需要根据给定的 Markdown 表格数据，判断合适的横坐标和纵坐标，用于生成可视化图表。请遵循以下规则：
                            1. 输出格式必须为 JSON，包含`chart_type`, `chart_title`, `name_key`, `value_keys`, `series_names` 字段。
                            2. `chart_type` 的值为字符串，代表图表类型，目前仅支持“柱状图”、“折线图”、“饼状图”。若用户指定了图表类型，则按用户的来，若没有指定，则你根据表格样例信息自动判断。
                            3. `chart_title` 的值为字符串，代表图表标题，若用户指定了标题，则按用户的来，若没有指定，则你根据表格样例信息自动生成。
                            4. `name_key` 的值为一个字符串，代表横坐标的 key，必须为 Markdown 表格中已有的表头字段。
                            5. `value_keys` 的值为一个字符串数组，代表纵坐标的 key，可包含多个 key，这些 key 必须为 Markdown 表格中已有的表头字段，尽可能把所有数值列都包含进来。
                            6. `series_names` 的值为一个字符串数组，是 `value_keys` 对应 key 的中文翻译，与 `value_keys` 数组元素一一对应。
                            7. 请根据 markdown 表格数据内容，抓取对数据分析有展现价值的 key。
                            8. 确保横纵坐标的选取有数据分析意义，避免选取序号等无分析价值的字段。
                            9. 只输出标准的 json 格式内容，不要包含```json```标签，不要输出其他任何文字。
                            """
                        ),
                        UserPromptMessage(
                            content=f"用户指定的类型：{chart_type}\n用户指定的标题：{chart_title}\n表格的样例数据:\n{sample_markdown}"
                        )
                    ],
                    stream=False
                )
            except Exception as e:
                yield self.create_text_message(f"调用大模型生成配置失败: {str(e)}")
                return

            # 提取大模型返回的 JSON 数据
            try:
                config_params = json.loads(response.message.content)
                required_fields = ["chart_type", "chart_title", "name_key", "value_keys", "series_names"]
                for field in required_fields:
                    if field not in config_params:
                        raise ValueError(f"大模型返回的 JSON 缺少必要字段: {field}")

                chart_type = config_params["chart_type"]
                chart_title = config_params["chart_title"]
                name_key = config_params["name_key"]
                value_keys = config_params["value_keys"]
                series_names = config_params["series_names"]

                if len(value_keys) != len(series_names):
                    raise ValueError("value_keys 和 series_names 的长度不一致")

                if name_key not in df.columns:
                    raise ValueError(f"name_key {name_key} 不存在于 DataFrame 中")

                for value_key in value_keys:
                    if value_key not in df.columns:
                        raise ValueError(f"value_key {value_key} 不存在于 DataFrame 中")

            except json.JSONDecodeError:
                yield self.create_text_message(f"大模型返回的内容不是有效的 JSON 格式")
                return

            # 根据图表类型生成 ECharts 配置
            supported_chart_types = ["饼状图", "柱状图", "折线图"]
            if chart_type not in supported_chart_types:
                yield self.create_text_message(f"不支持的图表类型: {chart_type}")
                return

            if chart_type == "饼状图":
                echarts_config = generate_echarts_pie(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names)
            elif chart_type == "柱状图":
                echarts_config = generate_echarts_bar(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names)
            elif chart_type == "折线图":
                echarts_config = generate_echarts_line(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names)

            yield self.create_text_message(f"\n```echarts\n{echarts_config}\n```")

        except Exception as e:
            yield self.create_text_message(f"生成失败！错误信息: {str(e)}")