"""
Seed script for ExamSaaS platform.
Creates initial data for development and testing.
WARNING: DEVELOPMENT ONLY - Never run in production!
"""
import logging
import os
import sys
import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

dotenv_path = Path(__file__).parent.parent / '.env'
if dotenv_path.exists():
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.config import Config
from app.models import (
    Institute, User, StudentProfile, TeacherProfile, Plan, Subscription,
    Wallet, WalletTransaction, Payment, Exam, Question, ExamAttempt, Result,
    Certificate, Ebook, SupportTicket, TicketMessage, AuditLog,
    FeatureFlags, Schedule, Security, QuestionOption, Answer, Violation,
    PerQuestionAnalysis, TopicPerformance, TicketAttachment, MessageAttachment,
    TransactionType, TransactionSource, TransactionPurpose
)
from app.helpers import generate_slug, generate_ticket_number, generate_certificate_code

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PASSWORD = "ExamSaaS@123"


def print_warning():
    """Print development warning."""
    print("\n" + "="*60)
    print("[SEED] WARNING: DEVELOPMENT ONLY - NEVER RUN IN PRODUCTION!")
    print("="*60 + "\n")


def drop_all_collections(db):
    """Drop all collections for clean slate."""
    collections = [
        'audit_logs', 'ticket_messages', 'support_tickets', 'certificates',
        'ai_recommendations', 'results', 'exam_attempts', 'questions',
        'exams', 'pdf_uploads', 'ebooks', 'payments', 'wallet_transactions',
        'wallets', 'subscriptions', 'plans', 'teacher_profiles',
        'student_profiles', 'users', 'institutes'
    ]
    for coll in collections:
        try:
            db.drop_collection(coll)
            logger.info(f"Dropped collection: {coll}")
        except Exception:
            pass


def create_indexes(db):
    """Create MongoDB indexes."""
    indexes = [
        ('users', [("email", 1)], True, None),
        ('users', [("institute", 1), ("role", 1)], False, None),
        ('users', [("google_id", 1)], False, True),
        ('exams', [("institute", 1), ("status", 1)], False, None),
        ('exams', [("created_by", 1)], False, None),
        ('exams', [("exam_type", 1), ("status", 1)], False, None),
        ('exam_attempts', [("exam", 1), ("student", 1)], False, None),
        ('exam_attempts', [("status", 1), ("created_at", -1)], False, None),
        ('results', [("student", 1), ("exam", 1)], False, None),
        ('results', [("institute", 1)], False, None),
        ('questions', [("institute", 1), ("topic", 1)], False, None),
        ('wallet_transactions', [("wallet", 1), ("created_at", -1)], False, None),
        ('support_tickets', [("status", 1), ("priority", -1)], False, None),
        ('audit_logs', [("actor", 1), ("created_at", -1)], False, None),
        ('certificates', [("certificate_code", 1)], True, None),
    ]
    
    for coll_name, keys, unique, sparse in indexes:
        coll = db[coll_name]
        try:
            coll.create_index(keys, unique=unique, sparse=sparse)
            logger.info(f"Created index on {coll_name}: {keys}")
        except Exception as e:
            logger.warning(f"Index creation warning for {coll_name}: {e}")


def create_plans(db):
    """Create subscription plans."""
    plans_data = [
        {
            'name': 'Free',
            'slug': 'free',
            'price': 0,
            'duration_days': 365,
            'max_students': 10,
            'max_teachers': 1,
            'exam_limit': 5,
            'ai_usage_limit': 0,
            'feature_flags': FeatureFlags(
                ebook_access=False,
                ai_recommendations=False,
                pdf_exam_generation=False,
                certificate_generation=False,
                live_monitoring=False,
                excel_export=False,
                marketplace_access=False
            ),
            'is_for': 'institute'
        },
        {
            'name': 'Starter',
            'slug': 'starter',
            'price': 99900,
            'duration_days': 30,
            'max_students': 100,
            'max_teachers': 5,
            'exam_limit': 50,
            'ai_usage_limit': 100,
            'feature_flags': FeatureFlags(
                ebook_access=True,
                ai_recommendations=False,
                pdf_exam_generation=False,
                certificate_generation=True,
                live_monitoring=False,
                excel_export=False,
                marketplace_access=False
            ),
            'is_for': 'institute'
        },
        {
            'name': 'Growth',
            'slug': 'growth',
            'price': 299900,
            'duration_days': 30,
            'max_students': 500,
            'max_teachers': 20,
            'exam_limit': 200,
            'ai_usage_limit': 500,
            'feature_flags': FeatureFlags(
                ebook_access=True,
                ai_recommendations=True,
                pdf_exam_generation=True,
                certificate_generation=True,
                live_monitoring=True,
                excel_export=True,
                marketplace_access=True
            ),
            'is_for': 'institute'
        },
        {
            'name': 'Enterprise',
            'slug': 'enterprise',
            'price': 999900,
            'duration_days': 30,
            'max_students': -1,
            'max_teachers': -1,
            'exam_limit': -1,
            'ai_usage_limit': -1,
            'feature_flags': FeatureFlags(
                ebook_access=True,
                ai_recommendations=True,
                pdf_exam_generation=True,
                certificate_generation=True,
                live_monitoring=True,
                excel_export=True,
                marketplace_access=True
            ),
            'is_for': 'institute'
        },
        {
            'name': 'Student Basic',
            'slug': 'student-basic',
            'price': 49900,
            'duration_days': 30,
            'max_students': 0,
            'max_teachers': 0,
            'exam_limit': 10,
            'ai_usage_limit': 50,
            'feature_flags': FeatureFlags(
                ebook_access=True,
                ai_recommendations=True,
                pdf_exam_generation=False,
                certificate_generation=False,
                live_monitoring=False,
                excel_export=False,
                marketplace_access=False
            ),
            'is_for': 'student'
        },
    ]
    
    plans = {}
    for plan_data in plans_data:
        plan = Plan(**plan_data)
        plan.save()
        plans[plan_data['slug']] = plan
        logger.info(f"Created plan: {plan.name}")
    
    return plans


