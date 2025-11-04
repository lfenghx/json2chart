#第四版，更智能的图表生成方案
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json
from utils.pie import generate_echarts_pie
from utils.line import generate_echarts_line
from utils.bar import generate_echarts_bar
from utils.radar import generate_echarts_radar
from utils.funnel import generate_echarts_funnel
from utils.scatter import generate_echarts_scatter


from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
import pandas as pd

class Json2chartTool(Tool):
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        chart_data = tool_parameters.get("chart_data", [])
        chart_title = tool_parameters.get("chart_title")
        chart_type = tool_parameters.get("chart_type")
        model = tool_parameters.get("model")
        saturation = tool_parameters.get("saturation", 0.5)
        brightness = tool_parameters.get("brightness", 0.95)
        
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

            # 提取数据样本时，优先使用去重后的数据，确保展示所有类型
            unique_df = df.drop_duplicates()
            if len(unique_df) > 20:
                sample_df = unique_df.head(20)
            else:
                sample_df = unique_df
            # 转换为类似 Markdown 格式，设置 index=False 避免输出索引列
            sample_data = sample_df.to_csv(sep='|', na_rep='nan', index=False)
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
                            2. `chart_type` 的值为字符串，代表图表类型，目前支持"柱状图"、"折线图"、"饼状图"、"雷达图"、"漏斗图"、"散点图"。若用户指定了图表类型，则按用户的来，若没有指定，则你根据表格样例信息自动判断。
                            3. `chart_title` 的值为字符串，代表图表标题，若用户指定了标题，则按用户的来，若没有指定，则你根据表格样例信息自动生成。
                            4. `name_key` 的值为一个字符串，代表横坐标的 key，必须为 Markdown 表格中已有的表头字段，且应为类别型数据。
                            5. `value_keys` 的值为一个字符串数组，代表纵坐标的 key，这些 key 必须为 Markdown 表格中已有的表头字段，且必须为数值类型数据。
                            6. `series_names` 的值为一个字符串数组，是 `value_keys` 对应 key 的中文翻译，与 `value_keys` 数组元素一一对应。
                            7. `group_key` 的值为一个字符串（可选），代表用于分组的字段名。当数据需要按某个维度分组展示多系列图表时使用，如课程号、产品类别等。
                            8. 请根据 markdown 表格数据内容，抓取对数据分析有展现价值的 key。
                            9. 确保横纵坐标的选取有数据分析意义，避免选取序号等无分析价值的字段。
                            10. 雷达图适合多维度对比分析，至少需要3个数值字段；散点图适合两个数值指标间的相关性分析，必须选择两个数值字段作为value_keys，name_key应选择类别型或ID型字段（不是数值字段）；漏斗图适合流程转化率分析，需要有明确的先后顺序。
                            11. 饼图通常只使用一个数值字段和一个类别字段；柱状图和折线图适合展示类别与数值的关系。
                            12. 当数据中存在明显的分组维度（如多个课程、多个产品等）且需要比较它们在同一指标上的差异时，应识别出合适的`group_key`，group_key应是类别型字段。
                            13. 对于散点图，当需要按类别区分不同数据点时，应将类别型字段设置为group_key，而不是name_key。
                            14. 请仔细识别数据类型，确保value_keys只包含可以进行数学运算的数值字段，避免选择文本或混合类型字段。
                            15. 只输出标准的 json 格式内容，不要包含```json```标签，不要输出其他任何文字。
                            
                            示例：
                            表格数据：
                            |产品|销量|利润|
                            |---|---|---|
                            |A|100|20|
                            |B|200|50|
                            |C|150|30|
                            
                            柱状图输出：
                            {"chart_type":"柱状图","chart_title":"产品销量与利润分析","name_key":"产品","value_keys":["销量","利润"],"series_names":["销量","利润"]}
                            
                            饼图输出：
                            {"chart_type":"饼状图","chart_title":"产品销量分布","name_key":"产品","value_keys":["销量"],"series_names":["销量"]}
                            
                            带分组的折线图输出（例如课程成绩数据）：
                            {"chart_type":"折线图","chart_title":"各课程成绩对比","name_key":"score_month","value_keys":["score"],"series_names":["成绩"],"group_key":"course_no"}
                            
                            散点图输出（例如产品价格与销量关系分析）：
                            {"chart_type":"散点图","chart_title":"产品价格与销量关系分析","name_key":"产品名称","value_keys":["价格(元)","月销量(台)"],"series_names":["价格(元)","月销量(台)"],"group_key":"品牌"}
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
                print("大模型输出的json:", response.message.content)
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
                # group_key是可选的
                group_key = config_params.get("group_key")

                if len(value_keys) != len(series_names):
                    raise ValueError("value_keys 和 series_names 的长度不一致")

                if name_key not in df.columns:
                    raise ValueError(f"name_key {name_key} 不存在于 DataFrame 中")

                for value_key in value_keys:
                    if value_key not in df.columns:
                        yield self.create_text_message(f"value_key {value_key} 不存在于 DataFrame 中")
                        return

            except json.JSONDecodeError:
                yield self.create_text_message(f"大模型返回的内容不是有效的 JSON 格式")
                return
            except Exception as e:
                # 当大模型配置无效时，尝试使用auto_detect_keys作为后备方案
                yield self.create_text_message(f"大模型配置验证失败: {str(e)}")
                # 导入auto_detect_keys函数
                from utils.chart import auto_detect_keys
                try:
                    yield self.create_text_message("正在尝试使用自动检测字段作为后备方案...")
                    # 自动检测合适的字段
                    detected_name_key, detected_value_keys = auto_detect_keys(data_list)
                    
                    # 根据检测到的字段自动选择图表类型
                    if chart_type is None:
                        if len(detected_value_keys) >= 3:
                            chart_type = "雷达图"
                        elif len(detected_value_keys) == 2:
                            chart_type = "散点图"
                        else:
                            chart_type = "柱状图"
                    
                    # 设置默认的series_names
                    detected_series_names = detected_value_keys
                    
                    yield self.create_text_message(f"自动检测结果: 图表类型={chart_type}, 类别字段={detected_name_key}, 数值字段={detected_value_keys}")
                    
                    # 使用检测到的字段继续处理
                    name_key = detected_name_key
                    value_keys = detected_value_keys
                    series_names = detected_series_names
                    group_key = None  # 自动检测模式下暂不支持group_key
                    
                    # 重新设置图表标题（如果未指定）
                    if chart_title is None:
                        chart_title = f"{name_key} 数据分析图表"
                except Exception as fallback_error:
                    yield self.create_text_message(f"自动检测字段也失败: {str(fallback_error)}")
                    return

            # 根据图表类型验证配置参数
            try:
                # 验证数据类型是否适合所选图表
                if chart_type == "散点图":
                    # 检查name_key是否是数值字段且value_keys只有一个元素
                    if len(value_keys) == 1 and name_key in df.columns:
                        try:
                            # 尝试将name_key转换为数值类型，检查是否为有效数值
                            df[name_key] = pd.to_numeric(df[name_key], errors='coerce')
                            if not df[name_key].isna().all():
                                # 如果name_key是数值字段，将其也加入value_keys
                                yield self.create_text_message(f"检测到name_key '{name_key}' 是数值字段，已自动将其作为第二个数值轴")
                                value_keys = [name_key] + value_keys
                                series_names = [name_key] + series_names
                        except:
                            pass
                    
                    # 如果最终还是少于两个数值字段，使用scatter.py中的自动补充逻辑
                    if len(value_keys) < 1:
                        raise ValueError("散点图需要至少一个数值字段")
                elif chart_type == "雷达图" and len(value_keys) < 3:
                    raise ValueError("雷达图需要至少三个数值字段进行多维度分析")
                elif chart_type == "饼状图" and len(value_keys) != 1:
                    # 饼图只使用第一个数值字段
                    yield self.create_text_message("饼图只支持一个数值字段，将使用第一个字段")
                    value_keys = value_keys[:1]
                    series_names = series_names[:1]
                
                # 验证字段是否为数值类型
                for value_key in value_keys:
                    try:
                        # 尝试将数据转换为数值类型，验证是否为有效数值
                        df[value_key] = pd.to_numeric(df[value_key], errors='coerce')
                        # 检查是否有值被转换为NaN
                        if df[value_key].isna().all():
                            raise ValueError(f"字段 {value_key} 无法转换为数值类型")
                    except Exception as e:
                        raise ValueError(f"字段 {value_key} 不是有效的数值类型: {str(e)}")
                
                # 根据图表类型生成 ECharts 配置
                supported_chart_types = ["饼状图", "柱状图", "折线图", "雷达图", "漏斗图", "散点图"]
                if chart_type not in supported_chart_types:
                    yield self.create_text_message(f"不支持的图表类型: {chart_type}")
                    return

                if chart_type == "饼状图":
                    echarts_config = generate_echarts_pie(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness)
                elif chart_type == "柱状图":
                    echarts_config = generate_echarts_bar(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness, group_key=group_key)
                elif chart_type == "折线图":
                    echarts_config = generate_echarts_line(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness, group_key=group_key)
                elif chart_type == "雷达图":
                    echarts_config = generate_echarts_radar(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness, group_key=group_key)
                elif chart_type == "漏斗图":
                    echarts_config = generate_echarts_funnel(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness)
                elif chart_type == "散点图":
                    echarts_config = generate_echarts_scatter(data_list, name_key=name_key, title=chart_title, value_keys=value_keys, series_names=series_names, saturation=saturation, brightness=brightness, group_key=group_key)

                yield self.create_text_message(f"\n```echarts\n{echarts_config}\n```")

            except Exception as e:
                yield self.create_text_message(f"生成失败！错误信息: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"生成失败！错误信息: {str(e)}")