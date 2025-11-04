from utils.chart import generate_colors, auto_detect_keys
import json

def generate_echarts_scatter(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None,
    saturation=0.5,  # 新增饱和度参数
    brightness=0.95,  # 新增亮度参数
    group_key: str = None  # 新增分组字段参数
) -> str:
    """生成通用 ECharts 散点图配置，支持自动推断字段、多维数据和分组显示"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    if not name_key:
        name_key, _ = auto_detect_keys(data_list)
    
    if not value_keys:
        # 散点图需要至少两个值字段
        _, value_key = auto_detect_keys(data_list)
        # 尝试找第二个数值字段作为y轴
        numeric_keys = [k for k, v in data_list[0].items() if isinstance(v, (int, float)) and k != value_key]
        if numeric_keys:
            value_keys = [value_key, numeric_keys[0]]
        else:
            value_keys = [value_key, value_key]  # 如果只有一个数值字段，就用它作为两个轴
    elif len(value_keys) < 2:
        # 如果只提供了一个值字段，找另一个数值字段
        numeric_keys = [k for k, v in data_list[0].items() if isinstance(v, (int, float)) and k != value_keys[0]]
        if numeric_keys:
            value_keys.append(numeric_keys[0])
        else:
            value_keys.append(value_keys[0])  # 如果只有一个数值字段，就用它作为两个轴
    
    if series_names is None:
        series_names = [f"{value_keys[0]}-{value_keys[1]}分布"]
    
    # 验证字段存在
    for value_key in value_keys[:2]:  # 散点图只需要前两个值字段
        if value_key not in data_list[0] or name_key not in data_list[0]:
            raise KeyError(f"数据中未找到推断的字段: '{value_key}' 或 '{name_key}'")
    
    # 自动生成标题
    if not title:
        if group_key:
            title = f"{name_key} {value_keys[0]}与{value_keys[1]}分组散点图"
        else:
            title = f"{name_key} {value_keys[0]}与{value_keys[1]}关系散点图"

    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "xAxis": {
            "type": "value",
            "name": value_keys[0],
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
            "name": value_keys[1],
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        },
        "series": []
    }

    # 处理分组逻辑
    if group_key and group_key in data_list[0]:
        # 获取所有唯一的分组值
        groups = set(item.get(group_key) for item in data_list)
        groups = sorted(groups)  # 排序确保展示顺序一致
        colors = generate_colors(len(groups), saturation=saturation, brightness=brightness)
        
        # 为每个分组创建系列
        for i, group_value in enumerate(groups):
            group_data = []
            for item in data_list:
                if item.get(group_key) == group_value:
                    # 确保我们有足够的value_keys来获取x和y值
                    if len(value_keys) >= 2:
                        x_val = item[value_keys[0]]
                        y_val = item[value_keys[1]]
                        data_point = [x_val, y_val]
                        # 如果有name_key，添加名称信息用于tooltip
                        if name_key in item:
                            data_point.append(item[name_key])
                        group_data.append(data_point)
            
            series_config = {
                "name": str(group_value),
                "type": "scatter",
                "data": group_data,
                "symbolSize": 8,
                "itemStyle": {
                    "color": colors[i],
                    "opacity": 0.8
                },
                "emphasis": {
                    "itemStyle": {
                        "opacity": 1,
                        "shadowBlur": 10,
                        "shadowColor": 'rgba(0, 0, 0, 0.3)'
                    },
                    "symbolSize": 12
                },
                "tooltip": {
                    "formatter": f"{{{{a}}}}<br/>{value_keys[0]}: {{{{c[0]}}}}<br/>{value_keys[1]}: {{{{c[1]}}}}" +
                                 (f"<br/>{name_key}: {{{{c[2]}}}}" if len(group_data) > 0 and len(group_data[0]) > 2 else "")
                }
            }
            config["series"].append(series_config)
        
        # 添加图例
        config["legend"] = {
            "data": [str(g) for g in groups],
            "left": "center",
            "bottom": "0%",
            "textStyle": {
                "fontSize": 12
            }
        }
        
        # 调整网格以适应图例
        config["grid"] = {
            "left": "10%",
            "right": "15%",
            "bottom": "15%",
            "containLabel": True
        }
    else:
        # 不分组的传统散点图逻辑
        scatter_data = []
        for item in data_list:
            x_val = item[value_keys[0]]
            y_val = item[value_keys[1]]
            data_point = [x_val, y_val]
            # 如果有name_key，添加名称信息用于tooltip
            if name_key in item:
                data_point.append(item[name_key])
            scatter_data.append(data_point)
        
        color_list = generate_colors(1, saturation=saturation, brightness=brightness)
        
        series_config = {
            "name": series_names[0],
            "type": "scatter",
            "data": scatter_data,
            "symbolSize": 8,
            "itemStyle": {
                "color": color_list[0],
                "opacity": 0.8
            },
            "emphasis": {
                "itemStyle": {
                    "opacity": 1,
                    "shadowBlur": 10,
                    "shadowColor": 'rgba(0, 0, 0, 0.3)'
                },
                "symbolSize": 12
            },
            "tooltip": {
                "formatter": f"{{{{a}}}}<br/>{value_keys[0]}: {{{{c[0]}}}}<br/>{value_keys[1]}: {{{{c[1]}}}}" +
                             (f"<br/>{name_key}: {{{{c[2]}}}}" if len(scatter_data) > 0 and len(scatter_data[0]) > 2 else "")
            }
        }
        config["series"].append(series_config)
    
    return json.dumps(config, indent=4, ensure_ascii=False)