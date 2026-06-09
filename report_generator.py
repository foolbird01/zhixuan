"""
报告生成器 - 把评估结果转成可阅读的报告

支持两种格式：
1. Markdown 报告（简单易读）
2. HTML 报告（漂亮，可转PDF）
3. PDF 报告（用 ReportLab 生成）

就像餐厅的"结账小票"，把整个评估过程的结果打印出来
"""

import sys
import json

# 修复 Windows GBK 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 不需要显示图形界面
import matplotlib.pyplot as plt
from models import BenchmarkReport
from config import REPORT_OUTPUT_DIR, TEMPLATE_DIR


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        """初始化 Jinja2 模板引擎"""
        # Jinja2 就像"邮件合并"功能
        # 你写一个模板（带占位符），然后填入实际数据，生成最终文档
        self.template_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=True,
        )
        
        # 确保输出目录存在
        os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
        
        print("✅ 报告生成器初始化完成")
    
    
    def generate_markdown_report(self, report: BenchmarkReport) -> str:
        """
        生成 Markdown 格式报告
        
        Markdown 就像"简化版HTML"
        - 用 # 表示标题
        - 用 **文字** 表示加粗
        - 用 | 分隔表示表格
        很多平台都能直接渲染（GitHub、语雀、飞书等）
        """
        
        # 报告内容（用 Markdown 格式）
        md_lines = []
        
        # ========== 标题 ==========
        md_lines.append(f"# {report.report_title}\n")
        md_lines.append(f"**报告ID**: {report.report_id}  ")
        md_lines.append(f"**生成时间**: {report.created_at}  ")
        md_lines.append(f"**评估批次**: {report.batch_name}  ")
        md_lines.append(f"**测试任务数**: {report.total_tasks}  ")
        md_lines.append(f"**测试模型**: {', '.join(report.models_tested)}  ")
        md_lines.append("\n---\n")
        
        # ========== 执行摘要 ==========
        md_lines.append("## 📊 执行摘要\n")
        
        if report.summary_stats:
            md_lines.append("| 模型 | 综合得分 | 质量得分 | 总成本 | 平均响应时间 |")
            md_lines.append("|------|---------|---------|--------|------------|")
            
            for model_name, stats in report.summary_stats.items():
                md_lines.append(
                    f"| {model_name} "
                    f"| {stats.get('avg_comprehensive_score', 0)} "
                    f"| {stats.get('avg_quality_score', 0)} "
                    f"| ${stats.get('total_cost', 0):.4f} "
                    f"| {stats.get('avg_latency', 0):.2f}s |"
                )
            
            md_lines.append("")
        
        md_lines.append("---\n")
        
        # ========== 详细评估结果 ==========
        md_lines.append("## 📝 详细评估结果\n")
        
        for i, task_result in enumerate(report.task_results):
            md_lines.append(f"### 任务 {i+1}: {task_result.task_id}\n")
            md_lines.append(f"**任务类型**: {task_result.task_type}  ")
            md_lines.append(f"**指令**: {task_result.instruction}  ")
            if task_result.input_text:
                md_lines.append(f"**输入**: {task_result.input_text[:100]}...  ")
            md_lines.append("")
            
            # 表格：各模型表现对比
            md_lines.append("| 模型 | 综合得分 | 质量得分 | 成本 | 响应时间 |")
            md_lines.append("|------|---------|---------|------|----------|")
            
            for model_name in report.models_tested:
                if model_name in task_result.comprehensive_scores:
                    comp_score = task_result.comprehensive_scores[model_name]
                    quality_score = task_result.quality_scores[model_name].overall_score if model_name in task_result.quality_scores else 0
                    cost = task_result.responses[model_name].cost if model_name in task_result.responses else 0
                    latency = task_result.responses[model_name].latency if model_name in task_result.responses else 0
                    
                    md_lines.append(
                        f"| {model_name} "
                        f"| {comp_score} "
                        f"| {quality_score} "
                        f"| ${cost:.6f} "
                        f"| {latency:.2f}s |"
                    )
            
            md_lines.append("")
            
            # 展示各模型的回复（折叠显示）
            md_lines.append("<details>")
            md_lines.append("<summary>点击查看各模型的详细回复</summary>\n")
            
            for model_name in report.models_tested:
                if model_name in task_result.responses:
                    resp = task_result.responses[model_name]
                    md_lines.append(f"#### {model_name}\n")
                    md_lines.append(f"**回复**:\n```\n{resp.output_text}\n```\n")
                    if model_name in task_result.quality_scores:
                        qs = task_result.quality_scores[model_name]
                        md_lines.append(f"**质量评分**: {qs.overall_score}/10  ")
                        md_lines.append(f"**评分理由**: {qs.reasoning}\n")
            
            md_lines.append("</details>\n")
            md_lines.append("---\n")
        
        
        # ========== 推荐结论 ==========
        if report.recommendation:
            md_lines.append("## 💡 推荐结论\n")
            
            if "best_overall" in report.recommendation:
                md_lines.append(f"**综合最优模型**: **{report.recommendation['best_overall']}**\n")
            
            if "best_cost_effective" in report.recommendation:
                md_lines.append(f"**性价比最高模型**: **{report.recommendation['best_cost_effective']}**\n")
            
            if "reasoning" in report.recommendation:
                md_lines.append(f"\n{report.recommendation['reasoning']}\n")
            
            md_lines.append("\n---\n")
        
        
        # ========== 成本预测 ==========
        if report.cost_projection:
            md_lines.append("## 💰 成本预测（不同调用量下）\n")
            md_lines.append("| 月调用量 | " + " | ".join(report.models_tested) + " |")
            md_lines.append("|" + "|".join(["---"] * (len(report.models_tested) + 1)) + "|")
            
            for projection in next(iter(report.cost_projection.values())):
                row = f"| {projection['monthly_calls']}次 "
                for model_name in report.models_tested:
                    if model_name in report.cost_projection:
                        # 找到对应调用量的成本
                        for p in report.cost_projection[model_name]:
                            if p["monthly_calls"] == projection["monthly_calls"]:
                                row += f"| ${p['monthly_cost']:.2f} "
                                break
                row += "|"
                md_lines.append(row)
            
            md_lines.append("")
        
        
        # ========== 附录 ==========
        md_lines.append("\n---\n")
        md_lines.append("## 📌 附录\n")
        md_lines.append("### 评估维度说明\n")
        md_lines.append("- **成本（30%）**: 模型API调用费用，越低越好")
        md_lines.append("- **速度（20%）**: 模型响应时间，越快越好")
        md_lines.append("- **质量（50%）**: 用 LLM-as-Judge 评估，满分10分\n")
        md_lines.append("\n### 评分标准\n")
        md_lines.append("- **9-10分**: 优秀，可直接用于生产")
        md_lines.append("- **7-8分**: 良好，基本满足需求")
        md_lines.append("- **5-6分**: 及格，需要人工审核")
        md_lines.append("- **0-4分**: 不及格，不建议使用\n")
        
        # 合并所有行
        md_content = "\n".join(md_lines)
        
        # 保存 Markdown 文件
        md_path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"✅ Markdown 报告已生成: {md_path}")
        return md_content
    
    
    def generate_html_report(self, report: BenchmarkReport) -> str:
        """
        生成 HTML 报告（漂亮，可转PDF）
        
        HTML 就像"网页版的Word"
        - 可以加CSS样式（字体、颜色、布局）
        - 可以嵌入图表（用 matplotlib 生成）
        - 可以在浏览器里直接查看
        """
        
        # 先生成一些图表（用 matplotlib）
        chart_paths = self._generate_charts(report)
        
        # 用 Jinja2 模板渲染 HTML
        template = self.template_env.get_template("report_template.html")
        
        # 准备模板数据
        template_data = {
            "report": report,
            "summary_stats": report.summary_stats,
            "task_results": report.task_results,
            "recommendation": report.recommendation,
            "cost_projection": report.cost_projection,
            "chart_paths": chart_paths,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 渲染模板
        html_content = template.render(**template_data)
        
        # 保存 HTML 文件
        html_path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"✅ HTML 报告已生成: {html_path}")
        return html_content
    
    
    def _generate_charts(self, report: BenchmarkReport) -> Dict[str, str]:
        """生成图表（用 matplotlib）"""
        
        chart_paths = {}
        charts_dir = os.path.join(REPORT_OUTPUT_DIR, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        # ========== 图表1：各模型综合得分对比（柱状图）====================
        if report.summary_stats:
            models = list(report.summary_stats.keys())
            scores = [report.summary_stats[m]["avg_comprehensive_score"] for m in models]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(models, scores, color=["#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de"])
            plt.title("各模型综合得分对比", fontsize=16, fontproperties="SimHei")
            plt.ylabel("综合得分（越高越好）", fontproperties="SimHei")
            plt.xticks(rotation=45, ha="right")
            
            # 在柱子上标数字
            for bar, score in zip(bars, scores):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f"{score:.1f}", ha="center", va="bottom")
            
            plt.tight_layout()
            chart_path = os.path.join(charts_dir, "comprehensive_scores.png")
            plt.savefig(chart_path, dpi=100)
            plt.close()
            chart_paths["comprehensive_scores"] = chart_path
        
        
        # ========== 图表2：成本对比（柱状图）====================
        if report.summary_stats:
            models = list(report.summary_stats.keys())
            costs = [report.summary_stats[m]["total_cost"] for m in models]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(models, costs, color=["#5470c6", "#91cc75", "#fac858"])
            plt.title("各模型总成本对比", fontsize=16, fontproperties="SimHei")
            plt.ylabel("总成本（USD）", fontproperties="SimHei")
            plt.xticks(rotation=45, ha="right")
            
            for bar, cost in zip(bars, costs):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, 
                         f"${cost:.4f}", ha="center", va="bottom")
            
            plt.tight_layout()
            chart_path = os.path.join(charts_dir, "cost_comparison.png")
            plt.savefig(chart_path, dpi=100)
            plt.close()
            chart_paths["cost_comparison"] = chart_path
        
        
        return chart_paths
    
    
    def generate_pdf_report(self, report: BenchmarkReport) -> str:
        """
        生成 PDF 报告（用 ReportLab）
        
        ReportLab 是 Python 的 PDF 生成库
        就像"代码版的 InDesign"
        可以精确控制每一行、每一页的布局
        """
        
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 注册中文字体（否则中文会显示成方块）
        # 需要系统里有中文字体（Windows自带 simhei.ttf）
        try:
            pdfmetrics.registerFont(TTFont("SimHei", "C:/Windows/Fonts/simhei.ttf"))
            chinese_font = "SimHei"
        except:
            print("⚠️ 中文字体加载失败，PDF可能无法显示中文")
            chinese_font = "Helvetica"
        
        # 创建 PDF
        pdf_path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.pdf")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # ========== 封面 ==========
        c.setFont(chinese_font, 24)
        c.drawCentredString(width/2, height-5*cm, "AI模型选型与投资回报分析报告")
        
        c.setFont(chinese_font, 14)
        c.drawCentredString(width/2, height-7*cm, f"报告ID: {report.report_id}")
        c.drawCentredString(width/2, height-8*cm, f"生成时间: {report.created_at}")
        c.drawCentredString(width/2, height-9*cm, f"评估批次: {report.batch_name}")
        
        c.showPage()  # 换页
        
        
        # ========== 汇总统计页 ==========
        c.setFont(chinese_font, 18)
        c.drawString(2*cm, height-2*cm, "执行摘要")
        
        if report.summary_stats:
            y = height - 4*cm
            c.setFont(chinese_font, 12)
            
            # 表头
            c.drawString(2*cm, y, "模型")
            c.drawString(6*cm, y, "综合得分")
            c.drawString(10*cm, y, "总成本")
            y -= 1*cm
            
            # 数据行
            for model_name, stats in report.summary_stats.items():
                c.drawString(2*cm, y, model_name)
                c.drawString(6*cm, y, f"{stats.get('avg_comprehensive_score', 0)}")
                c.drawString(10*cm, y, f"${stats.get('total_cost', 0):.4f}")
                y -= 1*cm
                
                if y < 3*cm:  # 换页
                    c.showPage()
                    y = height - 2*cm
        
        c.showPage()
        c.save()
        
        print(f"✅ PDF 报告已生成: {pdf_path}")
        return pdf_path
    
    
    def generate_report(self, report: BenchmarkReport, formats: List[str] = ["markdown", "html"]) -> Dict[str, str]:
        """
        生成报告（支持多种格式）
        
        参数：
        - report: 评估报告数据
        - formats: 要生成的格式列表，可选 "markdown", "html", "pdf"
        
        返回：
        - {"markdown": 文件路径, "html": 文件路径, ...}
        """
        
        result_paths = {}
        
        for fmt in formats:
            if fmt == "markdown":
                path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.md")
                self.generate_markdown_report(report)
                result_paths["markdown"] = path
            
            elif fmt == "html":
                path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.html")
                self.generate_html_report(report)
                result_paths["html"] = path
            
            elif fmt == "pdf":
                path = os.path.join(REPORT_OUTPUT_DIR, f"{report.report_id}.pdf")
                self.generate_pdf_report(report)
                result_paths["pdf"] = path
        
        
        return result_paths
