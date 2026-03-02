#!/usr/bin/env python3
"""
Генератор фикстуры курсов DevOps Learning Platform.
Запуск: python scripts/generate_courses_fixture.py > fixtures/courses.json

Фазы:
  1 — Курсы 1-3: Linux basics, Linux advanced, Bash
  2 — Курсы 4-6: Git, Сети, Docker
  3 — Курсы 7-9: CI/CD, Ansible, Terraform
  4 — Курсы 10-12: Kubernetes, Мониторинг, DevSecOps
"""
import json

data = []
_course_pk = 0
_module_pk = 0
_lesson_pk = 0
_quiz_pk = 0
_question_pk = 0
_answer_pk = 0


# ─────────────────────────────── helpers ────────────────────────────────── #

def course(slug, title, desc, icon, difficulty, category, hours, xp, prereqs=None):
    global _course_pk
    _course_pk += 1
    data.append({
        "model": "courses.course",
        "pk": _course_pk,
        "fields": {
            "slug": slug,
            "title_ru": title,
            "description_ru": desc,
            "icon": icon,
            "difficulty": difficulty,
            "category": category,
            "estimated_hours": hours,
            "xp_reward": xp,
            "order": _course_pk,
            "is_active": True,
            "prerequisites": prereqs or [],
        },
    })
    return _course_pk


def module(course_pk, title, order):
    global _module_pk
    _module_pk += 1
    data.append({
        "model": "courses.module",
        "pk": _module_pk,
        "fields": {"course": course_pk, "title_ru": title, "order": order},
    })
    return _module_pk


def theory(module_pk, title, content, order, xp=50):
    global _lesson_pk
    _lesson_pk += 1
    data.append({
        "model": "courses.lesson",
        "pk": _lesson_pk,
        "fields": {
            "module": module_pk,
            "title_ru": title,
            "lesson_type": "theory",
            "order": order,
            "xp_reward": xp,
            "content_md": content,
            "task": None,
        },
    })
    return _lesson_pk


def quiz_lesson(module_pk, title, order, xp=75):
    global _lesson_pk
    _lesson_pk += 1
    pk = _lesson_pk
    data.append({
        "model": "courses.lesson",
        "pk": pk,
        "fields": {
            "module": module_pk,
            "title_ru": title,
            "lesson_type": "quiz",
            "order": order,
            "xp_reward": xp,
            "content_md": "",
            "task": None,
        },
    })
    return pk


def lab(module_pk, title, task_pk, order, xp=150):
    global _lesson_pk
    _lesson_pk += 1
    data.append({
        "model": "courses.lesson",
        "pk": _lesson_pk,
        "fields": {
            "module": module_pk,
            "title_ru": title,
            "lesson_type": "lab",
            "order": order,
            "xp_reward": xp,
            "content_md": "",
            "task": task_pk,
        },
    })
    return _lesson_pk


def quiz(lesson_pk, threshold=70):
    global _quiz_pk
    _quiz_pk += 1
    data.append({
        "model": "courses.quiz",
        "pk": _quiz_pk,
        "fields": {"lesson": lesson_pk, "pass_threshold": threshold},
    })
    return _quiz_pk


def Q(quiz_pk, text, answers, qtype="single", explanation="", order=1):
    """answers = [(text, is_correct), ...]"""
    global _question_pk, _answer_pk
    _question_pk += 1
    qpk = _question_pk
    data.append({
        "model": "courses.quizquestion",
        "pk": qpk,
        "fields": {
            "quiz": quiz_pk,
            "text_ru": text,
            "question_type": qtype,
            "explanation_ru": explanation,
            "order": order,
        },
    })
    for text_a, correct in answers:
        _answer_pk += 1
        data.append({
            "model": "courses.quizanswer",
            "pk": _answer_pk,
            "fields": {"question": qpk, "text_ru": text_a, "is_correct": correct},
        })


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 1 — Linux для начинающих
# ═══════════════════════════════════════════════════════════════════════════ #
c1 = course(
    "linux-basics",
    "Linux для начинающих",
    "Фундамент любого DevOps-инженера. Файловая система, права, процессы, "
    "сеть, пакеты, systemd и cron — всё что нужно для уверенной работы в терминале.",
    "🐧", "beginner", "linux", 40, 800,
)

# ── Модуль 1: Введение ─────────────────────────────────────────────────────
m = module(c1, "Введение в Linux", 1)
theory(m, "Что такое Linux и зачем он DevOps-инженеру", """\
## Что такое Linux

Linux — свободная Unix-подобная операционная система с открытым исходным кодом.
Создана Линусом Торвальдсом в 1991 году.

### Почему Linux в DevOps?

- **~96%** серверов в мире работают на Linux
- Практически все облачные провайдеры (AWS, GCP, Azure) используют Linux по умолчанию
- Docker, Kubernetes, Ansible, Terraform — все инструменты написаны под Linux
- Бесплатный, надёжный, гибкий

### Ядро и дистрибутивы

```
Ядро Linux (kernel)
       │
   ┌───┴───┐
   │  Libc  │  ← системные вызовы
   └───┬───┘
       │
  ┌────┴─────┐
  │Дистрибутив│  ← Ubuntu, CentOS, Alpine, Debian…
  └──────────┘
```

| Дистрибутив | Область применения |
|---|---|
| **Ubuntu/Debian** | Серверы, облака, разработка |
| **Alpine** | Docker-образы (минимальный размер) |
| **CentOS/RHEL** | Enterprise, production |
| **Arch** | Продвинутые пользователи |

### Первые команды

```bash
uname -r          # версия ядра
cat /etc/os-release  # дистрибутив
whoami            # текущий пользователь
hostname          # имя хоста
uptime            # время работы системы
```
""", 1)

theory(m, "Дистрибутивы, пакетные менеджеры и оболочки", """\
## Оболочка (Shell)

Shell — программа-интерпретатор команд. Самая популярная — **bash**.

```bash
echo $SHELL       # текущая оболочка
cat /etc/shells   # все установленные оболочки
```

### Пакетные менеджеры

| Дистрибутив | Менеджер | Пример |
|---|---|---|
| Ubuntu/Debian | apt | `apt install nginx` |
| CentOS/RHEL | yum / dnf | `dnf install nginx` |
| Alpine | apk | `apk add nginx` |
| Arch | pacman | `pacman -S nginx` |

### Получение помощи

```bash
man ls            # полная документация команды
ls --help         # краткая справка
info bash         # подробная документация bash
tldr ls           # упрощённая шпаргалка (нужен tldr)
type ls           # тип команды (builtin/alias/binary)
which nginx       # путь к бинарнику
```

### Структура команды

```
command  [options]  [arguments]
   │         │           │
  ls        -la      /etc/nginx
```
""", 2)

ql = quiz_lesson(m, "Тест: введение в Linux", 3)
qz = quiz(ql)
Q(qz, "Какой командой узнать версию ядра Linux?",
  [("uname -r", True), ("kernel -v", False), ("linux --version", False), ("cat /proc/kernel", False)],
  explanation="uname -r выводит версию запущенного ядра. uname -a — полная информация о системе.")
Q(qz, "Какой пакетный менеджер используется в Ubuntu?",
  [("apt", True), ("yum", False), ("apk", False), ("pacman", False)],
  explanation="apt (Advanced Package Tool) — пакетный менеджер Debian/Ubuntu. yum/dnf — CentOS/RHEL.", order=2)
Q(qz, "На каком проценте серверов работает Linux?",
  [("~96%", True), ("~50%", False), ("~70%", False), ("~30%", False)],
  explanation="Согласно статистике W3Techs и опросам Linux Foundation, Linux занимает ~96% рынка серверов.", order=3)

# ── Модуль 2: Файловая система ─────────────────────────────────────────────
m = module(c1, "Навигация и файловая система", 2)
theory(m, "Структура файловой системы FHS", """\
## Иерархия файловой системы (FHS)

В Linux всё — файл. Структура начинается с корня `/`.

```
/
├── bin/      → основные команды (ls, cp, mv, cat)
├── sbin/     → системные команды (только root)
├── etc/      → конфигурационные файлы
├── home/     → домашние директории пользователей
│   └── user/ → /home/user == ~
├── root/     → домашняя директория root
├── var/      → переменные данные (логи, БД, кэш)
│   └── log/  → системные логи
├── tmp/      → временные файлы (чистятся при ребуте)
├── usr/      → программы и библиотеки
│   ├── bin/  → пользовательские программы
│   └── lib/  → библиотеки
├── lib/      → системные библиотеки
├── dev/      → устройства (диски, терминалы)
├── proc/     → информация о процессах (виртуальная ФС)
├── sys/      → параметры ядра (виртуальная ФС)
├── mnt/      → точки монтирования
└── opt/      → стороннее ПО
```

### Важные файлы конфигурации

| Файл | Назначение |
|---|---|
| `/etc/passwd` | Список пользователей |
| `/etc/shadow` | Хэши паролей |
| `/etc/hosts` | Локальный DNS |
| `/etc/resolv.conf` | DNS-серверы |
| `/etc/fstab` | Автомонтирование дисков |
| `/etc/crontab` | Системный cron |
""", 1)

theory(m, "Команды навигации: cd, ls, pwd, find", """\
## Навигация в терминале

### Основные команды

```bash
pwd               # текущая директория
ls                # список файлов
ls -la            # подробный список (включая скрытые)
ls -lh            # размеры в human-readable
cd /etc           # перейти в директорию
cd ..             # на уровень выше
cd ~              # домашняя директория
cd -              # предыдущая директория
```

### Полезные опции ls

```bash
ls -lt            # сортировка по времени (новые первые)
ls -lS            # сортировка по размеру
ls -R             # рекурсивный вывод
ls -d */          # только директории
```

### Поиск файлов: find

```bash
find / -name "nginx.conf"       # найти файл по имени
find /etc -name "*.conf"        # все .conf в /etc
find /var/log -mtime -1         # изменённые за последние 24ч
find /tmp -size +10M            # файлы > 10 МБ
find . -type d                  # только директории
find . -type f -exec rm {} \;   # найти и удалить
```

### Работа с путями

```bash
realpath ./file.txt   # абсолютный путь
basename /etc/nginx/nginx.conf  # → nginx.conf
dirname /etc/nginx/nginx.conf   # → /etc/nginx
```
""", 2)

ql = quiz_lesson(m, "Тест: файловая система", 3)
qz = quiz(ql)
Q(qz, "Какая директория содержит конфигурационные файлы?",
  [("/etc", True), ("/bin", False), ("/var", False), ("/usr", False)],
  explanation="/etc — стандартное место для конфигов в Linux (Editable Text Configuration).")
Q(qz, "Что делает команда 'cd -'?",
  [("Переходит в предыдущую директорию", True), ("Удаляет директорию", False),
   ("Переходит в корень", False), ("Создаёт директорию", False)],
  explanation="cd - переключает между текущей и предыдущей директорией — удобно при работе в двух местах.", order=2)
Q(qz, "Какая опция ls показывает скрытые файлы?",
  [("-a", True), ("-h", False), ("-r", False), ("-s", False)],
  explanation="ls -a показывает все файлы включая скрытые (начинающиеся с точки). -la — подробный список со скрытыми.", order=3)

lab(m, "Лабораторная: навигация по файловой системе", 2, 4)

# ── Модуль 3: Работа с файлами ─────────────────────────────────────────────
m = module(c1, "Работа с файлами и текстом", 3)
theory(m, "Создание, копирование, перемещение файлов", """\
## Операции с файлами

### Создание

```bash
touch file.txt          # создать пустой файл / обновить время изменения
mkdir dir               # создать директорию
mkdir -p a/b/c          # создать вложенные директории
echo "текст" > file.txt # создать файл с содержимым
cat > file.txt << EOF   # многострочный ввод
line1
line2
EOF
```

### Копирование и перемещение

```bash
cp file.txt backup.txt       # копировать файл
cp -r dir/ dir_backup/       # копировать директорию рекурсивно
cp -p file.txt /tmp/         # сохранить права и время
mv file.txt /tmp/            # переместить
mv old_name.txt new_name.txt # переименовать
```

### Удаление

```bash
rm file.txt          # удалить файл
rm -f file.txt       # принудительно (без подтверждения)
rm -r dir/           # удалить директорию рекурсивно
rm -rf dir/          # принудительно рекурсивно (ОСТОРОЖНО!)
rmdir empty_dir/     # удалить только пустую директорию
```

### Просмотр файлов

```bash
cat file.txt         # вывести содержимое
less file.txt        # постраничный просмотр (q — выход)
head -n 20 file.txt  # первые 20 строк
tail -n 20 file.txt  # последние 20 строк
tail -f /var/log/syslog  # следить за файлом в реальном времени
wc -l file.txt       # подсчёт строк
```
""", 1)

theory(m, "Текстовые утилиты: grep, sed, awk, cut", """\
## Мощный текстовый инструментарий

### grep — поиск по тексту

```bash
grep "error" /var/log/syslog          # найти строки с "error"
grep -i "error" file.txt              # без учёта регистра
grep -r "TODO" ./src/                 # рекурсивный поиск
grep -n "error" file.txt              # с номерами строк
grep -v "DEBUG" app.log               # исключить строки
grep -c "error" app.log               # подсчёт совпадений
grep -E "error|warn|crit" app.log     # регулярное выражение
grep -A 3 "error" app.log             # + 3 строки после
grep -B 2 "error" app.log             # + 2 строки до
```

### sed — потоковый редактор

```bash
sed 's/old/new/' file.txt             # заменить первое вхождение
sed 's/old/new/g' file.txt            # заменить все вхождения
sed -i 's/old/new/g' file.txt         # изменить файл напрямую
sed -n '10,20p' file.txt              # вывести строки 10-20
sed '/^#/d' nginx.conf                # удалить строки с комментариями
sed -i '/DEBUG/d' app.log             # удалить строки с DEBUG
```

### awk — построчная обработка

```bash
awk '{print $1}' file.txt             # первый столбец
awk '{print $1, $3}' file.txt         # первый и третий
awk -F: '{print $1}' /etc/passwd      # разделитель : → имена пользователей
awk '{sum += $1} END {print sum}'     # сумма первого столбца
awk 'NR>5 {print}' file.txt           # строки с 6-й
awk '/error/ {print NR, $0}'          # номер строки + строки с "error"
```

### cut — вырезать столбцы

```bash
cut -d: -f1 /etc/passwd               # первое поле (разделитель :)
cut -c1-10 file.txt                   # символы с 1 по 10
cut -d, -f2,4 data.csv                # 2-е и 4-е поле CSV
```

### Пример: разбор логов

```bash
# Топ-10 IP по запросам в nginx access.log
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```
""", 2)

ql = quiz_lesson(m, "Тест: работа с файлами", 3)
qz = quiz(ql)
Q(qz, "Какая команда следит за файлом логов в реальном времени?",
  [("tail -f", True), ("cat -f", False), ("less -f", False), ("watch cat", False)],
  explanation="tail -f (follow) непрерывно выводит новые строки файла. Незаменим для мониторинга логов.")
Q(qz, "Как grep найти строки НЕ содержащие слово 'DEBUG'?",
  [("grep -v 'DEBUG'", True), ("grep -x 'DEBUG'", False), ("grep -n 'DEBUG'", False), ("grep --exclude 'DEBUG'", False)],
  explanation="grep -v (invert) инвертирует совпадение — выводит строки, не содержащие паттерн.", order=2)
Q(qz, "Что делает sed -i 's/foo/bar/g' file.txt?",
  [("Заменяет все 'foo' на 'bar' в файле напрямую", True),
   ("Выводит изменения без сохранения", False),
   ("Удаляет строки с 'foo'", False),
   ("Добавляет 'bar' после каждой строки", False)],
  explanation="sed -i редактирует файл напрямую (in-place). Флаг g заменяет все вхождения в каждой строке.", order=3)

# ── Модуль 4: Права доступа ────────────────────────────────────────────────
m = module(c1, "Права доступа и пользователи", 4)
theory(m, "chmod, chown, umask — управление правами", """\
## Права доступа в Linux

Каждый файл имеет три набора прав: **u**ser (владелец), **g**roup (группа), **o**ther (остальные).

```
$ ls -la script.sh
-rwxr-xr-- 1 deploy www-data 1024 Jan 1 12:00 script.sh
 ├──┤├──┤├──┤
  u    g    o
```

| Символ | Число | Значение |
|---|---|---|
| r | 4 | Чтение |
| w | 2 | Запись |
| x | 1 | Выполнение |

### chmod

```bash
chmod 755 script.sh      # rwxr-xr-x (типично для скриптов)
chmod 644 file.txt       # rw-r--r-- (типично для файлов)
chmod 600 id_rsa         # rw------- (SSH ключ)
chmod 700 ~/.ssh         # rwx------ (папка SSH)
chmod +x script.sh       # добавить execute всем
chmod u+x,go-w file      # u:+x, g и o: -w
chmod -R 755 /var/www/   # рекурсивно
```

### chown

```bash
chown user file.txt           # сменить владельца
chown user:group file.txt     # владелец и группа
chown -R nginx:nginx /var/www/ # рекурсивно
chgrp www-data /var/log/nginx/ # только группу
```

### umask — маска прав по умолчанию

```bash
umask          # текущая маска (обычно 022)
umask 027      # новые файлы: 640, директории: 750
```

Итоговые права = базовые - umask:
- Файл: 666 - 022 = **644**
- Директория: 777 - 022 = **755**

### Специальные биты

```bash
chmod u+s /usr/bin/passwd  # SUID — запуск от имени владельца файла
chmod g+s /shared/         # SGID — файлы наследуют группу директории
chmod +t /tmp/             # Sticky bit — удалять только свои файлы
```
""", 1)

theory(m, "Пользователи и группы: useradd, usermod, sudo", """\
## Управление пользователями

### Создание и изменение

```bash
useradd -m -s /bin/bash deploy      # создать пользователя с домашней директорией
useradd -m -G docker,sudo deploy    # добавить в группы при создании
usermod -aG docker deploy           # добавить в группу docker (без -a — заменит!)
usermod -s /bin/bash deploy         # сменить оболочку
passwd deploy                       # установить пароль
userdel -r deploy                   # удалить пользователя и домашнюю папку
```

### Просмотр

```bash
id deploy                # UID, GID и группы пользователя
groups deploy            # только группы
cat /etc/passwd          # все пользователи (логин:x:UID:GID:описание:home:shell)
cat /etc/group           # все группы
getent passwd deploy     # информация о пользователе
w                        # кто сейчас авторизован
last                     # история входов
```

### sudo

```bash
sudo command             # выполнить от root
sudo -u postgres psql    # выполнить от имени postgres
sudo -i                  # интерактивная оболочка root
sudo !!                  # повторить последнюю команду с sudo
visudo                   # безопасное редактирование /etc/sudoers
```

Строка в `/etc/sudoers`:
```
deploy  ALL=(ALL) NOPASSWD: /usr/bin/docker
```
→ пользователь deploy может запускать docker без пароля.

### Переключение пользователей

```bash
su - deploy         # войти как deploy (с его окружением)
su -c "ls /root" root  # выполнить одну команду от root
```
""", 2)

ql = quiz_lesson(m, "Тест: права доступа", 3)
qz = quiz(ql)
Q(qz, "Что означают права 644 для файла?",
  [("Владелец: rw-, Группа: r--, Остальные: r--", True),
   ("Владелец: rwx, Группа: r--, Остальные: r--", False),
   ("Все: rw-", False),
   ("Владелец: rw-, Группа: rw-, Остальные: ---", False)],
  explanation="6=rw-, 4=r--. Типично для обычных файлов: владелец читает/пишет, остальные только читают.")
Q(qz, "Как безопасно добавить пользователя в группу docker БЕЗ удаления из других групп?",
  [("usermod -aG docker user", True), ("usermod -G docker user", False),
   ("groupadd docker user", False), ("useradd -G docker user", False)],
  explanation="Флаг -a (append) добавляет группу к существующим. Без -a флаг -G ЗАМЕНЯЕТ все группы!", order=2)
Q(qz, "Какой SSH-ключ должен иметь права?",
  [("600 (rw-------)", True), ("644 (rw-r--r--)", False),
   ("755 (rwxr-xr-x)", False), ("777 (rwxrwxrwx)", False)],
  explanation="SSH требует права 600 на приватный ключ. Если права шире — SSH откажет в подключении с ошибкой 'too open'.", order=3)

lab(m, "Лабораторная: права доступа к файлам", 3, 4)

# ── Модуль 5: Процессы ─────────────────────────────────────────────────────
m = module(c1, "Процессы и сигналы", 5)
theory(m, "Управление процессами: ps, top, kill", """\
## Процессы в Linux

Каждая программа — один или несколько процессов. У каждого процесса есть PID.

### Просмотр процессов

```bash
ps aux                    # все процессы (BSD-стиль)
ps -ef                    # все процессы (UNIX-стиль)
ps aux | grep nginx       # найти процессы nginx
pgrep nginx               # PID по имени
pgrep -u deploy           # процессы пользователя deploy
pidof nginx               # PID по точному имени

top                       # интерактивный мониторинг (q — выход)
htop                      # улучшенный top (F10 — выход)
```

### top: расшифровка

```
top - 12:00:01 up 5 days, load average: 0.15, 0.10, 0.08
Tasks: 120 total,   1 running, 119 sleeping
%Cpu(s): 2.3 us, 0.5 sy, 0.0 ni, 97.0 id
MiB Mem :  7982.8 total,  4123.1 free
```

- **load average** — средняя нагрузка за 1/5/15 минут
- **us** — userspace, **sy** — kernel, **id** — idle
- На 1 CPU нагрузка 1.0 = 100%

### Сигналы

```bash
kill -15 1234     # SIGTERM — мягкое завершение (по умолчанию)
kill -9 1234      # SIGKILL — принудительное (нельзя поймать!)
kill -1 1234      # SIGHUP — перечитать конфиг
kill -19 1234     # SIGSTOP — заморозить процесс
kill -18 1234     # SIGCONT — продолжить

killall nginx     # завершить все процессы по имени
pkill -f 'gunicorn'  # завершить по паттерну
```

### Фоновые процессы

```bash
command &         # запустить в фоне
jobs              # список фоновых задач
fg %1             # перевести job 1 на передний план
bg %1             # запустить остановленный job в фоне
Ctrl+Z            # остановить текущий процесс
nohup command &   # не завершать при выходе из терминала
disown %1         # открепить от текущей сессии
```
""", 1)

ql = quiz_lesson(m, "Тест: процессы и сигналы", 2)
qz = quiz(ql)
Q(qz, "Какой сигнал нельзя перехватить или заблокировать?",
  [("SIGKILL (9)", True), ("SIGTERM (15)", False), ("SIGHUP (1)", False), ("SIGINT (2)", False)],
  explanation="SIGKILL немедленно завершает процесс ядром. Процесс не может его перехватить, заблокировать или игнорировать.")
Q(qz, "Какая команда показывает список фоновых задач текущей сессии?",
  [("jobs", True), ("ps bg", False), ("bg list", False), ("task -l", False)],
  explanation="jobs показывает задачи текущей bash-сессии. ps aux показывает все процессы системы.", order=2)
Q(qz, "Что произойдёт если нажать Ctrl+Z в терминале?",
  [("Процесс будет приостановлен (SIGSTOP)", True),
   ("Процесс завершится (SIGTERM)", False),
   ("Процесс перейдёт в фон и продолжит работу", False),
   ("Терминал закроется", False)],
  explanation="Ctrl+Z отправляет SIGTSTP и приостанавливает процесс. Затем bg продолжит его в фоне, fg — на переднем плане.", order=3)

lab(m, "Лабораторная: управление процессами", 4, 4)

# ── Модуль 6: Пакеты ───────────────────────────────────────────────────────
m = module(c1, "Пакеты и программное обеспечение", 6)
theory(m, "apt, dpkg, snap — установка ПО в Ubuntu/Debian", """\
## Пакетные менеджеры Ubuntu/Debian

### apt — высокоуровневый менеджер

```bash
apt update                      # обновить список пакетов
apt upgrade                     # обновить установленные пакеты
apt full-upgrade                # обновить + удалить конфликтующие
apt install nginx               # установить пакет
apt install -y nginx            # без подтверждения
apt remove nginx                # удалить (конфиги остаются)
apt purge nginx                 # удалить вместе с конфигами
apt autoremove                  # удалить ненужные зависимости
apt search nginx                # поиск пакетов
apt show nginx                  # информация о пакете
apt list --installed            # список установленных
apt list --upgradable           # список пакетов с обновлениями
```

### dpkg — низкоуровневый менеджер

```bash
dpkg -i package.deb             # установить .deb файл
dpkg -l                         # список всех установленных
dpkg -l nginx                   # информация о пакете
dpkg -s nginx                   # статус пакета
dpkg -L nginx                   # файлы пакета nginx
dpkg -S /usr/sbin/nginx         # какому пакету принадлежит файл
dpkg -r nginx                   # удалить
```

### Добавление репозиториев

```bash
# Пример: добавление Docker репозитория
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo "deb [signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list
apt update && apt install docker-ce
```

### snap

```bash
snap install code --classic     # установить VS Code
snap list                       # список snap-пакетов
snap remove code                # удалить
snap refresh                    # обновить все snap
```
""", 1)

ql = quiz_lesson(m, "Тест: пакеты и ПО", 2)
qz = quiz(ql)
Q(qz, "Какая команда обновляет список доступных пакетов (не сами пакеты)?",
  [("apt update", True), ("apt upgrade", False), ("apt refresh", False), ("apt sync", False)],
  explanation="apt update скачивает актуальные списки пакетов из репозиториев. apt upgrade устанавливает обновления.")
Q(qz, "Как найти пакет, которому принадлежит файл /usr/sbin/nginx?",
  [("dpkg -S /usr/sbin/nginx", True), ("apt find /usr/sbin/nginx", False),
   ("dpkg -L nginx", False), ("which nginx", False)],
  explanation="dpkg -S (search) находит пакет по пути файла. dpkg -L (list) наоборот — показывает файлы пакета.", order=2)
Q(qz, "apt purge отличается от apt remove тем, что:",
  [("Удаляет также конфигурационные файлы", True),
   ("Удаляет зависимости", False),
   ("Удаляет без подтверждения", False),
   ("Удаляет snap-пакеты", False)],
  explanation="apt remove удаляет пакет, но оставляет конфиги. apt purge удаляет всё включая файлы конфигурации.", order=3)