def create_platform_users():
    """Create platform-level users."""
    users = {}
    
    superadmin = User(
        email='superadmin@examsaas.com',
        first_name='Super',
        last_name='Admin',
        role='super_admin',
        is_active=True,
        is_email_verified=True
    )
    superadmin.set_password(PASSWORD)
    superadmin.save()
    users['superadmin'] = superadmin
    
    platformadmin = User(
        email='platformadmin@examsaas.com',
        first_name='Platform',
        last_name='Admin',
        role='admin_public',
        is_active=True,
        is_email_verified=True
    )
    platformadmin.set_password(PASSWORD)
    platformadmin.save()
    users['platformadmin'] = platformadmin
    
    supportagent = User(
        email='support@examsaas.com',
        first_name='Support',
        last_name='Agent',
        role='support_agent',
        support_scope='platform',
        is_active=True,
        is_email_verified=True
    )
    supportagent.set_password(PASSWORD)
    supportagent.save()
    users['supportagent'] = supportagent
    
    for key, user in users.items():
        logger.info(f"Created platform user: {user.email}")
    
    return users


def create_institutes_and_admins(plans, creator):
    """Create institutes with their admins atomically."""
    institutes_data = [
        {
            'slug': 'sunrise-engineering',
            'name': 'Sunrise Engineering College',
            'admin_email': 'admin@sunrise.edu.in',
            'admin_first_name': 'Sunrise',
            'admin_last_name': 'Admin',
            'plan_slug': 'growth',
            'status': 'active',
            'city': 'Mumbai',
            'state': 'Maharashtra',
        },
        {
            'slug': 'delhi-public-coaching',
            'name': 'Delhi Public Coaching',
            'admin_email': 'admin@dpccoaching.com',
            'admin_first_name': 'DPC',
            'admin_last_name': 'Admin',
            'plan_slug': 'starter',
            'status': 'active',
            'city': 'Delhi',
            'state': 'Delhi',
        },
        {
            'slug': 'free-tier-academy',
            'name': 'Free Tier Academy',
            'admin_email': 'admin@freetieracademy.com',
            'admin_first_name': 'Free',
            'admin_last_name': 'Admin',
            'plan_slug': 'free',
            'status': 'active',
            'city': 'Pune',
            'state': 'Maharashtra',
        },
        {
            'slug': 'expired-institute',
            'name': 'Expired Institute',
            'admin_email': 'admin@expired.com',
            'admin_first_name': 'Expired',
            'admin_last_name': 'Admin',
            'plan_slug': 'starter',
            'status': 'expired',
            'city': 'Bangalore',
            'state': 'Karnataka',
        },
    ]
    
    institutes = {}
    for data in institutes_data:
        plan = plans[data['plan_slug']]
        
        admin = User(
            email=data['admin_email'],
            first_name=data['admin_first_name'],
            last_name=data['admin_last_name'],
            role='admin_college',
            is_active=True,
            is_email_verified=True
        )
        admin.set_password(PASSWORD)
        admin.save()
        
        institute = Institute(
            name=data['name'],
            slug=data['slug'],
            city=data['city'],
            state=data['state'],
            admin_type='institute_admin',
            is_active=True,
            created_by=creator
        )
        institute.save()
        
        wallet = Wallet(user=admin, balance=0, currency='INR')
        wallet.save()
        admin.wallet = wallet
        admin.institute = institute
        admin.save()
        
        now = datetime.utcnow()
        if data['status'] == 'active':
            expires_at = now + timedelta(days=plan.duration_days)
            sub_status = 'active'
        else:
            expires_at = now - timedelta(days=10)
            sub_status = 'expired'
        
        subscription = Subscription(
            institute=institute,
            plan=plan,
            status=sub_status,
            starts_at=now - timedelta(days=30),
            expires_at=expires_at,
            grace_until=expires_at + timedelta(days=7)
        )
        subscription.save()
        institute.subscription = subscription
        institute.save()
        
        institutes[data['slug']] = {
            'institute': institute,
            'admin': admin,
            'subscription': subscription
        }
        logger.info(f"Created institute: {institute.name}")
    
    return institutes


