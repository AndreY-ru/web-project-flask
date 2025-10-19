import pymysql as db
from config import host, user, password, port, db_name
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()
print()

def create_students_table():
    try:
        connection = db.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            cursorclass=db.cursors.DictCursor
        )
        print("Успешное подключение к базе данных!")

        with connection.cursor() as cursor:
            # 1. departments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `departments` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    short_name VARCHAR(20)
                )
            """)
            print("Таблица departments успешно создана!")

            # 2. groups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `student_groups` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    short_name VARCHAR(20) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    department_id INT,
                    study_form ENUM('очная', 'очно-заочная', 'заочная', 'сокращенная'),
                    course TINYINT NOT NULL,
                    key_groups VARCHAR(100) NOT NULL,
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                )
            """)
            print("Таблица student_groups успешно создана!")

            # 3. students
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    password_hash VARCHAR(255) NOT NULL,
                    city VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    surname VARCHAR(100) NOT NULL,
                    birth_date DATE,
                    phone VARCHAR(20),
                    VK_id VARCHAR(255) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    orientation VARCHAR(100) NOT NULL,
                    record_book VARCHAR(50),
                    schedule VARCHAR(255) NOT NULL,
                    profile_photo VARCHAR(255),  # Новое поле для пути к фото
                    group_id INT,
                    FOREIGN KEY (group_id) REFERENCES student_groups(id)
                )
            """)
            print("Таблица studens успешно создана!")

            # 4. news
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `news` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    publish_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    author VARCHAR(100),
                    link VARCHAR(255) DEFAULT NULL, -- опциональная ссылка на статью
                    is_global BOOLEAN DEFAULT FALSE -- новость для всех групп
                )
            """)
            print("Таблица news успешно создана!")

            # 5. news_groups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `news_groups` (
                    news_id INT,
                    group_id INT,
                    PRIMARY KEY (news_id, group_id),
                    FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE,
                    FOREIGN KEY (group_id) REFERENCES student_groups(id) ON DELETE CASCADE
                )
            """)
            print("Таблица news_groups успешно создана!")

            # 6. portfolio_items
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `portfolio_items` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    category ENUM('general', 'courseworks', 'practical', 'achievements', 'mobility') NOT NULL,
                    title VARCHAR(255),               -- заголовок или название записи (можно null, если не нужно)
                    description TEXT,                 -- основной текст из textarea
                    file_path VARCHAR(255),           -- путь к загруженному файлу (если есть)
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id)
                );
            """)
            print("Таблица portfolio_items успешно создана!")

            # 7. semesters - оставляем как есть, хорошая база
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `semesters` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,      -- Например, "1 семестр 2025"
                    start_date DATE,
                    end_date DATE,
                    is_current BOOLEAN DEFAULT FALSE  -- Добавил флаг текущего семестра
                );
            """)
            print("Таблица semesters успешно создана!")

            # 8. subjects - дисициплина
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `subjects` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(20) UNIQUE,  -- Код дисциплины (например "MATH-101")
                    description TEXT,
                    credits TINYINT,  -- Количество зачетных единиц
                    is_elective BOOLEAN DEFAULT FALSE  -- Элективный курс
                );
            """)
            print("Таблица subjects успешно создана!")

            # 9. subject_groups - связь предметов с группами (новая таблица)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `subject_groups` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_id INT NOT NULL,
                    group_id INT NOT NULL,
                    semester_id INT NOT NULL,
                    teacher_id INT,  -- Можно добавить позже
                    classroom VARCHAR(50),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id),
                    FOREIGN KEY (group_id) REFERENCES student_groups(id),
                    FOREIGN KEY (semester_id) REFERENCES semesters(id),
                    UNIQUE KEY unique_subject_group (subject_id, group_id, semester_id)
                );
            """)
            print("Таблица subject_groups успешно создана!")

            # 10. subject_assessments - формы отчетности
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `subject_assessments` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_group_id INT NOT NULL,
                    form_name VARCHAR(100) NOT NULL,  -- "Экзамен", "Контрольная работа"
                    max_score DECIMAL(5,2),
                    weight DECIMAL(3,2) DEFAULT 1.0,  -- Вес в итоговой оценке
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id)
                );
            """)
            print("Таблица subject_assessments успешно создана!")

            # 11. grades - модифицированная версия
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `grades` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    subject_group_id INT NOT NULL,
                    total_score DECIMAL(5,2) DEFAULT 0.0,
                    grade_letter VARCHAR(10),
                    is_passed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id),
                    UNIQUE KEY unique_student_subject (student_id, subject_group_id)
                );
            """)
            print("Таблица grades успешно создана!")

            # 12. grade_components - детализация оценок
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `grade_components` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    grade_id INT NOT NULL,
                    assessment_id INT NOT NULL,
                    score DECIMAL(5,2),
                    FOREIGN KEY (grade_id) REFERENCES grades(id),
                    FOREIGN KEY (assessment_id) REFERENCES subject_assessments(id)
                );
            """)
            print("Таблица grade_components успешно создана!")



            # 13. Преподаватели
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `teachers` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    surname VARCHAR(100) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    patronymic VARCHAR(100),
                    position VARCHAR(100),  -- Должность (доцент, профессор и т.д.)
                    department_id INT,
                    email VARCHAR(100),
                    profile_photo VARCHAR(255),
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                )
            """)
            print("Таблица teachers успешно создана!")

            # 14. Связь преподавателей с предметами
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `teacher_subjects` (
                    teacher_id INT NOT NULL,
                    subject_group_id INT NOT NULL,
                    PRIMARY KEY (teacher_id, subject_group_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id)
                )
            """)
            print("Таблица teacher_subjects успешно создана!")

            # 15. Учебные материалы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `course_materials` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_group_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    file_path VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id)
                )
            """)
            print("Таблица course_materials успешно создана!")

            # 16. Виды учебной деятельности
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `activity_types` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_group_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,  -- Лекции, практические и т.д.
                    max_score DECIMAL(5,2) NOT NULL,
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id)
                )
            """)
            print("Таблица activity_types успешно создана!")

            # 17. Оценки по видам деятельности
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `activity_scores` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    activity_type_id INT NOT NULL,
                    score DECIMAL(5,2) NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (activity_type_id) REFERENCES activity_types(id)
                )
            """)
            print("Таблица activity_scores успешно создана!")

            # 18. Учебные задания
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `assignments` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject_group_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    max_score DECIMAL(5,2) NOT NULL,
                    deadline DATETIME,
                    FOREIGN KEY (subject_group_id) REFERENCES subject_groups(id)
                )
            """)
            print("Таблица assignments успешно создана!")

            # 19. Статусы заданий студентов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `student_assignments` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT NOT NULL,
                    assignment_id INT NOT NULL,
                    status ENUM('Не отправлено', 'Отправлено', 'Проверено', 'Принято', 'На доработку') DEFAULT 'Не отправлено',
                    score DECIMAL(5,2),
                    feedback TEXT,
                    submitted_at DATETIME,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (assignment_id) REFERENCES assignments(id),
                    UNIQUE KEY unique_student_assignment (student_id, assignment_id)
                )
            """)
            print("Таблица student_assignments успешно создана!")




            #добавление кафедр
            departments_data = [
                ("Естественные и математические науки", "ЕМН"),
                ("Оборудование и технологии обработки материалов", "ОТМ"),
                ("Технолоия и оборудование химических, нефтегазовых и пищевых производств", "ТОХП"),
                ("Экономика и гуманитарные науки", "ЭГН"),
            ]

            cursor.executemany("INSERT INTO departments (name, short_name) VALUES (%s, %s)", departments_data)
            connection.commit()
            print("Тестовые кафедры добавлены.")

            #добавление групп
            student_groups_data = [
                ("ПИНЖ", "Программная инженерия", 1, "очная", 1, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "очная", 2, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "очная", 3, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "очная", 4, "09.03.04"),

                ("ИВЧТ", "Информатика и вычислительная техника", 1, "очная", 1, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "очная", 2, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "очная", 3, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "очная", 4, "09.03.01"),
                
                ("ТМОБ", "Технологические машины и оборудование", 2, "очная", 1, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "очная", 2, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "очная", 3, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "очная", 4, "15.03.02"),

                ("ПИНЖ", "Программная инженерия", 1, "заочная", 1, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "заочная", 2, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "заочная", 3, "09.03.04"),
                ("ПИНЖ", "Программная инженерия", 1, "заочная", 4, "09.03.04"),

                ("ИВЧТ", "Информатика и вычислительная техника", 1, "заочная", 1, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "заочная", 2, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "заочная", 3, "09.03.01"),
                ("ИВЧТ", "Информатика и вычислительная техника", 1, "заочная", 4, "09.03.01"),
                
                ("ТМОБ", "Технологические машины и оборудование", 2, "заочная", 1, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "заочная", 2, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "заочная", 3, "15.03.02"),
                ("ТМОБ", "Технологические машины и оборудование", 2, "заочная", 4, "15.03.02"),
            ]
            cursor.executemany("""
                INSERT INTO student_groups (short_name, name, department_id, study_form, course, key_groups)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, student_groups_data)

            connection.commit()
            print("Тестовые группы добавлены.")

            #добавление студентов
            students = [
                # ПИНЖ очное обучение 3 курса
                ('password', 'Энгельс', 'Григорьев', 'Андрей', 'Сергеевич', "uploads/profile_photos/2025-07-10_03-18-45.png", "231449",
                '2004-12-13', '79003134771', 'vk.com/ivanov', 'user1@example.com', 'Программная инженерия',
                'http://link.to/schedule1', 3),
                # ИВЧТ очное обучение 3 курса
                ('password', 'Саратов', 'Алиса', 'Витальевна', 'Некрасова', "uploads/profile_photos/profile_1_illust_88443693_20240214_221454.jpg", "221243",
                '2004-02-02', '79992223344', 'vk.com/petrova', 'user2@example.com', 'Информатика и вычислительная техника',
                'http://link.to/schedule2',7)
            ]

            cursor.executemany("""
                INSERT INTO students (
                    password_hash, city, surname, patronymic, first_name, profile_photo, record_book,
                    birth_date, phone, VK_id, email, orientation,
                    schedule, group_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s
                )
                """, students)
            connection.commit()
            print("Тестовые студенты добавлены.")

            # Список новостей
            news_data = [
                {
                    "title": "Летняя смена для студентов в ЭТИ СГТУ",
                    "content": "Открыта регистрация на летнюю смену, которая пройдет в июле!",
                    "author": "Отдел карьеры ЭТИ",
                    "is_global": True,
                    "groups": []  # пусто, значит для всех
                },
                {
                    "title": "Расписание зачетной недели",
                    "content": "Уважаемые студенты ПИНЖ 3 курса, опубликовано расписание зачетов.",
                    "author": "Андреева Милада Игоревна",
                    "is_global": False,
                    "groups": [3]  # сюда подставь group_id нужной группы
                },
                {
                    "title": "Объявление для 3 курса",
                    "content": "Студентам 3 курса необходимо пройти инструктаж по технике безопасности.",
                    "author": "Деканат",
                    "is_global": False,
                    "groups": [3, 7, 11]  # допустим, несколько групп 3 курса
                }
            ]


            for news in news_data:
                # Вставляем саму новость
                cursor.execute("""
                    INSERT INTO news (title, content, author, is_global)
                    VALUES (%s, %s, %s, %s)
                """, (
                    news["title"],
                    news["content"],
                    news["author"],
                    news["is_global"]
                ))

                news_id = cursor.lastrowid

                # Привязываем группы, если новость не глобальная
                if not news["is_global"] and news.get("groups"):
                    for group_id in news["groups"]:
                        cursor.execute("""
                            INSERT INTO news_groups (news_id, group_id)
                            VALUES (%s, %s)
                        """, (news_id, group_id))

            connection.commit()
            print("Все новости успешно добавлены!")
        
            # добавление портфолио
            portfolio_items = [
                # Портфолио студента 1
                (1, 'general', None, 'Общее описание портфолио студента 1.', None),
                (1, 'courseworks', 'Курсовая работа по математике', 'Работа выполнена в 3 семестре.', 'uploads/students/courseworks/math_coursework1.pdf'),
                (1, 'practical', 'Практическая работа по физике', 'Отчёт по лабораторной работе №2.', 'uploads/students/practical/physics_lab2.docx'),
                (1, 'achievements', None, 'Победа в олимпиаде по программированию.', None),
                (1, 'mobility', None, 'Участие в программе академической мобильности в Германии.', None),
                
                # Портфолио студента 2
                (2, 'general', None, 'Общее описание портфолио студента 2.', None),
                (2, 'courseworks', 'Курсовая работа по информатике', 'Исследование алгоритмов сортировки.', 'uploads/students/courseworks/it_coursework1.pdf'),
                (2, 'achievements', None, 'Публикация научной статьи.', None),
            ]

            cursor.executemany("""
                INSERT INTO portfolio_items (
                    student_id, category, title, description, file_path
                ) VALUES (
                    %s, %s, %s, %s, %s
                )
                """, portfolio_items)
            connection.commit()
            print("Тестовые данные портфолио добавлены.")


            # заполняем дисциплины студентов
            # 1. Семестры
            semesters = [
                ('1 семестр 2024', '2024-09-01', '2025-01-31', False),
                ('2 семестр 2025', '2025-02-01', '2025-07-19', False),
                ('3 семестр 2026', '2026-09-01', '2026-01-31', False),
                ('4 семестр 2026', '2026-09-01', '2027-01-31', False),
                ('5 семестр 2027', '2027-02-01', '2027-07-19', False),
                ('6 семестр 2027', '2027-09-01', '2028-01-31', True)   # текущий семестр
            ]

            cursor.executemany("""
                INSERT INTO semesters (name, start_date, end_date, is_current) VALUES (%s, %s, %s, %s)
            """, semesters)
            connection.commit()

            # 2. Дисциплины
            subjects = [
                ('Программирование', 'ОПК-6', 'Углубленное изучение C#', 3, False),
                ('Сети и телекомуникации', 'ОПК-3, 5', 'Углубленное изучение C#', 3, False),
                ('Математика', 'УК-1', 'Дополнительные главы математики', 4, False),
                ('Иностранный язык', 'УК-4', 'Деловое общение на английском языке', 3, False)
            ]

            cursor.executemany("""
                INSERT INTO subjects (name, code, description, credits, is_elective) VALUES (%s, %s, %s, %s, %s)
            """, subjects)
            connection.commit()
            

            # 3. Связь дисциплин с группами и семестрами (предполагаем, что group_id = 3 для теста)
            subject_groups = [
                # subject_id, group_id, semester_id, teacher_id, classroom
                # Пинж-31
                (1, 3, 5, None, 'Ауд.101'),  # Программирование в 5 семестре
                (3, 3, 5, None, 'Ауд.102'),  # Математика в 5 семестре
                (4, 3, 6, None, 'Ауд.103'),  # Английский в 6 семестре
                (3, 3, 6, None, 'Ауд.101'),  # Математика в 6 семестре
                # Ивчт-31
                (2, 7, 5, None, 'Ауд.104'),  # Сеть и телекоммуникации в 5 семестре
                (3, 7, 5, None, 'Ауд.102'),  # Математика в 5 семестре
                (4, 7, 6, None, 'Ауд.103'),  # Английский во 6 семестре
                (3, 7, 6, None, 'Ауд.101'),  # Программирование в 6 семестре
            ]

            cursor.executemany("""
                INSERT INTO subject_groups (subject_id, group_id, semester_id, teacher_id, classroom)
                VALUES (%s, %s, %s, %s, %s)
            """, subject_groups)
            connection.commit()
            

            # 4. Формы отчётности по предметам (subject_assessments)
            subject_assessments = [
                # Для ПИНЖ-31 (group_id=3)
                (1, 'Экзамен', 100, 0.7),               # Программирование (5 семестр)
                (1, 'Курсовая работа', 50, 0.3),        # Программирование (5 семестр)
                (2, 'Экзамен', 100, 0.6),               # Математика (5 семестр)
                (2, 'Контрольная работа', 40, 0.4),     # Математика (5 семестр)
                (3, 'Зачёт', 100, 1.0),                 # Английский (6 семестр)
                (4, 'Экзамен', 100, 0.8),               # Математика (6 семестр)
                (4, 'Практическая работа', 20, 0.2),    # Математика (6 семестр)
                
                # Для ИВЧТ-31 (group_id=7)
                (5, 'Экзамен', 100, 0.5),               # Сети и телекоммуникации (5 семестр)
                (5, 'Лабораторные работы', 50, 0.5),    # Сети и телекоммуникации (5 семестр)
                (6, 'Экзамен', 100, 0.7),               # Математика (5 семестр)
                (6, 'Тест', 30, 0.3),                   # Математика (5 семестр)
                (7, 'Зачёт', 100, 1.0),                 # Английский (6 семестр)
                (8, 'Экзамен', 100, 0.6),               # Программирование (6 семестр)
                (8, 'Проект', 40, 0.4)                  # Программирование (6 семестр)
            ]

            cursor.executemany("""
                INSERT INTO subject_assessments (subject_group_id, form_name, max_score, weight)
                VALUES (%s, %s, %s, %s)
            """, subject_assessments)
            connection.commit()
            
            # 5. Оценки студентов (grades)
            grades = [
                # Студент 1 (ПИНЖ-31)
                (1, 1, 85.0, 'отл', True),   # Программирование (5 семестр)
                (1, 2, 78.0, 'хор', True),   # Математика (5 семестр)
                (1, 3, 92.0, 'отл', True),   # Английский (6 семестр)
                (1, 4, 65.0, 'удовл', True), # Математика (6 семестр)
                
                # Студент 2 (ИВЧТ-31)
                (2, 5, 73.0, 'хор', True),   # Сети и телекоммуникации (5 семестр)
                (2, 6, 88.0, 'отл', True),   # Математика (5 семестр)
                (2, 7, 95.0, 'отл', True),   # Английский (6 семестр)
                (2, 8, 81.0, 'хор', True)    # Программирование (6 семестр)
            ]

            cursor.executemany("""
                INSERT INTO grades (student_id, subject_group_id, total_score, grade_letter, is_passed)
                VALUES (%s, %s, %s, %s, %s)
            """, grades)
            connection.commit()
            
            # 6. Детализация оценок (grade_components)
            grade_components = [
                # Оценки студента 1 (ПИНЖ-31)
                (1, 1, 60.0),   # Экзамен по программированию
                (1, 2, 25.0),   # Курсовая по программированию
                (2, 3, 50.0),   # Экзамен по математике (5 сем)
                (2, 4, 28.0),   # Контрольная по математике (5 сем)
                (3, 5, 92.0),   # Зачёт по английскому
                (4, 6, 55.0),   # Экзамен по математике (6 сем)
                (4, 7, 10.0),   # Практическая по математике (6 сем)
                
                # Оценки студента 2 (ИВЧТ-31)
                (5, 8, 40.0),   # Экзамен по сетям
                (5, 9, 33.0),   # Лабораторные по сетям
                (6, 10, 65.0),  # Экзамен по математике (5 сем)
                (6, 11, 23.0),  # Тест по математике (5 сем)
                (7, 12, 95.0),  # Зачёт по английскому
                (8, 13, 50.0),  # Экзамен по программированию (6 сем)
                (8, 14, 31.0)   # Проект по программированию (6 сем)
            ]

            cursor.executemany("""
                INSERT INTO grade_components (grade_id, assessment_id, score)
                VALUES (%s, %s, %s)
            """, grade_components)
            connection.commit()

            print("Тестовые данные по дисциплинам, семестрам и оценкам добавлены!")

            # 1. Добавляем преподавателей (оставляем без изменений, так как это общий список)
            teachers_data = [
                ("Ершов ", "Алексей", "Сергеевич", "uploads/profile_photos/Ershov_AS_480_2.png", "Доцент", 1, "Ershov@eti.ru"),
                ("Серебряков", "Андрей", "Владимирович", "uploads/profile_photos/98.jpg", "Доцент", 1, "Serebrikov@eti.ru"),
                ("Старухин", "Павел", "Юрьевич", "uploads/profile_photos/старухин.jpg", "Доцент", 1, "Staryhin@eti.ru"),
                ("Нагар", "Юлия", "Николаевна", "uploads/profile_photos/494.jpg", "Доцент", 1, "Nagar@eti.ru"),
                ("Лопухова ", "Марина", "Ивановна", "uploads/profile_photos/105.jpg", "ст.преподаватель", 4, "Lopyhova@eti.ru")
            ]
            cursor.executemany("""
                INSERT INTO teachers (surname, first_name, patronymic, profile_photo, position, department_id, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, teachers_data)
            print("Тестовые преподаватели добавлены")

            # 2. Связываем преподавателей с предметами (обновляем под новые subject_group_id)
            teacher_subjects_data = [
                (1, 1),  # Ершов преподает Программирование (ПИНЖ-31, 5 семестр)
                (2, 2),  # Серебряков преподает Математику (ПИНЖ-31, 5 семестр)
                (2, 4),  # Серебряков преподает Математику (ПИНЖ-31, 6 семестр)
                (3, 5),  # Старухин преподает Сети и телекоммуникации (ИВЧТ-31, 5 семестр)
                (4, 6),  # Нагар преподает Математику (ИВЧТ-31, 5 семестр)
                (5, 3)   # Лопухова преподает Английский (ПИНЖ-31, 6 семестр)
            ]
            cursor.executemany("""
                INSERT INTO teacher_subjects (teacher_id, subject_group_id)
                VALUES (%s, %s)
            """, teacher_subjects_data)
            print("Связи преподавателей с предметами добавлены")

            # 3. Добавляем учебные материалы (обновляем под новые subject_group_id)
            course_materials_data = [
                # Программирование (ПИНЖ-31, 5 семестр)
                (1, "Рабочая программа", "Титульный лист", "uploads/materials/programming/title.pdf"),
                (1, "Лекции", "Введение в C#", "uploads/materials/programming/lecture1.pdf"),
                
                # Математика (ПИНЖ-31, 5 семестр)
                (2, "Рабочая программа", "Структура курса", "uploads/materials/math/structure.pdf"),
                
                # Английский (ПИНЖ-31, 6 семестр)
                (3, "Учебное пособие", "Деловой английский", "uploads/materials/english/book.pdf"),
                
                # Сети и телекоммуникации (ИВЧТ-31, 5 семестр)
                (5, "Лабораторные работы", "Лаб 1: Настройка сети", "uploads/materials/networks/lab1.pdf"),
                
                # Математика (ИВЧТ-31, 5 семестр)
                (6, "Конспект лекций", "Линейная алгебра", "uploads/materials/math/lectures.pdf")
            ]
            cursor.executemany("""
                INSERT INTO course_materials (subject_group_id, title, description, file_path)
                VALUES (%s, %s, %s, %s)
            """, course_materials_data)
            print("Учебные материалы добавлены")

            # 4. Добавляем виды учебной деятельности (обновляем под новые subject_group_id)
            activity_types_data = [
                # Программирование (ПИНЖ-31, 5 семестр)
                (1, "Лекции", 20),
                (1, "Практические задания", 30),
                (1, "Курсовая работа", 50),
                
                # Математика (ПИНЖ-31, 5 семестр)
                (2, "Лекции", 20),
                (2, "Контрольные работы", 30),
                
                # Английский (ПИНЖ-31, 6 семестр)
                (3, "Тесты", 40),
                
                # Сети и телекоммуникации (ИВЧТ-31, 5 семестр)
                (5, "Лабораторные работы", 60),
                
                # Математика (ИВЧТ-31, 5 семестр)
                (6, "Семинары", 25)
            ]
            cursor.executemany("""
                INSERT INTO activity_types (subject_group_id, name, max_score)
                VALUES (%s, %s, %s)
            """, activity_types_data)
            print("Виды учебной деятельности добавлены")

            # 5. Добавляем оценки по видам деятельности (обновляем под новых студентов)
            activity_scores_data = [
                # Студент 1 (ПИНЖ-31)
                (1, 1, 18, '2025-10-15'),  # Лекции по программированию
                (1, 2, 25, '2025-10-20'),  # Практические по программированию
                (1, 4, 15, '2025-10-18'),  # Лекции по математике
                
                # Студент 2 (ИВЧТ-31)
                (2, 7, 55, '2025-11-05'),  # Лабораторные по сетям
                (2, 8, 20, '2025-11-10')   # Семинары по математике
            ]
            cursor.executemany("""
                INSERT INTO activity_scores (student_id, activity_type_id, score, date)
                VALUES (%s, %s, %s, %s)
            """, activity_scores_data)
            print("Оценки по видам деятельности добавлены")

            # 6. Добавляем задания (обновляем под новые subject_group_id)
            assignments_data = [
                # Программирование (ПИНЖ-31, 5 семестр)
                (1, "Курсовая работа", "Разработка приложения на C#", 50, '2025-12-15 23:59:59'),
                
                # Математика (ПИНЖ-31, 5 семестр)
                (2, "Контрольная работа 1", "Линейная алгебра", 30, '2025-11-20 23:59:59'),
                
                # Сети и телекоммуникации (ИВЧТ-31, 5 семестр)
                (5, "Лабораторная работа 2", "Настройка маршрутизации", 25, '2025-11-25 23:59:59'),
                
                # Математика (ИВЧТ-31, 5 семестр)
                (6, "Домашнее задание", "Матричные вычисления", 15, '2025-11-18 23:59:59')
            ]
            cursor.executemany("""
                INSERT INTO assignments (subject_group_id, title, description, max_score, deadline)
                VALUES (%s, %s, %s, %s, %s)
            """, assignments_data)
            print("Задания добавлены")

            # 7. Добавляем статусы заданий (обновляем под новых студентов)
            student_assignments_data = [
                # Студент 1 (ПИНЖ-31)
                (1, 1, "Проверено", 45, "Хорошая работа, но есть замечания"),
                (1, 2, "Отправлено", None, None),
                
                # Студент 2 (ИВЧТ-31)
                (2, 3, "Принято", 23, "Отличная работа"),
                (2, 4, "Проверено", 12, "Не все задачи решены")
            ]
            cursor.executemany("""
                INSERT INTO student_assignments (student_id, assignment_id, status, score, feedback)
                VALUES (%s, %s, %s, %s, %s)
            """, student_assignments_data)
            print("Статусы заданий добавлены")

            connection.commit()
            print("Все тестовые данные для страницы предмета успешно добавлены!")




    except Exception as ex:
        print("Ошибка при работе с БД:", ex)
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    create_students_table()