# ── Модуль 7: Сеть базовая ─────────────────────────────────────────────────
m = module(c1, "Базовые сетевые команды", 7)
theory(m, "ip, ping, ss, curl — диагностика сети", """\
## Сеть в Linux

### Интерфейсы и адреса

```bash
ip addr show              # все интерфейсы с IP
ip addr show eth0         # конкретный интерфейс
ip link show              # статус интерфейсов
ip route show             # таблица маршрутизации
ip route get 8.8.8.8      # маршрут до IP
```

### Проверка связи

```bash
ping google.com                  # проверить связь (Ctrl+C)
ping -c 4 google.com             # 4 пакета
ping -i 0.5 google.com           # интервал 0.5 сек
traceroute google.com            # путь до хоста
mtr google.com                   # интерактивный traceroute
```

### Порты и соединения: ss

```bash
ss -tuln          # все слушающие TCP/UDP порты
ss -tulnp         # + имена процессов
ss -s             # статистика
ss -tnp           # активные TCP соединения
ss dst 192.168.1.1  # соединения с указанным хостом
```

### curl — HTTP клиент

```bash
curl https://example.com                  # GET запрос
curl -I https://example.com               # только заголовки
curl -X POST -d '{"key":"val"}' url       # POST с JSON
curl -H "Authorization: Bearer TOKEN" url # заголовок
curl -o file.zip https://url/file.zip     # скачать файл
curl -L url                               # следовать редиректам
curl -v url                               # verbose (отладка)
curl --connect-timeout 5 url              # таймаут
```

### DNS

```bash
nslookup google.com           # DNS запрос
dig google.com                # подробный DNS запрос
dig google.com A              # только A-записи
dig @8.8.8.8 google.com      # запрос к конкретному DNS
host google.com               # простой DNS запрос
cat /etc/resolv.conf          # настроенные DNS-серверы
```
""", 1)

ql = quiz_lesson(m, "Тест: базовые сетевые команды", 2)
qz = quiz(ql)
Q(qz, "Какая команда показывает все слушающие порты с именами процессов?",
  [("ss -tulnp", True), ("netstat -a", False), ("ip port list", False), ("ps -net", False)],
  explanation="ss -tulnp: t=TCP, u=UDP, l=listening, n=numeric, p=process. Современная замена netstat.")
Q(qz, "Как скачать файл через curl и сохранить его локально?",
  [("curl -o file.zip URL", True), ("curl --save file.zip URL", False),
   ("curl -d file.zip URL", False), ("curl >> file.zip URL", False)],
  explanation="curl -o задаёт имя выходного файла. curl -O сохраняет с оригинальным именем из URL.", order=2)
Q(qz, "Что покажет команда 'ip route show'?",
  [("Таблицу маршрутизации", True), ("DNS маршруты", False),
   ("Список сетевых интерфейсов", False), ("Статистику по пакетам", False)],
  explanation="ip route show выводит таблицу маршрутизации: сети, шлюзы, интерфейсы.", order=3)

# ── Модуль 8: Архивы ───────────────────────────────────────────────────────
m = module(c1, "Архивы и хранилище", 8)
theory(m, "tar, gzip, rsync — архивирование и синхронизация", """\
## Работа с архивами

### tar — универсальный архиватор

```bash
# Создание архивов
tar -czf archive.tar.gz dir/   # gzip архив
tar -cjf archive.tar.bz2 dir/  # bzip2 архив
tar -cJf archive.tar.xz dir/   # xz архив (лучшее сжатие)
tar -cf archive.tar dir/        # без сжатия

# Распаковка
tar -xzf archive.tar.gz        # распаковать gzip
tar -xzf archive.tar.gz -C /tmp/ # в конкретную директорию
tar -tf archive.tar.gz          # просмотр содержимого

# Мнемоника флагов tar:
# c — create, x — extract, z — gzip, j — bzip2
# J — xz, f — file, v — verbose, t — list
```

### gzip / gunzip

```bash
gzip file.txt             # сжать → file.txt.gz
gzip -d file.txt.gz       # распаковать (= gunzip)
gzip -k file.txt          # сжать, сохранить оригинал
gzip -l archive.gz        # информация об архиве
zcat file.gz              # просмотр без распаковки
```

### zip / unzip

```bash
zip archive.zip file1 file2
zip -r archive.zip dir/
unzip archive.zip
unzip archive.zip -d /tmp/
unzip -l archive.zip      # содержимое
```

### rsync — умная синхронизация

```bash
rsync -av src/ dst/                     # локальная синхронизация
rsync -av src/ user@host:/dst/          # на удалённый хост
rsync -av --delete src/ dst/            # удалять лишние в dst
rsync -av --exclude='*.log' src/ dst/   # исключить файлы
rsync -azP src/ user@host:/dst/         # сжатие + прогресс
```

> rsync передаёт только изменённые части файлов — намного быстрее cp для больших данных.

### Проверка места на диске

```bash
df -h           # свободное место на разделах
df -i           # использование inodes
du -sh dir/     # размер директории
du -sh *        # размер каждой поддиректории
ncdu .          # интерактивный анализ (нужен apt install ncdu)
```
""", 1)

ql = quiz_lesson(m, "Тест: архивы", 2)
qz = quiz(ql)
Q(qz, "Какая команда создаёт сжатый tar.gz архив директории?",
  [("tar -czf archive.tar.gz dir/", True), ("tar -xzf archive.tar.gz dir/", False),
   ("gzip -r dir/ archive.tar.gz", False), ("zip -r archive.tar.gz dir/", False)],
  explanation="tar -czf: c=create, z=gzip, f=filename. Запомните: c — создать, x — распаковать.")
Q(qz, "Чем rsync лучше cp для больших файлов?",
  [("Передаёт только изменённые части файлов", True),
   ("Работает быстрее за счёт многопоточности", False),
   ("Использует меньше CPU", False),
   ("Автоматически сжимает файлы", False)],
  explanation="Алгоритм дельта-синхронизации rsync передаёт только изменённые блоки, что критически важно для больших файлов.", order=2)

# ── Модуль 9: Systemd ──────────────────────────────────────────────────────
m = module(c1, "Systemd и управление сервисами", 9)
theory(m, "systemctl — запуск и управление сервисами", """\
## Systemd

Systemd — система инициализации и менеджер сервисов Linux (PID 1).

### Управление сервисами

```bash
systemctl status nginx          # статус сервиса
systemctl start nginx           # запустить
systemctl stop nginx            # остановить
systemctl restart nginx         # перезапустить
systemctl reload nginx          # перечитать конфиг (без restart)
systemctl enable nginx          # автозапуск при загрузке
systemctl disable nginx         # отключить автозапуск
systemctl mask nginx            # полностью заблокировать
systemctl unmask nginx          # разблокировать
```

### Просмотр и диагностика

```bash
systemctl list-units            # все запущенные юниты
systemctl list-units --failed   # упавшие юниты
systemctl list-unit-files       # все юниты и их состояние
systemctl daemon-reload         # перечитать все unit-файлы (после изменений)
systemctl cat nginx             # показать unit-файл
```

### journald — просмотр логов

```bash
journalctl -u nginx             # логи сервиса nginx
journalctl -u nginx -f          # следить в реальном времени
journalctl -u nginx --since "1 hour ago"
journalctl -u nginx -n 100      # последние 100 строк
journalctl -p err               # только ошибки
journalctl --disk-usage         # размер логов
journalctl --vacuum-time=7d     # удалить логи старше 7 дней
```

### Структура unit-файла

```ini
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/myapp
ExecStart=/opt/myapp/run.sh
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
""", 1)

theory(m, "Создание собственных systemd-сервисов", """\
## Собственный systemd-сервис

### Пример: сервис для Python-приложения

```bash
# 1. Создать unit-файл
nano /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=My Django Application
Documentation=https://github.com/myorg/myapp
After=network.target postgresql.service redis.service
Requires=postgresql.service

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/opt/myapp
EnvironmentFile=/opt/myapp/.env
ExecStart=/opt/myapp/venv/bin/gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Применить и запустить
systemctl daemon-reload
systemctl enable --now myapp
systemctl status myapp
```

### Типы сервисов (Type=)

| Type | Когда использовать |
|---|---|
| `simple` | Процесс не форкается (по умолчанию) |
| `forking` | Процесс форкается в фон (старые демоны) |
| `oneshot` | Разовые задачи (скрипты) |
| `notify` | Процесс сигнализирует о готовности |

### Restart политики

| Значение | Когда перезапускать |
|---|---|
| `always` | Всегда |
| `on-failure` | Только при ненулевом exit-коде |
| `on-abnormal` | Сигналы, таймаут |
| `no` | Никогда |
""", 2)

ql = quiz_lesson(m, "Тест: systemd", 3)
qz = quiz(ql)
Q(qz, "Что делает 'systemctl enable --now nginx'?",
  [("Включает автозапуск И немедленно запускает", True),
   ("Только включает автозапуск", False),
   ("Только запускает сейчас", False),
   ("Перезапускает и включает автозапуск", False)],
  explanation="--now комбинирует enable (автозапуск) и start (запуск прямо сейчас) в одну команду.")
Q(qz, "Какую команду нужно выполнить после изменения unit-файла?",
  [("systemctl daemon-reload", True), ("systemctl reload", False),
   ("systemctl restart", False), ("systemctl refresh", False)],
  explanation="daemon-reload заставляет systemd перечитать все unit-файлы с диска. Без этого изменения не применятся.", order=2)
Q(qz, "Какая journalctl команда следит за логами nginx в реальном времени?",
  [("journalctl -u nginx -f", True), ("journalctl -u nginx --tail", False),
   ("tail -f journalctl nginx", False), ("journalctl -u nginx --live", False)],
  explanation="-f (follow) работает как tail -f, но для системного журнала. Очень удобно при отладке сервисов.", order=3)

lab(m, "Лабораторная: создание systemd-сервиса", 5, 4)

# ── Модуль 10: Cron ────────────────────────────────────────────────────────
m = module(c1, "Cron и планирование задач", 10)
theory(m, "crontab — автоматизация по расписанию", """\
## Cron

Cron — демон для запуска задач по расписанию.

### Синтаксис crontab

```
┌──────────── минута (0-59)
│ ┌────────── час (0-23)
│ │ ┌──────── день месяца (1-31)
│ │ │ ┌────── месяц (1-12)
│ │ │ │ ┌──── день недели (0-7, 0 и 7 = воскресенье)
│ │ │ │ │
* * * * *  command
```

### Примеры расписаний

```bash
# Каждую минуту
* * * * * /opt/check.sh

# Каждый час в :30
30 * * * * /opt/hourly.sh

# Каждый день в 2:00
0 2 * * * /opt/backup.sh

# По будням в 9:00
0 9 * * 1-5 /opt/report.sh

# Каждые 15 минут
*/15 * * * * /opt/ping.sh

# 1-го числа каждого месяца в полночь
0 0 1 * * /opt/monthly.sh

# Несколько значений: в 8, 12 и 18 часов
0 8,12,18 * * * /opt/task.sh
```

### Управление crontab

```bash
crontab -e          # редактировать crontab текущего пользователя
crontab -l          # показать crontab
crontab -r          # удалить crontab
crontab -u deploy -e  # crontab другого пользователя (root)
```

### Системный cron

```bash
/etc/cron.d/        # cron-файлы приложений
/etc/cron.hourly/   # скрипты раз в час
/etc/cron.daily/    # раз в день
/etc/cron.weekly/   # раз в неделю
/etc/cron.monthly/  # раз в месяц
```

### Перенаправление вывода

```bash
# Сохранять логи
0 2 * * * /opt/backup.sh >> /var/log/backup.log 2>&1

# Игнорировать вывод
*/5 * * * * /opt/check.sh > /dev/null 2>&1
```

### at — разовые задачи

```bash
at 14:30                  # ввести команды для выполнения в 14:30
at now + 1 hour           # через 1 час
atq                       # список запланированных задач
atrm 3                    # удалить задачу №3
```
""", 1)

ql = quiz_lesson(m, "Тест: cron и планирование", 2)
qz = quiz(ql)
Q(qz, "Какое расписание cron означает 'каждые 15 минут'?",
  [("*/15 * * * *", True), ("15 * * * *", False), ("* */15 * * *", False), ("0,15,30,45 * * * *", True)],
  qtype="multi",
  explanation="*/15 — каждые 15 минут (делитель). 0,15,30,45 — явное перечисление минут. Оба варианта верны.")
Q(qz, "Как запустить cron-задачу по будням в 9 утра?",
  [("0 9 * * 1-5 cmd", True), ("0 9 * * 0-4 cmd", False), ("9 0 * * 1-5 cmd", False), ("* 9 * * 1-5 cmd", False)],
  explanation="Дни недели: 1=понедельник, 5=пятница. Порядок полей: минута час день месяц день_недели.", order=2)

# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 2 — Продвинутый Linux
# ═══════════════════════════════════════════════════════════════════════════ #
c2 = course(
    "linux-advanced",
    "Продвинутый Linux",
    "Глубокое погружение: файловые системы, сетевой стек, диагностика производительности, "
    "безопасность SSH и firewall, ядро Linux. Уровень Senior DevOps.",
    "🔧", "advanced", "linux", 50, 1200, prereqs=[1],
)

# ── Модуль 11: ФС углубленно ───────────────────────────────────────────────
m = module(c2, "Файловые системы и LVM", 1)
theory(m, "LVM: управление логическими томами", """\
## LVM (Logical Volume Manager)

LVM — абстракция над физическими дисками для гибкого управления хранилищем.

```
Физические диски (sda, sdb)
         │
    Physical Volumes (PV)
         │
    Volume Group (VG)  ← объединяет несколько PV
         │
    Logical Volumes (LV) ← аналог разделов, гибко изменяемые
         │
    Файловые системы (ext4, xfs)
```

### Основные команды

```bash
# Physical Volumes
pvcreate /dev/sdb             # инициализировать диск как PV
pvdisplay                     # информация о PV
pvs                           # краткий список PV

# Volume Groups
vgcreate data_vg /dev/sdb /dev/sdc  # создать VG из двух дисков
vgextend data_vg /dev/sdd           # добавить диск в VG
vgdisplay data_vg
vgs

# Logical Volumes
lvcreate -L 50G -n data data_vg     # создать LV 50GB
lvcreate -l 100%FREE -n data data_vg # весь свободный объём
lvdisplay
lvs
lvextend -L +10G /dev/data_vg/data  # расширить LV на 10GB
lvreduce -L -5G /dev/data_vg/data   # уменьшить (осторожно!)
```

### Расширение файловой системы

```bash
# После расширения LV нужно расширить ФС:
# ext4:
resize2fs /dev/data_vg/data

# xfs (только расширение, не уменьшение):
xfs_growfs /mount/point

# Онлайн расширение (без размонтирования):
lvextend -L +10G -r /dev/data_vg/data   # -r = resize filesystem
```

### Снапшоты LVM

```bash
lvcreate -L 5G -s -n data_snap /dev/data_vg/data  # снапшот
lvremove /dev/data_vg/data_snap                     # удалить снапшот
```
""", 1)

theory(m, "mount, fstab, df, du — работа с дисками", """\
## Монтирование файловых систем

### mount / umount

```bash
mount /dev/sdb1 /mnt/data          # монтировать раздел
mount -t ext4 /dev/sdb1 /mnt/data  # явно указать ФС
mount -o ro /dev/sdb1 /mnt/data    # только для чтения
mount -o remount,rw /mnt/data      # перемонтировать с записью
umount /mnt/data                   # размонтировать
umount -l /mnt/data                # lazy (даже если занято)
lsblk                              # блочные устройства
blkid                              # UUID и типы ФС
```

### /etc/fstab — автомонтирование

```
# Device          Mountpoint    Type    Options         Dump Pass
UUID=abc123       /             ext4    defaults         0    1
UUID=def456       /data         ext4    defaults,noatime 0    2
tmpfs             /tmp          tmpfs   defaults,size=1G 0    0
//server/share    /mnt/smb      cifs    credentials=/etc/smb.cred 0 0
```

```bash
mount -a           # примонтировать всё из fstab
systemctl daemon-reload && mount -a  # после изменения fstab
```

### Создание файловых систем

```bash
mkfs.ext4 /dev/sdb1
mkfs.xfs /dev/sdb1
mkfs.btrfs /dev/sdb1

# Настройка ext4
tune2fs -l /dev/sdb1          # информация о ФС
tune2fs -m 1 /dev/sdb1        # зарезервировать 1% (по умолчанию 5%)
e2fsck -f /dev/sdb1           # проверка ФС
```

### Анализ использования

```bash
df -h               # свободное место (human-readable)
df -i               # использование inodes
du -sh /var/log/    # размер директории
du -sh * | sort -rh | head -10  # топ-10 по размеру
ncdu /var           # интерактивный анализ
lsof +D /var/log    # открытые файлы в директории
```
""", 2)

ql = quiz_lesson(m, "Тест: файловые системы и LVM", 3)
qz = quiz(ql)
Q(qz, "Какой правильный порядок создания LVM?",
  [("pvcreate → vgcreate → lvcreate", True),
   ("vgcreate → pvcreate → lvcreate", False),
   ("lvcreate → vgcreate → pvcreate", False),
   ("pvcreate → lvcreate → vgcreate", False)],
  explanation="Снизу вверх: сначала инициализируем физические тома (pvcreate), объединяем в группу (vgcreate), создаём логические тома (lvcreate).")
Q(qz, "Как расширить ext4 ФС после увеличения LV?",
  [("resize2fs /dev/vg/lv", True), ("fdisk /dev/vg/lv", False),
   ("xfs_growfs /mount", False), ("mkfs.ext4 /dev/vg/lv", False)],
  explanation="resize2fs изменяет размер ext4. Для xfs используется xfs_growfs. mkfs форматирует — все данные потеряются!", order=2)
Q(qz, "Что нужно сделать после изменения /etc/fstab?",
  [("mount -a", True), ("reboot", False), ("systemctl restart mount", False), ("fdisk -a", False)],
  explanation="mount -a монтирует всё из fstab немедленно. Перезагрузка тоже применит, но это необязательно.", order=3)

# ── Модуль 12: Сеть продвинутая ───────────────────────────────────────────
m = module(c2, "Сеть: диагностика и firewall", 2)
theory(m, "tcpdump, ss, iptables — сетевая диагностика", """\
## Продвинутые сетевые инструменты

### tcpdump — перехват пакетов

```bash
tcpdump -i eth0                          # захват на интерфейсе
tcpdump -i eth0 port 80                  # только порт 80
tcpdump -i eth0 host 192.168.1.1        # только с/к хосту
tcpdump -i eth0 -w capture.pcap         # сохранить в файл
tcpdump -r capture.pcap                 # читать файл
tcpdump -i eth0 'tcp port 443 and host google.com'
tcpdump -i eth0 -n -v port 53           # DNS запросы (-n без разрешения имён)
```

### ss — статистика сокетов

```bash
ss -s                    # сводная статистика
ss -tulnp                # слушающие порты + процессы
ss -tnp state ESTABLISHED # активные TCP
ss -tnp state TIME-WAIT   # соединения в TIME-WAIT
ss -tulnp | grep :8080    # кто слушает 8080
```

### iptables — firewall

```bash
# Просмотр правил
iptables -L -v -n                    # все правила с подробностями
iptables -L INPUT -v -n              # только цепочка INPUT
iptables -t nat -L -v -n             # NAT таблица

# Базовые правила
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # разрешить HTTP
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # разрешить SSH
iptables -A INPUT -j DROP                        # запретить всё остальное

# Блокировка
iptables -A INPUT -s 192.168.1.100 -j DROP      # заблокировать IP
iptables -D INPUT -s 192.168.1.100 -j DROP      # удалить правило

# Сохранение
iptables-save > /etc/iptables/rules.v4
iptables-restore < /etc/iptables/rules.v4
```

### ufw — упрощённый firewall

```bash
ufw enable                  # включить firewall
ufw status verbose          # статус с правилами
ufw allow 22/tcp            # разрешить SSH
ufw allow 80,443/tcp        # HTTP и HTTPS
ufw allow from 10.0.0.0/8   # разрешить подсеть
ufw deny 3306               # запретить MySQL
ufw delete allow 80/tcp     # удалить правило
ufw limit ssh               # rate limiting SSH (защита от bruteforce)
```
""", 1)

ql = quiz_lesson(m, "Тест: сеть и firewall", 2)
qz = quiz(ql)
Q(qz, "Как tcpdump захватить только HTTP трафик на порту 80?",
  [("tcpdump -i eth0 port 80", True), ("tcpdump -i eth0 http", False),
   ("tcpdump --filter port 80", False), ("tcpdump -p 80 eth0", False)],
  explanation="tcpdump использует BPF (Berkeley Packet Filter) синтаксис: port 80, host X, proto tcp и т.д.")
Q(qz, "Что делает 'iptables -A INPUT -j DROP' в конце набора правил?",
  [("Запрещает весь входящий трафик, не совпавший с предыдущими правилами", True),
   ("Удаляет правило DROP из INPUT", False),
   ("Запрещает весь трафик немедленно", False),
   ("Разрешает только явно указанный трафик", False)],
  explanation="-A добавляет правило в конец цепочки. DROP в конце — это 'default deny': всё не разрешённое выше — блокируется.", order=2)

# ── Модуль 13: Производительность ─────────────────────────────────────────
m = module(c2, "Диагностика производительности системы", 3)
theory(m, "top, vmstat, iostat, strace — анализ производительности", """\
## Инструменты диагностики

### Нагрузка системы

```bash
top                  # интерактивный мониторинг (нажми 1 — по CPU)
htop                 # улучшенный (F5 — дерево процессов)
uptime               # load average
nproc                # количество CPU

# load average интерпретация (на 4 CPU):
# 4.0 = 100% загрузка, 8.0 = 200% (очередь)
```

### Память

```bash
free -h              # RAM и swap
cat /proc/meminfo    # подробно
vmstat 1 5           # статистика каждую секунду, 5 раз
# r=runqueue, b=blocked, swpd=swap, si/so=swap in/out
```

### Диски

```bash
iostat -x 1          # I/O статистика по устройствам
iostat -xd /dev/sda 1 # конкретное устройство
iotop                 # топ процессов по I/O (apt install iotop)

# Ключевые метрики iostat:
# %util — загрузка устройства (>80% = проблема)
# await — среднее время ожидания I/O (мс)
# r/s, w/s — операции чтения/записи в секунду
```

### Сеть

```bash
iftop                 # трафик по соединениям (apt install iftop)
nethogs               # трафик по процессам (apt install nethogs)
nload -i eth0         # трафик интерфейса
```

### Трассировка

```bash
strace -p 1234        # системные вызовы процесса
strace -e trace=network nginx  # только сетевые вызовы
strace -c command     # статистика вызовов
lsof -p 1234          # открытые файлы процесса
lsof -i :8080         # процесс на порту 8080
```

### Профилирование

```bash
perf top              # горячие функции CPU
perf record -g ./app  # запись профиля
perf report           # анализ
```

### Быстрая диагностика (USE method)

**Utilization, Saturation, Errors** для каждого ресурса:
- CPU: `top`, `vmstat`, `mpstat`
- Memory: `free`, `vmstat`
- Disk: `iostat`, `df`
- Network: `iftop`, `ss`
""", 1)

ql = quiz_lesson(m, "Тест: производительность", 2)
qz = quiz(ql)
Q(qz, "Load average 4.0 на 4-ядерном процессоре означает:",
  [("100% загрузку всех ядер", True), ("400% загрузку", False),
   ("Проблему, нужно немедленно реагировать", False), ("25% загрузку каждого ядра", False)],
  explanation="load average = количество ядер → 100% загрузка. 4.0 на 4 CPU = полная загрузка без очереди. >4.0 — есть очередь.")
Q(qz, "Какой инструмент показывает I/O операции по процессам в реальном времени?",
  [("iotop", True), ("iostat", False), ("iftop", False), ("htop", False)],
  explanation="iotop — аналог top, но для дисковых операций. iostat показывает статистику по устройствам, а не процессам.", order=2)

# ── Модуль 14: Безопасность ────────────────────────────────────────────────
m = module(c2, "Безопасность Linux: SSH и hardening", 4)
theory(m, "SSH hardening, ключи, fail2ban", """\
## Защита SSH-сервера

### Ключи SSH (вместо паролей)

```bash
# Генерация ключа на клиенте
ssh-keygen -t ed25519 -C "deploy@server"   # Ed25519 (рекомендуется)
ssh-keygen -t rsa -b 4096 -C "backup key"  # RSA если нужна совместимость

# Копирование ключа на сервер
ssh-copy-id user@server
# или вручную:
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```

### /etc/ssh/sshd_config — защита

```ini
# Изменить порт (скрыть от автоматических сканеров)
Port 2222

# Запретить вход root
PermitRootLogin no

# Только ключи, без паролей
PasswordAuthentication no
PubkeyAuthentication yes

# Разрешить только конкретных пользователей
AllowUsers deploy admin

# Таймаут сессии
ClientAliveInterval 300
ClientAliveCountMax 2

# Отключить X11 и forwarding если не нужны
X11Forwarding no
AllowAgentForwarding no
```

```bash
sshd -t              # проверить конфиг без применения
systemctl restart sshd
```

### fail2ban — защита от bruteforce

```bash
apt install fail2ban

# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 2222
maxretry = 5        # попыток до бана
bantime = 3600      # бан на 1 час
findtime = 600      # окно: 5 попыток за 10 минут

# Управление
fail2ban-client status
fail2ban-client status sshd
fail2ban-client set sshd unbanip 1.2.3.4
fail2ban-client banned
```

### Аудит безопасности

```bash
last                       # история входов
lastfail                   # неудачные попытки
who                        # текущие пользователи
grep "Failed" /var/log/auth.log | tail -20
ss -tulnp                  # открытые порты
find / -perm -4000 2>/dev/null  # SUID файлы
```
""", 1)

ql = quiz_lesson(m, "Тест: безопасность SSH", 2)
qz = quiz(ql)
Q(qz, "Какой алгоритм ключа SSH рекомендуется использовать сегодня?",
  [("Ed25519", True), ("RSA 1024", False), ("DSA", False), ("ECDSA 256", False)],
  explanation="Ed25519 — современный, быстрый и безопасный алгоритм. RSA 4096 — приемлем, RSA 1024 и DSA — устарели.")
Q(qz, "Что нужно настроить в sshd_config для запрета входа с паролем?",
  [("PasswordAuthentication no", True), ("AuthenticationMethod key", False),
   ("PasswordLogin no", False), ("UsePAM no", False)],
  explanation="PasswordAuthentication no отключает аутентификацию по паролю. Всегда проверьте что ключ работает перед этим!", order=2)
Q(qz, "fail2ban банит IP адрес после 5 попыток входа за 10 минут. Какие параметры это настраивают?",
  [("maxretry=5 и findtime=600", True), ("bantime=5 и maxretry=600", False),
   ("maxretry=5 и bantime=600", False), ("findtime=5 и bantime=600", False)],
  explanation="maxretry — количество попыток, findtime — временное окно (в секундах), bantime — длительность бана.", order=3)

