#!/usr/bin/env python3
"""
调试脚本v2：更详细地分析1688商品页面
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_page():
    """调试1688页面结构"""
    print("=" * 60)
    print("调试1688商品页面SKU结构 v2")
    print("=" * 60)
    
    # 配置Chrome
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    try:
        # 打开商品页面
        test_url = "https://detail.1688.com/offer/725887578825.html"
        print(f"打开: {test_url}")
        driver.get(test_url)
        
        # 等待页面加载
        print("等待页面加载...")
        time.sleep(8)
        
        print(f"当前URL: {driver.current_url}")
        
        # 检查页面状态
        page_state = driver.execute_script("""
            return {
                readyState: document.readyState,
                bodyLength: document.body.innerHTML.length,
                title: document.title,
                hasLoginPopup: !!document.querySelector('[class*="login"]'),
                hasSkuArea: !!document.querySelector('[class*="sku"], [class*="obj-sku"]')
            };
        """)
        print(f"页面状态: {page_state}")
        
        # 检查是否有登录弹窗或需要登录
        login_check = driver.execute_script("""
            // 检查是否有登录相关元素
            var loginElements = document.querySelectorAll('[class*="login"], [class*="Login"]');
            var loginTexts = [];
            loginElements.forEach(function(el) {
                if (el.innerText && el.innerText.length < 100) {
                    loginTexts.push(el.innerText);
                }
            });
            
            // 检查页面是否显示需要登录
            var bodyText = document.body.innerText;
            var needLogin = bodyText.includes('请登录') || bodyText.includes('登录后查看');
            
            return {
                loginElementCount: loginElements.length,
                loginTexts: loginTexts.slice(0, 5),
                needLogin: needLogin
            };
        """)
        print(f"登录检查: {login_check}")
        
        # 获取页面所有class包含特定关键词的元素
        print("\n" + "=" * 60)
        print("搜索页面中的SKU相关元素...")
        print("=" * 60)
        
        sku_search = driver.execute_script("""
            var result = {
                byClass: {},
                byDataAttr: [],
                allClasses: []
            };
            
            // 搜索所有包含特定关键词的class
            var keywords = ['sku', 'spec', 'prop', 'attr', 'option', 'select', 'color', 'size'];
            var allElements = document.querySelectorAll('*');
            
            keywords.forEach(function(keyword) {
                result.byClass[keyword] = [];
            });
            
            for (var i = 0; i < allElements.length; i++) {
                var el = allElements[i];
                var className = el.className;
                if (typeof className === 'string' && className.length > 0) {
                    keywords.forEach(function(keyword) {
                        if (className.toLowerCase().includes(keyword)) {
                            if (result.byClass[keyword].length < 3) {
                                result.byClass[keyword].push({
                                    tag: el.tagName,
                                    class: className.substring(0, 100),
                                    text: el.innerText ? el.innerText.substring(0, 100) : ''
                                });
                            }
                        }
                    });
                }
                
                // 检查data属性
                if (el.dataset) {
                    var dataKeys = Object.keys(el.dataset);
                    dataKeys.forEach(function(key) {
                        if (key.toLowerCase().includes('sku') || key.toLowerCase().includes('spec')) {
                            if (result.byDataAttr.length < 5) {
                                result.byDataAttr.push({
                                    tag: el.tagName,
                                    dataKey: key,
                                    dataValue: el.dataset[key].substring(0, 50)
                                });
                            }
                        }
                    });
                }
            }
            
            return result;
        """)
        
        print("\n【按关键词搜索结果】")
        for keyword, elements in sku_search.get('byClass', {}).items():
            if elements:
                print(f"\n  关键词 '{keyword}':")
                for el in elements:
                    print(f"    - <{el['tag']}> class='{el['class'][:60]}'")
                    if el['text']:
                        print(f"      文本: {el['text'][:80]}")
        
        print("\n【data属性搜索结果】")
        for item in sku_search.get('byDataAttr', []):
            print(f"  - <{item['tag']}> data-{item['dataKey']}='{item['dataValue']}'")
        
        # 获取购买区域的HTML
        print("\n" + "=" * 60)
        print("获取购买区域HTML...")
        print("=" * 60)
        
        buy_area = driver.execute_script("""
            // 尝试找到购买区域
            var selectors = [
                '[class*="detail-buy"]',
                '[class*="buy-area"]',
                '[class*="purchase"]',
                '[class*="order-area"]',
                '[class*="mod-detail"]',
                '[class*="offer-detail"]'
            ];
            
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (el) {
                    return {
                        selector: selectors[i],
                        html: el.outerHTML.substring(0, 2000),
                        text: el.innerText.substring(0, 500)
                    };
                }
            }
            
            // 如果没找到，返回body的部分内容
            return {
                selector: 'body',
                html: document.body.innerHTML.substring(0, 2000),
                text: document.body.innerText.substring(0, 500)
            };
        """)
        
        print(f"找到区域: {buy_area.get('selector', '未知')}")
        print(f"文本内容: {buy_area.get('text', '')[:300]}...")
        
        # 等待用户查看
        print("\n" + "=" * 60)
        print("分析完成，10秒后关闭浏览器...")
        print("=" * 60)
        time.sleep(10)
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("浏览器已关闭")


if __name__ == "__main__":
    debug_page()
