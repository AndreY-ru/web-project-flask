# 🎓 Личный кабинет студента ЭТИ СГТУ

Веб-приложение для управления учебным процессом студентов, разработанное в рамках летней практики ЭТИ СГТУ.

## 🚀 О проекте

Проект создан с целью расширения функциональности стандартного личного кабинета студента и повышения его значимости в учебном процессе. В настоящее время ведется активная разработка и добавление нового функционала.

---

## 🖥️ Визуальная демонстрация

<div align="center" style="background-color:#0d1117; padding: 20px; border-radius: 15px;">
  
  <h3 align="center" style="color:#fff;">🔐 Авторизация</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/Авторизация.png" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Экран входа в систему с проверкой учетных данных</sub>
  
  <br><br>
  <h3 align="center" style="color:#fff;">👤 Главная страница и профиль</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/Главная.png" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Отображение личных данных, разделов и навигации</sub>

  <br><br>
  <h3 align="center" style="color:#fff;">📸 Смена аватара</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/ава.gif" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Процесс выбора и загрузки новой фотографии профиля</sub>
  
  <br><br>
  <h3 align="center" style="color:#fff;">🗂️ Работа с файлами в портфолио</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/загрузка_выгрузка.gif" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Загрузка и скачивание учебных материалов и работ</sub>

  <br><br>
  <h3 align="center" style="color:#fff;">📰 Новости и детали</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/Детали_новости.png" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Отображение списка и подробностей новостных объявлений</sub>

  <br><br>
  <h3 align="center" style="color:#fff;">📚 Дисциплины и оценки</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/Дисциплины.png" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Список предметов, баллы и прогресс обучения</sub>
  
  <br><br>
  <h3 align="center" style="color:#fff;">♿ Режим для слабовидящих</h3>
  <img src="https://github.com/AndreY-ru/web-project-flask/blob/main/Screenshot/для_слабовидящих.gif" width="80%" style="border-radius:10px;">
  <br>
  <sub style="color:gray;">Переключение режима с настройкой контраста, текста и озвучки</sub>
</div>

---
## 📋 Функциональность

- ✅ **Авторизация студентов** - вход через учетные данные
- 👤 **Личный кабинет** - персональные данные и профиль
- 📸 **Управление фото профиля** - загрузка и удаление
- 📚 **Портфолио достижений** - сбор академических работ
- 📰 **Новостная лента** - актуальные объявления
- 📊 **Учебная деятельность** - успеваемость и расписание
- 📎 **Файловый менеджер** - загрузка учебных материалов
- 🎯 **Система оценок** - отслеживание академического прогресса
- 📱 **Адаптация под разные экраны** - повышение удобства под разные экраны
- ♿ **Режим для слабовидящих** - полная кастомизация отображения контента + озвучка текста

## 🛠️ Технологии

### Backend:
- **Flask** - веб-фреймворк
- **Python** - основной язык программирования
- **PyMySQL** - подключение к MySQL
- **Werkzeug** - работа с файлами и безопасность
- **Unidecode** - обработка текста

### Frontend:
- **HTML/CSS** - верстка и стили
- **JavaScript** - интерактивность
- **AJAX** - динамическая загрузка данных

### База данных:
- **MySQL** - система управления базами данных

## ⚡ Быстрый старт

### Предварительные требования
- Python 3.8+
- MySQL 5.7+

### Установка зависимостей:
```python
pip install Flask PyMySQL Unidecode Werkzeug cryptography
```
### Настройка базы данных: 
- Создайте базу данных MySQL
- Запустите инициализацию БД: (в данном случае запустите `init_db.py`)
- Настройте подключение в файле config.py:

```python
host = "localhost"
user = "your_username"
password = "your_password"
port = 3306
db_name = "student_portal"
```
Запуск приложения
```python
python app.py
```
Приложение будет доступно по адресу: `http://localhost:5000`

### 📁 Структура проекта
```text
student_portal/                   # Корневая папка проекта
│
├── app/                          # Основное приложение
│   ├── static/                   # Статические файлы (CSS, JS, изображения, файлы)
│   │   ├── css/                  # CSS стили
│   │   │   └── style.css
│   │   ├── js/                   # JavaScript файлы
│   │   │   └── script.js
│   │   └──uploads/                # Загружаемые файлы
│   └── templates/                 # HTML-шаблоны Jinja2
│       ├── base.html              # Базовый шаблон
│       ├── user.html              # Главная страница
│       ├── login.html             # Авторизация
│       ├── education.html         # Образование
│       ├── news_list.html         # все новости
│       ├── news_detail.html       # детали новостей
│       ├── portfolio.html         # Портфолио
│       └── subject.html           # Дисциплины и оценки
├── config.py                      # Настройки приложения (подключение к БД и др.)
├── app.py                         # Точка входа — запуск Flask-приложения
└──init_db.py    	                 # Пайтон файл с настройкой БД – при тестировании БД
```

### 👨‍💻 Разработчик
**Григорьев Андрей Сергеевич**
<p align="center"><sub>© Разработано в рамках летней практики 2025 для ЭТИ СГТУ</sub></p>
