from utils.chart import generate_colors, auto_detect_keys
import json

def generate_echarts_funnel(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None,
    saturation=0.5,  # 新增饱和度参数
    brightness=0.95  # 新增亮度参数
) -> str:
    """生成通用 ECharts 漏斗图配置，支持自动推断字段和多维数据"""
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
    
    # 准备漏斗图数据，保持原始顺序
    echarts_data = [
        {"value": item[value_keys[0]], "name": item[name_key]}
        for item in data_list
    ]
    
    # 自动生成标题
    if not title:
        title = f"{name_key} {value_keys[0]}漏斗图"

    # 动态生成颜色列表
    color_list = generate_colors(len(data_list), saturation=saturation, brightness=brightness)

    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b}: {c} ({d}%)",
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "legend": {
            "data": [item[name_key] for item in data_list],
            "left": "center",
            "bottom": "0%",
            "textStyle": {
                "fontSize": 12
            }
        },
        "series": [
            {
                "name": series_names[0],
                "type": "funnel",
                "left": "10%",
                "top": 60,
                "bottom": 60,
                "width": "80%",
                "minSize": "0%",
                "maxSize": "100%",
                "sort": "none",
                "gap": 2,
                "label": {
                    "show": True,
                    "position": "inside",
                    "fontSize": 12
                },
                "labelLine": {
                    "length": 10,
                    "lineStyle": {
                        "width": 1,
                        "type": "solid"
                    }
                },
                "itemStyle": {
                    "borderColor": "#fff",
                    "borderWidth": 1
                },
                "emphasis": {
                    "label": {
                        "fontSize": 14,
                        "fontWeight": "bold"
                    }
                },
                "data": echarts_data
            }
        ],
        "color": color_list
    }
    
    return json.dumps(config, indent=4, ensure_ascii=False)