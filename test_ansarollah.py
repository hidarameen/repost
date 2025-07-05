#!/usr/bin/env python3
"""
اختبار موقع الأنصار الله
====================

سكريبت لاختبار استخراج المحتوى من موقع الأنصار الله اليمني
"""

import requests
import asyncio
from bs4 import BeautifulSoup
from newspaper import Article as NewsArticle
from readability import Document
import html2text
from datetime import datetime
from ansarollah_config import AnsarallahConfig

class AnsarallahTester:
    """فئة اختبار موقع الأنصار الله"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def test_article_extraction(self, url: str) -> dict:
        """اختبار استخراج محتوى مقال"""
        print(f"🔍 اختبار استخراج المحتوى من: {url}")
        
        try:
            # جلب الصفحة
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ تم جلب الصفحة بنجاح - حالة الاستجابة: {response.status_code}")
            
            # استخراج بيانات المقال
            article_data = self.extract_article_data(url, response.text)
            
            return article_data
            
        except Exception as e:
            print(f"❌ خطأ في استخراج المقال: {e}")
            return {}
    
    def extract_article_data(self, url: str, html_content: str) -> dict:
        """استخراج بيانات المقال من HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        article_data = {
            'url': url,
            'title': '',
            'content': '',
            'summary': '',
            'author': '',
            'date': '',
            'image_url': '',
            'category': ''
        }
        
        # استخراج العنوان
        print("\n📰 استخراج العنوان...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['title']:
            title_element = soup.select_one(selector)
            if title_element:
                article_data['title'] = title_element.get_text(strip=True)
                print(f"✅ العنوان: {article_data['title']}")
                break
        
        if not article_data['title']:
            # محاولة استخراج من title tag
            title_tag = soup.find('title')
            if title_tag:
                article_data['title'] = title_tag.get_text(strip=True)
                print(f"⚠️ العنوان من title tag: {article_data['title']}")
        
        # استخراج المحتوى
        print("\n📄 استخراج المحتوى...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['content']:
            content_element = soup.select_one(selector)
            if content_element:
                # تنظيف المحتوى
                for unwanted in content_element.find_all(['script', 'style', 'aside', 'nav']):
                    unwanted.decompose()
                
                # استخراج النص
                content_text = content_element.get_text(separator='\n', strip=True)
                article_data['content'] = content_text
                print(f"✅ المحتوى: {len(content_text)} حرف")
                
                # تحويل إلى HTML للـ markdown
                content_html = str(content_element)
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                article_data['content_markdown'] = h.handle(content_html)
                break
        
        # استخراج التاريخ
        print("\n📅 استخراج التاريخ...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['date']:
            date_element = soup.select_one(selector)
            if date_element:
                article_data['date'] = date_element.get_text(strip=True)
                print(f"✅ التاريخ: {article_data['date']}")
                break
        
        # استخراج الكاتب
        print("\n✍️ استخراج الكاتب...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['author']:
            author_element = soup.select_one(selector)
            if author_element:
                article_data['author'] = author_element.get_text(strip=True)
                print(f"✅ الكاتب: {article_data['author']}")
                break
        
        # استخراج الصورة
        print("\n🖼️ استخراج الصورة...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['image']:
            image_element = soup.select_one(selector)
            if image_element:
                image_url = image_element.get('src')
                if image_url:
                    if image_url.startswith('http'):
                        article_data['image_url'] = image_url
                    else:
                        article_data['image_url'] = f"https://www.ansarollah.com.ye{image_url}"
                    print(f"✅ الصورة: {article_data['image_url']}")
                    break
        
        # استخراج القسم
        print("\n📂 استخراج القسم...")
        for selector in AnsarallahConfig.CONTENT_SELECTORS['category']:
            category_element = soup.select_one(selector)
            if category_element:
                article_data['category'] = category_element.get_text(strip=True)
                print(f"✅ القسم: {article_data['category']}")
                break
        
        # إنشاء ملخص
        if article_data['content']:
            summary = self.create_summary(article_data['content'])
            article_data['summary'] = summary
            print(f"✅ الملخص: {len(summary)} حرف")
        
        return article_data
    
    def create_summary(self, content: str, max_length: int = 300) -> str:
        """إنشاء ملخص من المحتوى"""
        content = content.replace('\n', ' ').strip()
        
        if len(content) <= max_length:
            return content
        
        # البحث عن آخر جملة كاملة
        truncated = content[:max_length]
        last_sentence_end = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_sentence_end > max_length * 0.7:
            return content[:last_sentence_end + 1]
        else:
            return content[:max_length] + "..."
    
    def test_newspaper3k(self, url: str) -> dict:
        """اختبار استخراج باستخدام newspaper3k"""
        print(f"\n📰 اختبار newspaper3k على: {url}")
        
        try:
            article = NewsArticle(url)
            article.download()
            article.parse()
            
            result = {
                'title': article.title,
                'content': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'keywords': list(article.keywords)
            }
            
            print(f"✅ newspaper3k - العنوان: {result['title']}")
            print(f"✅ newspaper3k - المحتوى: {len(result['content'])} حرف")
            print(f"✅ newspaper3k - الصورة: {result['top_image']}")
            
            return result
            
        except Exception as e:
            print(f"❌ خطأ في newspaper3k: {e}")
            return {}
    
    def test_readability(self, url: str) -> dict:
        """اختبار استخراج باستخدام readability"""
        print(f"\n📖 اختبار readability على: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            doc = Document(response.text)
            
            result = {
                'title': doc.title(),
                'content': doc.summary(),
                'clean_content': BeautifulSoup(doc.summary(), 'html.parser').get_text()
            }
            
            print(f"✅ readability - العنوان: {result['title']}")
            print(f"✅ readability - المحتوى: {len(result['clean_content'])} حرف")
            
            return result
            
        except Exception as e:
            print(f"❌ خطأ في readability: {e}")
            return {}
    
    def compare_methods(self, url: str):
        """مقارنة طرق الاستخراج المختلفة"""
        print("=" * 80)
        print("🔬 مقارنة طرق الاستخراج")
        print("=" * 80)
        
        # الطريقة المخصصة
        custom_result = self.test_article_extraction(url)
        
        # newspaper3k
        newspaper_result = self.test_newspaper3k(url)
        
        # readability
        readability_result = self.test_readability(url)
        
        # طباعة النتائج
        print("\n" + "=" * 80)
        print("📊 ملخص النتائج")
        print("=" * 80)
        
        print(f"\n🔧 الطريقة المخصصة:")
        print(f"  العنوان: {custom_result.get('title', 'غير متوفر')}")
        print(f"  المحتوى: {len(custom_result.get('content', ''))} حرف")
        print(f"  الصورة: {'✅ متوفرة' if custom_result.get('image_url') else '❌ غير متوفرة'}")
        
        print(f"\n📰 Newspaper3k:")
        print(f"  العنوان: {newspaper_result.get('title', 'غير متوفر')}")
        print(f"  المحتوى: {len(newspaper_result.get('content', ''))} حرف")
        print(f"  الصورة: {'✅ متوفرة' if newspaper_result.get('top_image') else '❌ غير متوفرة'}")
        
        print(f"\n📖 Readability:")
        print(f"  العنوان: {readability_result.get('title', 'غير متوفر')}")
        print(f"  المحتوى: {len(readability_result.get('clean_content', ''))} حرف")
        
        # تحديد الطريقة الأفضل
        print(f"\n🏆 التوصية:")
        if len(custom_result.get('content', '')) > len(newspaper_result.get('content', '')):
            print("  الطريقة المخصصة تعطي نتائج أفضل")
        else:
            print("  newspaper3k يعطي نتائج أفضل")
        
        return {
            'custom': custom_result,
            'newspaper': newspaper_result,
            'readability': readability_result
        }

def main():
    """الدالة الرئيسية"""
    print("🤖 اختبار موقع الأنصار الله اليمني")
    print("=" * 80)
    
    # الرابط المطلوب اختباره
    test_url = "https://www.ansarollah.com.ye/archives/801488"
    
    tester = AnsarallahTester()
    
    # اختبار استخراج المحتوى
    results = tester.compare_methods(test_url)
    
    # إنشاء رسالة تجريبية
    if results['custom']:
        print("\n" + "=" * 80)
        print("📱 معاينة الرسالة")
        print("=" * 80)
        
        message = AnsarallahConfig.format_message(results['custom'])
        print(message)
    
    print("\n✅ انتهى الاختبار بنجاح!")

if __name__ == "__main__":
    main()