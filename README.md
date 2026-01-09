# 🛒 AI智能采购自动化助手

一键实现「输入选品信息 → 全流程自动执行」的采购闭环系统。

## ✨ 功能特性

- **多平台找品**: 自动从1688、京东企业购采集商品数据
- **AI智能选品**: 基于通义千问API进行智能比价推荐
- **自动化下单**: 支持Selenium浏览器自动化（免费）或影刀RPA
- **物流跟踪**: 调用快递100API实时追踪物流
- **自动入库**: 签收后自动生成入库单
- **库存管理**: 自动更新库存，低库存预警
- **数据双备份**: MySQL + Excel双重备份

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，填入你的配置信息：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_DATABASE=purchase_automation

# 通义千问API
DASHSCOPE_API_KEY=你的API密钥

# 快递100 API
KUAIDI100_API_KEY=你的API密钥
KUAIDI100_CUSTOMER=你的客户ID

# 影刀RPA（可选，如果使用Selenium则不需要）
YINGDAO_APP_ID=你的应用ID
YINGDAO_APP_SECRET=你的应用密钥
```

### 3. 初始化数据库

```bash
python run_purchase.py --init-db
```

### 4. 启动应用

**方式一：Web界面（推荐）**
```bash
python run_purchase.py --web
```
然后访问 http://localhost:8501

**方式二：命令行**
```bash
python run_purchase.py --product "A4打印纸" --quantity 10 --budget 500
```

## 🤖 Selenium自动下单（推荐）

系统支持使用Selenium实现浏览器自动化下单，完全免费且高度灵活。

### Selenium优势

- ✅ **完全免费**: 开源工具，无付费版限制
- ✅ **高度灵活**: 能自定义任何复杂逻辑
- ✅ **跨平台**: 支持Windows/Mac/Linux
- ✅ **可视化**: 可以看到整个下单过程

### 使用方法

```python
from src.services.selenium_order_executor import SeleniumOrderExecutor
from src.models.order import ShippingInfo
from src.models.demand import Recommendation

# 初始化执行器
executor = SeleniumOrderExecutor(headless=False)  # headless=False 可以看到浏览器操作

# 准备收货信息
shipping_info = ShippingInfo(
    receiver_name="张三",
    phone="13800138000",
    province="广东省",
    city="深圳市",
    district="南山区",
    address="科技园路1号"
)

# 执行下单（recommendation 来自AI选品结果）
order = executor.execute_order(
    recommendation=recommendation,
    shipping_info=shipping_info,
    quantity=10,
    purchase_demand="A4打印纸 10箱"
)

# 关闭浏览器
executor.close()
```

### 下单流程

1. **自动打开浏览器** → 访问电商平台
2. **等待用户登录** → 扫码或账号密码登录（首次需要）
3. **自动打开商品页** → 设置数量，加入购物车
4. **自动结算** → 选择收货地址，提交订单
5. **等待支付** → 用户在平台完成支付

### 注意事项

- 首次使用需要手动登录平台（扫码或账号密码）
- 登录后cookies会被保存，下次可自动恢复登录状态
- 建议设置 `headless=False` 以便查看下单过程
- 支付环节需要用户手动完成（安全考虑）

## 📁 项目结构

```
├── src/
│   ├── models/          # 数据模型
│   ├── services/        # 业务服务
│   │   ├── crawler_service.py          # 多平台数据采集
│   │   ├── ai_selector.py              # AI选品比价
│   │   ├── order_executor.py           # 自动化下单(Playwright)
│   │   ├── selenium_order_executor.py  # 自动化下单(Selenium)
│   │   ├── logistics_tracker.py        # 物流跟踪
│   │   ├── inventory_manager.py        # 库存管理
│   │   ├── alert_service.py            # 预警服务
│   │   ├── backup_service.py           # 数据备份
│   │   └── workflow_orchestrator.py    # 全流程编排
│   ├── repositories/    # 数据访问层
│   ├── config.py        # 配置文件
│   └── app.py           # Streamlit界面
├── database/
│   └── init.sql         # 数据库初始化脚本
├── data/
│   ├── backup/          # 数据库备份
│   └── excel/           # Excel备份文件
├── tests/               # 测试文件
├── .env                 # 环境配置
├── requirements.txt     # 依赖列表
└── run_purchase.py      # 启动脚本
```

## 🔧 配置说明

### 数据库配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DB_HOST | MySQL主机地址 | localhost |
| DB_PORT | MySQL端口 | 3306 |
| DB_USER | 数据库用户名 | root |
| DB_PASSWORD | 数据库密码 | - |
| DB_DATABASE | 数据库名 | purchase_automation |

### API配置

| 配置项 | 说明 | 获取地址 |
|--------|------|----------|
| DASHSCOPE_API_KEY | 通义千问API密钥 | https://dashscope.console.aliyun.com/ |
| KUAIDI100_API_KEY | 快递100 API密钥 | https://www.kuaidi100.com/openapi/ |
| YINGDAO_APP_ID | 影刀RPA应用ID | https://www.yingdao.com/ |

## 📊 数据库表结构

系统包含以下数据表：

- `product_table` - 商品信息表
- `order_table` - 订单信息表
- `inventory_table` - 库存信息表
- `inbound_table` - 入库单表
- `alert_table` - 预警记录表
- `demand_table` - 采购需求表

详细表结构见 `database/init.sql`

## 🔄 全流程说明

```
用户输入选品信息
       ↓
1. 多平台商品采集 (1688/京东)
       ↓
2. AI智能选品比价 (通义千问)
       ↓
3. 生成Top3推荐
       ↓
4. 用户确认/自动选择
       ↓
5. 自动化下单 (影刀RPA)
       ↓
6. 物流跟踪 (快递100)
       ↓
7. 签收自动入库
       ↓
8. 更新库存 + 数据备份
```

## ⚠️ 异常处理

系统会自动检测并预警以下异常：

- 物流停滞超48小时
- 未发货超72小时
- 下单失败
- 库存低于阈值

预警通过微信推送（需配置wxpy）或界面显示。

## 🧪 运行测试

```bash
python -m pytest tests/ -v
```

## 📝 License

MIT License
