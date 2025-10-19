import os
from flask import Flask, render_template, url_for, session, request, redirect, jsonify, flash, send_from_directory
import pymysql as db
from config import host, user, password, port, db_name
from unidecode import unidecode
from werkzeug.utils import secure_filename



# Создаем экземпляр Flask-приложения
app = Flask(__name__)
app.secret_key = 'мой_секретный_ключ'   # Ключ сессии, нужен для хранения информации о пользователе

# Папка для загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Подключение к базе данных
try:
    connection = db.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=db_name,
        cursorclass=db.cursors.DictCursor
    )
    print('''
            ---------------------
            Успешное подключение!
            ---------------------

        ''')
except Exception as ex:
    print("ошибка подключения: ")
    print(ex)

# Получение списка курсов по форме обучения (используется на странице входа)
@app.route('/get_courses')
def get_courses():
    study_form = request.args.get('study_form')  # Получаем значение формы обучения из URL-параметров
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT course FROM student_groups WHERE study_form = %s",
            (study_form,)
        )
        courses = [row['course'] for row in cursor.fetchall()] # Список уникальных курсов
    return jsonify(courses) # Возвращаем в формате JSON (для JavaScript)

@app.route('/get_groups')
def get_groups():
    study_form = request.args.get('study_form')
    course = request.args.get('course')
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, short_name 
            FROM student_groups 
            WHERE study_form = %s AND course = %s
            ORDER BY name
        """, (study_form, course))
        groups = cursor.fetchall()
    
    return jsonify([
        {
            'id': g['id'],
            'name': f"{g['short_name']}-{course}1({study_form[0]})"  # Формат: ПИНЖ-3о (3 курс, очная)
        } for g in groups
    ])

# Получение списка студентов по ID группы
@app.route('/get_students')
def get_students():
    group_id = request.args.get('group_id')
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, surname, first_name, patronymic FROM students WHERE group_id = %s",
            (group_id,)
        )
        students = cursor.fetchall()

    # Возвращаем полное имя студента + ID
    return jsonify([
        {
            'id': s['id'],
            'full_name': f"{s['surname']} {s['first_name']} {s['patronymic']}"
        } for s in students
    ])

# GET — отображает страницу логина.
# POST — проверяет данные и логинит пользователя
# Страница входа (login.html) и сама авторизация
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Получаем данные из формы
        student_id = request.form.get('student_id')
        password = request.form.get('password')

        # Проверка в базе
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()

        # Если студент найден и пароль совпадает — вход
        if student and student['password_hash'] == password: # В будущем здесь будет проверка хэша
            session['student_id'] = student['id']   # Сохраняем ID студента в сессии
            return redirect(url_for('user'))    # Переход в личный кабинет
        else:
            # ⬇ подгружаем формы, курсы, группы, студентов как при GET-запросе
            with connection.cursor() as cursor:
                cursor.execute("SELECT DISTINCT study_form FROM student_groups")
                forms = [row['study_form'] for row in cursor.fetchall()]

                cursor.execute("SELECT DISTINCT course FROM student_groups")
                courses = sorted(set([row['course'] for row in cursor.fetchall()]))

                cursor.execute("SELECT * FROM student_groups")
                groups = cursor.fetchall()

                cursor.execute("SELECT id, surname, first_name, patronymic, group_id FROM students")
                students = cursor.fetchall()

            # передаём переменную error в шаблон
            return render_template('login.html',
                                    error="Неверный логин или пароль",
                                    forms=forms,
                                    courses=courses,
                                    groups=groups,
                                    students=students,
                                    show_header=False)

    # При GET-запросе: подгружаем данные для формы
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT study_form FROM student_groups")
        forms = [row['study_form'] for row in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT course FROM student_groups")
        courses = sorted(set([row['course'] for row in cursor.fetchall()]))

        cursor.execute("SELECT * FROM student_groups")
        groups = cursor.fetchall()

        cursor.execute("SELECT id, surname, first_name, patronymic, group_id FROM students")
        students = cursor.fetchall()

    # Отправляем все данные в шаблон login.html
    return render_template('login.html', show_header=False, forms=forms, courses=courses, groups=groups, students=students)

# Отображение страницы пользователя (user.html)
@app.route('/user')
def user():
    student_id = session.get('student_id')

    if not student_id:
        return redirect(url_for('login'))

    with connection.cursor() as cursor:
        # Получаем данные студента
        cursor.execute("""
            SELECT
                s.first_name, s.patronymic, s.surname, s.city, s.email, s.birth_date,
                s.phone, s.VK_id, s.record_book, s.orientation, s.schedule,
                s.profile_photo,
                g.id AS group_id, g.name AS group_name, g.short_name AS group_short,
                g.course, g.study_form,
                d.name AS department_name, d.short_name AS department_short
            FROM students s
            LEFT JOIN student_groups g ON s.group_id = g.id
            LEFT JOIN departments d ON g.department_id = d.id
            WHERE s.id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if not student:
            return "Студент не найден", 404

        # Получаем новости, предназначенные для всех или для конкретной группы
        cursor.execute("""
            SELECT DISTINCT n.id, n.title, n.content, n.publish_date, n.author
            FROM news n
            LEFT JOIN news_groups ng ON n.id = ng.news_id
            WHERE ng.group_id = %s OR ng.group_id IS NULL
            ORDER BY n.publish_date DESC
            LIMIT 5
        """, (student['group_id'],))
        news = cursor.fetchall()

    return render_template("user.html", show_header=True, student=student, news=news)

