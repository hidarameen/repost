#!/bin/bash
# سكريپت تشغيل محسن لبوت الأنصار الله مع إصلاح المشاكل

echo "🚀 تشغيل بوت الأنصار الله اليمني (محسن)"
echo "============================================="

# فحص وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python 3 غير مثبت"
    exit 1
fi

echo "✅ Python متوفر: $(python3 --version)"

# فحص وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ خطأ: pip3 غير مثبت"
    exit 1
fi

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
mkdir -p data logs temp
echo "✅ المجلدات جاهزة"

# فحص وجود ملف .env
if [ ! -f .env ]; then
    echo "❌ خطأ: ملف .env غير موجود"
    echo "يرجى إنشاء ملف .env بالبيانات الصحيحة"
    exit 1
fi

echo "✅ ملف .env موجود"

# تثبيت المتطلبات إذا لزم الأمر
if [ ! -d "venv" ]; then
    echo "🔧 إنشاء البيئة الافتراضية..."
    python3 -m venv venv
fi

echo "🔧 تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo "📦 تثبيت المتطلبات..."
pip install -r requirements.txt

# تشغيل اختبار الإصلاح
echo ""
echo "🧪 تشغيل اختبار الإصلاح..."
python3 test-fix.py

echo ""
read -p "هل تريد المتابعة لتشغيل البوت؟ (y/n): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "تم إلغاء التشغيل"
    exit 0
fi

# إيقاف أي عملية سابقة
echo "🛑 إيقاف أي عملية سابقة..."
pkill -f "python3 main.py" 2>/dev/null || true

# تشغيل البوت
echo ""
echo "🚀 تشغيل البوت..."
echo "================================================="
echo "📅 التاريخ: $(date)"
echo "🕒 الوقت: $(date +%H:%M:%S)"
echo "📍 مجلد العمل: $(pwd)"
echo "================================================="

# تشغيل البوت مع إعادة التوجيه للسجلات
python3 main.py 2>&1 | tee logs/bot_$(date +%Y%m%d_%H%M%S).log