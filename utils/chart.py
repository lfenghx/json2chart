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

def generate_colors(num_colors, saturation=0.5, brightness=0.7):
    """
    动态生成指定数量的颜色，可自定义饱和度和亮度
    :param num_colors: 所需颜色的数量
    :param saturation: 颜色的饱和度，默认值为 0.7
    :param brightness: 颜色的亮度，默认值为 0.95
    :return: 颜色列表
    """
    colors = []
    for i in range(num_colors):
        hue = i / num_colors
        # 使用用户传入的饱和度和亮度生成颜色
        rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
        colors.append('#%02x%02x%02x' % tuple(int(c * 255) for c in rgb))
    return colors