# Добавьте новый маршрут для загрузки фото
@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'error': 'Не авторизован'}), 401

    if 'photo' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    # дополнительная проверка расширения (только изображения)
    ALLOWED_IMAGE_EXT = {'jpg','jpeg','png','gif'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_IMAGE_EXT:
        return jsonify({'error': 'Недопустимый формат файла'}), 400

    filename = f"profile_{student_id}_{secure_filename(unidecode(file.filename))}"
    save_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], 'profile_photos')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    file.save(save_path)

    relative_path = f"uploads/profile_photos/{filename}"
    with connection.cursor() as cursor:
        # удаляем старое фото (если есть)
        cursor.execute("SELECT profile_photo FROM students WHERE id = %s", (student_id,))
        row = cursor.fetchone()
        old_photo = row['profile_photo'] if row else None
        if old_photo:
            try:
                old_full = os.path.join(app.root_path, 'static', old_photo)
                if os.path.exists(old_full):
                    os.remove(old_full)
            except Exception:
                app.logger.exception("Не удалось удалить старое фото")

        cursor.execute("UPDATE students SET profile_photo = %s WHERE id = %s", (relative_path, student_id))
        connection.commit()

    return jsonify({'success': True, 'photo_url': url_for('static', filename=relative_path)})


# Добавьте маршрут для удаления фото
@app.route('/delete_profile_photo', methods=['POST'])
def delete_profile_photo():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'error': 'Не авторизован'}), 401

    with connection.cursor() as cursor:
        cursor.execute("SELECT profile_photo FROM students WHERE id = %s", (student_id,))
        photo = cursor.fetchone()['profile_photo']
        
        if photo:
            try:
                os.remove(os.path.join(app.root_path, 'static', photo))
            except:
                pass
            
        cursor.execute("UPDATE students SET profile_photo = NULL WHERE id = %s", (student_id,))
        connection.commit()

    return jsonify({'success': True})

@app.route('/news')
def news_list():
    cur = connection.cursor()
    cur.execute("SELECT id, title, LEFT(content, 200) AS preview, author, publish_date FROM news ORDER BY publish_date DESC")
    news_list = cur.fetchall()
    return render_template('news_list.html', show_header=True, news_list=news_list)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    cur = connection.cursor()
    cur.execute("SELECT id, title, content, author, publish_date FROM news WHERE id = %s", (news_id,))
    news = cur.fetchone()
    if not news:
        return "Новость не найдена", 404

    return render_template('news_detail.html', show_header=True, news=news)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/portfolio', methods=['GET', 'POST'])