def create_teachers(institutes):
    """Create teachers for institutes."""
    teachers = []
    
    teacher1 = User(
        email='teacher1@sunrise.edu.in',
        first_name='John',
        last_name='Smith',
        role='teacher',
        institute=institutes['sunrise-engineering']['institute'],
        is_active=True,
        is_email_verified=True
    )
    teacher1.set_password(PASSWORD)
    teacher1.save()
    
    wallet1 = Wallet(user=teacher1, balance=0)
    wallet1.save()
    teacher1.wallet = wallet1
    teacher1.save()
    
    teacher_profile1 = TeacherProfile(
        user=teacher1,
        teacher_code='TCH001',
        department='Computer Science',
        designation='Senior Lecturer'
    )
    teacher_profile1.save()
    teachers.append({'user': teacher1, 'profile': teacher_profile1})
    
    teacher2 = User(
        email='teacher2@sunrise.edu.in',
        first_name='Jane',
        last_name='Doe',
        role='teacher',
        institute=institutes['sunrise-engineering']['institute'],
        is_active=True,
        is_email_verified=True
    )
    teacher2.set_password(PASSWORD)
    teacher2.save()
    
    wallet2 = Wallet(user=teacher2, balance=0)
    wallet2.save()
    teacher2.wallet = wallet2
    teacher2.save()
    
    teacher_profile2 = TeacherProfile(
        user=teacher2,
        teacher_code='TCH002',
        department='Mathematics',
        designation='Assistant Professor'
    )
    teacher_profile2.save()
    teachers.append({'user': teacher2, 'profile': teacher_profile2})
    
    teacher3 = User(
        email='teacher1@dpccoaching.com',
        first_name='Physics',
        last_name='Teacher',
        role='teacher',
        institute=institutes['delhi-public-coaching']['institute'],
        is_active=True,
        is_email_verified=True
    )
    teacher3.set_password(PASSWORD)
    teacher3.save()
    
    wallet3 = Wallet(user=teacher3, balance=0)
    wallet3.save()
    teacher3.wallet = wallet3
    teacher3.save()
    
    teacher_profile3 = TeacherProfile(
        user=teacher3,
        teacher_code='TCH003',
        department='Physics',
        designation='Senior Faculty'
    )
    teacher_profile3.save()
    teachers.append({'user': teacher3, 'profile': teacher_profile3})
    
    for t in teachers:
        logger.info(f"Created teacher: {t['user'].email}")
    
    return teachers


def create_assigned_students(teacher1, institute):
    """Create 10 assigned students for teacher1."""
    students = []
    
    for i in range(1, 11):
        student = User(
            email=f'stu{i:03d}@sunrise.edu.in',
            first_name=f'Student{i:03d}',
            last_name='Assigned',
            role='student_assigned',
            institute=institute,
            is_active=True,
            is_email_verified=True
        )
        student.set_password(PASSWORD)
        student.save()
        
        wallet = Wallet(user=student, balance=0)
        wallet.save()
        student.wallet = wallet
        student.save()
        
        profile = StudentProfile(
            user=student,
            student_code=f'STU{i:03d}',
            batch='2024',
            section='A',
            year=2,
            teacher=teacher1,
            assigned_username=f'stu{i:03d}',
            assigned_password_hash='hashed_password_here'
        )
        profile.save()
        
        students.append({'user': student, 'profile': profile})
        logger.info(f"Created assigned student: {student.email}")
    
    return students


def create_registered_students(institutes, student_plan):
    """Create 3 registered students with wallets, one with subscription."""
    students = []
    
    for i in range(1, 4):
        student = User(
            email=f'student{i}@gmail.com',
            first_name=f'Registered{i}',
            last_name='Student',
            role='student_registered',
            is_active=True,
            is_email_verified=True
        )
        student.set_password(PASSWORD)
        student.save()
        
        wallet = Wallet(user=student, balance=50000 if i == 1 else 10000)
        wallet.save()
        student.wallet = wallet
        student.save()
        
        profile = StudentProfile(
            user=student,
            student_code=f'REG{i:03d}',
            batch='2024',
            year=3
        )
        profile.save()
        
        if i == 3:
            now = datetime.utcnow()
            subscription = Subscription(
                student=student,
                plan=student_plan,
                status='active',
                starts_at=now,
                expires_at=now + timedelta(days=30)
            )
            subscription.save()
            logger.info(f"Created student with subscription: {student.email}")
        else:
            logger.info(f"Created registered student: {student.email}")
        
        students.append({'user': student, 'profile': profile})
    
    return students