# ── Модуль 15: Systemd углубленно ─────────────────────────────────────────
m = module(c2, "Systemd углубленно: unit-файлы и journald", 5)
theory(m, "Unit-файлы: зависимости, таргеты, socket activation", """\
## Systemd углубленно

### Типы юнитов

| Тип | Расширение | Назначение |
|---|---|---|
| Service | .service | Фоновые процессы |
| Timer | .timer | Cron-замена |
| Socket | .socket | Socket activation |
| Mount | .mount | Точки монтирования |
| Target | .target | Группировка юнитов |
| Path | .path | Реакция на изменение файлов |

### Зависимости

```ini
[Unit]
# После — запускаться после этих юнитов
After=network.target postgresql.service

# Требовать — запускать вместе, падать вместе
Requires=postgresql.service

# Хотеть — запускать вместе, но не падать
Wants=redis.service

# Конфликтовать — не запускаться вместе
Conflicts=apache2.service
```

### Timer (замена cron)

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup

[Timer]
OnCalendar=daily          # каждый день в полночь
OnCalendar=*-*-* 02:00:00 # в 2:00
RandomizedDelaySec=30m    # +/-30 минут
Persistent=true           # запустить если пропустили

[Install]
WantedBy=timers.target
```

```bash
systemctl enable --now backup.timer
systemctl list-timers     # все активные таймеры
```

### Ограничение ресурсов

```ini
[Service]
MemoryLimit=512M
CPUQuota=50%
LimitNOFILE=65535
LimitNPROC=512
```

### journald фильтрация

```bash
journalctl -u nginx --since "2024-01-01" --until "2024-01-02"
journalctl -u nginx -p err                    # только ошибки
journalctl -u nginx -o json | jq              # JSON формат
journalctl -u nginx -o short-iso             # с ISO timestamp
journalctl --identifier=myapp                # по syslog identifier
journalctl _PID=1234                          # по PID
journalctl _COMM=nginx                        # по имени команды
```
""", 1)

ql = quiz_lesson(m, "Тест: systemd advanced", 2)
qz = quiz(ql)
Q(qz, "Чем systemd timer лучше cron?",
  [("Логируется в journald, поддерживает зависимости, Persistent=true", True),
   ("Использует меньше памяти", False),
   ("Проще синтаксис", False),
   ("Работает без root", False)],
  explanation="Timer: интеграция с journald, зависимости между юнитами, Persistent=true запускает пропущенные задачи, точный учёт времени.")
Q(qz, "Какое ограничение в [Service] ограничивает CPU до 50%?",
  [("CPUQuota=50%", True), ("CPULimit=0.5", False), ("LimitCPU=50", False), ("CPUMax=50%", False)],
  explanation="CPUQuota задаётся в процентах. 50% = одно ядро на двухядерной системе, 200% = два ядра.", order=2)

lab(m, "Лабораторная: фильтрация journald логов", 6, 3)

# ── Модуль 16: Ядро Linux ─────────────────────────────────────────────────
m = module(c2, "Ядро Linux: sysctl и модули", 6)
theory(m, "sysctl — параметры ядра, модули, /proc и /sys", """\
## Параметры ядра Linux

### sysctl — изменение параметров ядра

```bash
sysctl -a                        # все параметры
sysctl net.ipv4.ip_forward       # прочитать параметр
sysctl -w net.ipv4.ip_forward=1  # установить (временно)
sysctl -p                        # применить /etc/sysctl.conf
```

### /etc/sysctl.conf — постоянные настройки

```ini
# ─── Сеть ───────────────────────────────────────────
# Включить IP Forwarding (для маршрутизаторов, VPN, Docker)
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1

# Защита от SYN-flood
net.ipv4.tcp_syncookies = 1

# Не отвечать на broadcast ping
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Очередь соединений (для высоконагруженных серверов)
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# TIME_WAIT — ускорить переиспользование портов
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30

# ─── Память ─────────────────────────────────────────
# Файловый кэш vs swap (0=никогда, 10=редко, 60=default)
vm.swappiness = 10

# Лимит открытых файлов
fs.file-max = 2097152

# Для Elasticsearch / Kafka
vm.max_map_count = 262144
```

### Модули ядра

```bash
lsmod                         # загруженные модули
modinfo overlay               # информация о модуле
modprobe overlay              # загрузить модуль
modprobe -r overlay           # выгрузить
echo "overlay" >> /etc/modules-load.d/k8s.conf  # автозагрузка
```

### /proc — виртуальная ФС ядра

```bash
cat /proc/cpuinfo             # информация о CPU
cat /proc/meminfo             # память
cat /proc/net/dev             # сетевые интерфейсы
cat /proc/1/environ           # окружение процесса PID 1
ls /proc/1/fd                 # открытые файлы процесса
cat /proc/sys/vm/swappiness   # то же что sysctl vm.swappiness
```
""", 1)

ql = quiz_lesson(m, "Тест: ядро Linux", 2)
qz = quiz(ql)
Q(qz, "Какой sysctl параметр включает IP Forwarding (нужен для Docker/K8s)?",
  [("net.ipv4.ip_forward = 1", True), ("net.ipv4.routing = 1", False),
   ("net.core.ip_forward = 1", False), ("ip.forward = enabled", False)],
  explanation="net.ipv4.ip_forward=1 разрешает ядру пересылать пакеты между интерфейсами. Обязателен для Docker bridge сетей.")
Q(qz, "Как сделать параметр sysctl постоянным после перезагрузки?",
  [("Добавить в /etc/sysctl.conf и выполнить sysctl -p", True),
   ("Добавить в /etc/rc.local", False),
   ("Только sysctl -w (всегда постоянен)", False),
   ("Создать systemd unit", False)],
  explanation="sysctl -w временный (до ребута). Для постоянного: записать в /etc/sysctl.conf или /etc/sysctl.d/*.conf.", order=2)

# ── Модуль 17: Troubleshooting ────────────────────────────────────────────
m = module(c2, "Troubleshooting и диагностика", 7)
theory(m, "Системный подход к диагностике проблем", """\
## Методология диагностики

### USE Method (Brendan Gregg)

Для каждого ресурса проверяй:
- **U**tilization — насколько занят ресурс?
- **S**aturation — есть ли очередь/ожидание?
- **E**rrors — есть ли ошибки?

### Чеклист при проблеме с сервером

```bash
# 1. Общая картина
uptime && w                    # нагрузка и пользователи
free -h                        # память
df -h                          # диски
systemctl list-units --failed  # упавшие сервисы

# 2. Топ процессов
top -bn1 | head -20            # CPU
iostat -x 1 3                  # I/O

# 3. Сеть
ss -s                          # статистика соединений
ss -tulnp                      # открытые порты

# 4. Логи
journalctl -p err --since "1 hour ago"
dmesg | tail -50               # ошибки ядра
```

### Типичные проблемы

**Сервер не отвечает на SSH:**
```bash
# Проверь: firewall, sshd статус, disk full
ping server && telnet server 22
df -h  # disk full = сервис не может писать логи
```

**Нет места на диске:**
```bash
df -h && du -sh /* 2>/dev/null | sort -rh | head -10
journalctl --disk-usage
docker system df  # docker слои
find / -size +500M 2>/dev/null
```

**Высокая нагрузка CPU:**
```bash
top -bn1 | grep -A 20 "PID"    # топ процессов
ps aux --sort=-%cpu | head -10
perf top -g                     # горячие функции
```

**OOM (Out of Memory):**
```bash
dmesg | grep -i "out of memory"
dmesg | grep "oom"
journalctl -k | grep "killed"
```

**Проблемы с сетью:**
```bash
ping 8.8.8.8      # интернет
ping gateway      # шлюз
nslookup google.com # DNS
traceroute google.com
```
""", 1)

ql = quiz_lesson(m, "Тест: troubleshooting", 2)
qz = quiz(ql)
Q(qz, "Сервер вдруг перестал принимать новые соединения. С чего начать диагностику?",
  [("Проверить df -h (disk full), ss -s (лимит соединений), journalctl -p err", True),
   ("Сразу перезапустить сервер", False),
   ("Удалить временные файлы в /tmp", False),
   ("Обновить ядро", False)],
  explanation="Disk full — частая причина: сервис не может писать логи и отказывает. ss -s покажет лимит соединений. journalctl — ошибки.")
Q(qz, "Как найти что занимает больше всего места в /var?",
  [("du -sh /var/* | sort -rh | head -10", True),
   ("df -h /var", False),
   ("ls -lS /var", False),
   ("find /var -size +1M", False)],
  explanation="du -sh суммирует размер директорий, sort -rh сортирует по убыванию в human-readable формате.", order=2)

# ── Модуль 18: Bash-скриптинг в Linux ────────────────────────────────────
m = module(c2, "Bash-скриптинг для автоматизации", 8)
theory(m, "Скрипты мониторинга и автоматизации", """\
## Практические Bash-скрипты

### Шаблон production-скрипта

```bash
#!/usr/bin/env bash
set -euo pipefail   # e=exit on error, u=unset vars error, o=pipefail
IFS=$'\\n\\t'       # безопасный IFS

# Переменные
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/myscript.log"

# Логирование
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
err() { log "ERROR: $*" >&2; }

# Trap для очистки
cleanup() { log "Cleanup..."; rm -f /tmp/script.lock; }
trap cleanup EXIT INT TERM

# Mutex (защита от параллельного запуска)
exec 200>/tmp/script.lock
flock -n 200 || { err "Already running"; exit 1; }

log "Script started"
```

### Мониторинг диска

```bash
#!/usr/bin/env bash
THRESHOLD=80
ALERT_EMAIL="admin@example.com"

df -h | awk 'NR>1 {
    gsub(/%/, "", $5)
    if ($5+0 > threshold+0) print $0
}' threshold=$THRESHOLD | while read line; do
    echo "DISK ALERT: $line" | mail -s "Disk Full Warning" "$ALERT_EMAIL"
done
```

### Резервное копирование

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/backup"
SOURCE_DIR="/var/www"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

# Создать архив
tar -czf "${BACKUP_DIR}/backup_${DATE}.tar.gz" "$SOURCE_DIR"

# Удалить старые бэкапы
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$KEEP_DAYS -delete

echo "Backup completed: backup_${DATE}.tar.gz"
```

### Проверка доступности сервисов

```bash
#!/usr/bin/env bash
SERVICES=("nginx" "postgresql" "redis")
FAILED=0

for svc in "${SERVICES[@]}"; do
    if ! systemctl is-active --quiet "$svc"; then
        echo "FAILED: $svc"
        systemctl start "$svc" && echo "Restarted: $svc"
        FAILED=$((FAILED+1))
    fi
done

exit $FAILED
```
""", 1)

ql = quiz_lesson(m, "Тест: bash-скриптинг", 2)
qz = quiz(ql)
Q(qz, "Что делает 'set -euo pipefail' в начале bash-скрипта?",
  [("Завершает скрипт при ошибке, обращении к неустановленной переменной, и при ошибке в пайпе", True),
   ("Включает режим отладки", False),
   ("Запускает скрипт в безопасном режиме без изменений", False),
   ("Устанавливает переменную IFS", False)],
  explanation="-e: exit on error, -u: unset variable error, -o pipefail: ошибка в любой части pipe = ошибка команды. Стандарт для prod-скриптов.")
Q(qz, "Как защитить скрипт от параллельного запуска?",
  [("flock -n /tmp/script.lock", True), ("mutex script.sh", False),
   ("lock script.sh", False), ("pidfile script.pid", False)],
  explanation="flock создаёт файловую блокировку. -n = non-blocking: если уже заблокировано — сразу вернёт ошибку.", order=2)

# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 3 — Bash-скриптинг
# ═══════════════════════════════════════════════════════════════════════════ #
c3 = course(
    "bash-scripting",
    "Bash-скриптинг",
    "От переменных до production-скриптов. Автоматизация задач, обработка данных, "
    "работа с файлами, функции, регулярные выражения и обработка ошибок.",
    "📜", "intermediate", "linux", 30, 700, prereqs=[1],
)

# ── Модуль 19: Основы Bash ────────────────────────────────────────────────
m = module(c3, "Переменные и типы данных", 1)
theory(m, "Переменные, кавычки и подстановка", """\
## Переменные в Bash

### Объявление и использование

```bash
name="DevOps"               # присваивание (без пробелов вокруг =!)
echo $name                  # вывод
echo "${name}"              # безопаснее (явные границы)
echo "${name}Engineer"      # → DevOpsEngineer

readonly PI=3.14            # константа
unset name                  # удалить переменную

# Специальные переменные
echo $0    # имя скрипта
echo $1    # первый аргумент
echo $@    # все аргументы (список)
echo $#    # количество аргументов
echo $?    # код выхода последней команды
echo $$    # PID текущего процесса
echo $!    # PID последнего фонового процесса
```

### Кавычки

```bash
name="World"

echo "Hello $name"      # → Hello World  (интерполяция)
echo 'Hello $name'      # → Hello $name  (без интерполяции)
echo "It's a \"test\""  # → It's a "test" (экранирование)
```

### Подстановка команд

```bash
now=$(date +%Y-%m-%d)     # выполнить команду, результат в переменную
files=$(ls /etc/*.conf | wc -l)
echo "Config files: $files"

# Вложенная подстановка
outer=$(echo "inner: $(date)")
```

### Арифметика

```bash
a=10; b=3
echo $((a + b))         # 13
echo $((a * b))         # 30
echo $((a / b))         # 3 (целочисленное!)
echo $((a % b))         # 1 (остаток)
echo $((a ** 2))        # 100

((count++))             # инкремент
((total += 5))          # добавить 5

# bc — дробные числа
echo "scale=2; 10/3" | bc   # → 3.33
```

### Переменные окружения

```bash
export PATH="$PATH:/opt/myapp/bin"   # добавить в PATH
export MY_VAR="value"                 # экспортировать для дочерних процессов
env                                   # все переменные окружения
printenv MY_VAR                       # значение переменной
```
""", 1)

theory(m, "Условия и циклы", """\
## Управляющие конструкции

### if / elif / else

```bash
# Числа
if [ $x -eq 10 ]; then echo "равно"; fi
if [ $x -ne 10 ]; then echo "не равно"; fi
if [ $x -lt 10 ]; then echo "меньше"; fi
if [ $x -le 10 ]; then echo "меньше или равно"; fi
if [ $x -gt 10 ]; then echo "больше"; fi

# Строки
if [ "$str" = "hello" ]; then ...
if [ "$str" != "hello" ]; then ...
if [ -z "$str" ]; then echo "пустая строка"; fi
if [ -n "$str" ]; then echo "непустая строка"; fi

# Файлы
if [ -f file.txt ]; then echo "файл существует"; fi
if [ -d /tmp ]; then echo "директория"; fi
if [ -r file ]; then echo "есть право чтения"; fi
if [ -x script.sh ]; then echo "исполняемый"; fi
if [ file1 -nt file2 ]; then echo "file1 новее"; fi

# [[ — расширенные условия (bash)
if [[ "$str" =~ ^[0-9]+$ ]]; then echo "только цифры"; fi
if [[ -f file && -r file ]]; then echo "файл и читаем"; fi
```

### Циклы

```bash
# for по списку
for item in a b c d; do
    echo "$item"
done

# for по файлам
for file in /etc/*.conf; do
    echo "Config: $file"
done

# for C-style
for ((i=0; i<10; i++)); do
    echo $i
done

# while
count=0
while [ $count -lt 5 ]; do
    echo $count
    ((count++))
done

# until (противоположность while)
until ping -c1 server 2>/dev/null; do
    echo "Waiting for server..."
    sleep 5
done

# Итерация по строкам файла
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt
```

### case

```bash
case "$1" in
    start)   echo "Starting..." ;;
    stop)    echo "Stopping..." ;;
    restart) stop; start ;;
    *)       echo "Usage: $0 {start|stop|restart}"; exit 1 ;;
esac
```
""", 2)

ql = quiz_lesson(m, "Тест: переменные и условия", 3)
qz = quiz(ql)
Q(qz, "Как правильно объявить переменную в bash?",
  [('name="DevOps"', True), ('name = "DevOps"', False),
   ('$name="DevOps"', False), ('set name="DevOps"', False)],
  explanation='В bash пробелы вокруг = недопустимы при присваивании — это воспринимается как команда name с аргументами.')
Q(qz, "Что вернёт $? после успешно выполненной команды?",
  [("0", True), ("1", False), ("true", False), ("success", False)],
  explanation="По соглашению Unix: 0 = успех, любое другое число = ошибка. Это основа обработки ошибок в скриптах.", order=2)
Q(qz, "Как проверить что переменная НЕ пустая?",
  [('[ -n "$var" ]', True), ('[ -z "$var" ]', False),
   ('[ "$var" ]', True), ('[ !empty "$var" ]', False)],
  qtype="multi",
  explanation="-n (non-zero): непустая строка → true. [ \"$var\" ] без флага также возвращает true если строка непустая.", order=3)

# ── Модуль 20: Функции ────────────────────────────────────────────────────
m = module(c3, "Функции и аргументы", 2)
theory(m, "Функции: объявление, аргументы, возвращаемые значения", """\
## Функции в Bash

### Объявление

```bash
# Два способа объявления:
greet() {
    echo "Hello, $1!"
}

function greet {
    echo "Hello, $1!"
}

greet "DevOps"   # → Hello, DevOps!
```

### Аргументы функции

```bash
deploy() {
    local app="$1"       # local — переменная только внутри функции
    local env="${2:-production}"  # значение по умолчанию

    echo "Deploying $app to $env"
    echo "Args count: $#"
    echo "All args: $@"
}

deploy "myapp"          # → Deploying myapp to production
deploy "myapp" "staging" # → Deploying myapp to staging
```

### Возвращаемые значения

```bash
# return возвращает только числа 0-255 (exit code)
is_running() {
    pgrep -x "$1" > /dev/null
    return $?     # 0 = найден, 1 = не найден
}

if is_running nginx; then
    echo "nginx is running"
fi

# Для возврата строк — используй echo + подстановку команды
get_ip() {
    hostname -I | awk '{print $1}'
}

my_ip=$(get_ip)
echo "My IP: $my_ip"
```

### Практический пример

```bash
#!/usr/bin/env bash
set -euo pipefail

log()  { echo "[INFO]  $*"; }
err()  { echo "[ERROR] $*" >&2; }
die()  { err "$*"; exit 1; }

require_root() {
    [[ $EUID -eq 0 ]] || die "This script must be run as root"
}

check_command() {
    command -v "$1" &>/dev/null || die "Required command not found: $1"
}

# Использование
require_root
check_command docker
check_command git
log "All checks passed"
```
""", 1)

theory(m, "Массивы и строковые операции", """\
## Массивы

```bash
# Индексируемые массивы
fruits=("apple" "banana" "cherry")
fruits[3]="date"

echo "${fruits[0]}"       # первый элемент
echo "${fruits[@]}"       # все элементы
echo "${#fruits[@]}"      # количество элементов
echo "${!fruits[@]}"      # индексы

# Итерация
for fruit in "${fruits[@]}"; do
    echo "$fruit"
done

# Добавление
fruits+=("elderberry")

# Срез
echo "${fruits[@]:1:2}"   # элементы с индекса 1, 2 штуки
```

### Ассоциативные массивы (bash 4+)

```bash
declare -A config
config["host"]="localhost"
config["port"]="5432"
config["db"]="mydb"

echo "${config[host]}"
for key in "${!config[@]}"; do
    echo "$key = ${config[$key]}"
done
```

## Строковые операции

```bash
str="Hello, DevOps World!"

echo "${#str}"              # длина → 21
echo "${str,,}"             # нижний регистр
echo "${str^^}"             # верхний регистр
echo "${str:7:6}"           # подстрока: позиция 7, длина 6 → DevOps
echo "${str/DevOps/Linux}"  # замена первого вхождения
echo "${str//o/0}"          # замена всех вхождений

# Обрезка
file="/path/to/script.sh"
echo "${file##*/}"      # → script.sh (удалить всё до последнего /)
echo "${file%/*}"       # → /path/to  (удалить от последнего /)
echo "${file%.sh}"      # → /path/to/script (удалить суффикс)
echo "${file#/}"        # → path/to/script.sh (удалить первый /)

# Проверка
[[ "$str" == *"DevOps"* ]] && echo "contains DevOps"
[[ "$str" =~ ^Hello ]] && echo "starts with Hello"
```
""", 2)

ql = quiz_lesson(m, "Тест: функции и массивы", 3)
qz = quiz(ql)
Q(qz, "Почему важно использовать 'local' внутри функций?",
  [("Переменная не будет изменять глобальные переменные с тем же именем", True),
   ("Ускоряет выполнение функции", False),
   ("Делает переменную доступной вне функции", False),
   ("Позволяет использовать массивы", False)],
  explanation="local ограничивает область видимости переменной функцией. Без него переменная меняет глобальный контекст — частый источник ошибок.")
Q(qz, "Как получить количество элементов массива arr?",
  [("${#arr[@]}", True), ("${arr.length}", False), ("count arr", False), ("${arr[count]}", False)],
  explanation="${#arr[@]} — стандартный способ получить длину массива. # — оператор длины в bash.", order=2)

# ── Модуль 21: Обработка ошибок ───────────────────────────────────────────
m = module(c3, "Обработка ошибок и надёжность скриптов", 3)
theory(m, "set -euo pipefail, trap, exit codes", """\
## Надёжные скрипты

### Exit codes — коды возврата

```bash
# Соглашение:
# 0 = успех
# 1 = общая ошибка
# 2 = неправильное использование команды
# 126 = нет прав на выполнение
# 127 = команда не найдена
# 130 = прерван Ctrl+C

exit 0    # успех
exit 1    # ошибка

# Последний exit code
grep "error" file.log
echo $?   # 0 = найдено, 1 = не найдено
```

### set -euo pipefail

```bash
set -e          # выйти при первой ошибке
set -u          # ошибка при использовании неустановленной переменной
set -o pipefail # ошибка в пайпе = ошибка всей команды
set -x          # отладка: печатать каждую команду перед выполнением

# Отключить для блока:
set +e
risky_command || true    # или так — явно игнорировать ошибку
set -e

# Условное выполнение
command || { echo "Failed"; exit 1; }
command && echo "Success"
```

### trap — перехват событий

```bash
cleanup() {
    echo "Cleaning up..."
    rm -f /tmp/myapp.tmp
    kill $BACKGROUND_PID 2>/dev/null || true
}

# Выполнить cleanup при выходе (нормальном или по ошибке)
trap cleanup EXIT

# Обработать Ctrl+C
trap 'echo "Interrupted!"; exit 130' INT

# Обработать kill
trap 'echo "Terminated!"; cleanup; exit 143' TERM

# Временно отключить trap
trap - EXIT
```

### Валидация аргументов

```bash
usage() {
    echo "Usage: $0 <environment> <version>"
    echo "  environment: production|staging|dev"
    echo "  version:     semver (e.g. 1.2.3)"
    exit 1
}

[[ $# -ne 2 ]] && usage

ENV="$1"
VERSION="$2"

# Проверка допустимых значений
[[ "$ENV" =~ ^(production|staging|dev)$ ]] || {
    echo "Invalid environment: $ENV"
    usage
}

# Проверка формата semver
[[ "$VERSION" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+$ ]] || {
    echo "Invalid version format: $VERSION"
    usage
}
```
""", 1)

ql = quiz_lesson(m, "Тест: обработка ошибок", 2)
qz = quiz(ql)
Q(qz, "Что делает 'trap cleanup EXIT' в скрипте?",
  [("Вызывает функцию cleanup при любом выходе из скрипта", True),
   ("Завершает скрипт при ошибке в cleanup", False),
   ("Перехватывает только сигнал SIGTERM", False),
   ("Регистрирует cleanup как cron-задачу", False)],
  explanation="EXIT — специальный сигнал bash, срабатывающий при любом выходе (нормальный, ошибка, сигнал). Идеален для очистки ресурсов.")
Q(qz, "Скрипт: 'cmd1 | cmd2'. cmd1 упала. Что вернёт echo $? без pipefail?",
  [("0 если cmd2 успешна (exit code cmd2)", True),
   ("Ошибку cmd1", False),
   ("1 всегда", False),
   ("Код ошибки cmd1", False)],
  explanation="Без pipefail exit code пайпа = exit code ПОСЛЕДНЕЙ команды. -o pipefail делает ошибку в любой части пайпа = ошибка пайпа.", order=2)

# ── Модуль 22: Regex и текст ──────────────────────────────────────────────
m = module(c3, "Регулярные выражения и обработка текста", 4)
theory(m, "Regex, grep, sed, awk — продвинутая обработка текста", """\
## Регулярные выражения

### Основной синтаксис

```
.       → любой символ
*       → 0 или более предыдущего
+       → 1 или более (ERE)
?       → 0 или 1 (ERE)
^       → начало строки
$       → конец строки
[abc]   → один из символов
[^abc]  → не один из этих
[a-z]   → диапазон
\\d     → цифра (в PCRE)
\\w     → слово-символ [a-zA-Z0-9_]
\\s     → пробел, таб
{n,m}   → от n до m повторений (ERE)
(...)   → группа
|       → или (ERE)
```

### grep с regex

```bash
# BRE (Basic)
grep "^error" file.txt           # строки начинающиеся с "error"
grep "\.log$" file.txt           # строки заканчивающиеся на .log
grep "[0-9]\\{3\\}" file.txt     # ровно 3 цифры

# ERE (Extended) — grep -E или egrep
grep -E "error|warn|crit" file.txt
grep -E "^[0-9]{1,3}\\.[0-9]{1,3}" file.txt  # IP-подобные
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}" file.txt  # email

# PCRE — grep -P
grep -P "\\d{4}-\\d{2}-\\d{2}" file.txt  # дата YYYY-MM-DD
```

### Примеры из DevOps-практики

```bash
# Извлечь IP из логов
grep -oE "\\b([0-9]{1,3}\\.){3}[0-9]{1,3}\\b" access.log | sort -u

# HTTP статусы 5xx
grep -E '" 5[0-9]{2} ' access.log

# Строки с временем > 1000ms
grep -E "\\s[0-9]{4,}ms" access.log

# Извлечь значения из config
grep -oP 'port = \\K[0-9]+' config.ini

# sed с группами
echo "2024-01-15" | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\\3.\\2.\\1/'
# → 15.01.2024

# awk с regex
awk '/WARN|ERROR/ {print NR": "$0}' app.log
```
""", 1)

ql = quiz_lesson(m, "Тест: regex и обработка текста", 2)
qz = quiz(ql)
Q(qz, "Что соответствует регулярному выражению ^[0-9]+$?",
  [("Строка состоящая только из цифр", True),
   ("Строка начинающаяся с цифры", False),
   ("Строка содержащая хотя бы одну цифру", False),
   ("Строка между 0 и 9", False)],
  explanation="^$ — якоря начала и конца строки. [0-9]+ — одна или более цифр. Вместе: строка целиком из цифр.")
Q(qz, "Как извлечь только совпадающую часть (не всю строку) с grep?",
  [("grep -o", True), ("grep -m", False), ("grep -x", False), ("grep -e", False)],
  explanation="grep -o (only) выводит только совпавшую часть, а не всю строку. Незаменимо для парсинга данных.", order=2)

