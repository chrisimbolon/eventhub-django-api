# backend/apps/events/management/commands/create_sample_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User
from apps.events.models import Event, Registration
from apps.tracks.models import Track
from apps.session_manager.models import Session, Speaker


class Command(BaseCommand):
    help = 'Create sample data for EventHub API'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Creating sample data...'))

        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('Clearing existing data...')
        Registration.objects.all().delete()
        Session.objects.all().delete()
        Speaker.objects.all().delete()
        Track.objects.all().delete()
        Event.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create Users
        self.stdout.write('Creating users...')
        
        # Organizers
        organizer1 = User.objects.create_user(
            username='john_organizer',
            email='john@eventhub.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            role='organizer',
            phone='+1234567890',
            company='TechConf Inc',
            job_title='Event Manager',
            bio='Experienced event organizer with 10+ years in tech conferences.'
        )

        organizer2 = User.objects.create_user(
            username='sarah_organizer',
            email='sarah@eventhub.com',
            password='password123',
            first_name='Sarah',
            last_name='Smith',
            role='organizer',
            phone='+1234567891',
            company='DevEvents Ltd',
            job_title='Conference Director',
            bio='Passionate about bringing developers together.'
        )

        # Speakers
        speaker_user1 = User.objects.create_user(
            username='alice_speaker',
            email='alice@tech.com',
            password='password123',
            first_name='Alice',
            last_name='Johnson',
            role='speaker',
            phone='+1234567892',
            company='Google',
            job_title='Senior Engineer',
            bio='Python expert and open-source contributor.',
            linkedin='https://linkedin.com/in/alicejohnson',
            twitter='@alicejohnson',
            github='alicejohnson'
        )

        speaker_user2 = User.objects.create_user(
            username='bob_speaker',
            email='bob@startup.io',
            password='password123',
            first_name='Bob',
            last_name='Wilson',
            role='speaker',
            phone='+1234567893',
            company='StartupXYZ',
            job_title='CTO',
            bio='Full-stack developer and tech entrepreneur.',
            linkedin='https://linkedin.com/in/bobwilson',
            github='bobwilson'
        )

        speaker_user3 = User.objects.create_user(
            username='carol_speaker',
            email='carol@microsoft.com',
            password='password123',
            first_name='Carol',
            last_name='Davis',
            role='speaker',
            phone='+1234567894',
            company='Microsoft',
            job_title='Cloud Architect',
            bio='Specializing in cloud infrastructure and DevOps.',
            linkedin='https://linkedin.com/in/caroldavis',
            twitter='@caroldavis'
        )

        # Attendees
        attendees = []
        for i in range(1, 11):
            attendee = User.objects.create_user(
                username=f'attendee{i}',
                email=f'attendee{i}@example.com',
                password='password123',
                first_name=f'Attendee{i}',
                last_name='User',
                role='attendee',
                phone=f'+123456789{i}',
                company=f'Company{i}',
                job_title='Developer'
            )
            attendees.append(attendee)

        self.stdout.write(self.style.SUCCESS(f'✅ Created {13 + len(attendees)} users'))

        # Create Events
        self.stdout.write('Creating events...')
        
        now = timezone.now()
        
        # Event 1: PyCon 2025
        event1 = Event.objects.create(
            title='PyCon 2025',
            slug='pycon-2025',
            description='The largest annual gathering for the Python community. Join us for 3 days of talks, workshops, and networking with Python developers from around the world.',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=32),
            registration_start=now - timedelta(days=5),
            registration_end=now + timedelta(days=25),
            venue_name='San Francisco Convention Center',
            venue_address='747 Howard St, San Francisco, CA 94103',
            city='San Francisco',
            country='USA',
            capacity=500,
            organizer=organizer1,
            website='https://pycon.org'
        )

        # Event 2: DjangoCon Europe 2025
        event2 = Event.objects.create(
            title='DjangoCon Europe 2025',
            slug='djangocon-europe-2025',
            description='European Django conference bringing together Django developers, core contributors, and enthusiasts.',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=45),
            end_date=now + timedelta(days=47),
            registration_start=now - timedelta(days=3),
            registration_end=now + timedelta(days=40),
            venue_name='Berlin Tech Hub',
            venue_address='Französische Str. 12, 10117 Berlin',
            city='Berlin',
            country='Germany',
            capacity=300,
            organizer=organizer2,
            website='https://djangocon.eu'
        )

        # Event 3: React Summit 2025
        event3 = Event.objects.create(
            title='React Summit 2025',
            slug='react-summit-2025',
            description='The biggest React conference of the year featuring the latest in React, React Native, and the React ecosystem.',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=60),
            end_date=now + timedelta(days=61),
            registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=55),
            venue_name='Austin Innovation Center',
            venue_address='123 Frontend Blvd, Austin, TX 78701',
            city='Austin',
            country='USA',
            capacity=400,
            organizer=organizer1,
            website='https://reactsummit.com'
        )

        # Event 4: DevOps Days 2025
        event4 = Event.objects.create(
            title='DevOps Days 2025',
            slug='devops-days-2025',
            description='Learn the latest in DevOps practices, CI/CD, infrastructure as code, and cloud automation.',
            event_type='conference',
            status='published',
            start_date=now + timedelta(days=75),
            end_date=now + timedelta(days=76),
            registration_start=now,
            registration_end=now + timedelta(days=70),
            venue_name='Seattle Cloud Center',
            venue_address='321 Ops Street, Seattle, WA 98101',
            city='Seattle',
            country='USA',
            capacity=250,
            organizer=organizer2,
            website='https://devopsdays.org'
        )

        # Event 5: AI & ML Summit 2025
        event5 = Event.objects.create(
            title='AI & ML Summit 2025',
            slug='ai-ml-summit-2025',
            description='Exploring the future of artificial intelligence and machine learning with leading researchers and practitioners.',
            event_type='conference',
            status='draft',
            start_date=now + timedelta(days=90),
            end_date=now + timedelta(days=92),
            registration_start=now + timedelta(days=10),
            registration_end=now + timedelta(days=85),
            venue_name='London Future Tech Center',
            venue_address='555 AI Avenue, London EC1A 1BB',
            city='London',
            country='UK',
            capacity=600,
            organizer=organizer1,
            website='https://aimlsummit.com'
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 5 events'))

        # Create Tracks
        self.stdout.write('Creating tracks...')

        # PyCon tracks
        track1 = Track.objects.create(
            event=event1,
            name='Web Development',
            description='Sessions focused on web development with Python and Django',
            color='#3B82F6',
            room='Hall A'
        )

        track2 = Track.objects.create(
            event=event1,
            name='Data Science',
            description='Machine learning, data analysis, and AI with Python',
            color='#10B981',
            room='Hall B'
        )

        track3 = Track.objects.create(
            event=event1,
            name='DevOps & Cloud',
            description='Python in DevOps, cloud infrastructure, and automation',
            color='#F59E0B',
            room='Hall C'
        )

        # DjangoCon tracks
        track4 = Track.objects.create(
            event=event2,
            name='Django Core',
            description='Deep dive into Django framework internals and best practices',
            color='#0C4B33',
            room='Main Hall'
        )

        track5 = Track.objects.create(
            event=event2,
            name='Django REST Framework',
            description='Building powerful REST APIs with Django REST Framework',
            color='#6366F1',
            room='Workshop Room'
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 5 tracks'))

        # Create Speakers
        self.stdout.write('Creating speakers...')

        sp1 = Speaker.objects.create(
            user=speaker_user1,
            name='Alice Johnson',
            email='alice@tech.com',
            bio='Expert Python developer with 15 years of experience in web development and open source.',
            title='Senior Software Engineer',
            company='Google',
            linkedin='https://linkedin.com/in/alicejohnson',
            twitter='@alicejohnson',
            github='alicejohnson'
        )

        sp2 = Speaker.objects.create(
            user=speaker_user2,
            name='Bob Wilson',
            email='bob@startup.io',
            bio='Full-stack developer, startup founder, and technology enthusiast.',
            title='Chief Technology Officer',
            company='StartupXYZ',
            linkedin='https://linkedin.com/in/bobwilson',
            github='bobwilson'
        )

        sp3 = Speaker.objects.create(
            user=speaker_user3,
            name='Carol Davis',
            email='carol@microsoft.com',
            bio='Cloud architect specializing in Azure, AWS, and enterprise infrastructure.',
            title='Cloud Architect',
            company='Microsoft',
            linkedin='https://linkedin.com/in/caroldavis',
            twitter='@caroldavis'
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 3 speakers'))

        # Create Sessions
        self.stdout.write('Creating sessions...')

        # PyCon sessions - Day 1
        # Add hours to event start date to ensure sessions are within event dates
        pycon_day1_morning = event1.start_date + timedelta(hours=1)
        
        session1 = Session.objects.create(
            event=event1,
            track=track1,
            title='Building Scalable APIs with Django REST Framework',
            slug='building-scalable-apis-drf',
            description='Learn how to build production-ready REST APIs with DRF, including authentication, permissions, and performance optimization.',
            session_format='talk',
            level='intermediate',
            start_time=pycon_day1_morning,
            end_time=pycon_day1_morning + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall A',
            tags='django, rest-api, backend'
        )
        session1.speakers.add(sp1)

        session2 = Session.objects.create(
            event=event1,
            track=track2,
            title='Machine Learning with Python',
            slug='machine-learning-python',
            description='Introduction to machine learning using scikit-learn, TensorFlow, and PyTorch.',
            session_format='workshop',
            level='beginner',
            start_time=pycon_day1_morning,
            end_time=pycon_day1_morning + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall B',
            max_attendees=50,
            tags='ml, data-science, tensorflow'
        )
        session2.speakers.add(sp2)

        pycon_day1_midday = event1.start_date + timedelta(hours=3)
        
        session3 = Session.objects.create(
            event=event1,
            track=track3,
            title='Python in the Cloud',
            slug='python-cloud',
            description='Deploying and scaling Python applications on AWS, Azure, and Google Cloud.',
            session_format='talk',
            level='intermediate',
            start_time=pycon_day1_midday,
            end_time=pycon_day1_midday + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall C',
            tags='cloud, aws, azure, devops'
        )
        session3.speakers.add(sp3)

        pycon_day1_afternoon = event1.start_date + timedelta(hours=6)
        
        session4 = Session.objects.create(
            event=event1,
            track=track1,
            title='Advanced Django Patterns',
            slug='advanced-django-patterns',
            description='Best practices and design patterns in Django for building maintainable applications.',
            session_format='talk',
            level='advanced',
            start_time=pycon_day1_afternoon,
            end_time=pycon_day1_afternoon + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall A',
            tags='django, patterns, architecture'
        )
        session4.speakers.add(sp1)

        session5 = Session.objects.create(
            event=event1,
            track=track2,
            title='Data Visualization with Python',
            slug='data-viz-python',
            description='Creating beautiful and interactive charts with Matplotlib, Seaborn, and Plotly.',
            session_format='workshop',
            level='intermediate',
            start_time=pycon_day1_afternoon,
            end_time=pycon_day1_afternoon + timedelta(hours=1, minutes=30),
            duration_minutes=90,
            room='Hall B',
            max_attendees=40,
            tags='data-viz, matplotlib, plotly'
        )
        session5.speakers.add(sp2)

        # DjangoCon sessions
        djangocon_day1_morning = event2.start_date + timedelta(hours=1)
        
        session6 = Session.objects.create(
            event=event2,
            track=track4,
            title='Django 5.0 New Features',
            slug='django-5-new-features',
            description='Exploring the latest features and improvements in Django 5.0.',
            session_format='keynote',
            level='all',
            start_time=djangocon_day1_morning,
            end_time=djangocon_day1_morning + timedelta(hours=1),
            duration_minutes=60,
            room='Main Hall',
            tags='django, django5, new-features'
        )
        session6.speakers.add(sp1)

        djangocon_day1_midday = event2.start_date + timedelta(hours=3)
        
        session7 = Session.objects.create(
            event=event2,
            track=track5,
            title='Building Production-Ready APIs with DRF',
            slug='production-apis-drf',
            description='Complete guide to Django REST Framework for building robust, scalable APIs.',
            session_format='workshop',
            level='intermediate',
            start_time=djangocon_day1_midday,
            end_time=djangocon_day1_midday + timedelta(hours=2),
            duration_minutes=120,
            room='Workshop Room',
            max_attendees=30,
            tags='drf, api, rest'
        )
        session7.speakers.add(sp2)

        self.stdout.write(self.style.SUCCESS('✅ Created 7 sessions'))

        # Create Registrations
        self.stdout.write('Creating registrations...')

        registration_count = 0
        
        # Register attendees for PyCon
        for i, attendee in enumerate(attendees[:8]):
            Registration.objects.create(
                event=event1,
                attendee=attendee,
                status='confirmed',
                confirmation_date=timezone.now()
            )
            registration_count += 1

        # Register attendees for DjangoCon
        for i, attendee in enumerate(attendees[2:7]):
            Registration.objects.create(
                event=event2,
                attendee=attendee,
                status='confirmed',
                confirmation_date=timezone.now()
            )
            registration_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Created {registration_count} registrations'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🎉 Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'👥 Users: {User.objects.count()}')
        self.stdout.write(f'🎪 Events: {Event.objects.count()}')
        self.stdout.write(f'🎯 Tracks: {Track.objects.count()}')
        self.stdout.write(f'🎤 Speakers: {Speaker.objects.count()}')
        self.stdout.write(f'📅 Sessions: {Session.objects.count()}')
        self.stdout.write(f'🎫 Registrations: {Registration.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write('\n💡 Test credentials:')
        self.stdout.write('   Organizer: john@eventhub.com / password123')
        self.stdout.write('   Speaker: alice@tech.com / password123')
        self.stdout.write('   Attendee: attendee1@example.com / password123')
        self.stdout.write('\n🌐 Access API at: http://127.0.0.1:8000/api/v1/')
        self.stdout.write('📚 API Docs at: http://127.0.0.1:8000/api/docs/')
        self.stdout.write('🔧 Admin panel: http://127.0.0.1:8000/admin/')