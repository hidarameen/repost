# بوت مراقبة المواقع والنشر التلقائي

🤖 بوت متقدم لمراقبة المواقع الإخبارية ونشر المقالات الجديدة تلقائياً في قنوات التلقرام مع دعم صفحات Telegraph وإدارة الموافقات.

## ✨ المميزات الرئيسية

### 📍 مراقبة المواقع
- **مراقبة تلقائية**: فحص جميع أقسام الموقع كل دقيقة
- **أقسام متعددة**: إمكانية مراقبة أقسام مختلفة من الموقع
- **استخراج ذكي**: استخراج المحتوى والصور تلقائياً
- **فلترة المحتوى**: إمكانية استبعاد أو تضمين كلمات محددة

### 📢 النشر في التلقرام
- **وضعان للنشر**: النشر الكامل أو المختصر
- **دعم الصور**: نشر الصور مع المقالات
- **تقسيم النصوص**: تقسيم المقالات الطويلة على عدة رسائل
- **روابط مشاركة**: إنشاء روابط مشاركة للمقالات

### 📰 صفحات Telegraph
- **إنشاء تلقائي**: إنشاء صفحات Telegraph للمقالات الطويلة
- **تنسيق احترافي**: تنسيق المقالات بشكل جميل
- **صور محسنة**: رفع وتحسين الصور
- **معلومات كاملة**: إضافة معلومات المصدر والتاريخ

### 🔧 إدارة متقدمة
- **نظام الموافقات**: إرسال المقالات للمشرفين قبل النشر
- **إعدادات مخصصة**: header وfooter قابلة للتخصيص
- **تقارير يومية**: إحصائيات وتقارير دورية
- **إدارة الأقسام**: إضافة وإدارة أقسام الموقع

## 🚀 التثبيت والإعداد

### 1. متطلبات النظام
```bash
Python 3.8+
pip
```

### 2. تحميل المشروع
```bash
git clone https://github.com/yourusername/news-bot.git
cd news-bot
```

### 3. تثبيت المكتبات
```bash
pip install -r requirements.txt
```

### 4. إعداد البيئة
```bash
cp .env.example .env
```

### 5. تعديل ملف .env
```env
# إعدادات البوت
BOT_TOKEN=your_telegram_bot_token_here
CHANNEL_ID=@your_channel_username
ADMIN_IDS=["123456789", "987654321"]

# إعدادات الموقع
WEBSITE_URL=https://example.com
WEBSITE_SECTIONS=["news", "sports", "technology"]
CHECK_INTERVAL=60

# إعدادات النشر
AUTO_PUBLISH=false
ENABLE_TEXT_SHORTENING=true
MAX_MESSAGE_LENGTH=4000
SHORT_DESCRIPTION_LENGTH=200

# إعدادات التخصيص
CUSTOM_HEADER=📰 أحدث الأخبار
CUSTOM_FOOTER=🔗 تابعونا للمزيد
```

### 6. تشغيل البوت
```bash
python main.py
```

## 🎮 الاستخدام

### أوامر البوت

#### الأوامر الأساسية
- `/start` - بدء التشغيل
- `/help` - عرض المساعدة
- `/status` - حالة البوت والإحصائيات
- `/pending` - المقالات المعلقة للموافقة

#### إدارة الأقسام
- `/sections` - عرض الأقسام النشطة
- `/test` - اختبار النظام

#### الإعدادات
- `/settings` - إعدادات البوت

### أوضاع النشر

#### 1. النشر الكامل
```
AUTO_PUBLISH=true
ENABLE_TEXT_SHORTENING=false
```
- ينشر المقال كاملاً في القناة
- يقسم النصوص الطويلة على عدة رسائل
- يضيف الصور والروابط

#### 2. النشر المختصر
```
AUTO_PUBLISH=true
ENABLE_TEXT_SHORTENING=true
```
- ينشر ملخص المقال مع الصورة
- يضيف رابط "تكملة المقال" لصفحة Telegraph
- يحتوي على أزرار المشاركة

#### 3. النشر اليدوي
```
AUTO_PUBLISH=false
```
- يرسل المقالات للمشرفين أولاً
- يتطلب موافقة قبل النشر
- إمكانية التعديل والرفض

