# دليل Docker لبوت الأنصار الله اليمني

## 🐳 التنصيب والتشغيل عبر Docker

### المتطلبات الأساسية:
- Docker 20.10+
- Docker Compose 2.0+
- 2GB مساحة تخزين فارغة
- اتصال بالإنترنت

---

## 🚀 التشغيل السريع

### 1. نسخ المشروع:
```bash
git clone <repository-url>
cd ansarollah-news-bot
```

### 2. إعداد البيانات:
```bash
# نسخ ملف الإعدادات
cp .env.example .env

# تعديل البيانات
nano .env
```

### 3. تشغيل البوت:
```bash
# بناء وتشغيل البوت
docker-compose up -d

# مراقبة السجلات
docker-compose logs -f ansarollah-bot
```

---

## ⚙️ إعدادات Docker Compose

### الخدمات المتاحة:

#### 📰 البوت الرئيسي (`ansarollah-bot`):
- يراقب موقع الأنصار الله
- ينشر المقالات الجديدة
- يحفظ البيانات في قاعدة بيانات SQLite

#### 🗄️ Redis (`redis`):
- تخزين مؤقت للبيانات
- طوابير المهام
- تحسين الأداء

#### 🔍 Watchtower (`watchtower`) - اختياري:
- مراقبة التحديثات
- إعادة تشغيل تلقائية عند التحديث

#### 💾 النسخ الاحتياطي (`backup`) - اختياري:
- نسخ احتياطية دورية
- حذف النسخ القديمة تلقائياً

---

## 📁 هيكل المجلدات

```
ansarollah-news-bot/
├── docker-compose.yml          # إعدادات الخدمات
├── Dockerfile                  # بناء صورة البوت
├── docker-entrypoint.sh        # سكريبت البدء
├── .dockerignore              # ملفات مستبعدة
├── .env                       # إعدادات البوت
├── data/                      # قاعدة البيانات والملفات
├── logs/                      # سجلات النشاط
└── backups/                   # النسخ الاحتياطية
```

---

## 🎛️ أوامر الإدارة

### تشغيل البوت:
```bash
# تشغيل عادي
docker-compose up -d

# تشغيل مع إعادة البناء
docker-compose up -d --build

# تشغيل مع المراقبة والنسخ الاحتياطي
docker-compose --profile monitoring --profile backup up -d
```

### مراقبة البوت:
```bash
# عرض حالة الخدمات
docker-compose ps

# مراقبة السجلات
docker-compose logs -f ansarollah-bot

# مراقبة جميع الخدمات
docker-compose logs -f

# عرض إحصائيات الموارد
docker stats ansarollah-news-bot
```

### إيقاف البوت:
```bash
# إيقاف مؤقت
docker-compose stop

# إيقاف وحذف الحاويات
docker-compose down

# إيقاف وحذف كل شيء (بما في ذلك البيانات)
docker-compose down -v --remove-orphans
```

---

## 🔧 التخصيص والإعدادات

### تحديث ملف .env:
```bash
# إيقاف البوت
docker-compose stop ansarollah-bot

# تعديل الإعدادات
nano .env

# إعادة تشغيل البوت
docker-compose up -d ansarollah-bot
```

### إعدادات متقدمة:

#### تفعيل المراقبة التلقائية:
```bash
docker-compose --profile monitoring up -d watchtower
```

#### تفعيل النسخ الاحتياطي:
```bash
# إنشاء نسخة احتياطية فورية
docker-compose run --rm backup

# تفعيل النسخ الدورية (كل 6 ساعات)
echo "0 */6 * * * cd /path/to/bot && docker-compose run --rm backup" | crontab -
```

#### إعدادات الذاكرة:
```yaml
# في docker-compose.yml
services:
  ansarollah-bot:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

## 📊 مراقبة الأداء

### فحص حالة البوت:
```bash
# صحة الحاوية
docker-compose exec ansarollah-bot python3 -c "print('✅ البوت يعمل')"

# فحص قاعدة البيانات
docker-compose exec ansarollah-bot ls -la /app/data/

# فحص السجلات
docker-compose exec ansarollah-bot tail -20 /app/logs/bot_$(date +%Y%m%d).log
```

### مراقبة الموارد:
```bash
# استخدام الذاكرة والمعالج
docker stats ansarollah-news-bot ansarollah-redis

# مساحة التخزين
docker system df

# تنظيف الملفات غير المستخدمة
docker system prune -a
```

---

## 🛠️ استكشاف الأخطاء

### مشاكل شائعة وحلولها:

#### البوت لا يبدأ:
```bash
# فحص السجلات
docker-compose logs ansarollah-bot

# فحص الإعدادات
docker-compose exec ansarollah-bot cat /app/.env

