from utils.chart import generate_colors, auto_detect_keys
import json

def generate_echarts_pie(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None,
    saturation=0.5,  # 新增饱和度参数
    brightness=0.95  # 新增亮度参数
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

    # 生成颜色列表，按数据项数量生成，传入饱和度和亮度
    color_list = generate_colors(len(data_list), saturation=saturation, brightness=brightness)

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