def create_exams(teachers, institutes):
    """Create 3 exams."""
    exams = {}
    
    teacher1 = teachers[0]['user']
    institute1 = institutes['sunrise-engineering']['institute']
    
    exam1 = Exam(
        title='Data Structures Midterm',
        description='Midterm examination for Data Structures course',
        subject='Computer Science',
        topic='Data Structures',
        institute=institute1,
        created_by=teacher1,
        exam_type='institute',
        status='published',
        total_marks=100,
        passing_percentage=40.0,
        duration_minutes=60,
        schedule=Schedule(
            start_at=datetime.utcnow() - timedelta(days=7),
            end_at=datetime.utcnow() + timedelta(days=7),
            grace_minutes=5
        ),
        security=Security(
            camera_required=False,
            tab_switch_limit=3,
            fullscreen_required=False,
            copy_paste_disabled=True,
            shuffle_questions=True,
            shuffle_options=True
        ),
        result_mode='instant',
        access_mode='open',
        price=0,
        allowed_attempts=1,
        certificate_enabled=True
    )
    exam1.save()
    exams['ds_midterm'] = exam1
    logger.info(f"Created exam: {exam1.title}")
    
    exam2 = Exam(
        title='Mathematics Quiz',
        description='Quick quiz on mathematics fundamentals',
        subject='Mathematics',
        topic='Algebra',
        institute=institute1,
        created_by=teacher1,
        exam_type='institute',
        status='draft',
        total_marks=50,
        passing_percentage=50.0,
        duration_minutes=30,
        schedule=Schedule(grace_minutes=2),
        security=Security(),
        result_mode='delayed',
        access_mode='passcode',
        price=0,
        allowed_attempts=2,
        certificate_enabled=False
    )
    exam2.save()
    exams['math_quiz'] = exam2
    logger.info(f"Created exam: {exam2.title}")
    
    exam3 = Exam(
        title='JEE Mock Test - Physics',
        description='Full length JEE Physics mock test',
        subject='Physics',
        topic='JEE Physics',
        institute=institutes['delhi-public-coaching']['institute'],
        created_by=teachers[2]['user'],
        exam_type='public',
        status='published',
        total_marks=100,
        passing_percentage=35.0,
        duration_minutes=180,
        schedule=Schedule(
            start_at=datetime.utcnow() - timedelta(days=14),
            end_at=datetime.utcnow() + timedelta(days=30)
        ),
        security=Security(
            camera_required=True,
            tab_switch_limit=5,
            fullscreen_required=True,
            copy_paste_disabled=True,
            shuffle_questions=True
        ),
        result_mode='instant',
        access_mode='open',
        price=9900,
        allowed_attempts=1,
        certificate_enabled=True
    )
    exam3.save()
    exams['jee_physics'] = exam3
    logger.info(f"Created exam: {exam3.title}")
    
    return exams


