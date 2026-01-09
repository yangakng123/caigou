#!/usr/bin/env python3
"""
AI智能采购自动化助手 - 一键执行脚本
============================================

使用方法:
1. 配置 .env 文件（参考 .env.example）
2. 初始化数据库: python run_purchase.py --init-db
3. 启动Web界面: python run_purchase.py --web
4. 命令行执行: python run_purchase.py --product "商品名称" --quantity 10 --budget 1000

作者: AI采购助手
"""
import os
import sys
import argparse
import asyncio
from decimal import Decimal
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def init_database():
    """初始化数据库"""
    print("=" * 50)
    print("正在初始化数据库...")
    print("=" * 50)
    
    from src.config import DatabaseConfig
    import mysql.connector
    
    try:
        # 先连接MySQL（不指定数据库）
        conn = mysql.connector.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD
        )
        cursor = conn.cursor()
        
        # 读取并执行SQL脚本
        sql_file = os.path.join(os.path.dirname(__file__), 'database', 'init.sql')
        
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 分割SQL语句并执行
            statements = sql_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except mysql.connector.Error as e:
                        if e.errno != 1065:  # 忽略空查询错误
                            print(f"  警告: {e.msg}")
            
            print("✅ 数据库初始化完成！")
        else:
            print(f"❌ SQL文件不存在: {sql_file}")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {e}")
        print("\n请检查以下配置:")
        print(f"  - 主机: {DatabaseConfig.HOST}")
        print(f"  - 端口: {DatabaseConfig.PORT}")
        print(f"  - 用户: {DatabaseConfig.USER}")
        print(f"  - 数据库: {DatabaseConfig.DATABASE}")
        return False


def run_web_interface():
    """启动Web界面"""
    print("=" * 50)
    print("正在启动AI采购助手Web界面...")
    print("=" * 50)
    
    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "src/app.py", 
        "--server.headless", "true"
    ], env={**os.environ, "PYTHONPATH": os.path.dirname(__file__)})


async def run_auto_purchase(product_name: str, quantity: int, budget: float = None, 
                           specification: str = None, platforms: list = None):
    """
    执行全自动采购流程
    
    Args:
        product_name: 商品名称
        quantity: 采购数量
        budget: 预算上限（可选）
        specification: 规格要求（可选）
        platforms: 优先平台列表（可选）
    """
    print("=" * 60)
    print("🛒 AI智能采购自动化助手")
    print("=" * 60)
    print(f"📦 商品名称: {product_name}")
    print(f"📊 采购数量: {quantity}")
    if budget:
        print(f"💰 预算上限: ¥{budget}")
    if specification:
        print(f"📐 规格要求: {specification}")
    print("=" * 60)
    
    from src.models.enums import Platform
    from src.models.demand import PurchaseDemand
    from src.services.workflow_orchestrator import WorkflowOrchestrator
    
    # 构建采购需求
    if platforms is None:
        platforms = [Platform.ALIBABA_1688, Platform.JD_ENTERPRISE]
    else:
        platform_map = {
            "1688": Platform.ALIBABA_1688,
            "jd": Platform.JD_ENTERPRISE,
            "tmall": Platform.TMALL_SUPERMARKET
        }
        platforms = [platform_map.get(p.lower(), Platform.ALIBABA_1688) for p in platforms]
    
    demand = PurchaseDemand(
        product_name=product_name,
        specification=specification,
        quantity=quantity,
        budget=Decimal(str(budget)) if budget else None,
        preferred_platforms=platforms,
        additional_requirements=None
    )
    
    # 创建工作流编排器
    orchestrator = WorkflowOrchestrator()
    
    # 设置进度回调
    def progress_callback(step: str, status: str, message: str):
        status_icons = {
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "warning": "⚠️"
        }
        icon = status_icons.get(status, "📌")
        print(f"{icon} [{step}] {message}")
    
    orchestrator.set_progress_callback(progress_callback)
    
    try:
        # 执行全流程
        print("\n🚀 开始执行采购流程...\n")
        
        result = await orchestrator.execute_full_workflow(demand)
        
        print("\n" + "=" * 60)
        if result.get("status") == "completed":
            print("✅ 采购流程执行完成！")
            print(f"📋 工作流ID: {result.get('workflow_id')}")
            
            if result.get("order"):
                order = result["order"]
                print(f"📦 订单号: {order.order_id}")
                print(f"💰 支付金额: ¥{order.payment_amount}")
        
        elif result.get("status") == "pending_confirmation":
            print("⏸️ 流程暂停，等待确认")
            print(f"📋 工作流ID: {result.get('workflow_id')}")
            
            if result.get("recommendations"):
                print("\n🎯 AI推荐结果:")
                for rec in result["recommendations"][:3]:
                    print(f"  {rec.rank}. {rec.product_name}")
                    print(f"     单价: ¥{rec.unit_price}, 运费: ¥{rec.freight}")
                    print(f"     评分: {rec.total_score:.1f}分")
                    print(f"     理由: {rec.reason}")
                    print()
        
        elif result.get("status") == "failed":
            print("❌ 采购流程执行失败")
            print(f"错误信息: {result.get('error')}")
        
        print("=" * 60)
        return result
        
    except Exception as e:
        print(f"\n❌ 执行异常: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="AI智能采购自动化助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 初始化数据库
  python run_purchase.py --init-db
  
  # 启动Web界面
  python run_purchase.py --web
  
  # 命令行执行采购
  python run_purchase.py --product "A4打印纸" --quantity 10 --budget 500
  
  # 指定平台
  python run_purchase.py --product "办公椅" --quantity 5 --platforms 1688 jd
        """
    )
    
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--web", action="store_true", help="启动Web界面")
    parser.add_argument("--product", type=str, help="商品名称")
    parser.add_argument("--quantity", type=int, default=1, help="采购数量")
    parser.add_argument("--budget", type=float, help="预算上限")
    parser.add_argument("--spec", type=str, help="规格要求")
    parser.add_argument("--platforms", nargs="+", help="优先平台: 1688 jd tmall")
    
    args = parser.parse_args()
    
    if args.init_db:
        init_database()
    elif args.web:
        run_web_interface()
    elif args.product:
        asyncio.run(run_auto_purchase(
            product_name=args.product,
            quantity=args.quantity,
            budget=args.budget,
            specification=args.spec,
            platforms=args.platforms
        ))
    else:
        parser.print_help()
        print("\n💡 提示: 使用 --web 启动图形界面，或使用 --product 执行命令行采购")


if __name__ == "__main__":
    main()
很好