def portfolio():
    student_id = session.get('student_id')

    if not student_id:
        return redirect(url_for('login'))

    with connection.cursor() as cursor:
        if request.method == 'POST':
            # Получаем категорию из формы (скрытое поле)
            category = request.form.get('category')

            # Получаем title (для курсовых/практических), может быть пустым
            title = request.form.get('title') or None

            # Получаем описание
            description = request.form.get('description')

            # Обработка файла
            file = request.files.get('file')
            file_path = None
            if file and allowed_file(file.filename):
                original_filename = file.filename  # считали имя файла
                filename = secure_filename(unidecode(original_filename))  # преаброзуем все в латиницу, для безопасности
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'students', filename)
                file.save(save_path)
                # Относительный путь от папки static (для Flask и HTML)
                file_path = f'uploads/students/{filename}'  # только путь внутри static

            # Вставляем в БД
            cursor.execute("""
                INSERT INTO portfolio_items (student_id, category, title, description, file_path)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, category, title, description, file_path))
            connection.commit()

            flash('Данные успешно сохранены!')
            return redirect(url_for('portfolio'))

        # При GET-запросе получаем все портфолио этого студента, сгруппированные по категориям
        cursor.execute("""
            SELECT category, id, title, description, file_path, created_at
            FROM portfolio_items
            WHERE student_id = %s
            ORDER BY created_at DESC
        """, (student_id,))
        rows = cursor.fetchall()

    # Группируем по категориям в словарь
    portfolio_data = {
        'general': [],
        'courseworks': [],
        'practical': [],
        'achievements': [],
        'mobility': []
    }

    for row in rows:
        portfolio_data[row['category']].append(row)

    return render_template('portfolio.html', show_header=True, portfolio=portfolio_data)

@app.route('/portfolio/delete/<int:item_id>', methods=['POST'])
def delete_portfolio_item(item_id):
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))

    with connection.cursor() as cursor:
        # Получаем путь к файлу
        cursor.execute("""
            SELECT file_path FROM portfolio_items
            WHERE id = %s AND student_id = %s
        """, (item_id, student_id))
        item = cursor.fetchone()

        if not item:
            flash("Элемент не найден или вы не имеете доступа.", "error")
            return redirect(url_for('portfolio'))

        file_path = item['file_path']
        if file_path:  # проверяем, что путь не None
            full_path = os.path.join(app.root_path, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)

        # Удаляем из базы данных
        cursor.execute("""
            DELETE FROM portfolio_items WHERE id = %s AND student_id = %s
        """, (item_id, student_id))
        connection.commit()

    flash("Запись успешно удалена.", "success")
    return redirect(url_for('portfolio'))

@app.route('/education')
def education():
    # Проверяем авторизацию студента
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    
    # Считываем активный семестр из запроса
    active_semester_id = request.args.get('semester_id', type=int)

    with connection.cursor() as cursor:
        # 1. Получаем данные о группе студента
        cursor.execute("SELECT group_id FROM students WHERE id = %s", (student_id,))
        student_data = cursor.fetchone()
        
        if not student_data:
            return "Студент не найден в базе данных"
        
        group_id = student_data['group_id']  # Теперь group_id определена
        
        # 2. Получаем все семестры для группы студента
        cursor.execute("""
            SELECT DISTINCT s.id, s.name, s.start_date, s.end_date, s.is_current
            FROM semesters s
            JOIN subject_groups sg ON sg.semester_id = s.id
            WHERE sg.group_id = %s
            ORDER BY s.start_date
        """, (group_id,))
        semesters = cursor.fetchall()

        if not semesters:
            return "Для вашей группы нет данных о семестрах"
        
        # 3. Собираем данные по каждому семестру
        semester_data = []
        for semester in semesters:
            cursor.execute("""
                SELECT 
                    sub.name AS subject_name,
                    sub.id AS subject_id,
                    sg.id AS subject_group_id,  # Добавляем это
                    GROUP_CONCAT(DISTINCT sa.form_name SEPARATOR ' + ') AS assessment_forms,
                    MAX(IFNULL(g.total_score, 0)) AS total_score,
                    MAX(g.grade_letter) AS grade_letter,
                    MAX(g.is_passed) AS is_passed
                FROM subject_groups sg
                JOIN subjects sub ON sub.id = sg.subject_id
                JOIN subject_assessments sa ON sa.subject_group_id = sg.id
                LEFT JOIN grades g ON g.subject_group_id = sg.id AND g.student_id = %s
                WHERE sg.semester_id = %s AND sg.group_id = %s
                GROUP BY sub.id, sub.name, sg.id  # Группируем и по subject_group_id
            """, (student_id, semester['id'], group_id))
            subjects = cursor.fetchall()
            

            semester_data.append({
                'semester': semester,
                'subjects': subjects
            })
        
        return render_template('education.html', show_header=True,
                                semester_data=semester_data,
                                active_semester_id=active_semester_id)

@app.route('/subject/<int:subject_group_id>')  # Изменили параметр
def subject(subject_group_id):  # Изменили имя параметра
    student_id = session.get('student_id')
    if not student_id:
        return redirect(url_for('login'))
    
    with connection.cursor() as cursor:
        # 1. Проверяем, что студент имеет доступ к этой группе предметов
        cursor.execute("""
            SELECT st.group_id
            FROM students st
            JOIN subject_groups sg ON sg.group_id = st.group_id
            WHERE st.id = %s AND sg.id = %s
        """, (student_id, subject_group_id))
        access = cursor.fetchone()
        if not access:
            return "Доступ запрещен или предмет не найден", 403
        
        # 2. Получаем основную информацию о предмете
        cursor.execute("""
            SELECT
                s.id, s.name, s.code, s.description, s.credits,
                sg.id AS subject_group_id,
                sem.name AS semester_name,
                sem.id AS semester_id
            FROM subjects s
            JOIN subject_groups sg ON sg.subject_id = s.id
            JOIN semesters sem ON sem.id = sg.semester_id
            WHERE sg.id = %s
        """, (subject_group_id,))
        subject_data = cursor.fetchone()
        if not subject_data:
            return "Предмет не найден", 404
        
        # 3. Получаем преподавателей
        cursor.execute("""
            SELECT
                t.id, t.surname, t.first_name, t.patronymic,
                t.position, t.email, d.name AS department_name,
                t.profile_photo
            FROM teachers t
            JOIN teacher_subjects ts ON ts.teacher_id = t.id
            JOIN departments d ON d.id = t.department_id
            WHERE ts.subject_group_id = %s
        """, (subject_group_id,))
        teachers = cursor.fetchall()
        
        # 4. Получаем виды учебной деятельности
        cursor.execute("""
            SELECT
                at.id, at.name, at.max_score,
                COALESCE(SUM(acs.score), 0) AS student_score
            FROM activity_types at
            LEFT JOIN activity_scores acs ON
                acs.activity_type_id = at.id AND
                acs.student_id = %s
            WHERE at.subject_group_id = %s
            GROUP BY at.id
        """, (student_id, subject_group_id))
        activities = cursor.fetchall()
        
        # 5. Получаем задания и статусы
        cursor.execute("""
            SELECT
                a.id, a.title, a.description, a.max_score, a.deadline,
                sa.status, sa.score, sa.feedback
            FROM assignments a
            LEFT JOIN student_assignments sa ON
                sa.assignment_id = a.id AND
                sa.student_id = %s
            WHERE a.subject_group_id = %s
            ORDER BY a.deadline
        """, (student_id, subject_group_id))
        assignments = cursor.fetchall()
        
        # 6. Получаем материалы курса
        cursor.execute("""
            SELECT id, title, description, file_path
            FROM course_materials
            WHERE subject_group_id = %s
            ORDER BY created_at
        """, (subject_group_id,))
        materials = cursor.fetchall()
        
        return render_template('subject.html', show_header=True,
                            subject=subject_data,
                            teachers=teachers,
                            activities=activities,
                            assignments=assignments,
                            materials=materials,
                            semester_id=subject_data['semester_id'])

@app.route('/download/<int:file_id>')
def download(file_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT file_path FROM course_materials WHERE id = %s", (file_id,))
        file_data = cursor.fetchone()

        if not file_data or not file_data['file_path']:
            return "Файл не найден", 404

        # file_path в БД ожидается относительно static, например: 'uploads/materials/title.pdf'
        rel_path = file_data['file_path']
        full_path = os.path.join(app.root_path, 'static', rel_path)

        if not os.path.exists(full_path):
            return "Файл не найден", 404

        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)

        # Для совместимости используем позиционные аргументы
        return send_from_directory(directory, filename, as_attachment=True)



# Запуск сервера Flask
if __name__ == "__main__":
    app.run(debug=True)
    #Пока активен дебаг, то все ошибку выводятся на страницу сайта.
