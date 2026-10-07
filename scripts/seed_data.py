import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import (
    db, User, Subject, Topic, Lesson, Question, QuizSet, QuizQuestion, RoadmapItem, AuditLog
)

def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Check if already seeded
        if User.query.filter_by(username='admin').first():
            print("Database already contains seed data.")
            return

        print("Seeding demo data into database...")

        # 1. Admin User
        admin_user = User(
            username='admin',
            email='admin@tnpsc2a.org',
            full_name='TNPSC Master Administrator',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        # 2. Demo Student User
        student_user = User(
            username='student',
            email='student@tnpsc2a.org',
            full_name='Karthik Kumar',
            role='student'
        )
        student_user.set_password('student123')
        db.session.add(student_user)

        db.session.commit()

        # 3. Subject: Indian Polity
        subject_polity = Subject(
            name='Indian Polity',
            code='POLITY',
            description='Comprehensive coverage of Indian Constitution, Governance, Rights, and State Structure for Group 2A.',
            icon='landmark',
            order_index=1
        )
        db.session.add(subject_polity)
        db.session.commit()

        # 4. Topics
        topic_const_basics = Topic(
            subject_id=subject_polity.id,
            title='Constitution Basics',
            description='Framing of the Constitution, Preamble, Salient Features, and Sources.',
            order_index=1
        )
        topic_fund_rights = Topic(
            subject_id=subject_polity.id,
            title='Fundamental Rights',
            description='Part III Articles 12-35, Writs, Exceptions, and Amendments.',
            order_index=2
        )
        db.session.add_all([topic_const_basics, topic_fund_rights])
        db.session.commit()

        # 5. Lessons
        lesson1 = Lesson(
            topic_id=topic_const_basics.id,
            title='Introduction to Indian Constitution',
            content_summary='Learn about the Constituent Assembly, drafting committee, adoption, and key dates.',
            concept_body='''
<h3 class="text-xl font-bold text-slate-100 mb-3">1. What is a Constitution?</h3>
<p class="mb-4 text-slate-300">The Constitution is the supreme law of the land. It defines the framework, powers, and duties of government institutions and sets out the fundamental rights and duties of citizens.</p>

<h3 class="text-xl font-bold text-slate-100 mb-3">2. Formation of Constituent Assembly</h3>
<p class="mb-4 text-slate-300">The Constituent Assembly of India was formed under the Cabinet Mission Plan of 1946. First meeting held on December 9, 1946. Dr. Sachchidananda Sinha served as temporary President, later succeeded by Dr. Rajendra Prasad as permanent President.</p>

<h3 class="text-xl font-bold text-slate-100 mb-3">3. The Drafting Committee</h3>
<p class="mb-4 text-slate-300">The Drafting Committee was appointed on August 29, 1947, chaired by <strong>Dr. B.R. Ambedkar</strong> (Father of Indian Constitution). It took 2 years, 11 months, and 18 days to draft the document.</p>
''',
            examples='Think of the Constitution as the supreme rulebook of a grand nation-wide tournament. No referee (government body) or player (citizen) can violate the written rulebook without facing disqualification (judicial review by courts).',
            important_points='''• Constituent Assembly setup: Cabinet Mission Plan 1946
• Drafting Committee Chairman: Dr. B.R. Ambedkar
• Total Time Taken: 2 Years, 11 Months, 18 Days
• Adopted: 26th November 1949 (celebrated as Law/Constitution Day)
• Came into full force: 26th January 1950 (Republic Day)
• Original Document: 395 Articles, 8 Schedules, 22 Parts''',
            memory_tricks='Mnemonic for key office holders: "Drafted by Ambedkar, Presided by Rajendra, Objective Resolution by Nehru!"',
            estimated_minutes=15,
            order_index=1
        )

        lesson2 = Lesson(
            topic_id=topic_fund_rights.id,
            title='Overview of Fundamental Rights (Articles 12 to 35)',
            content_summary='Detailed breakdown of the 6 fundamental rights guaranteed under Part III of the Indian Constitution.',
            concept_body='''
<h3 class="text-xl font-bold text-slate-100 mb-3">1. Part III: Magna Carta of India</h3>
<p class="mb-4 text-slate-300">Fundamental Rights are enshrined in Part III of the Constitution from Articles 12 to 35. Inspired by the American Bill of Rights, they are justiciable in nature, meaning citizens can approach courts if violated.</p>

<h3 class="text-xl font-bold text-slate-100 mb-3">2. Six Fundamental Rights</h3>
<ol class="list-decimal pl-6 mb-4 text-slate-300 space-y-2">
  <li><strong>Right to Equality</strong> (Articles 14–18)</li>
  <li><strong>Right to Freedom</strong> (Articles 19–22)</li>
  <li><strong>Right against Exploitation</strong> (Articles 23–24)</li>
  <li><strong>Right to Freedom of Religion</strong> (Articles 25–28)</li>
  <li><strong>Cultural and Educational Rights</strong> (Articles 29–30)</li>
  <li><strong>Right to Constitutional Remedies</strong> (Article 32) — Called "Heart and Soul of the Constitution" by Dr. B.R. Ambedkar.</li>
</ol>
''',
            examples='If a public restaurant denies entry to a person based solely on their caste or religion, it violates Article 15 (Right to Equality), and the affected citizen can move directly to the Supreme Court under Article 32.',
            important_points='''• Part III of Constitution (Articles 12 to 35)
• Originally 7 rights; Right to Property (Art 31) deleted by 44th Amendment 1978 and made legal right (Art 300A)
• Article 32: Heart & Soul of Constitution (Writs: Habeas Corpus, Mandamus, Prohibition, Quo-Warranto, Certiorari)
• Justiciable in Supreme Court (Art 32) and High Courts (Art 226)''',
            memory_tricks='Mnemonic for 6 Rights: "Equal Free Exploitation Relieves Cultural Remedies" (Equality, Freedom, Against Exploitation, Religion, Cultural/Edu, Remedies)',
            estimated_minutes=20,
            order_index=1
        )
        db.session.add_all([lesson1, lesson2])
        db.session.commit()

        # 6. Questions
        q1 = Question(
            subject_id=subject_polity.id,
            topic_id=topic_const_basics.id,
            question_text='Who was appointed as the Chairman of the Drafting Committee of the Indian Constitution in 1947?',
            option_a='Dr. Rajendra Prasad',
            option_b='Dr. B.R. Ambedkar',
            option_c='Jawaharlal Nehru',
            option_d='Sardar Vallabhbhai Patel',
            correct_option='B',
            explanation='Dr. B.R. Ambedkar was appointed as Chairman of the 7-member Drafting Committee set up on August 29, 1947.',
            difficulty='easy',
            marks=1
        )

        q2 = Question(
            subject_id=subject_polity.id,
            topic_id=topic_const_basics.id,
            question_text='On which date was the Constitution of India formally adopted by the Constituent Assembly?',
            option_a='15th August 1947',
            option_b='26th January 1950',
            option_c='26th November 1949',
            option_d='30th January 1948',
            correct_option='C',
            explanation='The Constitution was formally adopted on 26th November 1949 (now celebrated as Constitution Day), while it came into full enforcement on 26th January 1950.',
            difficulty='medium',
            marks=1
        )

        q3 = Question(
            subject_id=subject_polity.id,
            topic_id=topic_fund_rights.id,
            question_text='Which Constitutional Amendment Act removed the Right to Property from the list of Fundamental Rights?',
            option_a='42nd Amendment Act, 1976',
            option_b='44th Amendment Act, 1978',
            option_c='86th Amendment Act, 2002',
            option_d='73rd Amendment Act, 1992',
            correct_option='B',
            explanation='The 44th Amendment Act of 1978 removed the Right to Property from Part III (Fundamental Rights) and made it a legal right under Article 300A in Part XII.',
            difficulty='medium',
            marks=1
        )

        q4 = Question(
            subject_id=subject_polity.id,
            topic_id=topic_fund_rights.id,
            question_text='Which article was described by Dr. B.R. Ambedkar as the "Heart and Soul" of the Indian Constitution?',
            option_a='Article 14',
            option_b='Article 19',
            option_c='Article 21',
            option_d='Article 32',
            correct_option='D',
            explanation='Article 32 guarantees the Right to Constitutional Remedies (Writs), granting citizens direct recourse to the Supreme Court.',
            difficulty='easy',
            marks=1
        )

        db.session.add_all([q1, q2, q3, q4])
        db.session.commit()

        # 7. QuizSet
        quiz_set1 = QuizSet(
            title='Polity Basics & Fundamental Rights Mastery Quiz',
            description='Test your knowledge on Constitution Assembly formation, drafting history, and fundamental rights (Articles 12-35).',
            subject_id=subject_polity.id,
            topic_id=topic_const_basics.id,
            time_limit_minutes=10,
            pass_percentage=60.0
        )
        db.session.add(quiz_set1)
        db.session.commit()

        # Link questions to quiz set
        qq1 = QuizQuestion(quiz_set_id=quiz_set1.id, question_id=q1.id, order_index=1)
        qq2 = QuizQuestion(quiz_set_id=quiz_set1.id, question_id=q2.id, order_index=2)
        qq3 = QuizQuestion(quiz_set_id=quiz_set1.id, question_id=q3.id, order_index=3)
        qq4 = QuizQuestion(quiz_set_id=quiz_set1.id, question_id=q4.id, order_index=4)
        db.session.add_all([qq1, qq2, qq3, qq4])
        db.session.commit()

        # 8. Roadmap Items
        road1 = RoadmapItem(
            title='Phase 1: Indian Polity Foundation & Constitutional Framework',
            description='Master the basics of Indian Constitution, Constituent Assembly history, Preamble, and Articles 1-35.',
            year=1,
            month=1,
            subject_id=subject_polity.id,
            topic_id=topic_const_basics.id,
            lesson_id=lesson1.id,
            target_date='2026-10-31',
            estimated_study_time='12 hours',
            priority='high',
            order_index=1
        )
        road2 = RoadmapItem(
            title='Phase 2: Fundamental Rights, Directive Principles & Fundamental Duties',
            description='Deep dive into Articles 12-51A, Supreme Court land mark cases, and constitutional amendments.',
            year=1,
            month=2,
            subject_id=subject_polity.id,
            topic_id=topic_fund_rights.id,
            lesson_id=lesson2.id,
            target_date='2026-11-30',
            estimated_study_time='15 hours',
            priority='high',
            order_index=2
        )
        db.session.add_all([road1, road2])
        db.session.commit()

        # 9. Audit Log
        AuditLog.log_action(
            admin_user.id,
            'SEED_DATABASE',
            'System',
            None,
            'Initial demo dataset seeded (Polity, Constitution Basics, Fundamental Rights, Quiz Set)'
        )

        print("Seed data successfully added!")

if __name__ == '__main__':
    seed()