## ⚙️ الإعدادات المتقدمة

### إعدادات الأقسام
```env
SECTION_NEWS_SETTINGS={"custom_header": "📰 أخبار عاجلة", "default_tags": ["news"]}
SECTION_SPORTS_SETTINGS={"custom_header": "⚽ الرياضة", "default_tags": ["sports"]}
```

### الفلاتر
```env
EXCLUDE_KEYWORDS=["spam", "ads", "advertisement"]
INCLUDE_KEYWORDS=["breaking", "urgent", "exclusive"]
```

### إعدادات Telegraph
```env
TELEGRAPH_TOKEN=your_telegraph_token
TELEGRAPH_AUTHOR=News Bot
TELEGRAPH_AUTHOR_URL=https://t.me/your_bot
```

## 📊 الإحصائيات والتقارير

### التقرير اليومي
يرسل البوت تقريراً يومياً يحتوي على:
- عدد الأقسام النشطة
- عدد المقالات المنشورة
- عدد المقالات المعلقة
- حالة النظام

### إحصائيات الأقسام
- عدد المقالات لكل قسم
- آخر وقت فحص
- معدل النشر

## 🔧 الصيانة والإدارة

### تنظيف البيانات
```bash
# تنظيف تلقائي كل 5 دقائق
schedule.every(5).minutes.do(cleanup_old_data)
```

### النسخ الاحتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
cp bot_data.db backup_$(date +%Y%m%d).db
```

### مراقبة الأخطاء
```bash
# عرض سجل الأخطاء
tail -f bot.log
```

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة

#### 1. عدم عمل البوت
```bash
# تحقق من صحة التوكن
python -c "from config import Config; print(Config.BOT_TOKEN)"
```

#### 2. عدم وجود مقالات جديدة
```bash
# اختبر الأقسام يدوياً
python -c "from main import NewsBot; bot = NewsBot(); print(bot.test_section('https://example.com/news'))"
```

#### 3. مشاكل Telegraph
```bash
# تحقق من الاتصال
python -c "from telegraph_manager import TelegraphManager; tm = TelegraphManager(); print(tm.account_info)"
```

## 🤝 المساهمة

نرحب بمساهماتكم! يرجى:

1. Fork المشروع
2. إنشاء branch للميزة الجديدة
3. Commit التغييرات
4. إرسال Pull Request

## 📞 الدعم

للدعم والمساعدة:
- إنشاء Issue في GitHub
- التواصل عبر التلقرام: @your_support_bot

## 📄 الرخصة

هذا المشروع مرخص تحت رخصة MIT - انظر ملف [LICENSE](LICENSE) للتفاصيل.

## 🔄 التحديثات

### الإصدار 1.0.0
- ✅ مراقبة المواقع
- ✅ النشر التلقائي
- ✅ دعم Telegraph
- ✅ نظام الموافقات
- ✅ إدارة الأقسام

### الإصدار 1.1.0 (قريباً)
- 🔄 دعم RSS feeds
- 🔄 إشعارات push
- 🔄 واجهة ويب للإدارة
- 🔄 دعم أكثر من موقع

## 🎯 أمثلة للاستخدام

### مثال 1: موقع أخبار عربي
```env
WEBSITE_URL=https://arabic-news.com
WEBSITE_SECTIONS=["أخبار محلية", "أخبار عالمية", "رياضة", "تكنولوجيا"]
CUSTOM_HEADER=📰 أخبار عاجلة
CUSTOM_FOOTER=🔗 تابعونا على قناتنا
```

### مثال 2: مدونة تقنية
```env
WEBSITE_URL=https://tech-blog.com
WEBSITE_SECTIONS=["programming", "ai", "blockchain"]
ENABLE_TEXT_SHORTENING=true
TELEGRAPH_AUTHOR=Tech News Bot
```

### مثال 3: موقع رياضي
```env
WEBSITE_URL=https://sports-site.com
WEBSITE_SECTIONS=["football", "basketball", "tennis"]
SECTION_FOOTBALL_SETTINGS={"custom_header": "⚽ كرة القدم", "default_tags": ["football"]}
```

---

Made with ❤️ for the Arabic community