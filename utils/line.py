from utils.chart import generate_colors, auto_detect_keys
import json

def generate_echarts_line(
    data_list: list,
    name_key: str = None,
    value_keys: list = None,
    title: str = None,
    series_names: list = None,
    saturation=0.5,  # 新增饱和度参数
    brightness=0.95,  # 新增亮度参数
    group_key=None  # 新增分组参数
) -> str:
    """生成通用 ECharts 折线图配置，支持自动推断字段和多维数据，支持按字段分组"""
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
    required_fields = [name_key] + value_keys
    if group_key:
        required_fields.append(group_key)
    
    for field in required_fields:
        if field not in data_list[0]:
            raise KeyError(f"数据中未找到字段: '{field}'")
    
    # 构造配置
    config = {
        "animation": True,
        "animationDuration": 1000,
        "title": {"text": title, "left": "center"},
        "tooltip": {
            "trigger": "axis",  # 改为axis触发，更适合多系列图表
            "formatter": "{b}<br/>{a}: {c}",
            "backgroundColor": 'rgba(50,50,50,0.9)',
            "textStyle": {
                "color": '#fff'
            },
            "borderColor": '#333',
            "borderWidth": 1
        },
        "legend": {  # 新增图例配置
            "left": "center",
            "bottom": "10%",
            "textStyle": {
                "fontSize": 12
            }
        },
        "series": []
    }
    
    # 按group_key分组生成多系列折线图
    if group_key:
        # 获取所有唯一的分组值
        groups = list(set(item[group_key] for item in data_list))
        groups.sort()  # 排序确保展示顺序一致
        # 获取所有唯一的x轴值
        x_axis_data = list(set(item[name_key] for item in data_list))
        x_axis_data.sort()  # 排序确保展示顺序一致
        
        # 为x轴配置
        config["xAxis"] = {
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
        }
        
        # 为y轴配置
        config["yAxis"] = {
            "type": "value",
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        }
        
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
                # 为每个x轴值准备数据，确保顺序一致
                series_data = []
                for x_value in x_axis_data:
                    # 查找对应的y值，如果不存在则用None表示
                    found = False
                    for item in group_data:
                        if item[name_key] == x_value:
                            series_data.append(item[value_key])
                            found = True
                            break
                    if not found:
                        series_data.append(None)
                
                # 使用series_names中的名称或默认名称
                series_name = series_names[i] if i < len(series_names) else value_key
                full_series_name = f"{group}-{series_name}"
                
                series_config = {
                    "name": full_series_name,
                    "type": "line",
                    "data": series_data,
                    "smooth": True,
                    "lineStyle": {
                        "width": 2,
                        "color": color_list[color_index]
                    },
                    "itemStyle": {
                        "color": color_list[color_index]
                    },
                    "symbol": 'circle',
                    "symbolSize": 8,
                    "connectNulls": True  # 连接空值点
                }
                config["series"].append(series_config)
                legend_data.append(full_series_name)
                color_index += 1
        
        # 设置图例数据
        config["legend"]["data"] = legend_data
        
        # 自动生成标题
        if not title:
            title = f"不同{group_key}的{', '.join(value_keys)}对比折线图"
    else:
        # 原有逻辑 - 基于value_keys生成多系列
        x_axis_data = [item[name_key] for item in data_list]
        series_data_list = []
        for value_key in value_keys:
            series_data = [item[value_key] for item in data_list]
            series_data_list.append(series_data)
        
        # 自动生成标题
        if not title:
            title = f"{name_key} {', '.join(value_keys)}分布折线图"

        # 动态生成颜色列表（按系列数量生成）
        color_list = generate_colors(len(value_keys), saturation=saturation, brightness=brightness)
        
        # 为x轴配置
        config["xAxis"] = {
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
        }
        
        # 为y轴配置
        config["yAxis"] = {
            "type": "value",
            "splitLine": {
                "show": True,
                "lineStyle": {
                    "color": ['#eee'],
                    "type": 'dashed'
                }
            }
        }
        
        # 设置图例数据
        config["legend"]["data"] = series_names
        
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
    
    # 更新标题
    config["title"]["text"] = title
    
    return json.dumps(config, indent=4, ensure_ascii=False)