# ── Модуль 23: Практические скрипты ──────────────────────────────────────
m = module(c3, "Практические скрипты DevOps", 5)
theory(m, "Реальные скрипты: деплой, мониторинг, резервное копирование", """\
## Production-скрипты

### Деплой с нулевым временем простоя

```bash
#!/usr/bin/env bash
set -euo pipefail

APP="myapp"
DEPLOY_DIR="/opt/${APP}"
BACKUP_DIR="/opt/${APP}_backup"
NEW_RELEASE="$1"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Проверки
[[ $# -ne 1 ]] && { echo "Usage: $0 <version>"; exit 1; }
[[ -d "$DEPLOY_DIR" ]] || { log "Deploy dir not found"; exit 1; }

log "Starting deploy: $NEW_RELEASE"

# Backup
log "Creating backup..."
cp -r "$DEPLOY_DIR" "$BACKUP_DIR"

# Deploy
log "Deploying..."
tar -xzf "${NEW_RELEASE}.tar.gz" -C "$DEPLOY_DIR" --strip-components=1

# Migrate
log "Running migrations..."
cd "$DEPLOY_DIR"
./venv/bin/python manage.py migrate --noinput

# Reload (zero-downtime с gunicorn)
log "Reloading gunicorn..."
kill -HUP $(cat /tmp/gunicorn.pid)

log "Deploy complete!"

# Rollback при ошибке (через trap)
rollback() {
    log "ROLLING BACK..."
    cp -r "$BACKUP_DIR" "$DEPLOY_DIR"
    systemctl restart myapp
}
trap rollback ERR
```

### Мониторинг и алертинг

```bash
#!/usr/bin/env bash
# Проверка сервисов и отправка алерта в Telegram

BOT_TOKEN="your_token"
CHAT_ID="your_chat_id"

send_alert() {
    local msg="$1"
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \\
        -d "chat_id=${CHAT_ID}&text=${msg}&parse_mode=HTML" > /dev/null
}

check_service() {
    local name="$1"
    local url="$2"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url")
    if [[ "$code" != "200" ]]; then
        send_alert "🚨 <b>DOWN</b>: ${name} returned HTTP ${code}"
        return 1
    fi
}

check_service "API" "https://api.myapp.com/health"
check_service "Frontend" "https://myapp.com"
```
""", 1)

ql = quiz_lesson(m, "Тест: практические скрипты", 2)
qz = quiz(ql)
Q(qz, "Как реализовать автоматический откат при ошибке в bash-скрипте?",
  [("trap rollback ERR", True), ("catch rollback", False), ("on_error rollback", False), ("if $? != 0; rollback; fi", False)],
  explanation="trap rollback ERR выполняет функцию rollback при любой ошибке (ERR сигнал). Работает с set -e.")