def create_questions(exams, teachers, institutes):
    """Create questions for exams."""
    questions = {'ds': [], 'math': [], 'jee': []}
    
    teacher1 = teachers[0]['user']
    teacher3 = teachers[2]['user']
    institute1 = institutes['sunrise-engineering']['institute']
    institute2 = institutes['delhi-public-coaching']['institute']
    
    ds_topics = ['Arrays', 'Linked Lists', 'Stacks', 'Queues', 'Trees']
    ds_questions_data = [
        ('What is the time complexity of accessing an element in an array by index?', 'Arrays', 'easy', [('O(1)', True), ('O(n)', False), ('O(log n)', False), ('O(n^2)', False)]),
        ('Which data structure uses LIFO principle?', 'Stacks', 'easy', [('Queue', False), ('Stack', True), ('Array', False), ('Linked List', False)]),
        ('What is the maximum number of nodes at level k in a binary tree?', 'Trees', 'medium', [('2^k', True), ('2k', False), ('k^2', False), ('k/2', False)]),
        ('Which traversal visits root before its subtrees?', 'Trees', 'easy', [('Inorder', False), ('Preorder', True), ('Postorder', False), ('Level order', False)]),
        ('What is the time complexity of searching in a hash table?', 'Arrays', 'easy', [('O(1) average', True), ('O(n)', False), ('O(log n)', False), ('O(n^2)', False)]),
        ('Which data structure is best for BFS traversal?', 'Queues', 'easy', [('Stack', False), ('Queue', True), ('Array', False), ('Tree', False)]),
        ('What is the worst-case time complexity of quicksort?', 'Arrays', 'medium', [('O(n log n)', False), ('O(n^2)', True), ('O(n)', False), ('O(log n)', False)]),
        ('How many pointers does each node have in a doubly linked list?', 'Linked Lists', 'easy', [('1', False), ('2', True), ('3', False), ('0', False)]),
        ('What is the space complexity of recursive Fibonacci?', 'Arrays', 'medium', [('O(n)', True), ('O(1)', False), ('O(n^2)', False), ('O(log n)', False)]),
        ('Which sorting algorithm has best average-case time complexity?', 'Arrays', 'easy', [('Bubble Sort', False), ('Selection Sort', False), ('Merge Sort', True), ('Insertion Sort', False)]),
        ('What type of linked list has a cycle?', 'Linked Lists', 'medium', [('Circular', True), ('Doubly', False), ('Singly', False), ('None', False)]),
        ('What is the height of a complete binary tree with n nodes?', 'Trees', 'hard', [('log2(n)', True), ('n', False), ('n/2', False), ('sqrt(n)', False)]),
        ('Which operation is O(1) in a hash table?', 'Arrays', 'easy', [('Insert', True), ('Search worst-case', False), ('Delete worst-case', False), ('All of above worst-case', False)]),
        ('What is the maximum number of edges in a directed graph with n nodes?', 'Arrays', 'medium', [('n', False), ('n*(n-1)', True), ('n*(n-1)/2', False), ('n^2', False)]),
        ('Which data structure is used in function call stack?', 'Stacks', 'easy', [('Queue', False), ('Stack', True), ('Array', False), ('Heap', False)]),
        ('What is the time complexity of inserting at beginning of linked list?', 'Linked Lists', 'easy', [('O(1)', True), ('O(n)', False), ('O(log n)', False), ('O(1) always', False)]),
        ('How do you find the middle element of a linked list in one pass?', 'Linked Lists', 'medium', [('Two pointers', True), ('Counter', False), ('Recursive', False), ('Array conversion', False)]),
        ('What is the worst-case time for searching in BST?', 'Trees', 'easy', [('O(log n)', False), ('O(n)', True), ('O(1)', False), ('O(n log n)', False)]),
        ('Which tree is self-balancing?', 'Trees', 'easy', [('Binary Tree', False), ('AVL Tree', True), ('Binary Search Tree', False), ('Expression Tree', False)]),
        ('What is the time complexity of heap sort?', 'Arrays', 'medium', [('O(n log n)', True), ('O(n^2)', False), ('O(n)', False), ('O(log n)', False)]),
        ('Which data structure prevents deadlocks?', 'Stacks', 'hard', [('Queue', False), ('Semaphore', True), ('Stack', False), ('Monitor', False)]),
        ('What is the memory representation of 2D array?', 'Arrays', 'easy', [('Contiguous', True), ('Scattered', False), ('Linked', False), ('Hierarchical', False)]),
        ('Which algorithm uses divide and conquer?', 'Arrays', 'easy', [('Merge Sort', True), ('Linear Search', False), ('Hashing', False), ('Traversal', False)]),
        ('What is the time to delete from beginning of singly linked list?', 'Linked Lists', 'easy', [('O(1)', True), ('O(n)', False), ('O(log n)', False), ('O(n^2)', False)]),
        ('Which traversal gives nodes in sorted order for BST?', 'Trees', 'easy', [('Preorder', False), ('Postorder', False), ('Inorder', True), ('Level order', False)]),
    ]
    
    for q_text, topic, difficulty, options_data in ds_questions_data:
        options = [QuestionOption(option_id=chr(65+i), text=opt[0]) for i, opt in enumerate(options_data)]
        correct_id = next(chr(65+i) for i, opt in enumerate(options_data) if opt[1])
        
        q = Question(
            text=q_text,
            question_type='mcq',
            options=options,
            correct_option_id=correct_id,
            subject='Computer Science',
            topic=topic,
            difficulty=difficulty,
            marks=4,
            source='manual',
            institute=institute1,
            created_by=teacher1,
            is_reviewed=True,
            is_approved=True
        )
        q.save()
        questions['ds'].append(q)
    
    math_questions_data = [
        ('Solve: x^2 - 5x + 6 = 0', 'Algebra', 'easy', [('x=2,3', True), ('x=1,6', False), ('x=-2,-3', False), ('x=0,5', False)]),
        ('What is derivative of x^3?', 'Calculus', 'easy', [('3x^2', True), ('x^2', False), ('3x^3', False), ('x^4/4', False)]),
        ('Find LCM of 12 and 18', 'Number Theory', 'easy', [('36', True), ('24', False), ('72', False), ('6', False)]),
        ('What is sin(30)?', 'Trigonometry', 'easy', [('0.5', True), ('0.707', False), ('1', False), ('0', False)]),
        ('Solve: 2x + 3 = 7', 'Algebra', 'easy', [('x=2', True), ('x=3', False), ('x=1', False), ('x=4', False)]),
        ('What is log base 10 of 1000?', 'Algebra', 'easy', [('3', True), ('10', False), ('100', False), ('1', False)]),
        ('Find area of circle with r=7', 'Geometry', 'medium', [('154', True), ('44', False), ('21', False), ('616', False)]),
        ('What is derivative of sin(x)?', 'Calculus', 'easy', [('cos(x)', True), ('-cos(x)', False), ('sin(x)', False), ('tan(x)', False)]),
        ('Simplify: (a+b)^2', 'Algebra', 'easy', [('a^2 + 2ab + b^2', True), ('a^2 + b^2', False), ('a^2 - 2ab + b^2', False), ('2a + 2b', False)]),
        ('What is 5! ?', 'Combinatorics', 'easy', [('120', True), ('60', False), ('24', False), ('720', False)]),
    ]
    
    for q_text, topic, difficulty, options_data in math_questions_data:
        options = [QuestionOption(option_id=chr(65+i), text=opt[0]) for i, opt in enumerate(options_data)]
        correct_id = next(chr(65+i) for i, opt in enumerate(options_data) if opt[1])
        
        q = Question(
            text=q_text,
            question_type='mcq',
            options=options,
            correct_option_id=correct_id,
            subject='Mathematics',
            topic=topic,
            difficulty=difficulty,
            marks=5,
            source='manual',
            institute=institute1,
            created_by=teacher1,
            is_reviewed=True,
            is_approved=True
        )
        q.save()
        questions['math'].append(q)
    
    jee_questions_data = [
        ('A particle moves with constant velocity. Its acceleration is:', 'Mechanics', 'easy', [('Zero', True), ('Constant', False), ('Increasing', False), ('Decreasing', False)]),
        ('The unit of force in SI is:', 'Units', 'easy', [('Newton', True), ('Dyne', False), ('Joule', False), ('Watt', False)]),
        ('Which phenomenon proves wave nature of light?', 'Optics', 'medium', [('Photoelectric effect', False), ('Interference', True), ('Photoelectron', False), ('Black body', False)]),
        ('The dimensional formula of Planck constant is:', 'Modern Physics', 'hard', [('ML^2T^-1', True), ('MLT^-2', False), ('ML^2T^-2', False), ('MLT^-1', False)]),
        ('Two bodies of masses m and 4m are moving with equal kinetic energy. Ratio of momenta is:', 'Mechanics', 'medium', [('1:2', True), ('1:4', False), ('4:1', False), ('1:1', False)]),
        ('The frequency of AC in India is:', 'Electricity', 'easy', [('50 Hz', True), ('60 Hz', False), ('100 Hz', False), ('25 Hz', False)]),
        ('Which lens is used to correct myopia?', 'Optics', 'easy', [('Concave', True), ('Convex', False), ('Plano-convex', False), ('Cylindrical', False)]),
        ('The work done in moving a charge in electric field depends on:', 'Electricity', 'easy', [('Path', False), ('Initial and final position', True), ('Time taken', False), ('Mass', False)]),
        ('Radioactivity is a:', 'Modern Physics', 'easy', [('Spontaneous process', True), ('Induced process', False), ('Chemical process', False), ('Reversible process', False)]),
        ('Young modulus of a wire depends on:', 'Properties of Matter', 'medium', [('Length', False), ('Material', True), ('Cross-section', False), ('Mass', False)]),
        ('The escape velocity from Earth surface is approximately:', 'Mechanics', 'medium', [('11.2 km/s', True), ('8.5 km/s', False), ('16.5 km/s', False), ('22.4 km/s', False)]),
        ('Which color has highest wavelength?', 'Optics', 'easy', [('Red', True), ('Blue', False), ('Green', False), ('Violet', False)]),
        ('The phenomenon of splitting of white light is called:', 'Optics', 'easy', [('Dispersion', True), ('Diffraction', False), ('Polarization', False), ('Scattering', False)]),
        ('A body is moving with uniform acceleration. Its velocity-time graph is:', 'Kinematics', 'easy', [('Straight line', True), ('Parabola', False), ('Hyperbola', False), ('Circle', False)]),
        ('The resistance of a wire depends on:', 'Electricity', 'easy', [('Length and area', True), ('Only length', False), ('Only area', False), ('Volume', False)]),
    ]
    
    for q_text, topic, difficulty, options_data in jee_questions_data:
        options = [QuestionOption(option_id=chr(65+i), text=opt[0]) for i, opt in enumerate(options_data)]
        correct_id = next(chr(65+i) for i, opt in enumerate(options_data) if opt[1])
        
        q = Question(
            text=q_text,
            question_type='mcq',
            options=options,
            correct_option_id=correct_id,
            subject='Physics',
            topic=topic,
            difficulty=difficulty,
            marks=4,
            source='manual',
            institute=institute2,
            created_by=teacher3,
            is_reviewed=True,
            is_approved=True
        )
        q.save()
        questions['jee'].append(q)
    
    for key, qs in questions.items():
        logger.info(f"Created {len(qs)} questions for {key}")
    
    return questions