# إعادة بناء الصورة
docker-compose build --no-cache ansarollah-bot
```

#### مشاكل الاتصال:
```bash
# فحص الشبكة
docker-compose exec ansarollah-bot ping google.com

# فحص Telegram API
docker-compose exec ansarollah-bot curl -s https://api.telegram.org/

# فحص موقع الأنصار الله
docker-compose exec ansarollah-bot curl -s https://www.ansarollah.com.ye
```

#### مشاكل قاعدة البيانات:
```bash
# فحص قاعدة البيانات
docker-compose exec ansarollah-bot sqlite3 /app/data/ansarollah_bot.db ".tables"

# إعادة إنشاء قاعدة البيانات
docker-compose exec ansarollah-bot rm /app/data/ansarollah_bot.db
docker-compose restart ansarollah-bot
```

#### مشاكل المساحة:
```bash
# تنظيف السجلات القديمة
docker-compose exec ansarollah-bot find /app/logs -name "*.log" -mtime +7 -delete

# تنظيف النسخ الاحتياطية القديمة
docker-compose exec ansarollah-bot find /app/data -name "*.backup" -mtime +30 -delete
```

---

## 🔄 التحديث والصيانة

### تحديث البوت:
```bash
# إيقاف البوت
docker-compose down

# تحديث الكود
git pull

# إعادة بناء وتشغيل
docker-compose up -d --build
```

### نسخ احتياطية دورية:
```bash
# سكريبت نسخ احتياطي يومي
cat > backup-daily.sh << 'EOF'
#!/bin/bash
cd /path/to/ansarollah-news-bot
docker-compose run --rm backup
docker system prune -f
EOF

chmod +x backup-daily.sh

# إضافة للـ crontab
echo "0 3 * * * /path/to/backup-daily.sh" | crontab -
```

### تحديث Docker Images:
```bash
# تحديث الصور الأساسية
docker-compose pull

# إعادة بناء الصور المحلية
docker-compose build --pull
```

---

## 🐳 أوامر Docker المتقدمة

### دخول الحاوية:
```bash
# دخول البوت الرئيسي
docker-compose exec ansarollah-bot bash

# دخول Redis
docker-compose exec redis redis-cli

# تشغيل أمر واحد
docker-compose exec ansarollah-bot python3 test_config.py
```

### نسخ الملفات:
```bash
# نسخ من الحاوية
docker cp ansarollah-news-bot:/app/data/ansarollah_bot.db ./backup.db

# نسخ إلى الحاوية
docker cp new-config.env ansarollah-news-bot:/app/.env
```

### إعادة تشغيل خدمة واحدة:
```bash
# إعادة تشغيل البوت فقط
docker-compose restart ansarollah-bot

# إعادة تشغيل Redis فقط
docker-compose restart redis
```

---

## 📋 قائمة مراجعة التنصيب

### قبل التشغيل:
- [ ] تم تثبيت Docker و Docker Compose
- [ ] تم نسخ وتعديل ملف .env
- [ ] تم إنشاء البوت في Telegram
- [ ] تم إضافة البوت للقناة كمشرف
- [ ] تتوفر مساحة تخزين كافية (2GB+)

### بعد التشغيل:
- [ ] البوت يعمل: `docker-compose ps`
- [ ] السجلات تظهر بدء التشغيل: `docker-compose logs ansarollah-bot`
- [ ] يمكن الوصول لموقع الأنصار الله
- [ ] الاتصال بـ Telegram API يعمل
- [ ] قاعدة البيانات تم إنشاؤها

### اختبار البوت:
- [ ] إرسال `/start` للبوت
- [ ] إرسال `/status` للتحقق من الحالة
- [ ] فحص ظهور مقالات جديدة

---

## 🎯 مثال تشغيل كامل

```bash
# 1. نسخ المشروع
git clone <repository-url>
cd ansarollah-news-bot

# 2. إعداد البيئة
cp .env.example .env
nano .env  # تعديل البيانات

# 3. تشغيل البوت
docker-compose up -d

# 4. مراقبة التشغيل
docker-compose logs -f ansarollah-bot

# 5. فحص الحالة
docker-compose ps
docker-compose exec ansarollah-bot python3 test_config.py

# 6. اختبار البوت
# إرسال /start للبوت في Telegram
```

---

## 🎉 النتيجة النهائية

بعد التشغيل الناجح:
- ✅ البوت يعمل على مدار الساعة
- ✅ مراقبة موقع الأنصار الله كل دقيقتين
- ✅ نشر تلقائي للمقالات الجديدة
- ✅ نسخ احتياطية دورية
- ✅ مراقبة وتحديث تلقائي
- ✅ سجلات شاملة للنشاط

**Docker يوفر بيئة موثوقة ومعزولة لتشغيل البوت!** 🐳🤖