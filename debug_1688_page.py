#!/usr/bin/env python3
"""
调试脚本：分析1688商品页面的SKU结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def debug_page():
    """调试1688页面结构"""
    print("=" * 60)
    print("调试1688商品页面SKU结构")
    print("=" * 60)
    
    # 配置Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 打开商品页面
        test_url = "https://detail.1688.com/offer/725887578825.html"
        print(f"打开: {test_url}")
        driver.get(test_url)
        time.sleep(5)
        
        print(f"当前URL: {driver.current_url}")
        
        # 检查是否需要登录
        if "login" in driver.current_url.lower():
            print("需要登录，等待20秒...")
            time.sleep(20)
            driver.get(test_url)
            time.sleep(5)
        
        # 分析页面结构
        print("\n" + "=" * 60)
        print("分析页面SKU结构...")
        print("=" * 60)
        
        # 执行JavaScript分析
        analysis = driver.execute_script("""
            var result = {
                skuContainers: [],
                skuItems: [],
                clickableItems: [],
                pageInfo: {}
            };
            
            // 1. 查找可能的SKU容器
            var containerSelectors = [
                '[class*="obj-sku"]',
                '[class*="sku-wrapper"]',
                '[class*="skuList"]',
                '[class*="sku-list"]',
                '[data-spm*="sku"]',
                '[class*="detail-sku"]',
                '[class*="offer-sku"]'
            ];
            
            containerSelectors.forEach(function(sel) {
                var elems = document.querySelectorAll(sel);
                if (elems.length > 0) {
                    result.skuContainers.push({
                        selector: sel,
                        count: elems.length,
                        html: elems[0].outerHTML.substring(0, 500)
                    });
                }
            });
            
            // 2. 查找SKU选项元素
            var itemSelectors = [
                '[class*="obj-content"]',
                '[class*="obj-item"]',
                '[class*="sku-item"]',
                '[class*="prop-item"]'
            ];
            
            itemSelectors.forEach(function(sel) {
                var elems = document.querySelectorAll(sel);
                if (elems.length > 0) {
                    var texts = [];
                    for (var i = 0; i < Math.min(elems.length, 5); i++) {
                        texts.push(elems[i].innerText.substring(0, 100));
                    }
                    result.skuItems.push({
                        selector: sel,
                        count: elems.length,
                        sampleTexts: texts
                    });
                }
            });
            
            // 3. 查找可点击的规格选项
            var clickableSelectors = [
                '[class*="obj-item"]:not([class*="disabled"])',
                '[class*="sku-item"]:not([class*="disabled"])',
                'span[class*="item"]',
                'a[class*="item"]'
            ];
            
            clickableSelectors.forEach(function(sel) {
                var elems = document.querySelectorAll(sel);
                if (elems.length > 0) {
                    var items = [];
                    for (var i = 0; i < Math.min(elems.length, 10); i++) {
                        var el = elems[i];
                        var rect = el.getBoundingClientRect();
                        items.push({
                            text: el.innerText.split('\\n')[0].substring(0, 50),
                            className: el.className.substring(0, 100),
                            visible: rect.width > 0 && rect.height > 0,
                            position: {top: rect.top, left: rect.left}
                        });
                    }
                    result.clickableItems.push({
                        selector: sel,
                        count: elems.length,
                        items: items
                    });
                }
            });
            
            // 4. 获取页面基本信息
            var titleElem = document.querySelector('[class*="title"], h1, .mod-detail-title');
            result.pageInfo.title = titleElem ? titleElem.innerText.substring(0, 100) : '未找到标题';
            result.pageInfo.url = window.location.href;
            
            return result;
        """)
        
        # 打印分析结果
        print("\n【SKU容器】")
        for container in analysis.get('skuContainers', []):
            print(f"  选择器: {container['selector']}, 数量: {container['count']}")
            print(f"  HTML片段: {container['html'][:200]}...")
        
        print("\n【SKU选项元素】")
        for item in analysis.get('skuItems', []):
            print(f"  选择器: {item['selector']}, 数量: {item['count']}")
            print(f"  示例文本: {item['sampleTexts']}")
        
        print("\n【可点击元素】")
        for clickable in analysis.get('clickableItems', []):
            print(f"  选择器: {clickable['selector']}, 数量: {clickable['count']}")
            for item in clickable['items'][:5]:
                print(f"    - 文本: {item['text']}, 可见: {item['visible']}, 类名: {item['className'][:50]}")
        
        print("\n【页面信息】")
        print(f"  标题: {analysis.get('pageInfo', {}).get('title', '未知')}")
        print(f"  URL: {analysis.get('pageInfo', {}).get('url', '未知')}")
        
        # 等待用户查看
        print("\n" + "=" * 60)
        print("分析完成，5秒后关闭浏览器...")
        print("=" * 60)
        time.sleep(5)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("浏览器已关闭")


if __name__ == "__main__":
    debug_page()