Q(qz, "Как получить HTTP статус-код через curl без загрузки тела ответа?",
  [('curl -s -o /dev/null -w "%{http_code}" URL', True),
   ("curl --status URL", False),
   ("curl -I URL | grep HTTP", True),
   ("curl --code URL", False)],
  qtype="multi",
  explanation="-o /dev/null отбрасывает тело, -w форматирует вывод. curl -I запрашивает только заголовки (HEAD-запрос).", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 4 — Git & GitHub
# ═══════════════════════════════════════════════════════════════════════════ #
c4 = course(
    "git-github",
    "Git & GitHub",
    "Система контроля версий с нуля до профессионального уровня. "
    "Ветки, слияния, конфликты, Pull Requests, Git Flow и основы GitOps.",
    "🌿", "beginner", "devops", 20, 600,
)

# ── Модуль 24: Git основы ─────────────────────────────────────────────────
m = module(c4, "Git: основы и первые коммиты", 1)
theory(m, "Что такое Git: init, add, commit, status", """\
## Git — система контроля версий

Git отслеживает изменения в файлах и позволяет вернуться к любому состоянию.

### Первоначальная настройка

```bash
git config --global user.name "Ivan Petrov"
git config --global user.email "ivan@example.com"
git config --global init.defaultBranch main
git config --global core.editor "nano"
git config --list                    # посмотреть все настройки
```

### Создание репозитория

```bash
git init myproject        # новый репозиторий
cd myproject

# или клонировать существующий
git clone https://github.com/org/repo.git
git clone git@github.com:org/repo.git  # по SSH (рекомендуется)
```

### Базовый рабочий цикл

```
Working Directory → Staging Area → Repository
     (изменения)     (git add)    (git commit)
```

```bash
git status                    # состояние рабочей директории
git add file.txt              # добавить файл в staging
git add .                     # добавить все изменения
git add -p                    # интерактивно выбрать изменения
git commit -m "feat: add login endpoint"
git commit --amend            # изменить последний коммит (до push!)
```

### .gitignore

```gitignore
# Зависимости
node_modules/
__pycache__/
*.pyc
venv/

# Окружение
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp

# Сборки
dist/
build/
*.log
```

```bash
git rm --cached file.txt  # убрать из git, оставить локально
```
""", 1)

theory(m, "История: log, diff, show, blame", """\
## Просмотр истории

### git log

```bash
git log                          # полная история
git log --oneline                # одна строка на коммит
git log --oneline --graph --all  # граф всех веток
git log -10                      # последние 10 коммитов
git log --author="Ivan"          # фильтр по автору
git log --since="2 weeks ago"    # за последние 2 недели
git log -- path/to/file          # история конкретного файла
git log --grep="fix"             # поиск в сообщениях коммитов
```

### git diff

```bash
git diff                         # изменения не в staging
git diff --staged                # изменения в staging (перед коммитом)
git diff HEAD~1                  # сравнить с предыдущим коммитом
git diff main..feature           # сравнить ветки
git diff abc123 def456           # сравнить два коммита
git diff --stat                  # только статистика (файлы, строки)
```

### git show / blame

```bash
git show abc1234                 # содержимое коммита
git show HEAD:file.txt           # файл в текущем состоянии
git show HEAD~2:file.txt         # файл 2 коммита назад

git blame file.txt               # кто и когда изменил каждую строку
git blame -L 10,20 file.txt      # только строки 10-20
```

### Ссылки на коммиты

```
HEAD        → текущий коммит
HEAD~1      → предыдущий (= HEAD^)
HEAD~3      → 3 коммита назад
abc1234     → конкретный коммит по хэшу (достаточно первых 7 символов)
main@{3}    → ветка main 3 позиции назад
```
""", 2)

ql = quiz_lesson(m, "Тест: основы Git", 3)
qz = quiz(ql)
Q(qz, "В каком порядке файл попадает в коммит?",
  [("Working Dir → git add → Staging → git commit → Repository", True),
   ("Working Dir → git commit → Repository", False),
   ("Staging → git add → Working Dir → git commit", False),
   ("git init → git add → Working Dir → git commit", False)],
  explanation="Git трёхзонная модель: рабочая директория → индекс (staging, git add) → репозиторий (git commit).")
Q(qz, "Как посмотреть изменения которые УЖЕ добавлены в staging (git add)?",
  [("git diff --staged", True), ("git diff", False), ("git status --diff", False), ("git show --staged", False)],
  explanation="git diff показывает изменения НЕ в staging. git diff --staged (или --cached) — изменения которые войдут в следующий коммит.", order=2)
Q(qz, "HEAD~3 означает:",
  [("Коммит на 3 позиции раньше текущего", True), ("Третья ветка", False),
   ("Третий файл в коммите", False), ("Коммит с хэшем начинающимся на 3", False)],
  explanation="HEAD — текущий коммит. HEAD~N — N коммитов назад по линии первых родителей.", order=3)

# ── Модуль 25: Ветки ──────────────────────────────────────────────────────
m = module(c4, "Ветки и слияние", 2)
theory(m, "branch, checkout, merge — работа с ветками", """\
## Ветки в Git

Ветка — это просто указатель на коммит. Создание ветки — мгновенная операция.

### Создание и переключение

```bash
git branch feature/login         # создать ветку
git checkout feature/login       # переключиться
git checkout -b feature/login    # создать + переключиться (одна команда)
git switch -c feature/login      # современный синтаксис (git 2.23+)

git branch                       # список локальных веток
git branch -a                    # все ветки (включая remote)
git branch -d feature/login      # удалить ветку (слитую)
git branch -D feature/login      # принудительно удалить
git branch -m old-name new-name  # переименовать
```

### Слияние (merge)

```bash
# Слить feature в main:
git checkout main
git merge feature/login

# Типы слияний:
# Fast-forward: main просто перемещается вперёд (нет дивергенции)
# 3-way merge: создаётся merge-коммит (ветки разошлись)

git merge --no-ff feature/login  # всегда создавать merge-коммит
git merge --squash feature/login # все коммиты → один (без истории ветки)
git merge --abort                # отменить слияние (при конфликте)
```

### Разрешение конфликтов

```bash
# При конфликте Git помечает файлы:
<<<<<<< HEAD
код из текущей ветки (main)
=======
код из сливаемой ветки (feature)
>>>>>>> feature/login

# 1. Открыть файл и разрешить вручную
# 2. git add file_with_conflict.py
# 3. git commit
```

### rebase — переписать историю

```bash
git checkout feature
git rebase main          # перенести коммиты feature на вершину main
git rebase -i HEAD~3     # интерактивный rebase: squash, reword, drop

# rebase vs merge:
# merge — сохраняет историю ветвления
# rebase — линейная история, чище для review
```
""", 1)

ql = quiz_lesson(m, "Тест: ветки и слияние", 2)
qz = quiz(ql)
Q(qz, "Какая команда создаёт ветку И сразу переключается на неё?",
  [("git checkout -b feature", True), ("git branch -c feature", False),
   ("git switch feature", False), ("git branch feature && git checkout feature", True)],
  qtype="multi",
  explanation="git checkout -b и современный git switch -c делают то же самое: создают + переключают.")
Q(qz, "Чем rebase отличается от merge?",
  [("rebase создаёт линейную историю, переписывая коммиты; merge сохраняет граф ветвления", True),
   ("rebase быстрее merge", False),
   ("merge работает только с remote ветками", False),
   ("rebase нельзя использовать в команде", False)],
  explanation="rebase 'перекладывает' коммиты на новое основание. История чище, но НЕЛЬЗЯ rebase-ить опубликованные (pushed) коммиты!", order=2)

# ── Модуль 26: Remote ─────────────────────────────────────────────────────
m = module(c4, "Remote-репозитории и GitHub", 3)
theory(m, "remote, push, pull, fetch — работа с сервером", """\
## Remote-репозитории

### Настройка remote

```bash
git remote -v                           # список remote
git remote add origin git@github.com:user/repo.git
git remote set-url origin NEW_URL       # изменить URL
git remote remove origin                # удалить remote
```

### Отправка и получение изменений

```bash
git push origin main                    # отправить ветку main
git push -u origin feature/login        # -u = upstream (запомнить remote)
git push                                # после -u можно без аргументов
git push --force-with-lease             # force push с защитой (лучше --force)

git fetch origin                        # скачать изменения (без merge)
git pull                                # = fetch + merge
git pull --rebase                       # = fetch + rebase (чище история)
git pull origin main                    # явно указать remote и ветку
```

### Отслеживание remote-веток

```bash
git branch -u origin/main main         # связать локальную с remote
git branch -vv                          # статус всех веток
git remote show origin                  # подробная информация о remote
```

### Теги

```bash
git tag v1.0.0                          # annotated tag
git tag -a v1.0.0 -m "Release 1.0.0"   # с сообщением
git push origin v1.0.0                  # опубликовать тег
git push origin --tags                  # все теги
git tag -d v1.0.0                       # удалить локально
git push origin --delete v1.0.0         # удалить remote
```

### SSH-ключи для GitHub

```bash
ssh-keygen -t ed25519 -C "github@example.com"
cat ~/.ssh/id_ed25519.pub   # скопировать и добавить в GitHub Settings → SSH Keys
ssh -T git@github.com       # проверить подключение
```
""", 1)

theory(m, "Pull Requests, Code Review, GitHub Actions basics", """\
## GitHub: совместная работа

### Pull Request (PR)

1. Создать ветку: `git checkout -b feature/my-feature`
2. Сделать коммиты
3. Запушить: `git push -u origin feature/my-feature`
4. Открыть PR на GitHub
5. Code Review
6. Merge

### Шаблон коммит-сообщения (Conventional Commits)

```
<тип>(<область>): <краткое описание>

[опциональное тело]

[опциональные сноски]
```

**Типы:**
- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — документация
- `refactor:` — рефакторинг
- `test:` — тесты
- `chore:` — служебные задачи (CI, зависимости)
- `perf:` — оптимизация

```
feat(auth): add JWT refresh token rotation

Implemented automatic token rotation on refresh.
Old tokens are invalidated after rotation.

Closes #123
```

### .github/workflows: первый взгляд

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

### GitHub CLI

```bash
gh pr create --title "feat: add feature" --body "Description"
gh pr list
gh pr merge 42 --squash
gh issue create --title "Bug: ..." --body "Steps to reproduce..."
gh repo clone org/repo
```
""", 2)

ql = quiz_lesson(m, "Тест: remote и GitHub", 3)
qz = quiz(ql)
Q(qz, "В чём разница между git fetch и git pull?",
  [("fetch только скачивает изменения; pull скачивает И сливает в текущую ветку", True),
   ("fetch работает быстрее", False),
   ("pull скачивает только последний коммит", False),
   ("fetch нельзя использовать без remote", False)],
  explanation="fetch безопасен: обновляет remote-tracking ветки без изменения рабочей директории. pull = fetch + merge/rebase.")
Q(qz, "Какой тип Conventional Commit использовать для исправления бага?",
  [("fix:", True), ("bug:", False), ("patch:", False), ("hotfix:", False)],
  explanation="Conventional Commits: feat (новое), fix (баг), docs, refactor, test, chore, perf. Используется для автогенерации changelog.", order=2)

# ── Модуль 27: Git Flow ───────────────────────────────────────────────────
m = module(c4, "Стратегии ветвления и Git Flow", 4)
theory(m, "Git Flow, GitHub Flow, trunk-based development", """\
## Стратегии ветвления

### Git Flow (Vincent Driessen)

```
main ──────────────────────────────── v1.0 ── v1.1
        │                               │
develop ┼───────────────────────────────┤
        │                               │
feature/x ─────── merge                 │
                                        │
release/1.0 ───── QA ──── merge ────────┤
                                        │
hotfix/critical ──────────── merge ─────┘
```

**Ветки:**
- `main` — только production-ready код, всегда стабильный
- `develop` — основная ветка разработки
- `feature/*` — новые функции (от develop)
- `release/*` — подготовка релиза (багфиксы, версия)
- `hotfix/*` — срочные исправления в production (от main)

```bash
# Git Flow CLI
apt install git-flow
git flow init
git flow feature start my-feature
git flow feature finish my-feature
git flow release start 1.0.0
git flow release finish 1.0.0
```

### GitHub Flow (упрощённый)

```
main ─────────────── PR ──── merge ──── deploy
           │                     │
feature ───┘                     │
```

1. `main` всегда деплоится
2. Новая ветка для каждой задачи
3. Коммиты + PR
4. Review + merge → автодеплой

**Когда использовать:** continuous delivery, небольшие команды.

### Trunk-Based Development

- Все разработчики коммитят в `main` (trunk)
- Очень маленькие коммиты (несколько раз в день)
- Feature Flags для скрытия незавершённых функций
- Обязательные CI-тесты перед merge

**Когда использовать:** Google, Facebook стиль. Высокая скорость + зрелый CI/CD.

### Полезные команды

```bash
git stash                 # временно сохранить изменения
git stash pop             # восстановить
git stash list            # список stash
git cherry-pick abc1234   # перенести коммит в текущую ветку
git bisect start          # бинарный поиск коммита с багом
git bisect good v1.0
git bisect bad HEAD
```
""", 1)

ql = quiz_lesson(m, "Тест: стратегии ветвления", 2)
qz = quiz(ql)
Q(qz, "В Git Flow, от какой ветки создаётся hotfix?",
  [("main", True), ("develop", False), ("release", False), ("feature", False)],
  explanation="hotfix создаётся от main (production) и сливается обратно в main И develop. Это позволяет чинить production не трогая develop.")
Q(qz, "Что такое Feature Flags в контексте trunk-based development?",
  [("Механизм включения/выключения функций без деплоя нового кода", True),
   ("Git теги для feature-веток", False),
   ("Флаги сборки в Makefile", False),
   ("Разрешения на создание веток в GitHub", False)],
  explanation="Feature flags позволяют коммитить незавершённый код в main, но скрывать его за условием. Основа trunk-based development.", order=2)

# ── Модуль 28: Advanced Git ───────────────────────────────────────────────
m = module(c4, "Продвинутые возможности Git", 5)
theory(m, "reflog, submodules, hooks, worktree", """\
## Продвинутый Git

### reflog — история всех действий

```bash
git reflog              # все изменения HEAD (даже удалённые ветки!)
git checkout HEAD@{5}   # вернуться к состоянию 5 действий назад

# Восстановить удалённую ветку:
git reflog | grep "feature/deleted"
git checkout -b feature/deleted abc1234
```

### Git Hooks — автоматизация

```bash
ls .git/hooks/          # примеры хуков (*.sample)
```

```bash
# .git/hooks/pre-commit (chmod +x)
#!/bin/sh
# Запрет коммита файлов с секретами
if grep -r "password\s*=" --include="*.py" .; then
    echo "ERROR: Possible credentials detected!"
    exit 1
fi

# .git/hooks/commit-msg
#!/bin/sh
# Проверка формата сообщения (Conventional Commits)
if ! grep -qE "^(feat|fix|docs|chore|refactor|test|perf):" "$1"; then
    echo "ERROR: Commit message must follow Conventional Commits"
    exit 1
fi
```

### Submodules

```bash
# Добавить библиотеку как подмодуль
git submodule add https://github.com/org/lib.git libs/lib
git submodule update --init --recursive   # после clone
git submodule update --remote              # обновить до последнего
```

### git worktree — несколько рабочих директорий

```bash
git worktree add ../hotfix hotfix/critical  # вторая рабочая директория
git worktree list
git worktree remove ../hotfix
```

### Полезные алиасы

```bash
git config --global alias.lg "log --oneline --graph --all --decorate"
git config --global alias.st "status -s"
git config --global alias.co "checkout"
git config --global alias.unstage "reset HEAD --"
```
""", 1)

ql = quiz_lesson(m, "Тест: продвинутый Git", 2)
qz = quiz(ql)
Q(qz, "Для чего используется git reflog?",
  [("Восстановить удалённые коммиты или ветки, посмотреть историю всех действий", True),
   ("Показать remote-репозитории", False),
   ("Сравнить ветки", False),
   ("Сбросить все изменения", False)],
  explanation="reflog — спасательный круг Git. Записывает все изменения HEAD, даже после reset --hard или удаления ветки.")
Q(qz, "Git hook pre-commit выполняется:",
  [("До создания коммита, может отменить его при exit 1", True),
   ("После push на remote", False),
   ("При переключении веток", False),
   ("При pull от remote", False)],
  explanation="pre-commit выполняется перед сохранением коммита. Если скрипт возвращает != 0, коммит отменяется. Используется для линтинга, проверки секретов.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 5 — Сети для DevOps
# ═══════════════════════════════════════════════════════════════════════════ #
c5 = course(
    "networking-devops",
    "Сети для DevOps",
    "TCP/IP, DNS, HTTP/HTTPS, балансировка нагрузки, SSL/TLS, firewall. "
    "Всё что нужно для работы с серверами, облаком и Kubernetes.",
    "🌐", "intermediate", "networks", 25, 700, prereqs=[1],
)

# ── Модуль 29: OSI и TCP/IP ───────────────────────────────────────────────
m = module(c5, "Модель OSI и стек TCP/IP", 1)
theory(m, "7 уровней OSI и стек TCP/IP", """\
## Модель OSI

| Уровень | Имя | Протоколы | Данные |
|---|---|---|---|
| 7 | Application | HTTP, DNS, FTP, SMTP | Данные |
| 6 | Presentation | TLS, SSL, JPEG | Данные |
| 5 | Session | NetBIOS, RPC | Данные |
| 4 | Transport | TCP, UDP | Сегменты |
| 3 | Network | IP, ICMP, OSPF | Пакеты |
| 2 | Data Link | Ethernet, MAC | Фреймы |
| 1 | Physical | Кабели, Wi-Fi | Биты |

**Мнемоника (снизу вверх):** Please Do Not Throw Sausage Pizza Away

### Стек TCP/IP (4 уровня)

```
Приложение (HTTP, DNS, SSH, SMTP)
Transport  (TCP, UDP)
Internet   (IP, ICMP)
Network    (Ethernet, Wi-Fi)
```

### TCP vs UDP

| Характеристика | TCP | UDP |
|---|---|---|
| Установка соединения | Трёхстороннее рукопожатие | Нет |
| Надёжность | Гарантия доставки | Нет гарантии |
| Порядок пакетов | Гарантирован | Не гарантирован |
| Скорость | Медленнее | Быстрее |
| Использование | HTTP, SSH, БД | DNS, видео, VoIP |

### TCP Handshake

```
Client          Server
  │── SYN ────→ │   (хочу соединение)
  │← SYN-ACK ──│   (принял, подтверждаю)
  │── ACK ────→ │   (подтверждаю)
  │            │   соединение установлено
```

### Порты

```
0-1023   → well-known (SSH:22, HTTP:80, HTTPS:443, DNS:53)
1024-49151 → registered (PostgreSQL:5432, Redis:6379, Docker:2375)
49152-65535 → ephemeral (временные порты клиента)
```
""", 1)

theory(m, "IP-адресация, CIDR и маршрутизация", """\
## IP-адресация

### IPv4

```
192.168.1.100 / 24
│             │  └─ маска: /24 = 255.255.255.0
│             └─── IP-адрес
└──────────────── 4 октета по 8 бит = 32 бита
```

### CIDR — бесклассовая маршрутизация

| Нотация | Маска | Хостов |
|---|---|---|
| /8  | 255.0.0.0 | 16 млн |
| /16 | 255.255.0.0 | 65 534 |
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /30 | 255.255.255.252 | 2 |
| /32 | 255.255.255.255 | 1 (один хост) |

### Приватные диапазоны (RFC 1918)

```
10.0.0.0/8        → крупные корпоративные сети
172.16.0.0/12     → Docker, VPN
192.168.0.0/16    → домашние сети
127.0.0.0/8       → loopback (localhost)
```

### Маршрутизация

```bash
ip route show                 # таблица маршрутизации
ip route add 10.0.0.0/8 via 192.168.1.1  # добавить маршрут
ip route del 10.0.0.0/8                   # удалить

# Пример таблицы:
# default via 192.168.1.1 dev eth0   ← шлюз по умолчанию
# 192.168.1.0/24 dev eth0            ← локальная сеть
# 10.244.0.0/16 via 10.0.0.1         ← например, K8s pod network
```

### NAT (Network Address Translation)

```
Приватная сеть         Internet
10.0.0.0/24     NAT Router      Google 8.8.8.8
10.0.0.10 ──→  │ 1.2.3.4 │──→ 8.8.8.8:53
               └─────────┘
```

NAT позволяет множеству устройств выходить в интернет через один публичный IP.
""", 2)

ql = quiz_lesson(m, "Тест: OSI и IP-адресация", 3)
qz = quiz(ql)
Q(qz, "На каком уровне OSI работает IP-протокол?",
  [("3 (Network)", True), ("4 (Transport)", False), ("2 (Data Link)", False), ("5 (Session)", False)],
  explanation="IP — протокол сетевого уровня (L3). TCP/UDP — транспортный (L4). Ethernet — канальный (L2).")
Q(qz, "Сколько хостов вмещает подсеть /24?",
  [("254", True), ("256", False), ("255", False), ("512", False)],
  explanation="2^(32-24) = 2^8 = 256. Минус: адрес сети (первый) и broadcast (последний) = 254 хоста.")
Q(qz, "Что произойдёт если одна сторона отправит данные по UDP и они не дойдут?",
  [("Данные потеряются — UDP не гарантирует доставку", True),
   ("UDP автоматически переотправит", False),
   ("Соединение разорвётся", False),
   ("Данные буферизуются до доставки", False)],
  explanation="UDP — connectionless протокол без гарантий. Используется там где скорость важнее надёжности (DNS, streaming, games).", order=3)

# ── Модуль 30: DNS ────────────────────────────────────────────────────────
m = module(c5, "DNS — система доменных имён", 2)
theory(m, "DNS: зоны, записи, dig, nslookup", """\
## DNS

DNS переводит доменные имена в IP-адреса.

### Типы DNS-записей

| Тип | Назначение | Пример |
|---|---|---|
| **A** | Домен → IPv4 | myapp.com → 1.2.3.4 |
| **AAAA** | Домен → IPv6 | myapp.com → 2001:db8::1 |
| **CNAME** | Псевдоним | www → myapp.com |
| **MX** | Почтовый сервер | @ → mail.myapp.com |
| **TXT** | Текст (SPF, DKIM) | "v=spf1 include:..." |
| **NS** | Name Server | @ → ns1.cloudflare.com |
| **SOA** | Зона авторитативности | - |
| **PTR** | IP → домен (reverse) | 1.2.3.4 → myapp.com |
| **SRV** | Сервис + порт | _https._tcp → ... |

### Иерархия DNS

```
. (root)
└── com (TLD)
    └── myapp (SLD)
        └── www (subdomain)
```

Запрос `www.myapp.com`:
1. Кэш браузера → /etc/hosts
2. Локальный resolver (8.8.8.8)
3. Root servers → .com TLD
4. myapp.com nameserver
5. Ответ: 1.2.3.4

### Диагностика

```bash
dig myapp.com              # DNS запрос
dig myapp.com A            # только A записи
dig myapp.com MX           # почтовые серверы
dig @8.8.8.8 myapp.com     # запрос к конкретному DNS
dig +trace myapp.com       # полный путь резолвинга
dig -x 1.2.3.4             # reverse lookup (PTR)

nslookup myapp.com         # простой запрос
host myapp.com             # ещё проще

# Кэш
resolvectl flush-caches    # сбросить кэш (systemd-resolved)
```

### /etc/hosts — локальный DNS

```
127.0.0.1   localhost
127.0.1.1   myhost
10.0.0.5    db.internal postgres
10.0.0.6    redis.internal
```

### TTL (Time To Live)

TTL определяет как долго запись кэшируется. При смене IP уменьши TTL заранее:
- За 24ч до смены: установить TTL=300 (5 минут)
- После смены: TTL обратно на 3600+
""", 1)

ql = quiz_lesson(m, "Тест: DNS", 2)
qz = quiz(ql)
Q(qz, "Какой тип DNS-записи указывает на псевдоним другого домена?",
  [("CNAME", True), ("A", False), ("PTR", False), ("NS", False)],
  explanation="CNAME (Canonical Name) — псевдоним. www.myapp.com CNAME myapp.com. Нельзя использовать на root домене (@).")
Q(qz, "Как сделать reverse DNS lookup (IP → домен)?",
  [("dig -x 1.2.3.4", True), ("dig PTR 1.2.3.4", False), ("nslookup --reverse 1.2.3.4", False), ("host --ptr 1.2.3.4", False)],
  explanation="dig -x автоматически формирует PTR запрос. Также: nslookup 1.2.3.4 или host 1.2.3.4.", order=2)
Q(qz, "Что нужно сделать с TTL ПЕРЕД сменой IP-адреса сервера?",
  [("Уменьшить TTL до 300 (5 мин) заранее, чтобы смена распространилась быстро", True),
   ("Увеличить TTL до максимума", False),
   ("TTL не влияет на скорость обновления", False),
   ("Удалить DNS запись", False)],
  explanation="Высокий TTL = долгое кэширование. Снизь TTL за 24-48ч до смены → кэши быстро обновятся → минимальный downtime.", order=3)

# ── Модуль 31: HTTP/HTTPS ─────────────────────────────────────────────────
m = module(c5, "HTTP/HTTPS и работа с API", 3)
theory(m, "HTTP методы, статусы, заголовки, curl", """\
## HTTP/HTTPS

### Методы HTTP

| Метод | Назначение | Идемпотент |
|---|---|---|
| GET | Получить ресурс | Да |
| POST | Создать ресурс | Нет |
| PUT | Заменить ресурс | Да |
| PATCH | Частично обновить | Нет |
| DELETE | Удалить ресурс | Да |
| HEAD | GET без тела | Да |
| OPTIONS | Узнать возможности | Да |

### Статус-коды

```
1xx — информационные
2xx — успех
  200 OK            → всё хорошо
  201 Created       → создан (POST)
  204 No Content    → успех, нет тела
3xx — редиректы
  301 Moved Permanently → постоянный редирект (SEO)
  302 Found             → временный редирект
  304 Not Modified      → кэш актуален
4xx — ошибки клиента
  400 Bad Request       → неверный запрос
  401 Unauthorized      → нужна аутентификация
  403 Forbidden         → нет прав
  404 Not Found         → не найдено
  422 Unprocessable     → ошибка валидации
  429 Too Many Requests → rate limit
5xx — ошибки сервера
  500 Internal Server Error
  502 Bad Gateway       → upstream недоступен
  503 Service Unavailable → сервис перегружен
  504 Gateway Timeout   → upstream не ответил
```

### Заголовки

```http
# Запрос
GET /api/users HTTP/1.1
Host: api.myapp.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json
Accept: application/json
Cache-Control: no-cache

# Ответ
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Remaining: 99
Cache-Control: max-age=3600
```

### curl — работа с API

```bash
# GET
curl https://api.example.com/users

# POST JSON
curl -X POST https://api.example.com/users \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer TOKEN" \\
  -d '{"name": "Ivan", "email": "ivan@example.com"}'

# Отладка
curl -v URL          # verbose: запрос + ответ
curl -I URL          # только заголовки ответа
curl -w "\\n%{http_code}\\n%{time_total}s\\n" URL  # код и время

# Сохранить
curl -L -o file.tar.gz URL     # скачать с редиректами
curl -C - -o file.tar.gz URL   # продолжить прерванную загрузку
```
""", 1)

ql = quiz_lesson(m, "Тест: HTTP", 2)
qz = quiz(ql)
Q(qz, "Какой HTTP статус означает что ресурс создан успешно?",
  [("201 Created", True), ("200 OK", False), ("204 No Content", False), ("202 Accepted", False)],
  explanation="201 Created — стандартный ответ на успешный POST. 200 OK — общий успех. 204 — успех без тела ответа.")
Q(qz, "Чем 401 отличается от 403?",
  [("401 — не аутентифицирован (нет токена); 403 — аутентифицирован, но нет прав", True),
   ("401 — сервер недоступен; 403 — ресурс не найден", False),
   ("401 и 403 — одно и то же", False),
   ("403 — не аутентифицирован; 401 — нет прав", False)],
  explanation="401 Unauthorized: 'кто ты?' — нужна аутентификация. 403 Forbidden: 'знаю кто ты, но не пущу' — нет прав.", order=2)

# ── Модуль 32: Nginx / Reverse Proxy ─────────────────────────────────────
m = module(c5, "Nginx: reverse proxy и балансировка", 4)
theory(m, "Nginx: конфигурация, upstream, load balancing", """\
## Nginx как reverse proxy

### Базовая конфигурация

```nginx
# /etc/nginx/sites-available/myapp
server {
    listen 80;
    server_name myapp.com www.myapp.com;

    # Статические файлы
    location /static/ {
        alias /var/www/myapp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API → backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    # SPA fallback
    location / {
        root /var/www/myapp/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

### Балансировка нагрузки

```nginx
upstream backend {
    # Round-robin (по умолчанию)
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;

    # Weighted (весовая)
    server 10.0.0.1:8000 weight=3;
    server 10.0.0.2:8000 weight=1;

    # Least connections
    least_conn;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;

    # IP hash (sticky sessions)
    ip_hash;
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;

    # Health check
    server 10.0.0.3:8000 backup;   # резервный
    server 10.0.0.4:8000 down;     # выключен
}
```

### Управление Nginx

```bash
nginx -t                    # проверить конфигурацию
nginx -s reload             # перезагрузить без downtime
systemctl reload nginx      # через systemd

ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/
nginx -T | grep server_name  # все server_name
```
""", 1)

ql = quiz_lesson(m, "Тест: Nginx и балансировка", 2)
qz = quiz(ql)
Q(qz, "Что такое reverse proxy?",
  [("Сервер принимающий запросы от клиентов и перенаправляющий их к backend-серверам", True),
   ("Прокси который скрывает IP клиента от интернета", False),
   ("Балансировщик только для TCP", False),
   ("CDN-сервер для статических файлов", False)],
  explanation="Reverse proxy стоит перед backend: принимает клиентские запросы, балансирует нагрузку, терминирует SSL, кэширует.")
Q(qz, "Какой метод балансировки направит одного клиента всегда на один сервер?",
  [("ip_hash", True), ("round-robin", False), ("least_conn", False), ("random", False)],
  explanation="ip_hash вычисляет хэш от IP клиента → всегда один сервер. Нужен для sticky sessions (хранение сессии на сервере).", order=2)

lab(m, "Лабораторная: настройка виртуального хоста Nginx", 7, 3)

# ── Модуль 33: SSL/TLS ────────────────────────────────────────────────────
m = module(c5, "SSL/TLS и HTTPS", 5)
theory(m, "TLS handshake, сертификаты, Let's Encrypt, certbot", """\
## SSL/TLS

### TLS Handshake (упрощённо)

```
Client                          Server
  │── ClientHello ─────────────→│  (версии TLS, cipher suites)
  │← ServerHello ───────────────│  (выбранный cipher, сертификат)
  │← Certificate ───────────────│  (публичный ключ + цепочка CA)
  │  [проверка сертификата]     │
  │── ClientKeyExchange ────────→│  (pre-master secret, шифр. публ. ключом)
  │← ChangeCipherSpec ──────────│
  │── Finished ────────────────→│
  │← Finished ─────────────────│  соединение установлено
```

### Let's Encrypt + Certbot

```bash
apt install certbot python3-certbot-nginx

# Получить сертификат и настроить Nginx автоматически
certbot --nginx -d myapp.com -d www.myapp.com

# Только сертификат (без изменения nginx)
certbot certonly --nginx -d myapp.com

# Проверить автообновление
systemctl status certbot.timer
certbot renew --dry-run

# Сертификаты хранятся в:
# /etc/letsencrypt/live/myapp.com/fullchain.pem
# /etc/letsencrypt/live/myapp.com/privkey.pem
```

### Nginx HTTPS конфигурация

```nginx
server {
    listen 80;
    server_name myapp.com;
    return 301 https://$host$request_uri;  # редирект HTTP → HTTPS
}

server {
    listen 443 ssl http2;
    server_name myapp.com;

    ssl_certificate /etc/letsencrypt/live/myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.com/privkey.pem;

    # Современные настройки TLS
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS (браузер 1 год использует только HTTPS)
    add_header Strict-Transport-Security "max-age=31536000" always;

    # ...остальная конфигурация
}
```

### Диагностика SSL

```bash
# Проверить сертификат
openssl s_client -connect myapp.com:443 -servername myapp.com
echo | openssl s_client -connect myapp.com:443 2>/dev/null | openssl x509 -noout -dates
curl -vI https://myapp.com 2>&1 | grep -E "SSL|issuer|expire"
```
""", 1)

ql = quiz_lesson(m, "Тест: SSL/TLS", 2)
qz = quiz(ql)
Q(qz, "Что такое HSTS?",
  [("HTTP заголовок принуждающий браузер использовать только HTTPS", True),
   ("Алгоритм шифрования TLS", False),
   ("Тип SSL сертификата", False),
   ("HTTP/2 заголовок безопасности", False)],
  explanation="Strict-Transport-Security: браузер запоминает что сайт только HTTPS и не делает HTTP запросы даже при попытке. Защита от downgrade атак.")
Q(qz, "Как часто Let's Encrypt сертификаты нужно обновлять?",
  [("Каждые 90 дней (certbot делает это автоматически)", True),
   ("Каждый год", False),
   ("Каждые 2 года", False),
   ("Никогда — они бессрочные", False)],
  explanation="Let's Encrypt сертификаты действительны 90 дней. certbot устанавливает systemd timer для автообновления каждые ~60 дней.", order=2)

lab(m, "Лабораторная: настройка SSL/HTTPS в Nginx", 8, 3)

# ── Модуль 34: Firewall продвинутый ───────────────────────────────────────
m = module(c5, "Firewall и сетевая безопасность", 6)
theory(m, "ufw, iptables, nftables — защита сервера", """\
## Firewall в Linux

### ufw — простой firewall

```bash
ufw enable
ufw default deny incoming    # запретить всё входящее
ufw default allow outgoing   # разрешить всё исходящее

# Разрешить сервисы
ufw allow ssh                # 22/tcp
ufw allow 80/tcp             # HTTP
ufw allow 443/tcp            # HTTPS
ufw allow from 10.0.0.0/8   # весь трафик из подсети
ufw allow from 1.2.3.4 to any port 5432  # PostgreSQL только с одного IP

# Rate limiting (защита SSH от bruteforce)
ufw limit ssh

ufw status numbered          # список правил с номерами
ufw delete 3                 # удалить правило №3
ufw reload                   # применить изменения
```

### iptables — продвинутый firewall

```
Цепочки (chains):
  INPUT   → входящий трафик к хосту
  OUTPUT  → исходящий трафик от хоста
  FORWARD → транзитный трафик (маршрутизация)

Таблицы:
  filter  → разрешить/запретить (по умолчанию)
  nat     → NAT, MASQUERADE, REDIRECT
  mangle  → изменение пакетов
```

```bash
# Базовая защита сервера
iptables -F                                      # очистить правила
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT               # loopback
iptables -A INPUT -p tcp --dport 22 -j ACCEPT   # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT   # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT  # HTTPS
iptables -A INPUT -j DROP                        # остальное — DROP

# NAT (для маршрутизации через сервер)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

### Диагностика сети

```bash
# Проверить достижимость
ping -c3 8.8.8.8
traceroute google.com
mtr --report google.com      # статистика потерь по каждому хопу

# Открытые соединения
ss -tulnp
netstat -tulnp               # старый способ

# Захват трафика
tcpdump -i eth0 port 80 -w capture.pcap
tcpdump -r capture.pcap | head -20
```
""", 1)

ql = quiz_lesson(m, "Тест: firewall", 2)
qz = quiz(ql)
Q(qz, "Какая команда ufw защищает SSH от bruteforce (rate limiting)?",
  [("ufw limit ssh", True), ("ufw deny ssh", False), ("ufw allow ssh --rate 5/min", False), ("fail2ban ssh", False)],
  explanation="ufw limit включает rate limiting: если > 6 подключений за 30 секунд с одного IP — блокировать. Встроенная защита.")
Q(qz, "Правило iptables '--state ESTABLISHED,RELATED' нужно для:",
  [("Разрешить ответные пакеты для уже установленных соединений", True),
   ("Блокировать новые соединения", False),
   ("Разрешить только TCP соединения", False),
   ("Логировать все соединения", False)],
  explanation="Stateful firewall: ESTABLISHED/RELATED разрешают ответы на легитимные запросы. Без этого правила сервер не мог бы отправлять ответы.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 6 — Docker
# ═══════════════════════════════════════════════════════════════════════════ #
c6 = course(
    "docker",
    "Docker",
    "Контейнеризация от основ до production. Dockerfile, образы, volumes, "
    "сети, Docker Compose, мультистейдж сборки и безопасность контейнеров.",
    "🐳", "intermediate", "docker", 35, 900, prereqs=[1, 3],
)

# ── Модуль 35: Введение в контейнеры ──────────────────────────────────────
m = module(c6, "Контейнеры: основы и архитектура", 1)
theory(m, "Контейнеры vs VMs, namespaces, cgroups", """\
## Что такое контейнеры

### Контейнеры vs Виртуальные машины

```
Виртуальные машины:           Контейнеры:
┌─────────┬─────────┐        ┌──────┬──────┬──────┐
│   App A │  App B  │        │App A │App B │App C │
│  OS     │  OS     │        ├──────┴──────┴──────┤
│  Guest  │  Guest  │        │    Docker Engine   │
├─────────┴─────────┤        ├────────────────────┤
│    Hypervisor     │        │   Host OS Kernel   │
├───────────────────┤        ├────────────────────┤
│    Host OS        │        │    Hardware        │
├───────────────────┤        └────────────────────┘
│    Hardware       │
└───────────────────┘
```

| | ВМ | Контейнер |
|---|---|---|
| Изоляция | Полная (гипервизор) | Ядро shared |
| Размер | ГБ | МБ |
| Запуск | Минуты | Секунды |
| Производительность | -5-15% | ~0% overhead |
| Безопасность | Выше | Ниже (shared kernel) |

### Как работают контейнеры

**Namespaces** — изоляция ресурсов:
- `pid` — независимое дерево процессов (PID 1 внутри)
- `net` — собственный сетевой стек
- `mnt` — независимая файловая система
- `uts` — hostname, domainname
- `user` — UID/GID маппинг

**cgroups** — ограничение ресурсов:
- CPU: `--cpus=0.5` (половина ядра)
- Memory: `--memory=256m`
- I/O: `--device-read-bps`

### Установка Docker

```bash
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER     # добавить в группу
newgrp docker                 # применить без logout
docker version               # проверить установку
docker info                  # информация о daemon
```
""", 1)

theory(m, "Первые шаги: run, ps, stop, rm, images", """\
## Работа с контейнерами

### Запуск контейнеров

```bash
docker run nginx                          # запустить nginx
docker run -d nginx                       # в фоне (detached)
docker run -d -p 8080:80 nginx            # маппинг портов host:container
docker run -d --name my-nginx nginx       # с именем
docker run -it ubuntu bash               # интерактивно
docker run --rm ubuntu echo "hello"      # удалить после выхода
docker run -e MY_VAR=value nginx          # переменная окружения
docker run -v /host/path:/container/path nginx  # bind mount
docker run --memory=256m --cpus=0.5 nginx  # лимиты ресурсов
```

### Управление контейнерами

```bash
docker ps                     # запущенные контейнеры
docker ps -a                  # все (включая остановленные)
docker stop my-nginx          # мягкая остановка (SIGTERM)
docker kill my-nginx          # принудительная (SIGKILL)
docker start my-nginx         # запустить остановленный
docker restart my-nginx       # перезапустить
docker rm my-nginx            # удалить контейнер
docker rm -f my-nginx         # принудительно удалить запущенный
docker rm $(docker ps -aq)    # удалить все остановленные
```

### Работа с образами

```bash
docker images                 # список локальных образов
docker pull ubuntu:22.04      # скачать образ
docker push myrepo/myapp:v1   # опубликовать
docker rmi nginx              # удалить образ
docker tag myapp:latest myrepo/myapp:v1.0.0  # тег

# Очистка
docker system prune           # удалить неиспользуемое
docker system prune -a        # включая неиспользуемые образы
docker system df              # сколько места занято
```

### Отладка

```bash
docker logs my-nginx          # логи контейнера
docker logs -f my-nginx       # следить за логами
docker logs --tail 50 my-nginx
docker exec -it my-nginx bash # войти в запущенный контейнер
docker exec my-nginx nginx -t # выполнить команду
docker inspect my-nginx       # полная информация (JSON)
docker stats                  # live статистика ресурсов
docker top my-nginx           # процессы в контейнере
```
""", 2)

ql = quiz_lesson(m, "Тест: основы Docker", 3)
qz = quiz(ql)
Q(qz, "Какой флаг запускает контейнер в фоновом режиме?",
  [("-d (detached)", True), ("-b (background)", False), ("-f (foreground)", False), ("-n (nodaemon)", False)],
  explanation="docker run -d запускает контейнер в detached режиме, возвращая контроль терминалу. Контейнер работает в фоне.")
Q(qz, "В чём главное отличие контейнеров от виртуальных машин?",
  [("Контейнеры разделяют ядро хоста; ВМ имеют собственное ядро через гипервизор", True),
   ("Контейнеры быстрее только из-за меньшего размера образа", False),
   ("ВМ не могут запускать несколько приложений", False),
   ("Контейнеры используют аппаратную виртуализацию", False)],
  explanation="Контейнеры = изоляция через namespaces/cgroups на уровне ядра. ВМ = полная эмуляция железа. Отсюда: контейнеры легче и быстрее.", order=2)
Q(qz, "Что делает docker run --rm?",
  [("Автоматически удаляет контейнер после его остановки", True),
   ("Запускает контейнер как root", False),
   ("Удаляет образ после запуска", False),
   ("Перезапускает контейнер при падении", False)],
  explanation="--rm = remove: контейнер автоматически удаляется после завершения. Удобно для разовых задач и тестов.", order=3)

# ── Модуль 36: Dockerfile ─────────────────────────────────────────────────
m = module(c6, "Dockerfile: создание образов", 2)
theory(m, "FROM, RUN, COPY, CMD, ENTRYPOINT и другие инструкции", """\
## Dockerfile

### Все инструкции

```dockerfile
# Базовый образ
FROM ubuntu:22.04
FROM python:3.11-slim   # предпочтительно: slim/alpine меньше

# Метаданные
LABEL maintainer="team@company.com"
LABEL version="1.0"

# Переменные сборки (только во время build)
ARG APP_VERSION=1.0.0
ARG DEBIAN_FRONTEND=noninteractive

# Переменные окружения (runtime + build)
ENV APP_PORT=8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Рабочая директория (создаётся если нет)
WORKDIR /app

# Копирование файлов
COPY requirements.txt .         # файл в WORKDIR
COPY . .                        # всё (использовать .dockerignore!)
ADD archive.tar.gz /app/        # ADD умеет распаковывать архивы
ADD https://url/file /app/      # ADD умеет скачивать (но лучше curl)

# Выполнение команд (создаёт слой)
RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        curl git && \\
    rm -rf /var/lib/apt/lists/*  # очистить кэш apt в том же слое!

RUN pip install --no-cache-dir -r requirements.txt

# Открытые порты (документация, не публикует!)
EXPOSE 8000

# Volumes (точки монтирования)
VOLUME /app/media

# Пользователь (никогда не запускать как root!)
RUN useradd -m -u 1001 appuser
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Точка входа (не переопределяется в docker run)
ENTRYPOINT ["python", "-m", "gunicorn"]

# Аргументы по умолчанию для ENTRYPOINT (переопределяется)
CMD ["config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### CMD vs ENTRYPOINT

```dockerfile
# Только CMD: docker run img /bin/bash → заменяет CMD
CMD ["python", "app.py"]

# ENTRYPOINT + CMD: docker run img --port 9000 → добавляет к ENTRYPOINT
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8000"]
```
""", 1)

theory(m, "Best practices: слои, .dockerignore, безопасность", """\
## Dockerfile Best Practices

### Порядок инструкций (кэш слоёв)

```dockerfile
# НЕПРАВИЛЬНО: COPY . . делает все дальнейшие слои некэшируемыми
FROM python:3.11-slim
COPY . .
RUN pip install -r requirements.txt   # всегда пересобирается!

# ПРАВИЛЬНО: сначала зависимости, потом код
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .               # кэш инвалидируется только при изменении requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                              # код меняется часто, но зависимости уже кэшированы
```

### .dockerignore

```dockerignore
.git
.gitignore
.env
*.env
__pycache__
*.pyc
*.pyo
node_modules
.coverage
.pytest_cache
docs/
*.md
Dockerfile*
docker-compose*.yml
```

### Минимальный размер образа

```dockerfile
# Используй slim или alpine базы
FROM python:3.11-slim      # ~120MB vs python:3.11 (~900MB)
FROM node:20-alpine        # ~170MB vs node:20 (~1GB)

# Объединяй RUN команды
RUN apt-get update && \\
    apt-get install -y --no-install-recommends curl && \\
    rm -rf /var/lib/apt/lists/*

# Не устанавливай dev-зависимости в production образ
RUN pip install --no-cache-dir gunicorn==21.2.0
```

### Безопасность

```dockerfile
# Никогда не root!
RUN useradd -r -u 1001 -g app appuser
USER appuser

# Не хранить секреты в Dockerfile!
# ПЛОХО: ENV DB_PASSWORD=secret
# ХОРОШО: передавать через -e или --env-file

# Сканировать образы
# docker scout cves myimage:latest
# trivy image myimage:latest
```

### Мультистейдж (следующая тема)

```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Финальный образ: только nginx + статика, без node_modules!
```
""", 2)

ql = quiz_lesson(m, "Тест: Dockerfile", 3)
qz = quiz(ql)
Q(qz, "Почему COPY requirements.txt должен быть ПЕРЕД COPY . . в Dockerfile?",
  [("Чтобы кэш слоя с pip install не инвалидировался при изменении кода", True),
   ("Потому что Docker читает файлы по алфавиту", False),
   ("COPY . . не умеет копировать .txt файлы", False),
   ("Для уменьшения размера образа", False)],
  explanation="Docker кэширует слои. COPY requirements.txt → pip install кэшируется. COPY . . инвалидирует кэш при любом изменении кода, но зависимости уже закэшированы.")
Q(qz, "В чём разница CMD и ENTRYPOINT?",
  [("ENTRYPOINT не переопределяется в docker run; CMD — дефолтные аргументы для ENTRYPOINT", True),
   ("CMD запускается при сборке; ENTRYPOINT при запуске", False),
   ("ENTRYPOINT для Linux; CMD для Windows контейнеров", False),
   ("Разницы нет, это синонимы", False)],
  explanation="ENTRYPOINT = основная команда (не меняется). CMD = аргументы по умолчанию (меняются через docker run img ARGS).", order=2)
Q(qz, "Как правильно установить пакеты apt в Dockerfile?",
  [("RUN apt-get update && apt-get install -y pkg && rm -rf /var/lib/apt/lists/*", True),
   ("RUN apt install pkg", False),
   ("RUN apt-get update\nRUN apt-get install pkg", False),
   ("ADD apt://pkg /app/", False)],
  explanation="Всё в одном RUN: update + install + очистка кэша. Раздельные RUN создают отдельные слои — кэш apt остаётся в промежуточном слое.", order=3)

# ── Модуль 37: Volumes и сети ─────────────────────────────────────────────
m = module(c6, "Volumes и сети Docker", 3)
theory(m, "bind mount, named volumes, bridge/host/overlay сети", """\
## Volumes в Docker

### Типы хранилищ

```
Host               Container
┌──────────────┐   ┌─────────────┐
│ /host/path ──┼───┼→ /app/data  │  bind mount
│              │   │             │
│ docker volume┼───┼→ /app/data  │  named volume (рекомендуется)
│              │   │             │
│      RAM ────┼───┼→ /tmp/cache │  tmpfs (только в памяти)
└──────────────┘   └─────────────┘
```

```bash
# Named volume (управляется Docker, лучше для данных)
docker volume create pgdata
docker run -v pgdata:/var/lib/postgresql/data postgres
docker volume ls
docker volume inspect pgdata
docker volume rm pgdata

# Bind mount (привязка к папке хоста, удобно для разработки)
docker run -v $(pwd):/app myapp
docker run -v /etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx  # :ro = read-only

# tmpfs (только в памяти, не на диске)
docker run --tmpfs /tmp:size=100m myapp
```

## Сети Docker

### Типы сетей

```bash
docker network ls             # список сетей
docker network inspect bridge # подробности
```

| Тип | Описание | Использование |
|---|---|---|
| **bridge** | Изолированная виртуальная сеть (по умолчанию) | Обычные контейнеры |
| **host** | Использует сетевой стек хоста | Максимальная производительность |
| **none** | Без сети | Полная изоляция |
| **overlay** | Между Docker Swarm нодами | Multi-host |

### Пользовательские bridge сети

```bash
docker network create mynet
docker run -d --network mynet --name db postgres
docker run -d --network mynet --name app myapp
# Контейнеры в одной сети обращаются друг к другу по имени:
# app может обратиться к db как http://db:5432

docker network connect mynet existing-container  # добавить сеть
docker network disconnect mynet container        # убрать
```

### Публикация портов

```bash
docker run -p 8080:80 nginx          # localhost:8080 → container:80
docker run -p 127.0.0.1:8080:80 nginx  # только localhost (не 0.0.0.0)
docker run -P nginx                  # все EXPOSE → случайные порты хоста
docker port my-nginx                 # посмотреть маппинг портов
```
""", 1)

ql = quiz_lesson(m, "Тест: volumes и сети", 2)
qz = quiz(ql)
Q(qz, "В чём преимущество named volumes перед bind mounts для production?",
  [("Управляются Docker, переносимы, не зависят от пути на хосте", True),
   ("Быстрее по скорости I/O", False),
   ("Автоматически бэкапятся", False),
   ("Не занимают место на диске", False)],
  explanation="Named volumes: Docker управляет хранением, независимы от ОС хоста, легко мигрировать. Bind mounts привязаны к конкретному пути хоста.")
Q(qz, "Как контейнеры в одной Docker bridge сети обращаются друг к другу?",
  [("По имени контейнера (автоматический DNS)", True),
   ("Только по IP-адресу", False),
   ("Через хост (localhost)", False),
   ("Только через опубликованные порты", False)],
  explanation="Docker создаёт встроенный DNS для пользовательских bridge сетей. Имя контейнера = hostname. В default bridge сети DNS недоступен.", order=2)

# ── Модуль 38: Docker Compose ─────────────────────────────────────────────
m = module(c6, "Docker Compose", 4)
theory(m, "docker-compose.yml: services, volumes, networks, depends_on", """\
## Docker Compose

Compose позволяет описать многоконтейнерное приложение в одном YAML файле.

### Полный пример docker-compose.yml

```yaml
version: '3.9'   # или без version (новый синтаксис)

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}   # из .env файла
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        APP_VERSION: "1.0.0"
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./backend:/app          # dev: hot reload
      - media_data:/app/media
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend

networks:
  default:
    driver: bridge

volumes:
  postgres_data:
  media_data:
```

### Команды

```bash
docker compose up -d          # запустить в фоне
docker compose up -d --build  # пересобрать образы
docker compose down           # остановить и удалить контейнеры
docker compose down -v        # + удалить volumes
docker compose ps             # статус сервисов
docker compose logs -f backend  # логи конкретного сервиса
docker compose exec backend bash  # войти в контейнер
docker compose restart backend    # перезапустить сервис
docker compose build --no-cache   # пересобрать без кэша
docker compose pull               # обновить образы
docker compose config             # проверить и вывести итоговый конфиг
```
""", 1)

ql = quiz_lesson(m, "Тест: Docker Compose", 2)
qz = quiz(ql)
Q(qz, "Что означает condition: service_healthy в depends_on?",
  [("Дождаться пока сервис пройдёт healthcheck прежде чем запускать зависимый", True),
   ("Перезапускать зависимый при падении", False),
   ("Запускать только если сервис в сети", False),
   ("Мониторить здоровье сервиса", False)],
  explanation="Без condition: service_healthy зависимый сервис запустится сразу после старта контейнера, но до того как DB будет готова принять соединения.")
Q(qz, "Как перезапустить только один сервис в Compose не трогая остальные?",
  [("docker compose restart backend", True), ("docker compose up -d", False),
   ("docker restart backend", False), ("docker compose reload backend", False)],
  explanation="docker compose restart <service> перезапускает конкретный сервис. docker compose up -d пересоздаёт изменившиеся сервисы.", order=2)

# ── Модуль 39: Мультистейдж ───────────────────────────────────────────────
m = module(c6, "Мультистейдж сборки", 5)
theory(m, "Multi-stage builds: FROM...AS, COPY --from", """\
## Мультистейдж сборки

Позволяют использовать большие образы для сборки, но деплоить маленький финальный.

### Python: с venv

```dockerfile
# ── Stage 1: Builder ──────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────
FROM python:3.11-slim

# Копируем только установленные пакеты из builder
COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

RUN useradd -r -u 1001 appuser
USER appuser

EXPOSE 8000
CMD ["gunicorn", "app:application", "--bind", "0.0.0.0:8000"]
```

### Node.js + Nginx (React SPA)

```dockerfile
# ── Stage 1: Build frontend ───────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci --only=production=false
COPY . .
RUN npm run build

# ── Stage 2: Serve ────────────────────────────────
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
# Финальный образ: ~25MB vs ~1GB builder
```

### Go: статический бинарь

```dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.* .
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server ./cmd/server

# Минимальный образ - только бинарь!
FROM scratch

COPY --from=builder /app/server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
# Размер образа: ~10MB
```

### Полезные паттерны

```dockerfile
# Именованные стейджи можно пропускать
FROM base AS test
RUN go test ./...

FROM base AS production
# тест не попадает в production
```

```bash
# Собрать только конкретный стейдж
docker build --target builder -t myapp:builder .
```
""", 1)

ql = quiz_lesson(m, "Тест: мультистейдж", 2)
qz = quiz(ql)
Q(qz, "Главное преимущество мультистейдж сборок:",
  [("Финальный образ содержит только runtime артефакты, без инструментов сборки", True),
   ("Ускоряет процесс сборки", False),
   ("Позволяет использовать несколько FROM без последствий", False),
   ("Автоматически оптимизирует слои", False)],
  explanation="multi-stage: builder-образ с компилятором/npm/etc → финальный образ только с бинарём/статикой. Размер может уменьшиться с 1GB до 20MB.")
Q(qz, "Как скопировать файлы из предыдущего стейджа?",
  [("COPY --from=builder /app/dist /app/dist", True),
   ("COPY [builder] /app/dist /app/dist", False),
   ("ADD stage:builder /app/dist /app/dist", False),
   ("FROM builder COPY /app/dist", False)],
  explanation="COPY --from=<stage_name> копирует из именованного стейджа (AS builder). Можно также --from=0 (по индексу).", order=2)

# ── Модуль 40: Безопасность Docker ────────────────────────────────────────
m = module(c6, "Безопасность Docker", 6)
theory(m, "non-root, cap_drop, seccomp, secrets, сканирование образов", """\
## Безопасность контейнеров

### Запуск не от root

```dockerfile
# В Dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser
USER appuser

# Или для Alpine
RUN addgroup -S appgroup && adduser -S -G appgroup appuser
USER appuser
```

```bash
docker run --user 1001:1001 myimage
```

### Capability dropping

Linux capabilities — гранулярные привилегии вместо root.

```bash
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE nginx
# Убрать всё, добавить только нужное (привязка к порту <1024)
```

```yaml
# docker-compose.yml
services:
  app:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### Read-only filesystem

```bash
docker run --read-only --tmpfs /tmp myapp
# Файловая система только для чтения, /tmp в RAM
```

### Secrets в Docker Compose

```yaml
services:
  app:
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

### seccomp профиль

```bash
docker run --security-opt seccomp=profile.json myapp
# Ограничить syscalls которые может делать контейнер
```

### Сканирование образов

```bash
# Trivy (рекомендуется)
trivy image myapp:latest
trivy image --severity HIGH,CRITICAL myapp:latest

# Docker Scout (встроен)
docker scout cves myapp:latest
docker scout recommendations myapp:latest

# В CI/CD (GitHub Actions)
# - uses: aquasecurity/trivy-action@master
#   with:
#     image-ref: myapp:latest
#     exit-code: 1     # упасть при критических уязвимостях
```

### Общие правила

1. Никогда не запускать как root (USER appuser)
2. Использовать официальные базовые образы
3. Регулярно обновлять базовые образы
4. Не хранить секреты в образе (ENV, ARG)
5. cap_drop ALL в production
6. Сканировать образы в CI/CD
7. Использовать digest вместо :latest в production
""", 1)

ql = quiz_lesson(m, "Тест: безопасность Docker", 2)
qz = quiz(ql)
Q(qz, "Почему нельзя запускать контейнер от root?",
  [("Если контейнер взломан, атакующий получит root-доступ к хосту", True),
   ("Docker запрещает root по умолчанию", False),
   ("Root контейнеры не могут использовать сеть", False),
   ("Root контейнеры не могут читать volumes", False)],
  explanation="Контейнеры не дают полной изоляции. Root в контейнере = root на хосте если есть уязвимость. Non-root USER — первая линия защиты.")
Q(qz, "Что делает --cap-drop ALL в Docker?",
  [("Убирает все Linux capabilities у контейнера (принцип минимальных привилегий)", True),
   ("Отключает сетевые возможности", False),
   ("Запрещает монтирование volumes", False),
   ("Ограничивает память до минимума", False)],
  explanation="Linux capabilities делят root привилегии на гранулярные права. --cap-drop ALL убирает все, затем --cap-add добавляет только необходимые.", order=2)

lab(m, "Лабораторная: Break & Fix Docker-контейнер", 10, 3)



# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 7 — CI/CD с GitHub Actions
# ═══════════════════════════════════════════════════════════════════════════ #
c7 = course(
    "cicd-github-actions",
    "CI/CD с GitHub Actions",
    "Непрерывная интеграция и доставка: концепции CI/CD, GitHub Actions от основ до "
    "продвинутых паттернов, Docker в пайплайнах, стратегии деплоя.",
    "⚙️", "intermediate", "cicd", 30, 800, prereqs=[4, 6],
)

m = module(c7, "Концепции CI/CD", 1)
theory(m, "CI, Continuous Delivery и Continuous Deployment", """\
## CI/CD

### Непрерывная интеграция (CI)
Каждый коммит автоматически: собирается, проверяется линтером, тестируется, упаковывается.

### Continuous Delivery vs Deployment
| | Delivery | Deployment |
|---|---|---|
| Деплой | Ручное нажатие | Полностью авто |
| Риск | Ниже | Выше |
| Скорость | Средняя | Максимальная |

### DevOps Pipeline
```
Code → Build → Test → Security → Package → Deploy → Monitor
```

### DORA метрики (Elite команды)
- Deployment Frequency: >1/день
- Lead Time: <1ч
- MTTR: <1ч  
- Change Failure Rate: <5%
""", 1)

ql = quiz_lesson(m, "Тест: концепции CI/CD", 2)
qz = quiz(ql)
Q(qz, "В чём разница Continuous Delivery и Continuous Deployment?",
  [("Delivery требует ручного подтверждения; Deployment деплоит автоматически", True),
   ("Это одно и то же", False), ("Delivery только для Docker", False), ("Deployment только для K8s", False)],
  explanation="Delivery: всегда готово к деплою, но нажимает человек. Deployment: каждый зелёный пайплайн = автодеплой.")
Q(qz, "MTTR в DORA метриках — это:",
  [("Mean Time To Restore — среднее время восстановления после инцидента", True),
   ("Mean Time To Release", False), ("Maximum Test Time Required", False), ("Minimum Terraform Run Time", False)],
  explanation="DORA: Deployment Frequency, Lead Time, MTTR (восстановление), Change Failure Rate.", order=2)

m = module(c7, "GitHub Actions: основы", 2)
theory(m, "Workflows, events, jobs, steps, runners", """\
## GitHub Actions

### Структура workflow

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml
```

### Переменные и секреты
```yaml
steps:
  - run: echo "Deploying to ${{ vars.DEPLOY_HOST }}"
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

### Кэш зависимостей
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### Условия
```yaml
- name: Deploy
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh

- name: Notify failure  
  if: failure()
  run: ./notify.sh
```
""", 1)

theory(m, "Matrix builds, reusable workflows, environments", """\
## Продвинутые паттерны

### Matrix builds
```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ['3.10', '3.11', '3.12']
        os: [ubuntu-latest, windows-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pytest
```

### Environments с approvals
```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://myapp.com
    steps:
      - run: ./deploy.sh
```
В Settings → Environments → Required reviewers: @devops-team

### Outputs между jobs
```yaml
jobs:
  build:
    outputs:
      tag: ${{ steps.meta.outputs.tags }}
    steps:
      - id: meta
        run: echo "tags=myapp:$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
  deploy:
    needs: build
    steps:
      - run: docker pull ${{ needs.build.outputs.tag }}
```
""", 2)

ql = quiz_lesson(m, "Тест: GitHub Actions", 3)
qz = quiz(ql)
Q(qz, "Где хранятся секреты (API ключи) в GitHub Actions?",
  [("Settings → Secrets and variables → Actions", True),
   ("В .env файле репозитория", False), ("В workflow YAML", False), ("GitHub Packages", False)],
  explanation="Секреты зашифрованы в GitHub Settings. Доступны через ${{ secrets.NAME }}. НИКОГДА не коммить в репозиторий!")
Q(qz, "Для чего используется matrix strategy?",
  [("Запускать workflow с разными параметрами (версии, ОС) параллельно", True),
   ("Распределить нагрузку между runners", False),
   ("Оптимизировать время сборки", False),
   ("Создать зависимости между jobs", False)],
  explanation="Matrix автоматически создаёт комбинации. Python 3.10/3.11/3.12 × ubuntu/windows = 6 параллельных jobs.", order=2)
Q(qz, "Что делает needs: [previous-job] в job?",
  [("Ждёт успешного завершения previous-job перед запуском", True),
   ("Копирует артефакты из previous-job", False),
   ("Запускает jobs последовательно", False),
   ("Передаёт secrets между jobs", False)],
  explanation="needs устанавливает зависимость и последовательность. Без needs все jobs параллельны.", order=3)

m = module(c7, "Docker в CI/CD пайплайне", 3)
theory(m, "Build, push, scan, deploy с Docker в GitHub Actions", """\
## Docker в GitHub Actions

```yaml
name: Docker CI/CD
on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=sha-

      - uses: docker/setup-buildx-action@v3

      - id: build
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  scan:
    needs: build-push
    runs-on: ubuntu-latest
    steps:
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-push.outputs.digest }}
          exit-code: 1
          severity: CRITICAL

  deploy:
    needs: [build-push, scan]
    environment: production
    runs-on: ubuntu-latest
    steps:
      - uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: deploy
          key: ${{ secrets.SSH_KEY }}
          script: docker compose pull && docker compose up -d
```
""", 1)

ql = quiz_lesson(m, "Тест: Docker в CI/CD", 2)
qz = quiz(ql)
Q(qz, "Зачем cache-from/cache-to: type=gha в docker/build-push-action?",
  [("Кэшировать Docker слои между запусками для ускорения сборки", True),
   ("Кэшировать результаты тестов", False),
   ("Хранить образы в GitHub Actions", False),
   ("Избежать повторного логина", False)],
  explanation="GHA кэш хранит Docker layer cache. Повторная сборка использует кэшированные слои → с 5 минут до 30 секунд.")
Q(qz, "Почему scan должен быть ПОСЛЕ сборки но ПЕРЕД деплоем?",
  [("Нельзя сканировать до сборки; нельзя деплоить уязвимый образ", True),
   ("Trivy требует полный образ в registry", False),
   ("Это только рекомендация", False),
   ("Сканирование блокирует registry", False)],
  explanation="Security gate: образ собран (есть что сканировать) → проверен (нет критических CVE) → деплой. Нарушение порядка ломает смысл проверки.", order=2)

m = module(c7, "Стратегии деплоя", 4)
theory(m, "Blue-green, canary, rolling, feature flags", """\
## Стратегии деплоя

### Rolling Update
```
v1 v1 v1 v1 → v2 v1 v1 v1 → v2 v2 v1 v1 → v2 v2 v2 v2
```
+ Нет downtime, минимальные ресурсы  
− Временно работают обе версии

### Blue-Green
```
LB → Blue (v1, active)
   → Green (v2, idle) ← деплоим → тестируем → переключаем LB
```
+ Мгновенный rollback (переключить LB)  
− Двойные ресурсы

### Canary
```
LB → v1 (95%)
   → v2 (5%) → мониторинг → 10% → 50% → 100%
```
+ Минимальный риск (только 5% пользователей)

### Feature Flags
```python
if is_enabled("new_checkout", user=request.user):
    return new_checkout_view(request)
return old_checkout_view(request)
```
Инструменты: LaunchDarkly, Unleash, Flagsmith
""", 1)

ql = quiz_lesson(m, "Тест: стратегии деплоя", 2)
qz = quiz(ql)
Q(qz, "Главное преимущество Blue-Green деплоя:",
  [("Мгновенный rollback: переключить балансировщик обратно", True),
   ("Меньше ресурсов чем rolling", False),
   ("Нет нужды в балансировщике", False),
   ("Автоматически тестирует на production", False)],
  explanation="Blue-Green: два окружения живут одновременно. Rollback = 1 переключение LB. Rolling rollback сложнее.")
Q(qz, "Canary release направляет 5% трафика на новую версию. Зачем?",
  [("Выявить проблемы на малой части пользователей перед полным rollout", True),
   ("Уменьшить нагрузку на новый сервер", False),
   ("Требование compliance", False),
   ("Тестировать балансировщик", False)],
  explanation="Canary: реальные пользователи тестируют, но при ошибке затронуто только 5%. Ключ: мониторинг метрик.", order=2)

m = module(c7, "GitLab CI/CD", 5)
theory(m, ".gitlab-ci.yml: stages, jobs, runners, artifacts", """\
## GitLab CI/CD

```yaml
stages: [build, test, security, deploy]

variables:
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

build:
  stage: build
  image: docker:24
  services: [docker:dind]
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $IMAGE .
    - docker push $IMAGE

test:
  stage: test
  image: python:3.11-slim
  services:
    - postgres:15-alpine
  script: [pip install -r requirements.txt, pytest]
  artifacts:
    reports:
      junit: report.xml

trivy:
  stage: security
  image: aquasec/trivy
  script: trivy image --exit-code 1 --severity CRITICAL $IMAGE

deploy-prod:
  stage: deploy
  environment:
    name: production
    url: https://myapp.com
  script: ssh deploy@$PROD "docker pull $IMAGE && docker compose up -d"
  when: manual
  only: [tags]
```

### Ключевые переменные GitLab
```
$CI_COMMIT_SHORT_SHA  → короткий хэш
$CI_COMMIT_TAG        → тег
$CI_REGISTRY_IMAGE    → путь образа
$CI_PIPELINE_ID       → ID пайплайна
```
""", 1)

ql = quiz_lesson(m, "Тест: GitLab CI", 2)
qz = quiz(ql)
Q(qz, "Что означает 'when: manual' в GitLab CI?",
  [("Job запускается только по нажатию кнопки в интерфейсе GitLab", True),
   ("Job запускается вручную через API", False),
   ("Job требует ручного тестирования", False),
   ("Только для администраторов", False)],
  explanation="when: manual создаёт кнопку в UI пайплайна. Удобно для prod деплоя: автоматический staging, ручной production.")
Q(qz, "Для чего используется services в GitLab CI job?",
  [("Запустить дополнительные контейнеры (БД, Redis) рядом с job", True),
   ("Указать зависимые jobs", False), ("Подключить внешние API", False), ("Настроить healthcheck", False)],
  explanation="services запускает Docker-контейнеры доступные job по hostname. Аналог docker-compose для CI.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 8 — Ansible
# ═══════════════════════════════════════════════════════════════════════════ #
c8 = course(
    "ansible", "Ansible",
    "Автоматизация инфраструктуры: от первого ping до ролей и Vault. "
    "Настройка серверов, управление конфигурациями, идемпотентные playbooks.",
    "🤖", "intermediate", "iac", 35, 900, prereqs=[1, 3],
)

m = module(c8, "Введение в IaC и Ansible", 1)
theory(m, "Что такое IaC, установка Ansible, архитектура", """\
## Infrastructure as Code

IaC — управление инфраструктурой через код, а не ручные действия.

| Тип | Инструменты |
|---|---|
| Configuration Management | **Ansible**, Chef, Puppet |
| Provisioning | Terraform, Pulumi |
| Orchestration | Kubernetes |

### Ansible — agentless подход
```
Control Node (ваш ПК/CI)
      │ SSH
      ├──→ server1 (web)
      ├──→ server2 (db)
      └──→ server3 (cache)
```
Ansible копирует Python-модули на сервер, выполняет, удаляет — агент не нужен!

### Установка
```bash
pip install ansible
ansible --version

# Проверить SSH доступ к серверам:
ssh deploy@server1 "python3 --version"
```

### Идемпотентность
Многократный запуск playbook = тот же результат что и однократный.
Нет "установить ещё раз" — модули проверяют текущее состояние.
""", 1)

ql = quiz_lesson(m, "Тест: введение в Ansible", 2)
qz = quiz(ql)
Q(qz, "В чём главное отличие Ansible от Puppet и Chef?",
  [("Ansible agentless — не требует агента на управляемых серверах", True),
   ("Ansible работает быстрее", False), ("Больше модулей", False), ("Использует JSON", False)],
  explanation="Agentless = SSH. Не нужно устанавливать агент на каждом сервере. Упрощает архитектуру и безопасность.")
Q(qz, "Что такое идемпотентность в Ansible?",
  [("Многократный запуск playbook даёт тот же результат что и однократный", True),
   ("Playbook запускается только раз", False),
   ("Параллельное выполнение на всех серверах", False),
   ("Ansible не изменяет существующие файлы", False)],
  explanation="Идемпотентность: запустил 1 или 100 раз — результат одинаковый. Модули проверяют состояние прежде чем действовать.", order=2)

m = module(c8, "Inventory — список хостов", 2)
theory(m, "INI и YAML inventory, группы, host_vars, group_vars", """\
## Inventory

### INI формат
```ini
[webservers]
web1.example.com
web2.example.com ansible_user=deploy

[databases]
db1.example.com

[production:children]
webservers
databases

[webservers:vars]
nginx_port=80
```

### YAML формат
```yaml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 10.0.0.1
          nginx_port: 80
      vars:
        ansible_user: deploy
    databases:
      hosts:
        db1.example.com:
          ansible_host: 10.0.0.10
```

### group_vars и host_vars
```
inventory/
├── hosts.yml
├── group_vars/
│   ├── all.yml          # все хосты
│   └── webservers.yml   # только webservers
└── host_vars/
    └── web1.example.com.yml
```

### Команды
```bash
ansible-inventory --list    # просмотр
ansible-inventory --graph   # граф групп
ansible all -m ping         # проверить все хосты
```
""", 1)

ql = quiz_lesson(m, "Тест: inventory", 2)
qz = quiz(ql)
Q(qz, "Где хранятся переменные для группы 'webservers' в Ansible?",
  [("group_vars/webservers.yml", True), ("vars/webservers.yml", False),
   ("inventory/webservers/vars.yml", False), ("defaults/webservers.yml", False)],
  explanation="group_vars/<group_name>.yml — стандарт. host_vars/<hostname>.yml — для конкретного хоста.")
Q(qz, "Что такое [production:children] в INI inventory?",
  [("Группа production включает другие группы как дочерние", True),
   ("Производственные серверы", False), ("Под-инвентарь", False), ("Зависимости", False)],
  explanation=":children — meta-группа. production:children = webservers + databases в одной группе.", order=2)

m = module(c8, "Ad-hoc команды и модули", 3)
theory(m, "ping, command, shell, apt, service, copy, user", """\
## Ad-hoc команды

Одноразовые команды без playbook. Для быстрых задач и диагностики.

```bash
# Синтаксис
ansible <hosts> -m <module> -a "<args>"

# ping — проверить доступность (SSH + Python)
ansible all -m ping

# command — выполнить (без shell)
ansible all -m command -a "uptime"
ansible webservers -m command -a "df -h"

# shell — через /bin/sh (пайпы работают!)
ansible all -m shell -a "ps aux | grep nginx"

# apt — пакеты
ansible webservers -m apt -a "name=nginx state=present update_cache=yes" -b

# service — сервисы
ansible webservers -m service -a "name=nginx state=started enabled=yes" -b

# copy — файлы
ansible webservers -m copy -a "src=nginx.conf dest=/etc/nginx/nginx.conf" -b

# user — пользователи
ansible all -m user -a "name=deploy shell=/bin/bash groups=sudo" -b
```

### Ключевые опции
```bash
-b           # --become (sudo)
-f 10        # параллельность (forks)
--check      # dry-run
--diff       # показать diff
-vvv         # verbose (отладка)
```
""", 1)

ql = quiz_lesson(m, "Тест: ad-hoc команды", 2)
qz = quiz(ql)
Q(qz, "Чем модуль 'command' отличается от 'shell'?",
  [("command не использует shell — нет пайпов и $VAR; shell запускает через /bin/sh", True),
   ("command быстрее", False), ("shell только для Linux", False), ("command не требует become", False)],
  explanation="command безопаснее (нет shell injection). shell мощнее (пайпы, перенаправления). Используй command по умолчанию.")
Q(qz, "Флаг -b в ansible означает:",
  [("--become: выполнить с sudo", True),
   ("--background", False), ("--batch", False), ("--binary", False)],
  explanation="-b включает privilege escalation. По умолчанию становится root через sudo.", order=2)

m = module(c8, "Playbooks: handlers, when, loop, register", 4)
theory(m, "play, tasks, handlers, условия, циклы, сохранение результатов", """\
## Playbooks

```yaml
---
- name: Настройка веб-серверов
  hosts: webservers
  become: true
  vars:
    nginx_port: 80

  tasks:
    - name: Установить nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Скопировать конфиг
      template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/myapp
      notify: Reload nginx        # вызвать handler при изменении

    - name: Запустить nginx
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: Reload nginx          # только при notify + только если changed
      service:
        name: nginx
        state: reloaded
```

### when — условия
```yaml
- name: Ubuntu only
  apt:
    name: nginx
  when: ansible_os_family == "Debian"
```

### loop — циклы
```yaml
- name: Создать пользователей
  user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
  loop:
    - { name: deploy, groups: docker }
    - { name: monitor, groups: adm }
```

### register — сохранить результат
```yaml
- name: Проверить nginx
  command: nginx -v
  register: nginx_ver
  ignore_errors: yes

- name: Установить если нет
  apt:
    name: nginx
  when: nginx_ver.rc != 0
```
""", 1)

ql = quiz_lesson(m, "Тест: playbooks", 2)
qz = quiz(ql)
Q(qz, "Когда вызывается handler в Ansible?",
  [("Только если notify-задача изменила состояние (changed), один раз в конце play", True),
   ("После каждой задачи с notify", False),
   ("При каждом запуске playbook", False),
   ("Если все задачи успешны", False)],
  explanation="Handler: ОДИН РАЗ в конце play, только если задача реально изменила систему. Идеально для reload nginx.")
Q(qz, "Что делает 'register: result' в task?",
  [("Сохраняет результат задачи в переменную для следующих задач", True),
   ("Регистрирует в системном журнале", False),
   ("Создаёт checkpoint", False),
   ("Фиксирует в inventory", False)],
  explanation="register сохраняет stdout, stderr, rc, changed и т.д. Используется в when условиях следующих задач.", order=2)

m = module(c8, "Переменные, шаблоны Jinja2 и роли", 5)
theory(m, "vars, facts, templates, roles, ansible-galaxy, Vault", """\
## Переменные и шаблоны

### Ansible Facts
```yaml
- setup:  # автоматически в начале play

# Доступные факты:
# ansible_os_family       → Debian, RedHat
# ansible_hostname        → имя хоста  
# ansible_default_ipv4.address → IP
# ansible_memtotal_mb     → RAM
# ansible_processor_vcpus → CPU
```

### Jinja2 шаблон
```jinja2
{# templates/nginx.conf.j2 #}
upstream backend {
{% for host in groups['webservers'] %}
    server {{ hostvars[host]['ansible_default_ipv4']['address'] }}:{{ app_port }};
{% endfor %}
}
server {
    listen {{ nginx_port }};
    {% if ssl_enabled %}
    ssl_certificate {{ ssl_cert }};
    {% endif %}
}
```

## Роли

```
roles/nginx/
├── defaults/main.yml   # переменные (низкий приоритет)
├── tasks/main.yml      # задачи
├── handlers/main.yml   # handlers
├── templates/          # Jinja2 шаблоны
├── files/              # статические файлы
└── meta/main.yml       # зависимости
```

```yaml
# Использование роли
- hosts: webservers
  roles:
    - common
    - role: nginx
      vars:
        nginx_port: 8080
```

```bash
ansible-galaxy install geerlingguy.nginx
ansible-galaxy role init my_role
```

## Ansible Vault
```bash
ansible-vault create group_vars/all/vault.yml
ansible-vault encrypt secrets.yml
ansible-vault edit vault.yml
ansible-playbook site.yml --ask-vault-pass
```
""", 1)

ql = quiz_lesson(m, "Тест: роли и Vault", 2)
qz = quiz(ql)
Q(qz, "Зачем нужен Ansible Vault?",
  [("Хранить секреты (пароли, ключи) в зашифрованном виде прямо в репозитории", True),
   ("Ускорить выполнение playbook", False),
   ("Управлять доступом к серверам", False),
   ("Версионировать inventory", False)],
  explanation="Vault шифрует файлы AES256. Секреты можно коммитить в git — без пароля vault расшифровать невозможно.")
Q(qz, "Разница defaults/main.yml и vars/main.yml в роли:",
  [("defaults — низший приоритет (легко переопределить); vars — высший приоритет роли", True),
   ("defaults для строк; vars для сложных типов", False),
   ("Нет разницы", False),
   ("defaults только при первом запуске", False)],
  explanation="defaults/ предназначены для переопределения пользователем роли. vars/ — внутренние переменные роли.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 9 — Terraform
# ═══════════════════════════════════════════════════════════════════════════ #
c9 = course(
    "terraform", "Terraform",
    "Infrastructure as Code для облаков: создание и управление инфраструктурой "
    "через код. HCL, провайдеры, state, модули и production практики.",
    "🏗️", "intermediate", "iac", 35, 900, prereqs=[8],
)

m = module(c9, "HCL синтаксис и основные команды", 1)
theory(m, "terraform init/plan/apply, ресурсы, переменные, outputs", """\
## Terraform

### HCL — язык конфигурации
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" { region = "eu-west-1" }

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = var.instance_type
  tags = { Name = "WebServer" }
}

data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = ["production-vpc"]
  }
}
```

### Переменные
```hcl
variable "instance_type" {
  type    = string
  default = "t3.micro"
  sensitive = false
}

variable "db_password" {
  type      = string
  sensitive = true   # не выводить в логах!
}

output "server_ip" {
  value = aws_instance.web.public_ip
}

locals {
  common_tags = {
    Project   = "MyApp"
    ManagedBy = "Terraform"
  }
}
```

### Жизненный цикл
```bash
terraform init      # скачать провайдеры
terraform validate  # проверить синтаксис
terraform fmt       # форматировать
terraform plan      # dry-run (показать изменения)
terraform apply     # применить
terraform destroy   # удалить всё
terraform output    # показать outputs
```
""", 1)

theory(m, "count, for_each, depends_on, lifecycle", """\
## Продвинутые ресурсы

### for_each — несколько ресурсов из map
```hcl
variable "servers" {
  default = {
    web = { type = "t3.micro",  zone = "eu-west-1a" }
    api = { type = "t3.small",  zone = "eu-west-1b" }
  }
}

resource "aws_instance" "servers" {
  for_each = var.servers

  ami               = data.aws_ami.ubuntu.id
  instance_type     = each.value.type
  availability_zone = each.value.zone
  tags = { Name = each.key }
}
# aws_instance.servers["web"].public_ip
```

### lifecycle
```hcl
resource "aws_db_instance" "main" {
  lifecycle {
    prevent_destroy       = true   # защита от случайного удаления!
    create_before_destroy = true   # zero-downtime замена
    ignore_changes        = [tags]
  }
}
```

### depends_on — явные зависимости
```hcl
resource "aws_instance" "web" {
  depends_on = [aws_iam_role_policy.web_policy]
  # неявная: subnet_id = aws_subnet.main.id
}
```
""", 2)

ql = quiz_lesson(m, "Тест: Terraform основы", 3)
qz = quiz(ql)
Q(qz, "В каком порядке выполняются команды Terraform?",
  [("init → plan → apply", True), ("plan → init → apply", False),
   ("init → apply → plan", False), ("validate → apply", False)],
  explanation="init: скачать провайдеры. plan: показать изменения. apply: создать ресурсы.")
Q(qz, "Чем for_each лучше count?",
  [("for_each использует ключи — удаление элемента не пересоздаёт остальные", True),
   ("for_each быстрее", False), ("count нельзя с map", False), ("for_each балансирует ресурсы", False)],
  explanation="count[0,1,2]: удалить индекс 1 → 2 становится 1 → пересоздаётся! for_each{web,api}: удалить api → web не трогается.", order=2)
Q(qz, "sensitive = true для variable означает:",
  [("Значение скрыто в логах и выводе terraform (но хранится в state)", True),
   ("Значение зашифровано в state", False),
   ("Доступно только администраторам", False),
   ("Не сохраняется в state", False)],
  explanation="sensitive скрывает из консоли. НО хранится в tfstate открытым текстом — защищайте state файл!", order=3)

m = module(c9, "State и remote backend", 2)
theory(m, "tfstate, S3+DynamoDB backend, workspaces, import", """\
## Terraform State

State — соответствие между Terraform ресурсами и реальными.

### Remote Backend (S3 + DynamoDB)
```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-tf-state"
    key            = "production/terraform.tfstate"
    region         = "eu-west-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # блокировка!
  }
}
```

### Workspaces
```bash
terraform workspace new staging
terraform workspace new production
terraform workspace select staging
terraform workspace show

# В конфиге:
# instance_type = terraform.workspace == "production" ? "t3.medium" : "t3.micro"
```

### Управление state
```bash
terraform state list                     # ресурсы в state
terraform state show aws_instance.web    # детали
terraform state rm aws_instance.web      # убрать из state (не удалять!)
terraform import aws_instance.web i-123  # импортировать существующий
```

### Правила безопасности
- S3 с шифрованием (encrypt = true)
- Версионирование S3 бакета
- IAM политики для ограничения доступа
- **Никогда** не коммитить terraform.tfstate в git!
""", 1)

ql = quiz_lesson(m, "Тест: state и backend", 2)
qz = quiz(ql)
Q(qz, "Зачем DynamoDB при S3 backend?",
  [("Блокировка state: предотвращает одновременный apply нескольких пользователей", True),
   ("Хранить историю изменений", False),
   ("Ускорить чтение", False),
   ("Аутентификация в AWS", False)],
  explanation="State locking: DynamoDB хранит lock-запись. Второй apply получит ошибку и подождёт. Без locking → параллельный apply → повреждённый state.")
Q(qz, "Что делает 'terraform state rm' с ресурсом?",
  [("Удаляет из state, но НЕ уничтожает реальный ресурс в облаке", True),
   ("Уничтожает ресурс в облаке и state", False),
   ("Сбрасывает state до предыдущей версии", False),
   ("Переносит в другой workspace", False)],
  explanation="state rm убирает из 'поля зрения' Terraform. Реальный ресурс остаётся в облаке. Используется при рефакторинге.", order=2)

m = module(c9, "Модули и production практики", 3)
theory(m, "Создание модулей, Terraform Registry, CI/CD, tflint", """\
## Terraform Modules

### Структура модуля
```
modules/web-server/
├── main.tf       # ресурсы
├── variables.tf  # входные переменные
└── outputs.tf    # выходные значения
```

```hcl
# Использование
module "web_prod" {
  source        = "./modules/web-server"
  name          = "web-prod"
  instance_type = "t3.medium"
  vpc_id        = aws_vpc.main.id
}

# Terraform Registry
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  cidr    = "10.0.0.0/16"
}

output "web_ip" { value = module.web_prod.public_ip }
```

## CI/CD с Terraform
```yaml
# GitHub Actions
- uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: 1.6.0

- name: Terraform Plan (на PR)
  run: terraform plan -out=tfplan
  if: github.event_name == 'pull_request'

- name: Terraform Apply (на main)
  run: terraform apply -auto-approve
  if: github.ref == 'refs/heads/main'
```

## Инструменты
```bash
tflint               # линтер
checkov -d .         # security сканер  
infracost breakdown  # оценка стоимости
terraform-docs markdown . > README.md
```

## Ключевые правила
1. Никогда не изменять state вручную
2. Всегда plan перед apply
3. Remote state с locking в команде
4. prevent_destroy для production данных
5. Версионировать провайдеры (~> 5.0)
""", 1)

ql = quiz_lesson(m, "Тест: модули и практики", 2)
qz = quiz(ql)
Q(qz, "Как обратиться к output модуля 'web_server'?",
  [("module.web_server.public_ip", True), ("web_server.output.public_ip", False),
   ("output.web_server.public_ip", False), ("modules.web_server.public_ip", False)],
  explanation="Синтаксис: module.<module_name>.<output_name>. Аналогично ресурсам: resource_type.name.attribute.")
Q(qz, "Почему важно версионировать провайдеры (version = '~> 5.0')?",
  [("Без версии terraform init скачает последнюю — breaking changes могут сломать инфраструктуру", True),
   ("Для ускорения init", False),
   ("Обязательное требование", False),
   ("Для совместимости с Terragrunt", False)],
  explanation="~> 5.0 = принимать 5.x но не 6.0. Новая major версия может иметь несовместимые изменения.", order=2)




# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 10 — Kubernetes
# ═══════════════════════════════════════════════════════════════════════════ #
c10 = course(
    "kubernetes", "Kubernetes",
    "Оркестрация контейнеров: архитектура K8s, Pods, Deployments, Services, "
    "Ingress, ConfigMap, Secrets, RBAC, Helm и production-паттерны.",
    "☸️", "advanced", "docker", 60, 1500, prereqs=[6, 9],
)

m = module(c10, "Архитектура Kubernetes", 1)
theory(m, "Control Plane, Worker Nodes, kubectl основы", """\
## Архитектура Kubernetes

### Control Plane (мастер-узлы)
```
┌─────────────────────────────────────────┐
│             Control Plane               │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ kube-apiserver│  │   etcd (state)   │ │
│  └──────────────┘  └──────────────────┘ │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  scheduler   │  │controller-manager│ │
│  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
Worker Node  Worker Node
┌─────────┐ ┌─────────┐
│ kubelet │ │ kubelet │  ← агент, управляет Pods
│kube-proxy│ │kube-proxy│ ← сетевые правила
│ runtime │ │ runtime │  ← containerd/CRI-O
└─────────┘ └─────────┘
```

| Компонент | Роль |
|---|---|
| **kube-apiserver** | Единая точка входа для всех запросов |
| **etcd** | Распределённое key-value хранилище состояния |
| **scheduler** | Выбирает узел для размещения Pod |
| **controller-manager** | Поддерживает желаемое состояние |
| **kubelet** | Запускает и следит за Pods на узле |
| **kube-proxy** | iptables/ipvs правила для Service |

### kubectl — CLI для K8s

```bash
# Контексты
kubectl config get-contexts           # список контекстов
kubectl config use-context prod       # переключиться
kubectl config current-context        # текущий

# Основные команды
kubectl get nodes                     # узлы кластера
kubectl get pods -n kube-system       # системные pods
kubectl get all -n myapp              # всё в namespace
kubectl describe pod myapp-abc123     # подробности
kubectl logs myapp-abc123 -f          # логи
kubectl exec -it myapp-abc123 -- bash # войти в pod
kubectl apply -f manifest.yml         # применить манифест
kubectl delete -f manifest.yml        # удалить ресурсы
kubectl get events --sort-by=.lastTimestamp  # события
```

### Namespaces

```bash
kubectl create namespace myapp
kubectl get ns
kubectl config set-context --current --namespace=myapp
```
""", 1)

theory(m, "Pods: spec, containers, probes, resources", """\
## Pod — минимальная единица в K8s

Pod содержит один или несколько контейнеров с общей сетью и хранилищем.

### Манифест Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  namespace: production
  labels:
    app: myapp
    version: "1.0"
spec:
  containers:
    - name: app
      image: myrepo/myapp:1.0
      ports:
        - containerPort: 8000
      env:
        - name: DB_HOST
          value: "postgres"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password

      # Лимиты ресурсов
      resources:
        requests:          # гарантированные ресурсы
          memory: "128Mi"
          cpu: "250m"      # 250 millicores = 0.25 CPU
        limits:            # максимум
          memory: "512Mi"
          cpu: "500m"

      # Проверки здоровья
      livenessProbe:       # перезапустить если упал
        httpGet:
          path: /health
          port: 8000
        initialDelaySeconds: 10
        periodSeconds: 30
        failureThreshold: 3

      readinessProbe:      # не направлять трафик пока не готов
        httpGet:
          path: /ready
          port: 8000
        initialDelaySeconds: 5
        periodSeconds: 10

  initContainers:
    - name: wait-for-db
      image: busybox
      command: ['sh', '-c', 'until nc -z postgres 5432; do sleep 2; done']
```

### requests vs limits

- **requests**: K8s гарантирует эти ресурсы при планировании
- **limits**: контейнер не может превысить (OOMKilled если память)
- CPU throttling при превышении лимита CPU
- 1000m (millicores) = 1 CPU core
""", 2)

ql = quiz_lesson(m, "Тест: архитектура K8s", 3)
qz = quiz(ql)
Q(qz, "Какой компонент K8s хранит всё состояние кластера?",
  [("etcd", True), ("kube-apiserver", False), ("scheduler", False), ("kubelet", False)],
  explanation="etcd — распределённое key-value хранилище. Всё состояние K8s хранится в etcd. Потеря etcd = потеря кластера. Резервное копирование etcd критично!")
Q(qz, "В чём разница livenessProbe и readinessProbe?",
  [("liveness перезапускает контейнер при падении; readiness убирает из балансировки если не готов", True),
   ("liveness для базы данных; readiness для приложений", False),
   ("readiness только для HTTP; liveness для TCP", False),
   ("Это одно и то же", False)],
  explanation="liveness: 'живой ли процесс?' — перезапуск при fail. readiness: 'готов ли принимать трафик?' — убирает из Service endpoints.", order=2)
Q(qz, "Что происходит если Pod превышает limits.memory?",
  [("Контейнер убивается (OOMKilled) и перезапускается", True),
   ("Pod переносится на другой узел", False),
   ("K8s предупредит но продолжит работу", False),
   ("Превышение лимита невозможно", False)],
  explanation="OOM (Out of Memory) Killer ядра Linux убивает процесс. K8s записывает причину OOMKilled. Limits.memory — жёсткий лимит.", order=3)

m = module(c10, "Deployments и контроллеры", 2)
theory(m, "Deployment, ReplicaSet, DaemonSet, StatefulSet, Job", """\
## Контроллеры K8s

### Deployment — для stateless приложений

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp

  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # временно +1 pod во время обновления
      maxUnavailable: 0    # ни один pod не будет недоступен

  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: myrepo/myapp:1.0
          resources:
            requests: { memory: "128Mi", cpu: "100m" }
            limits:   { memory: "256Mi", cpu: "500m" }
```

```bash
kubectl rollout status deployment/myapp    # статус обновления
kubectl rollout history deployment/myapp   # история
kubectl rollout undo deployment/myapp      # откат
kubectl rollout undo deployment/myapp --to-revision=2  # к версии 2
kubectl scale deployment myapp --replicas=5            # масштабировать
```

### DaemonSet — по одному Pod на каждый узел

```yaml
kind: DaemonSet  # logshipper, node-exporter, kube-proxy
```

### StatefulSet — для stateful (БД, Kafka)

```yaml
kind: StatefulSet
# Стабильные имена: myapp-0, myapp-1, myapp-2
# Стабильное хранилище: PVC на каждый pod
# Порядок запуска/остановки гарантирован
```

### Job и CronJob

```yaml
# Job — разовая задача
apiVersion: batch/v1
kind: Job
spec:
  completions: 1
  parallelism: 1
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: migrate
          image: myapp
          command: ["python", "manage.py", "migrate"]

# CronJob — по расписанию (замена cron)
kind: CronJob
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec: ...
```
""", 1)

ql = quiz_lesson(m, "Тест: контроллеры", 2)
qz = quiz(ql)
Q(qz, "Чем StatefulSet отличается от Deployment?",
  [("Стабильные имена подов, гарантированный порядок, персистентное хранилище на каждый pod", True),
   ("StatefulSet только для БД", False),
   ("Deployment не поддерживает replicas", False),
   ("StatefulSet не поддерживает обновления", False)],
  explanation="StatefulSet: myapp-0, myapp-1... (всегда одинаковые имена), PVC не удаляется при удалении пода, порядок старта/остановки. Для Postgres, Kafka, Elasticsearch.")
Q(qz, "DaemonSet запускает pod:",
  [("На каждом узле кластера (ровно один)", True),
   ("На всех узлах с label", False),
   ("На мастер-узлах", False),
   ("На случайном узле", False)],
  explanation="DaemonSet: один pod на каждый worker node. Используется для node-exporter, fluentd, kube-proxy, cni-плагина.", order=2)

m = module(c10, "Services и Ingress", 3)
theory(m, "ClusterIP, NodePort, LoadBalancer, Ingress, IngressController", """\
## Services в Kubernetes

Service — стабильный DNS-адрес и IP для набора Pods (за счёт selector).

### Типы Services

```yaml
# ClusterIP (по умолчанию) — только внутри кластера
apiVersion: v1
kind: Service
metadata:
  name: myapp-svc
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
# DNS: myapp-svc.production.svc.cluster.local

---
# NodePort — доступ снаружи через порт узла (30000-32767)
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8000
      nodePort: 30080   # Node IP:30080 → pod:8000

---
# LoadBalancer — создаёт облачный LB (AWS ELB, GCP LB)
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8000
```

### Ingress — HTTP маршрутизация

```yaml
# Нужен Ingress Controller: nginx-ingress, traefik, kong
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
    - hosts: [myapp.com, api.myapp.com]
      secretName: myapp-tls
  rules:
    - host: myapp.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
    - host: api.myapp.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backend-svc
                port:
                  number: 8000
```

```bash
# Установка nginx-ingress (helm)
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace

kubectl get ingress -A
```
""", 1)

ql = quiz_lesson(m, "Тест: Services и Ingress", 2)
qz = quiz(ql)
Q(qz, "Какой тип Service создаёт облачный балансировщик нагрузки?",
  [("LoadBalancer", True), ("NodePort", False), ("ClusterIP", False), ("ExternalName", False)],
  explanation="LoadBalancer: K8s запрашивает у облачного провайдера (AWS ELB, GCP LB) внешний IP и настраивает маршрутизацию. Требует облачную среду.")
Q(qz, "Зачем нужен Ingress если есть LoadBalancer?",
  [("Ingress маршрутизирует HTTP/HTTPS по hostname и path — один LB для всех сервисов", True),
   ("Ingress быстрее LoadBalancer", False),
   ("LoadBalancer не поддерживает HTTPS", False),
   ("Ingress работает без облака", False)],
  explanation="Каждый LoadBalancer стоит денег. Ingress: один LB → IngressController → маршрутизация по host/path к разным сервисам. Экономия + SSL termination.", order=2)

m = module(c10, "ConfigMap, Secrets, Volumes", 4)
theory(m, "ConfigMap, Secret, PersistentVolume, PVC, StorageClass", """\
## Конфигурация и хранилище

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  APP_ENV: production
  LOG_LEVEL: info
  nginx.conf: |
    server {
      listen 80;
      ...
    }
```

```yaml
# Использование в Pod
spec:
  containers:
    - name: app
      # Как переменные окружения
      envFrom:
        - configMapRef:
            name: myapp-config

      # Как volume (файл)
      volumeMounts:
        - name: config
          mountPath: /etc/nginx/nginx.conf
          subPath: nginx.conf

  volumes:
    - name: config
      configMap:
        name: myapp-config
```

### Secret

```yaml
# Base64 кодирование (не шифрование!)
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  password: cGFzc3dvcmQxMjM=   # base64: password123

# Или stringData (автоматически кодируется)
stringData:
  password: "password123"
```

```bash
kubectl create secret generic db-secret \
  --from-literal=password=secret123

kubectl create secret tls myapp-tls \
  --cert=tls.crt --key=tls.key
```

> Secrets НЕ зашифрованы по умолчанию! Используйте Sealed Secrets или External Secrets для production.

### PersistentVolume и PVC

```yaml
# PersistentVolumeClaim — запрос хранилища
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  storageClassName: fast-ssd   # StorageClass
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 50Gi

# В Pod:
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: postgres-pvc
```
""", 1)

ql = quiz_lesson(m, "Тест: ConfigMap и Secrets", 2)
qz = quiz(ql)
Q(qz, "Secrets в Kubernetes по умолчанию:",
  [("Хранятся в etcd в base64 (не зашифрованы, только закодированы)", True),
   ("Зашифрованы AES-256", False),
   ("Хранятся только в памяти", False),
   ("Автоматически ротируются", False)],
  explanation="base64 != шифрование! Secrets безопаснее чем ConfigMap (RBAC, audit), но в etcd хранятся открыто. Для production: etcd encryption at rest + External Secrets Operator.")
Q(qz, "Чем ConfigMap отличается от Secret?",
  [("Secret для чувствительных данных (пароли, ключи); ConfigMap для обычной конфигурации", True),
   ("ConfigMap только для строк; Secret для бинарных данных", False),
   ("Secret доступен только одному namespace", False),
   ("ConfigMap нельзя монтировать как volume", False)],
  explanation="Функционально похожи, но Secret: ограниченный RBAC доступ, не выводится в describe, base64. ConfigMap: человекочитаемый, для не-секретных конфигов.", order=2)

m = module(c10, "RBAC и безопасность", 5)
theory(m, "ServiceAccount, Role, RoleBinding, ClusterRole, NetworkPolicy", """\
## RBAC в Kubernetes

Role-Based Access Control — кто может делать что с какими ресурсами.

### Концепция

```
Subject (кто?)        Verb (что?)      Resource (с чем?)
ServiceAccount   →    get, list,  →    pods, deployments,
User                  create,          secrets, configmaps
Group                 delete, patch    services, ingresses
```

### Role и RoleBinding (namespace)

```yaml
# Role — набор разрешений в namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: production
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "update"]

---
# RoleBinding — привязать Role к субъекту
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
  - kind: ServiceAccount
    name: myapp-sa
    namespace: production
  - kind: User
    name: developer@company.com
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### ServiceAccount для Pod

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/myapp  # IRSA для AWS

---
# Использовать в Deployment
spec:
  template:
    spec:
      serviceAccountName: myapp-sa
```

### NetworkPolicy — firewall для Pods

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
```
""", 1)

ql = quiz_lesson(m, "Тест: RBAC и безопасность", 2)
qz = quiz(ql)
Q(qz, "Чем Role отличается от ClusterRole в K8s?",
  [("Role действует только в одном namespace; ClusterRole — во всём кластере", True),
   ("ClusterRole мощнее Role по набору verb", False),
   ("Role только для ServiceAccount; ClusterRole для Users", False),
   ("Нет разницы, это синонимы", False)],
  explanation="Role + RoleBinding = права в конкретном namespace. ClusterRole + ClusterRoleBinding = права во всём кластере. Принцип минимальных привилегий: предпочитай Role.")
Q(qz, "Для чего нужны NetworkPolicy в Kubernetes?",
  [("Ограничить сетевой трафик между Pods (по умолчанию все pods могут общаться со всеми)", True),
   ("Настроить DNS для Pods", False),
   ("Ограничить внешний трафик через Ingress", False),
   ("Балансировать нагрузку между Pods", False)],
  explanation="По умолчанию K8s — flat network: любой Pod → любой Pod. NetworkPolicy добавляет firewall правила на уровне Pods. Требует CNI поддержки (Calico, Cilium).", order=2)

m = module(c10, "Helm и управление приложениями", 6)
theory(m, "Helm charts, values.yaml, helm install/upgrade/rollback", """\
## Helm — пакетный менеджер K8s

### Структура Helm Chart

```
myapp/
├── Chart.yaml          # метаданные
├── values.yaml         # дефолтные значения
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── _helpers.tpl    # вспомогательные шаблоны
│   └── NOTES.txt       # сообщение после установки
└── charts/             # зависимости
```

### Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: My Application Helm Chart
type: application
version: 1.2.0          # версия chart
appVersion: "2.5.1"     # версия приложения
```

### values.yaml

```yaml
replicaCount: 3

image:
  repository: myrepo/myapp
  tag: "1.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  host: myapp.com
  tls: true

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"

postgresql:
  enabled: true
  auth:
    password: ""    # задать при установке!
```

### Templates с Helm

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### Команды Helm

```bash
# Поиск и установка
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo nginx

helm install myapp ./myapp -n production \
  --set postgresql.auth.password=secret123 \
  --values prod-values.yaml

helm upgrade myapp ./myapp -n production --atomic   # rollback при ошибке
helm rollback myapp 2 -n production                  # откат к ревизии 2
helm uninstall myapp -n production

# Статус
helm list -n production
helm history myapp -n production
helm get values myapp -n production
```
""", 1)

ql = quiz_lesson(m, "Тест: Helm", 2)
qz = quiz(ql)
Q(qz, "Что такое values.yaml в Helm chart?",
  [("Файл с параметрами по умолчанию, которые можно переопределить при установке", True),
   ("Файл с секретами (зашифрованными)", False),
   ("Конфигурация самого Helm", False),
   ("Список зависимостей chart", False)],
  explanation="values.yaml = дефолтные значения. При установке: --values prod.yaml или --set key=value переопределяют их. Шаблоны используют .Values.key.")
Q(qz, "Флаг --atomic в helm upgrade означает:",
  [("Откатиться к предыдущей версии если upgrade не прошёл успешно", True),
   ("Применить изменения атомарно (всё или ничего)", False),
   ("Заблокировать параллельные upgrade", False),
   ("Не создавать новые ресурсы если они уже существуют", False)],
  explanation="--atomic: если upgrade завершился неудачно (Pod crashloop, probe fail) — Helm автоматически делает rollback. Безопаснее для production.", order=2)

m = module(c10, "HPA, PDB и production-паттерны", 7)
theory(m, "HPA, VPA, PodDisruptionBudget, resource quotas, best practices", """\
## Production-паттерны K8s

### HPA — Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70    # при >70% CPU — добавить pods
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

```bash
kubectl get hpa
kubectl describe hpa myapp-hpa
```

### PodDisruptionBudget (PDB)

```yaml
# Гарантировать минимум работающих pods при node drain / rolling update
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2       # или maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

### Resource Quotas (для namespace)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
    pods: "50"
```

### Чеклист production-деплоя

```yaml
✓ resources.requests и resources.limits заданы
✓ livenessProbe и readinessProbe настроены
✓ replicas >= 2 (для HA)
✓ PodDisruptionBudget создан
✓ HPA настроен (если нужен автоскейлинг)
✓ Pod не работает от root (runAsNonRoot: true)
✓ readOnlyRootFilesystem: true
✓ securityContext настроен
✓ NetworkPolicy ограничивает трафик
✓ Resource quotas для namespace
✓ Affinity/anti-affinity (pods на разных нодах)
```

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
        - securityContext:
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
            capabilities:
              drop: [ALL]
```
""", 1)

ql = quiz_lesson(m, "Тест: production K8s", 2)
qz = quiz(ql)
Q(qz, "Что делает HorizontalPodAutoscaler при нагрузке CPU > 70%?",
  [("Добавляет новые Pods в Deployment до maxReplicas", True),
   ("Увеличивает ресурсы CPU у существующих Pods", False),
   ("Переносит Pods на более мощные узлы", False),
   ("Уменьшает лимиты CPU", False)],
  explanation="HPA мониторит метрики и изменяет replicas в Deployment/StatefulSet. Горизонтальное масштабирование = добавление экземпляров. VPA = вертикальное (ресурсы).")
Q(qz, "Зачем PodDisruptionBudget?",
  [("Гарантирует минимум работающих pods при обслуживании узлов (drain) или rolling update", True),
   ("Ограничивает количество pods в namespace", False),
   ("Защищает от OOM", False),
   ("Настраивает автоскейлинг", False)],
  explanation="При kubectl drain node K8s выселяет Pods. PDB: minAvailable=2 → K8s не выселит pod если это нарушит минимум. Защита от accidental downtime.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 11 — Мониторинг: Prometheus & Grafana
# ═══════════════════════════════════════════════════════════════════════════ #
c11 = course(
    "monitoring-prometheus-grafana",
    "Мониторинг: Prometheus & Grafana",
    "Observability для DevOps: метрики, алерты, дашборды. Prometheus, "
    "PromQL, Alertmanager, Grafana, Loki для логов и трейсинг.",
    "📊", "intermediate", "devops", 30, 800, prereqs=[6],
)

m = module(c11, "Observability: три столпа", 1)
theory(m, "Метрики, логи, трейсы. USE и RED методология", """\
## Observability

Observability (наблюдаемость) — способность понять внутреннее состояние системы
по внешним сигналам: метрикам, логам и трейсам.

### Три столпа

| Столп | Что даёт | Инструменты |
|---|---|---|
| **Метрики** | Числа во времени: CPU, RPS, latency | Prometheus, InfluxDB |
| **Логи** | Дискретные события с контекстом | Loki, ELK, Splunk |
| **Трейсы** | Путь запроса через микросервисы | Jaeger, Tempo, Zipkin |

### USE Method (инфраструктура)

Для каждого ресурса:
- **U**tilization — насколько занят (%)
- **S**aturation — есть ли очередь/ожидание
- **E**rrors — ошибки

```
CPU: utilization=80%, saturation=run queue 5, errors=0
Disk: utilization=60%, saturation=await >100ms, errors=I/O errors
Network: utilization=40%, saturation=drops, errors=interface errors
```

### RED Method (сервисы)

Для каждого сервиса/endpoint:
- **R**ate — запросов в секунду
- **E**rrors — процент ошибок
- **D**uration — latency (p50, p95, p99)

```
API /checkout:
  Rate: 150 req/s
  Errors: 0.1% (5xx)
  Duration: p50=45ms, p95=200ms, p99=500ms
```

### SLI, SLO, SLA

```
SLI (Service Level Indicator) — метрика:
  "99.5% запросов выполнено за < 300ms"

SLO (Service Level Objective) — цель:
  "SLI должен быть >= 99% за 30 дней"

SLA (Service Level Agreement) — договор:
  "при нарушении SLO — компенсация"

Error Budget = 100% - SLO = 0.1% downtime/month = ~43 минуты
```
""", 1)

ql = quiz_lesson(m, "Тест: observability основы", 2)
qz = quiz(ql)
Q(qz, "Что измеряет 'D' в RED методологии мониторинга сервисов?",
  [("Duration — задержка запросов (latency: p50, p95, p99)", True),
   ("Deployment frequency", False),
   ("Database queries", False),
   ("Downtime percentage", False)],
  explanation="RED для сервисов: Rate (RPS), Errors (%), Duration (latency). p95=200ms означает: 95% запросов быстрее 200мс.")
Q(qz, "Error Budget в SLO — это:",
  [("Допустимый процент отказов (100% - SLO). Например SLO 99.9% = 0.1% бюджет ошибок", True),
   ("Количество денег на исправление ошибок", False),
   ("Лимит на количество инцидентов в месяц", False),
   ("Размер очереди ошибок в мониторинге", False)],
  explanation="Error Budget: 99.9% SLO → 0.1% можно 'потратить' на даунтайм. ~43 мин/мес. Если бюджет исчерпан — стоп-фича, только стабильность.", order=2)

m = module(c11, "Prometheus: архитектура и метрики", 2)
theory(m, "Scraping, exporters, типы метрик, labels, node_exporter", """\
## Prometheus

### Архитектура

```
┌─────────────────────────────────────────┐
│              Prometheus                 │
│  ┌──────────┐  ┌──────────┐            │
│  │  Scraper │  │   TSDB   │            │
│  │ (pull)   │  │(хранение)│            │
│  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌──────────┐            │
│  │  Rules   │  │  Alert   │            │
│  │ (PromQL) │  │  Manager │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
        │ pull /metrics
        ├── node_exporter:9100    (OS метрики)
        ├── myapp:8000/metrics    (app метрики)
        ├── postgres_exporter     (БД метрики)
        └── blackbox_exporter     (endpoint checks)
```

### Типы метрик

```python
from prometheus_client import Counter, Gauge, Histogram, Summary

# Counter — только растёт (запросы, ошибки)
http_requests_total = Counter('http_requests_total',
  'Total requests', ['method', 'path', 'status'])
http_requests_total.labels(method='GET', path='/api', status='200').inc()

# Gauge — любое значение (RAM, температура, queue size)
active_connections = Gauge('active_connections', 'Current connections')
active_connections.set(42)
active_connections.inc()
active_connections.dec()

# Histogram — распределение (latency)
request_duration = Histogram('request_duration_seconds',
  'Request duration', buckets=[.01, .05, .1, .25, .5, 1, 2.5, 5])
request_duration.observe(0.123)

# Summary — квантили (p50, p95, p99)
```

### prometheus.yml — конфигурация

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['node1:9100', 'node2:9100']

  - job_name: 'myapp'
    metrics_path: /metrics
    static_configs:
      - targets: ['myapp:8000']
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```
""", 1)

ql = quiz_lesson(m, "Тест: Prometheus", 2)
qz = quiz(ql)
Q(qz, "Какой тип метрики Prometheus использовать для измерения latency запросов?",
  [("Histogram (или Summary)", True), ("Counter", False), ("Gauge", False), ("Timer", False)],
  explanation="Histogram: записывает в бакеты (0-10ms, 10-50ms...), позволяет вычислять percentiles через PromQL. Counter только растёт. Gauge — текущее значение.")
Q(qz, "Prometheus использует pull или push модель сбора метрик?",
  [("Pull — Prometheus сам scrape-ит /metrics endpoint каждые N секунд", True),
   ("Push — приложения отправляют метрики в Prometheus", False),
   ("Обе модели одновременно", False),
   ("Depends on exporter type", False)],
  explanation="Pull модель: Prometheus scrape-ит цели. Преимущества: легко обнаружить упавшие цели, централизованный контроль. Pushgateway — для batch jobs.", order=2)

m = module(c11, "PromQL: язык запросов", 3)
theory(m, "Селекторы, функции rate/irate/increase, агрегация, alerting rules", """\
## PromQL

### Базовые запросы

```promql
# Просмотр метрики
http_requests_total

# Фильтрация по labels
http_requests_total{job="myapp", status="200"}
http_requests_total{status=~"5.."}         # regex: все 5xx
http_requests_total{status!~"2.."}         # не 2xx

# Range vector (диапазон времени)
http_requests_total[5m]                    # значения за 5 минут
```

### Функции

```promql
# rate — среднее в секунду за период (для counter)
rate(http_requests_total[5m])
# irate — мгновенная скорость (для спайков)
irate(http_requests_total[5m])
# increase — прирост за период
increase(http_requests_total[1h])

# Пример: RPS по endpoint
rate(http_requests_total{job="myapp"}[5m])

# Latency p95 из histogram
histogram_quantile(0.95, 
  rate(request_duration_seconds_bucket[5m])
)

# Процент ошибок
rate(http_requests_total{status=~"5.."}[5m])
/
rate(http_requests_total[5m])
* 100
```

### Агрегация

```promql
# Сумма по всем instances
sum(rate(http_requests_total[5m]))

# Группировка по полю
sum by (status)(rate(http_requests_total[5m]))
sum without (instance)(rate(http_requests_total[5m]))

# Топ-5 процессов по CPU
topk(5, rate(process_cpu_seconds_total[5m]))

# Свободная память в %
(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
```

### Alerting Rules

```yaml
# rules/myapp.yml
groups:
  - name: myapp
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          /
          rate(http_requests_total[5m])
          > 0.05
        for: 5m           # должно выполняться 5 минут
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.instance }}"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighMemoryUsage
        expr: |
          (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) > 0.85
        for: 2m
        labels:
          severity: warning
```
""", 1)

ql = quiz_lesson(m, "Тест: PromQL", 2)
qz = quiz(ql)
Q(qz, "Что делает функция rate() в PromQL?",
  [("Вычисляет среднее значение counter в секунду за заданный период", True),
   ("Возвращает последнее значение метрики", False),
   ("Вычисляет максимальное значение за период", False),
   ("Конвертирует Gauge в Counter", False)],
  explanation="rate(http_requests_total[5m]) = (последнее - первое значение за 5 мин) / 300 секунд. Даёт RPS. Только для Counter типа метрик.")
Q(qz, "Как вычислить p95 latency из Histogram метрики?",
  [("histogram_quantile(0.95, rate(duration_seconds_bucket[5m]))", True),
   ("percentile(95, duration_seconds[5m])", False),
   ("p95(rate(duration_seconds[5m]))", False),
   ("quantile(0.95, duration_seconds_sum)", False)],
  explanation="histogram_quantile вычисляет квантиль из _bucket метрики. 0.95 = p95. rate() для получения per-second rate из бакетов за период.", order=2)

m = module(c11, "Alertmanager и Grafana", 4)
theory(m, "Alertmanager: routes/receivers. Grafana: dashboards, variables, alerts", """\
## Alertmanager

Получает алерты от Prometheus, дедуплицирует, группирует и отправляет уведомления.

### alertmanager.yml

```yaml
global:
  slack_api_url: 'https://hooks.slack.com/services/...'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s        # ждать перед первой нотификацией
  group_interval: 5m     # интервал повторных уведомлений
  repeat_interval: 4h    # повтор если алерт не resolve
  receiver: 'slack-ops'

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      continue: true     # продолжить matching следующих routes

    - match:
        team: database
      receiver: 'slack-db-team'

receivers:
  - name: 'slack-ops'
    slack_configs:
      - channel: '#ops-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'your-key'

inhibit_rules:
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['alertname']  # подавить warning если есть critical
```

## Grafana

### Основные концепции

```
Data Source → Query → Panel → Dashboard

Data Sources: Prometheus, Loki, InfluxDB, PostgreSQL...
Panels: Graph, Stat, Table, Gauge, Heatmap, Logs...
Variables: ${namespace}, ${instance} — фильтры дашборда
```

### Полезные дашборды (импорт по ID)

| ID | Дашборд |
|---|---|
| 1860 | Node Exporter Full |
| 3662 | Prometheus 2.0 Stats |
| 13332 | Kubernetes Cluster |
| 15661 | Kubernetes Pod |
| 12611 | Loki Logs |

```bash
# Установка Grafana через Docker
docker run -d -p 3000:3000 \
  -v grafana_data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=secret \
  grafana/grafana:latest
```

### Grafana как code (Grafana-as-Code)

```bash
# grafonnet, grafana-dashboard-exporter
# Terraform provider для Grafana
```
""", 1)

ql = quiz_lesson(m, "Тест: Alertmanager и Grafana", 2)
qz = quiz(ql)
Q(qz, "Что делает inhibit_rules в Alertmanager?",
  [("Подавляет менее серьёзные алерты если уже есть более серьёзный о той же проблеме", True),
   ("Ограничивает количество алертов в час", False),
   ("Блокирует алерты от конкретных хостов", False),
   ("Отменяет алерт если он длится меньше N минут", False)],
  explanation="Inhibition: если есть critical алерт — не отправлять warning для той же проблемы. Убирает шум. Например: node down → не слать алерты сервисов на этой ноде.")
Q(qz, "Зачем использовать Variables в Grafana дашборде?",
  [("Динамические фильтры: выбрать namespace/instance/job без создания отдельных дашбордов", True),
   ("Хранить значения между перезагрузками", False),
   ("Шифровать данные в дашборде", False),
   ("Версионировать дашборды", False)],
  explanation="Variables ${namespace} = dropdown фильтр. Один дашборд для всех namespaces/instances. Запросы используют переменную: {namespace='$namespace'}.", order=2)

m = module(c11, "Loki: сбор и анализ логов", 5)
theory(m, "Loki + Promtail, LogQL, интеграция с Grafana", """\
## Loki — система агрегации логов

«Prometheus для логов»: индексирует только labels, не содержимое → дёшево.

### Архитектура

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│Promtail  │────→│  Loki    │────→│ Grafana  │
│(агент)   │     │(хранение)│     │(запросы) │
└──────────┘     └──────────┘     └──────────┘

Promtail читает /var/log/*.log и отправляет в Loki с labels.
```

### Установка (Docker Compose)

```yaml
services:
  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]
    volumes:
      - ./loki-config.yml:/etc/loki/config.yml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
```

### promtail-config.yml

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: nginx
    static_configs:
      - targets: [localhost]
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log

  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: [__meta_docker_container_name]
        target_label: container
```

### LogQL — язык запросов

```logql
# Все логи nginx за последний час
{job="nginx"}

# Фильтрация по содержимому
{job="nginx"} |= "error"
{job="nginx"} != "healthcheck"
{job="nginx"} |~ "5[0-9]{2}"   # regex: 5xx

# Парсинг JSON логов
{job="myapp"} | json | level="error"

# Парсинг logfmt
{job="myapp"} | logfmt | duration > 1s

# Метрики из логов
rate({job="nginx"} |= "error" [5m])
count_over_time({job="nginx"} |~ "5[0-9]{2}" [1h])
```
""", 1)

ql = quiz_lesson(m, "Тест: Loki и логи", 2)
qz = quiz(ql)
Q(qz, "Чем Loki отличается от ELK Stack в подходе к индексированию?",
  [("Loki индексирует только labels, не содержимое логов — это дешевле и быстрее", True),
   ("Loki индексирует всё содержимое как Elasticsearch", False),
   ("Loki не поддерживает полнотекстовый поиск", False),
   ("Loki хранит только последние 24ч логов", False)],
  explanation="ELK: полное индексирование → дорого. Loki: только labels (job, container, host) + сжатые чанки. Поиск по содержимому через grep-подобные фильтры в LogQL.")
Q(qz, "Что делает оператор |= в LogQL?",
  [("Фильтрует строки логов содержащие подстроку", True),
   ("Объединяет несколько log streams", False),
   ("Парсит JSON из лога", False),
   ("Применяет regex к логу", False)],
  explanation="|= 'error' — содержит строку. != 'debug' — не содержит. |~ 'regex' — соответствует regex. !~ 'regex' — не соответствует.", order=2)


# ═══════════════════════════════════════════════════════════════════════════ #
#  КУРС 12 — DevSecOps
# ═══════════════════════════════════════════════════════════════════════════ #
c12 = course(
    "devsecops", "DevSecOps",
    "Безопасность встроенная в CI/CD: SAST, DAST, container security, "
    "secrets management, supply chain security и compliance as code.",
    "🔐", "advanced", "devops", 25, 700, prereqs=[6, 7],
)

m = module(c12, "Shift-left: безопасность в DevOps", 1)
theory(m, "OWASP Top 10, threat modeling, security в CI/CD", """\
## DevSecOps — Security as Code

«Сдвиг влево» (shift-left): выявлять уязвимости на этапе разработки,
а не после деплоя в production.

```
Traditional:  Dev → Build → Test → Deploy → [Security Audit]
DevSecOps:    [Sec]Dev → [Sec]Build → [Sec]Test → [Sec]Deploy → [Sec]Monitor
```

### OWASP Top 10 (2021)

| # | Уязвимость | Пример |
|---|---|---|
| A01 | Broken Access Control | Доступ к чужим данным |
| A02 | Cryptographic Failures | Пароли в MD5, HTTP |
| A03 | Injection | SQL, NoSQL, OS injection |
| A04 | Insecure Design | Нет rate limiting |
| A05 | Security Misconfiguration | Default passwords, debug mode |
| A06 | Vulnerable Components | npm audit: 47 vulnerabilities |
| A07 | Auth Failures | Брутфорс, слабые токены |
| A08 | Software Integrity Failures | Непроверенные зависимости |
| A09 | Logging Failures | Нет аудита, нет алертов |
| A10 | SSRF | Запросы к internal network |

### Security Gates в CI/CD

```yaml
# .github/workflows/security.yml
jobs:
  security:
    steps:
      - name: SAST (Static Analysis)
        uses: returntocorp/semgrep-action@v1

      - name: Dependency scan
        run: |
          pip audit           # Python
          npm audit --audit-level high  # Node.js

      - name: Container scan
        uses: aquasecurity/trivy-action@master
        with:
          exit-code: 1
          severity: HIGH,CRITICAL

      - name: Secret scan
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified

      - name: IaC scan
        run: checkov -d . --framework terraform --soft-fail
```

### Принцип Defense in Depth

```
Уровень 1: Network (firewall, WAF, DDoS)
Уровень 2: Host (hardening, patch, EDR)
Уровень 3: Application (OWASP, auth, validation)
Уровень 4: Data (encryption, backup, DLP)
Уровень 5: Monitoring (SIEM, alerting, IR)
```
""", 1)

ql = quiz_lesson(m, "Тест: DevSecOps основы", 2)
qz = quiz(ql)
Q(qz, "Что означает 'shift-left' в контексте безопасности?",
  [("Проверять безопасность на ранних этапах разработки, а не только перед деплоем", True),
   ("Переместить security команду в левое крыло офиса", False),
   ("Уменьшить количество security проверок", False),
   ("Использовать только open-source инструменты безопасности", False)],
  explanation="Чем раньше найдена уязвимость — тем дешевле исправить. В dev: минуты. В prod: часы + инцидент + репутационные риски. Shift-left = безопасность с первого коммита.")
Q(qz, "Какая OWASP категория описывает SQL-инъекции?",
  [("A03: Injection", True), ("A01: Broken Access Control", False),
   ("A06: Vulnerable Components", False), ("A05: Security Misconfiguration", False)],
  explanation="A03 Injection: SQL, NoSQL, OS, LDAP injection. Профилактика: параметризованные запросы, ORM, валидация входных данных.", order=2)

m = module(c12, "SAST, DAST и анализ зависимостей", 2)
theory(m, "semgrep, bandit, trivy, OWASP ZAP, dependency scanning", """\
## Статический и динамический анализ

### SAST — Static Application Security Testing

Анализ исходного кода без выполнения.

```bash
# Semgrep — универсальный (Python, JS, Go, Java...)
pip install semgrep
semgrep --config=auto .                    # дефолтные правила
semgrep --config=p/django .               # правила для Django
semgrep --config=p/secrets .              # поиск секретов

# Bandit — только Python
pip install bandit
bandit -r ./src -l                        # рекурсивно, только high
bandit -r ./src -f json -o bandit.json   # JSON отчёт для CI

# Sonar Scanner
docker run sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey=myapp \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.login=token
```

### Анализ зависимостей (SCA)

```bash
# Python
pip audit                    # CVE в пакетах
safety check -r requirements.txt

# Node.js
npm audit
npm audit --audit-level=high  # только high/critical

# Trivy — универсальный
trivy fs .                           # файловая система
trivy image myapp:latest             # Docker образ
trivy repo https://github.com/...   # git репозиторий
trivy --severity HIGH,CRITICAL myapp:latest

# Snyk
snyk test                   # анализ зависимостей
snyk monitor                # отслеживать постоянно
snyk container test myapp:latest
```

### DAST — Dynamic Application Security Testing

Тестирование работающего приложения.

```bash
# OWASP ZAP — полное сканирование
docker run owasp/zap2docker-stable zap-baseline.py \
  -t https://staging.myapp.com \
  -r zap-report.html

# Nuclei — шаблонное сканирование
nuclei -u https://staging.myapp.com \
  -t nuclei-templates/vulnerabilities/ \
  -severity critical,high

# В CI/CD (только после деплоя в staging):
- name: DAST scan
  run: |
    docker run owasp/zap2docker-stable zap-baseline.py \
      -t $STAGING_URL -J zap.json
  continue-on-error: true   # не блокировать при находках
```

### Secret Detection

```bash
# TruffleHog — поиск в git истории
trufflehog git https://github.com/org/repo --only-verified

# Gitleaks
gitleaks detect --source . --report-format json
gitleaks protect --staged  # pre-commit hook
```
""", 1)

ql = quiz_lesson(m, "Тест: SAST и DAST", 2)
qz = quiz(ql)
Q(qz, "В чём разница SAST и DAST?",
  [("SAST анализирует исходный код статически; DAST тестирует работающее приложение", True),
   ("SAST только для Python; DAST для всех языков", False),
   ("DAST быстрее SAST", False),
   ("SAST и DAST — одно и то же", False)],
  explanation="SAST: код → уязвимости (быстро, без запуска, много false positives). DAST: запущенное приложение → реальные уязвимости (медленно, но более точно).")
Q(qz, "Команда 'trivy image myapp:latest' делает:",
  [("Сканирует Docker образ на CVE уязвимости в ОС пакетах и языковых зависимостях", True),
   ("Запускает образ и тестирует его", False),
   ("Удаляет уязвимые слои образа", False),
   ("Проверяет Dockerfile на ошибки конфигурации", False)],
  explanation="Trivy анализирует: базовый образ (Ubuntu, Alpine пакеты), pip/npm/gem/maven зависимости, конфиги Dockerfile. Без запуска контейнера.", order=2)

m = module(c12, "Container Security и Supply Chain", 3)
theory(m, "Image hardening, Falco runtime, SBOM, sigstore/cosign", """\
## Безопасность контейнеров

### Hardening образов

```dockerfile
# ✓ Минимальный базовый образ
FROM python:3.11-slim          # не FROM python:3.11
FROM gcr.io/distroless/python3  # ещё меньше (без shell!)

# ✓ Non-root пользователь
RUN useradd -r -u 1001 appuser
USER appuser

# ✓ Read-only filesystem
# docker run --read-only --tmpfs /tmp myapp

# ✓ Конкретный тег (не :latest)
FROM nginx:1.25.3-alpine       # не FROM nginx:latest

# ✓ Конкретный digest
FROM nginx@sha256:a08f...      # неизменяемый
```

### Trivy в CI/CD

```yaml
- name: Scan image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    exit-code: 1
    severity: CRITICAL
    ignore-unfixed: true      # игнорировать без патча

- name: Upload to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

### Falco — Runtime Security

```yaml
# Обнаруживает аномальное поведение в реальном времени
# Правила Falco:
- rule: Shell spawned in container
  desc: A shell was spawned in a container
  condition: >
    spawned_process and container
    and proc.name in (shell_binaries)
  output: "Shell spawned in container (user=%user.name container=%container.name)"
  priority: WARNING

- rule: Sensitive file read
  condition: >
    open_read and container
    and (fd.name startswith /etc/shadow or
         fd.name startswith /etc/ssh)
  output: "Sensitive file read in container"
  priority: ERROR
```

### SBOM и Supply Chain

```bash
# SBOM — Software Bill of Materials (список всех зависимостей)
syft myapp:latest -o spdx-json > sbom.json
grype sbom:sbom.json            # проверить SBOM на CVE

# Подписать образ (sigstore/cosign)
cosign sign myrepo/myapp:latest
cosign verify myrepo/myapp:latest

# В CI/CD (после push образа):
- run: cosign sign --key cosign.key myrepo/myapp:${{ github.sha }}
```
""", 1)

ql = quiz_lesson(m, "Тест: container security", 2)
qz = quiz(ql)
Q(qz, "Почему лучше использовать digest вместо тега в FROM?",
  [("Digest неизменяем: FROM nginx@sha256:abc гарантирует точно этот образ навсегда", True),
   ("Digest быстрее загружается", False),
   ("Тег :latest не работает в production", False),
   ("Digest уменьшает размер образа", False)],
  explanation="Тег может быть перезаписан. FROM nginx:1.25 сегодня и через месяц = разные образы! Digest sha256 — криптографический хэш, неизменяем.")
Q(qz, "Что такое SBOM?",
  [("Software Bill of Materials — полный список компонентов и зависимостей в приложении/образе", True),
   ("Security Baseline Operations Manual", False),
   ("System Backup Operations Manager", False),
   ("Список CVE уязвимостей", False)],
  explanation="SBOM: как состав продукта. Позволяет быстро найти что затронуто новой CVE. Стандарты: SPDX, CycloneDX. Требуется по US Executive Order 14028.", order=2)

m = module(c12, "Secrets Management и Compliance", 4)
theory(m, "HashiCorp Vault, SOPS, External Secrets, CIS Benchmarks", """\
## Управление секретами

### HashiCorp Vault

```bash
# Запуск Vault (dev mode)
docker run -d -p 8200:8200 \
  -e VAULT_DEV_ROOT_TOKEN_ID=myroot \
  hashicorp/vault

export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='myroot'

# Базовые операции
vault kv put secret/myapp db_password=secret123
vault kv get secret/myapp
vault kv get -field=db_password secret/myapp

# Аренда секретов (динамические)
vault secrets enable database
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@postgres:5432/mydb" \
  allowed_roles="myapp"

# Каждый раз новый временный пароль!
vault read database/creds/myapp
```

### External Secrets Operator (K8s)

```yaml
# Синхронизирует секреты из Vault/AWS SM/GCP SM в K8s Secret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: myapp-secret     # K8s Secret который создаётся
  data:
    - secretKey: db_password
      remoteRef:
        key: secret/myapp
        property: db_password
```

### SOPS — зашифрованные файлы

```bash
# Шифровать файл с ключом AWS KMS
sops --kms arn:aws:kms:eu-west-1:123:key/abc \
  --encrypt secrets.yaml > secrets.enc.yaml

# Расшифровать
sops --decrypt secrets.enc.yaml

# Работать с зашифрованным файлом напрямую
sops secrets.enc.yaml    # открывает в редакторе
```

### Compliance as Code

```bash
# CIS Benchmarks — проверка конфигурации безопасности
# kube-bench — K8s
docker run --rm aquasec/kube-bench:latest

# OpenSCAP — Linux hardening
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis \
  /usr/share/xml/scap/ssg/content/ssg-ubuntu2204-ds.xml

# Checkov — IaC
checkov -d . \
  --framework terraform,kubernetes \
  --check CKV_K8S_14,CKV_K8S_37   # конкретные проверки

# OPA/Gatekeeper — Policy as Code для K8s
# Запрещает запуск от root, требует labels, limits
```
""", 1)

ql = quiz_lesson(m, "Тест: secrets management", 2)
qz = quiz(ql)
Q(qz, "Главное преимущество динамических секретов HashiCorp Vault:",
  [("Каждое приложение получает временный уникальный пароль с TTL — утечка одного не компрометирует всё", True),
   ("Пароли автоматически сложнее", False),
   ("Секреты не хранятся на диске", False),
   ("Vault быстрее чем .env файлы", False)],
  explanation="Динамические секреты: Vault создаёт временный DB пользователь только для этого прило��ения. Истёк TTL → пользователь удалён. Утечка = ограниченный ущерб.")
Q(qz, "External Secrets Operator в K8s нужен для:",
  [("Синхронизации секретов из внешних хранилищ (Vault, AWS SM) в K8s Secrets автоматически", True),
   ("Шифрования K8s Secrets", False),
   ("Замены Kubernetes Secrets", False),
   ("Ротации TLS сертификатов", False)],
  explanation="ESO: единый источник правды (Vault/AWS SM) → автоматически создаёт K8s Secrets. Не нужно вручную синхронизировать. Поддерживает rotation.", order=2)



# ─────────────────────────────── финальный вывод ────────────────────────── #
print(json.dumps(data, ensure_ascii=False, indent=2))