def create_exam_attempts_and_results(exams, questions, students, institutes):
    """Create exam attempts and results."""
    institute1 = institutes['sunrise-engineering']['institute']
    exam1 = exams['ds_midterm']
    ds_questions = questions['ds'][:25]
    
    assigned_students = [s['user'] for s in students['assigned']]
    results_created = []
    
    passed_students = assigned_students[:2]
    failed_students = assigned_students[2:4]
    auto_submit_student = assigned_students[4]
    
    for i, student in enumerate(passed_students):
        started = datetime.utcnow() - timedelta(minutes=45)
        submitted = started + timedelta(minutes=45)
        
        answers = []
        correct_count = 0
        for j, q in enumerate(ds_questions):
            is_correct = random.random() > 0.3
            correct_count += 1 if is_correct else 0
            
            answer = Answer(
                question_id=str(q.id),
                selected_option_id=q.correct_option_id if is_correct else 'A',
                flagged=False,
                time_spent_seconds=random.randint(30, 120)
            )
            answers.append(answer)
        
        attempt = ExamAttempt(
            exam=exam1,
            student=student,
            status='submitted',
            started_at=started,
            submitted_at=submitted,
            answers=answers,
            tab_switch_count=random.randint(0, 2),
            access_method='direct',
            ip_address='192.168.1.100'
        )
        attempt.save()
        
        score = correct_count * 4
        percentage = (correct_count / 25) * 100
        passed = percentage >= 40
        
        result = Result(
            exam=exam1,
            student=student,
            attempt=attempt,
            institute=institute1,
            score=score,
            total_marks=100,
            percentage=percentage,
            passed=passed,
            grade='A' if percentage >= 80 else 'B' if percentage >= 60 else 'C',
            correct_count=correct_count,
            wrong_count=25 - correct_count,
            unattempted_count=0,
            is_published=True
        )
        result.save()
        results_created.append(result)
        
        if passed and exam1.certificate_enabled:
            cert = Certificate(
                student=student,
                exam=exam1,
                result=result,
                institute=institute1,
                certificate_code=generate_certificate_code(),
                student_name=student.full_name,
                exam_name=exam1.title,
                institute_name=institute1.name,
                score=percentage,
                grade=result.grade,
                issued_at=datetime.utcnow()
            )
            cert.save()
            logger.info(f"Created certificate for {student.email}")
        
        logger.info(f"Created attempt and result for passed student: {student.email}")
    
    for i, student in enumerate(failed_students):
        started = datetime.utcnow() - timedelta(minutes=30)
        submitted = started + timedelta(minutes=30)
        
        answers = []
        correct_count = 0
        for j, q in enumerate(ds_questions):
            is_correct = random.random() > 0.7
            correct_count += 1 if is_correct else 0
            
            answer = Answer(
                question_id=str(q.id),
                selected_option_id='A' if not is_correct else q.correct_option_id,
                flagged=False,
                time_spent_seconds=random.randint(20, 60)
            )
            answers.append(answer)
        
        attempt = ExamAttempt(
            exam=exam1,
            student=student,
            status='submitted',
            started_at=started,
            submitted_at=submitted,
            answers=answers,
            tab_switch_count=random.randint(0, 2),
            access_method='direct'
        )
        attempt.save()
        
        score = correct_count * 4
        percentage = (correct_count / 25) * 100
        passed = percentage >= 40
        
        result = Result(
            exam=exam1,
            student=student,
            attempt=attempt,
            institute=institute1,
            score=score,
            total_marks=100,
            percentage=percentage,
            passed=passed,
            grade='F',
            correct_count=correct_count,
            wrong_count=25 - correct_count,
            unattempted_count=0,
            is_published=True
        )
        result.save()
        logger.info(f"Created failed result for: {student.email}")
    
    started = datetime.utcnow() - timedelta(minutes=20)
    answers = []
    for j, q in enumerate(ds_questions[:15]):
        answer = Answer(
            question_id=str(q.id),
            selected_option_id=q.correct_option_id,
            flagged=False,
            time_spent_seconds=random.randint(30, 90)
        )
        answers.append(answer)
    
    attempt = ExamAttempt(
        exam=exam1,
        student=auto_submit_student,
        status='auto_submitted',
        started_at=started,
        submitted_at=datetime.utcnow(),
        answers=answers,
        tab_switch_count=3,
        violations=[
            Violation(type='tab_switch', occurred_at=started + timedelta(minutes=5), screenshot_url=None),
            Violation(type='tab_switch', occurred_at=started + timedelta(minutes=10), screenshot_url=None),
            Violation(type='tab_switch', occurred_at=started + timedelta(minutes=15), screenshot_url=None),
        ],
        access_method='direct'
    )
    attempt.save()
    logger.info(f"Created auto-submitted attempt for: {auto_submit_student.email}")
    
    return results_created


