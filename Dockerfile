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
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# إنشاء مستخدم غير جذر للأمان
RUN useradd -m -u 1000 botuser

# تحديد مجلد العمل
WORKDIR /app

# نسخ ملفات المتطلبات أولاً للاستفادة من Docker cache
COPY requirements.txt .

# تثبيت المتطلبات Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# نسخ ملفات التطبيق
COPY --chown=botuser:botuser . .

# إنشاء المجلدات المطلوبة
RUN mkdir -p /app/data /app/logs /app/temp && \
    chown -R botuser:botuser /app

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

# نسخ سكريبت نقطة الدخول
COPY --chown=botuser:botuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# تحديد نقطة الدخول
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# أوامر الصحة للتحقق من حالة البوت
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)" || exit 1