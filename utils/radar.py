from utils.chart import generate_colors, auto_detect_keys
import json

def generate_echarts_radar(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None,
    saturation=0.5,  # 新增饱和度参数
    brightness=0.95,  # 新增亮度参数
    group_key: str = None  # 新增分组参数
) -> str:
    """生成通用 ECharts 雷达图配置，支持自动推断字段和多维数据，支持按字段分组"""
    if not data_list:
        raise ValueError("数据列表不能为空")
    
    if not name_key:
        name_key, _ = auto_detect_keys(data_list)
    
    if not value_keys:
        _, value_key = auto_detect_keys(data_list)
        value_keys = [value_key]
    
    if series_names is None:
        series_names = [f"{value_key}" for value_key in value_keys]
    
    # 验证字段存在
    required_fields = [name_key] + value_keys
    if group_key:
        required_fields.append(group_key)
    
    for field in required_fields:
        if field not in data_list[0]:
            raise KeyError(f"数据中未找到字段: '{field}'")
    
    # 准备雷达图的数据结构
    indicators = [{"name": value_key, "max": max(item[value_key] for item in data_list) * 1.1} for value_key in value_keys]
    
    # 自动生成标题
    if not title:
        if group_key:
            title = f"不同{group_key}的{name_key}多维特征雷达图"
        else:
            title = f"{name_key} 多维特征雷达图"

    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b}: {c}",
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "radar": {
            "indicator": indicators,
            "radius": "65%",
            "shape": "circle",
            "splitNumber": 5,
            "axisName": {
                "color": "#666",
                "fontSize": 12
            },
            "splitLine": {
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            },
            "splitArea": {
                "show": True,
                "areaStyle": {
                    "color": ['rgba(255,255,255,0.2)', 'rgba(238,238,238,0.3)']
                }
            }
        },
        "series": []
    }
    
    # 按group_key分组生成多系列雷达图
    if group_key:
        # 获取所有唯一的分组值
        groups = list(set(item[group_key] for item in data_list))
        groups.sort()  # 排序确保展示顺序一致
        
        # 动态生成颜色列表（按分组-指标组合数量生成）
        total_series = len(groups) * len(value_keys)
        color_list = generate_colors(total_series, saturation=saturation, brightness=brightness)
        
        # 图例数据列表
        legend_data = []
        color_index = 0
        
        # 为每个分组-指标组合生成一个系列
        for group in groups:
            # 过滤出该分组的数据
            group_data = [item for item in data_list if item[group_key] == group]
            
            # 为每个value_key生成一个系列
            for i, value_key in enumerate(value_keys):
                # 使用series_names中的名称或默认名称
                series_name = series_names[i] if i < len(series_names) else value_key
                full_series_name = f"{group}-{series_name}"
                
                # 为该分组-指标组合构建雷达图数据
                group_series_data = []
                for item in group_data:
                    item_data = [item[value_key]]
                    group_series_data.append({
                        "value": item_data,
                        "name": item[name_key]
                    })
                
                series_config = {
                    "name": full_series_name,
                    "type": "radar",
                    "data": group_series_data,
                    "symbolSize": 6,
                    "lineStyle": {
                        "width": 2,
                        "color": color_list[color_index]
                    },
                    "itemStyle": {
                        "color": color_list[color_index]
                    },
                    "areaStyle": {
                        "opacity": 0.3
                    }
                }
                config["series"].append(series_config)
                legend_data.append(full_series_name)
                color_index += 1
        
        # 设置图例数据
        config["legend"] = {
            "data": legend_data,
            "left": "center",
            "bottom": "0%",
            "textStyle": {
                "fontSize": 12
            }
        }
    else:
        # 原有逻辑 - 不分组的雷达图
        series_data = []
        for item in data_list:
            item_data = [item[value_key] for value_key in value_keys]
            series_data.append({
                "value": item_data,
                "name": item[name_key]
            })
        
        # 动态生成颜色列表
        color_list = generate_colors(len(data_list), saturation=saturation, brightness=brightness)
        
        config["legend"] = {
            "data": [item[name_key] for item in data_list],
            "left": "center",
            "bottom": "0%",
            "textStyle": {
                "fontSize": 12
            }
        }
        
        series_config = {
            "name": series_names[0],
            "type": "radar",
            "data": series_data,
            "symbolSize": 6,
            "lineStyle": {
                "width": 2
            },
            "areaStyle": {
                "opacity": 0.3
            }
        }
        config["series"].append(series_config)
        config["color"] = color_list
    
    return json.dumps(config, indent=4, ensure_ascii=False)