def create_ebooks(institutes, uploader):
    """Create sample ebooks."""
    institute1 = institutes['sunrise-engineering']['institute']
    
    ebook1 = Ebook(
        title='Introduction to Data Structures',
        description='A comprehensive guide to data structures and algorithms',
        subject='Computer Science',
        topics='Arrays,Linked Lists,Stacks,Queues',
        cloudinary_url='https://example.com/ebooks/ds-intro.pdf',
        file_size_bytes=5242880,
        page_count=250,
        access_level='free',
        price=0,
        institute=institute1,
        uploaded_by=uploader
    )
    ebook1.save()
    
    ebook2 = Ebook(
        title='Advanced Physics for JEE',
        description='Complete physics preparation for JEE Main and Advanced',
        subject='Physics',
        topics='Mechanics,Optics,Electricity,Thermodynamics',
        cloudinary_url='https://example.com/ebooks/advanced-physics.pdf',
        file_size_bytes=15728640,
        page_count=800,
        access_level='subscription',
        price=0,
        institute=None,
        uploaded_by=uploader
    )
    ebook2.save()
    
    logger.info("Created 2 ebooks")
    return [ebook1, ebook2]


def create_support_tickets(users, institutes):
    """Create support tickets."""
    user1 = users['platformadmin']
    institute1 = institutes['sunrise-engineering']['institute']
    admin = institutes['sunrise-engineering']['admin']
    
    ticket1 = SupportTicket(
        ticket_number=generate_ticket_number(),
        user=user1,
        institute=institute1,
        category='technical',
        priority='high',
        status='open',
        subject='Unable to access exam after payment',
        description='I paid for the JEE Mock Test but cannot access the exam. Please help.',
        attachments=[]
    )
    ticket1.save()
    
    msg1 = TicketMessage(
        ticket=ticket1,
        sender=user1,
        sender_role='user',
        message='Hi, I facing an issue with exam access.',
        is_internal_note=False
    )
    msg1.save()
    
    msg2 = TicketMessage(
        ticket=ticket1,
        sender=admin,
        sender_role='admin',
        message='Checking the payment status...',
        is_internal_note=True
    )
    msg2.save()
    
    ticket2 = SupportTicket(
        ticket_number=generate_ticket_number(),
        user=user1,
        institute=institute1,
        category='billing',
        priority='medium',
        status='resolved',
        subject='Refund request for duplicate payment',
        description='I was charged twice for the same exam.',
        resolved_at=datetime.utcnow() - timedelta(days=1)
    )
    ticket2.save()
    
    msg3 = TicketMessage(
        ticket=ticket2,
        sender=user1,
        sender_role='user',
        message='Please refund the extra payment.',
        is_internal_note=False
    )
    msg3.save()
    
    msg4 = TicketMessage(
        ticket=ticket2,
        sender=users['supportagent'],
        sender_role='support_agent',
        message='Refund processed. Amount will reflect in 5-7 business days.',
        is_internal_note=False
    )
    msg4.save()
    
    logger.info("Created 2 support tickets")


