# استخدام Python 3.11 كصورة أساسية
FROM python:3.11-slim

# تحديد معلومات المطور
LABEL maintainer="Ansarollah Bot Developer"
LABEL description="بوت موقع الأنصار الله اليمني للتلقرام"
LABEL version="1.0"

# تحديث النظام وتثبيت المتطلبات الأساسية
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير جذر للأمان
RUN useradd -m -u 1000 botuser

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p /app/data /app/logs /app/temp

# تغيير ملكية الملفات للمستخدم الجديد
RUN chown -R botuser:botuser /app

# التبديل للمستخدم الجديد
USER botuser

# إنشاء ملف إعدادات افتراضي إذا لم يكن موجوداً
RUN if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || true; fi

# تعيين متغيرات البيئة
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# كشف المنفذ (للمراقبة إذا لزم الأمر)
EXPOSE 8080

# تحديد نقطة الدخول
ENTRYPOINT ["python3", "main.py"]

# أوامر الصحة للتحقق من حالة البوت
HEALTHCHECK --interval=60s --timeout=10s --start-period=20s --retries=3 \
  CMD python3 -c "import requests; requests.get('https://api.telegram.org/', timeout=5)" || exit 1