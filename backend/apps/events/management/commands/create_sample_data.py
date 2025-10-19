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
        speaker1 = User.objects.create_user(
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

        speaker2 = User.objects.create_user(
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

        speaker3 = User.objects.create_user(
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
        
        event1 = Event.objects.create(
            title='PyCon 2025',
            slug='pycon-2025',
            description='The largest annual gathering for the Python community.',
            start_date=now + timedelta(days=30),
            end_date=now + timedelta(days=32),
            venue='Convention Center',
            address='123 Tech Street, San Francisco, CA 94102',
            city='San Francisco',
            country='USA',
            capacity=500,
            is_published=True,
            organizer=organizer1
        )

        event2 = Event.objects.create(
            title='DjangoCon Europe 2025',
            slug='djangocon-europe-2025',
            description='European Django conference bringing together Django developers.',
            start_date=now + timedelta(days=45),
            end_date=now + timedelta(days=47),
            venue='Tech Hub',
            address='456 Dev Avenue, Berlin, Germany',
            city='Berlin',
            country='Germany',
            capacity=300,
            is_published=True,
            organizer=organizer2
        )

        event3 = Event.objects.create(
            title='React Summit 2025',
            slug='react-summit-2025',
            description='The biggest React conference of the year.',
            start_date=now + timedelta(days=60),
            end_date=now + timedelta(days=61),
            venue='Innovation Center',
            address='789 Frontend Blvd, Austin, TX 78701',
            city='Austin',
            country='USA',
            capacity=400,
            is_published=True,
            organizer=organizer1
        )

        event4 = Event.objects.create(
            title='DevOps Days 2025',
            slug='devops-days-2025',
            description='Learn the latest in DevOps practices and tools.',
            start_date=now + timedelta(days=75),
            end_date=now + timedelta(days=76),
            venue='Cloud Center',
            address='321 Ops Street, Seattle, WA 98101',
            city='Seattle',
            country='USA',
            capacity=250,
            is_published=True,
            organizer=organizer2
        )

        event5 = Event.objects.create(
            title='AI & ML Summit 2025',
            slug='ai-ml-summit-2025',
            description='Exploring the future of artificial intelligence and machine learning.',
            start_date=now + timedelta(days=90),
            end_date=now + timedelta(days=92),
            venue='Future Tech Center',
            address='555 AI Avenue, London, UK',
            city='London',
            country='UK',
            capacity=600,
            is_published=True,
            organizer=organizer1
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 5 events'))

        # Create Tracks
        self.stdout.write('Creating tracks...')

        # PyCon tracks
        track1 = Track.objects.create(
            name='Web Development',
            description='Sessions focused on web development with Python',
            event=event1,
            color='#3B82F6'
        )

        track2 = Track.objects.create(
            name='Data Science',
            description='Machine learning and data analysis sessions',
            event=event1,
            color='#10B981'
        )

        track3 = Track.objects.create(
            name='DevOps',
            description='Python in DevOps and cloud infrastructure',
            event=event1,
            color='#F59E0B'
        )

        # DjangoCon tracks
        track4 = Track.objects.create(
            name='Django Core',
            description='Deep dive into Django framework',
            event=event2,
            color='#0C4B33'
        )

        track5 = Track.objects.create(
            name='Django REST Framework',
            description='Building APIs with DRF',
            event=event2,
            color='#6366F1'
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 5 tracks'))

        # Create Speakers
        self.stdout.write('Creating speakers...')

        sp1 = Speaker.objects.create(
            user=speaker1,
            bio='Expert Python developer with 15 years of experience.'
        )

        sp2 = Speaker.objects.create(
            user=speaker2,
            bio='Full-stack developer and startup founder.'
        )

        sp3 = Speaker.objects.create(
            user=speaker3,
            bio='Cloud architect specializing in Azure and AWS.'
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 3 speakers'))

        # Create Sessions
        self.stdout.write('Creating sessions...')

        # PyCon sessions
        Session.objects.create(
            title='Building Scalable APIs with Django REST Framework',
            description='Learn how to build production-ready REST APIs.',
            event=event1,
            track=track1,
            start_time=event1.start_date.replace(hour=9, minute=0),
            end_time=event1.start_date.replace(hour=10, minute=30),
            room='Hall A',
            speaker=sp1,
            capacity=100
        )

        Session.objects.create(
            title='Machine Learning with Python',
            description='Introduction to ML using scikit-learn and TensorFlow.',
            event=event1,
            track=track2,
            start_time=event1.start_date.replace(hour=9, minute=0),
            end_time=event1.start_date.replace(hour=10, minute=30),
            room='Hall B',
            speaker=sp2,
            capacity=150
        )

        Session.objects.create(
            title='Python in the Cloud',
            description='Deploying Python applications to AWS and Azure.',
            event=event1,
            track=track3,
            start_time=event1.start_date.replace(hour=11, minute=0),
            end_time=event1.start_date.replace(hour=12, minute=30),
            room='Hall A',
            speaker=sp3,
            capacity=100
        )

        Session.objects.create(
            title='Advanced Django Patterns',
            description='Best practices and design patterns in Django.',
            event=event1,
            track=track1,
            start_time=event1.start_date.replace(hour=14, minute=0),
            end_time=event1.start_date.replace(hour=15, minute=30),
            room='Hall A',
            speaker=sp1,
            capacity=100
        )

        Session.objects.create(
            title='Data Visualization with Python',
            description='Creating beautiful charts with Matplotlib and Plotly.',
            event=event1,
            track=track2,
            start_time=event1.start_date.replace(hour=14, minute=0),
            end_time=event1.start_date.replace(hour=15, minute=30),
            room='Hall B',
            speaker=sp2,
            capacity=150
        )

        # DjangoCon sessions
        Session.objects.create(
            title='Django 5.0 New Features',
            description='Exploring the latest features in Django 5.0.',
            event=event2,
            track=track4,
            start_time=event2.start_date.replace(hour=9, minute=0),
            end_time=event2.start_date.replace(hour=10, minute=0),
            room='Main Hall',
            speaker=sp1,
            capacity=200
        )

        Session.objects.create(
            title='Building APIs with DRF',
            description='Complete guide to Django REST Framework.',
            event=event2,
            track=track5,
            start_time=event2.start_date.replace(hour=10, minute=30),
            end_time=event2.start_date.replace(hour=12, minute=0),
            room='Main Hall',
            speaker=sp2,
            capacity=200
        )

        self.stdout.write(self.style.SUCCESS('✅ Created 7 sessions'))

        # Create Registrations
        self.stdout.write('Creating registrations...')

        registration_count = 0
        for i, attendee in enumerate(attendees[:8]):
            Registration.objects.create(
                event=event1,
                user=attendee,
                status='confirmed'
            )
            registration_count += 1

        for i, attendee in enumerate(attendees[2:7]):
            Registration.objects.create(
                event=event2,
                user=attendee,
                status='confirmed'
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
        self.stdout.write('📚 Docs at: http://127.0.0.1:8000/api/docs/')