def create_audit_logs(users):
    """Create sample audit logs."""
    superadmin = users['superadmin']
    
    audit_actions = [
        ('login', 'Super Admin logged in'),
        ('create', 'Institute created'),
        ('update', 'Plan updated'),
        ('create', 'User account created'),
    ]
    
    for action, description in audit_actions:
        log = AuditLog(
            actor=superadmin,
            actor_role='super_admin',
            action=action,
            target_type='system',
            target_id='system',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0',
            metadata={'description': description}
        )
        log.save()
    
    logger.info("Created audit logs")


def seed_database():
    """Main seed function."""
    print_warning()
    
    logger.info("Starting database seeding...")
    
    config = Config.from_env()
    
    from mongoengine import connect
    db_name = os.environ.get('MONGO_DB', 'exams')
    
    if 'mongodb+srv' in config.MONGO_URI:
        connect(db=db_name, host=config.MONGO_URI, alias='default')
    else:
        connect(db=db_name, host=config.MONGO_URI)
    
    app = create_app(config)
    
    with app.app_context():
        from pymongo import MongoClient
        client = MongoClient(config.MONGO_URI)
        db = client[db_name]
        
        logger.info("Step 1: Dropping all collections...")
        drop_all_collections(db)
        
        logger.info("Step 2: Creating indexes...")
        create_indexes(db)
        
        logger.info("Step 3: Creating plans...")
        plans = create_plans(db)
        
        logger.info("Step 4: Creating platform users...")
        platform_users = create_platform_users()
        
        logger.info("Step 5: Creating institutes and admins...")
        institutes = create_institutes_and_admins(plans, platform_users['superadmin'])
        
        logger.info("Step 6: Creating teachers...")
        teachers = create_teachers(institutes)
        
        logger.info("Step 7: Creating assigned students...")
        assigned_students = create_assigned_students(
            teachers[0]['user'],
            institutes['sunrise-engineering']['institute']
        )
        
        logger.info("Step 8: Creating registered students...")
        registered_students = create_registered_students(institutes, plans['student-basic'])
        
        logger.info("Step 9: Creating exams...")
        exams = create_exams(teachers, institutes)
        
        logger.info("Step 10: Creating questions...")
        questions = create_questions(exams, teachers, institutes)
        
        logger.info("Step 11: Creating exam attempts and results...")
        create_exam_attempts_and_results(exams, questions, {
            'assigned': assigned_students,
            'registered': registered_students
        }, institutes)
        
        logger.info("Step 12: Creating ebooks...")
        create_ebooks(institutes, teachers[0]['user'])
        
        logger.info("Step 13: Creating support tickets...")
        create_support_tickets(platform_users, institutes)
        
        logger.info("Step 14: Creating audit logs...")
        create_audit_logs(platform_users)
    
    print("\n" + "="*60)
    print("SEED DATA SUMMARY")
    print("="*60)
    print(f"\nPassword for all users: {PASSWORD}\n")
    print("-" * 60)
    print(f"{'Role':<20} {'Email':<40} {'Password'}")
    print("-" * 60)
    
    print(f"{'Super Admin':<20} {'superadmin@examsaas.com':<40} {PASSWORD}")
    print(f"{'Platform Admin':<20} {'platformadmin@examsaas.com':<40} {PASSWORD}")
    print(f"{'Support Agent':<20} {'support@examsaas.com':<40} {PASSWORD}")
    
    for slug, data in institutes.items():
        admin = data['admin']
        print(f"{'Institute Admin':<20} {admin.email:<40} {PASSWORD}")
    
    for teacher in teachers:
        t = teacher['user']
        print(f"{'Teacher':<20} {t.email:<40} {PASSWORD}")
    
    for i, student in enumerate(assigned_students[:3]):
        s = student['user']
        print(f"{'Assigned Student':<20} {s.email:<40} {PASSWORD}")
    
    for i, student in enumerate(registered_students):
        s = student['user']
        print(f"{'Registered Student':<20} {s.email:<40} {PASSWORD}")
    
    print("-" * 60)
    print(f"\nTotal: 1 Super Admin, 1 Platform Admin, 1 Support Agent")
    print(f"       4 Institutes, 3 Teachers, 10 Assigned Students, 3 Registered Students")
    print(f"       3 Exams, 60 Questions, 5 Attempts with Results")
    print("="*60)
    
    logger.info("Database seeding completed successfully!")
    print("\nDatabase seeded successfully!")


if __name__ == "__main__":
    seed_database()
