# apps/mice/migrations/0001_initial.py
import uuid
import apps.mice.models
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # Use swappable_dependency for events app — finds the last migration automatically
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ── Vendor ────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id',               models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('created_by',       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendors', to=settings.AUTH_USER_MODEL)),
                ('name',             models.CharField(db_index=True, max_length=255)),
                ('category',         models.CharField(choices=[('venue','Venue'),('catering','Catering'),('av_technical','AV & Technical'),('decoration','Decoration & Staging'),('entertainment','Entertainment & Talent'),('photography','Photography & Video'),('transportation','Transportation'),('accommodation','Accommodation'),('crew','Crew & HR'),('design','Design & Multimedia'),('other','Other')], max_length=50)),
                ('contact_name',     models.CharField(blank=True, max_length=200)),
                ('contact_phone',    models.CharField(blank=True, max_length=30)),
                ('contact_email',    models.EmailField(blank=True)),
                ('address',          models.TextField(blank=True)),
                ('notes',            models.TextField(blank=True)),
                ('default_rate',     models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('default_rate_unit',models.CharField(blank=True, max_length=20)),
                ('is_active',        models.BooleanField(default=True)),
                ('created_at',       models.DateTimeField(auto_now_add=True)),
                ('updated_at',       models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_vendor', 'ordering': ['name']},
        ),

        # ── MICEProject ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='MICEProject',
            fields=[
                ('id',               models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('event',            models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mice_project', to='events.event')),
                ('organizer',        models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mice_projects', to=settings.AUTH_USER_MODEL)),
                ('client_company',   models.CharField(max_length=255)),
                ('client_pic',       models.CharField(max_length=200)),
                ('client_address',   models.TextField(blank=True)),
                ('client_email',     models.EmailField(blank=True)),
                ('client_phone',     models.CharField(blank=True, max_length=30)),
                ('quotation_number', models.CharField(blank=True, max_length=100)),
                ('status',           models.CharField(choices=[('draft','Draft'),('quoted','Quotation Sent'),('approved','Client Approved'),('active','Active / In Execution'),('completed','Completed'),('cancelled','Cancelled')], db_index=True, default='draft', max_length=20)),
                ('project_start',    models.DateField(blank=True, null=True)),
                ('project_end',      models.DateField(blank=True, null=True)),
                ('approved_at',      models.DateTimeField(blank=True, null=True)),
                ('internal_notes',   models.TextField(blank=True)),
                ('created_at',       models.DateTimeField(auto_now_add=True)),
                ('updated_at',       models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_project', 'ordering': ['-created_at']},
        ),
        migrations.AddIndex(model_name='miceproject', index=models.Index(fields=['organizer', 'status'], name='mice_project_org_status_idx')),
        migrations.AddIndex(model_name='miceproject', index=models.Index(fields=['organizer', 'created_at'], name='mice_project_org_created_idx')),

        # ── SubEvent ──────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='SubEvent',
            fields=[
                ('id',              models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('mice_project',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_events', to='mice.miceproject')),
                ('title',           models.CharField(max_length=200)),
                ('description',     models.TextField(blank=True)),
                ('venue_name',      models.CharField(blank=True, max_length=255)),
                ('venue_address',   models.TextField(blank=True)),
                ('start_datetime',  models.DateTimeField(blank=True, null=True)),
                ('end_datetime',    models.DateTimeField(blank=True, null=True)),
                ('capacity',        models.PositiveIntegerField(default=0)),
                ('sort_order',      models.PositiveIntegerField(default=0)),
                ('is_active',       models.BooleanField(default=True)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_sub_event', 'ordering': ['sort_order', 'start_datetime']},
        ),

        # ── Quotation ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id',                   models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('mice_project',         models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotations', to='mice.miceproject')),
                ('revision',             models.PositiveIntegerField(default=1)),
                ('status',               models.CharField(choices=[('draft','Draft'),('sent','Sent to Client'),('approved','Approved by Client'),('rejected','Rejected'),('superseded','Superseded by Revision')], db_index=True, default='draft', max_length=20)),
                ('fee_management_pct',   models.DecimalField(decimal_places=4, default=Decimal('0.10'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('ppn_pct',              models.DecimalField(decimal_places=4, default=Decimal('0.11'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('pph_vendor_pct',       models.DecimalField(decimal_places=4, default=Decimal('0.02'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('sodaqoh_pct',          models.DecimalField(decimal_places=4, default=Decimal('0.025'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('subtotal_modal',       models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('subtotal_client',      models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('fee_management_amt',   models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_before_tax',     models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('ppn_amt',              models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_after_tax',      models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('margin_produksi',      models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('margin_fee_amt',       models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('total_margin',         models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('sodaqoh_amt',          models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('net_margin',           models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('margin_pct_of_total',  models.DecimalField(decimal_places=4, default=0, max_digits=6)),
                ('payment_term_1',       models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('payment_term_2',       models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('payment_term_1_due',   models.DateField(blank=True, null=True)),
                ('payment_term_2_due',   models.DateField(blank=True, null=True)),
                ('payment_term_1_paid',  models.BooleanField(default=False)),
                ('payment_term_2_paid',  models.BooleanField(default=False)),
                ('client_token',         models.CharField(default=apps.mice.models._generate_quotation_token, max_length=48, unique=True)),
                ('sent_at',              models.DateTimeField(blank=True, null=True)),
                ('approved_at',          models.DateTimeField(blank=True, null=True)),
                ('notes',                models.TextField(blank=True)),
                ('created_at',           models.DateTimeField(auto_now_add=True)),
                ('updated_at',           models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_quotation', 'ordering': ['-revision']},
        ),
        migrations.AlterUniqueTogether(name='quotation', unique_together={('mice_project', 'revision')}),
        migrations.AddIndex(model_name='quotation', index=models.Index(fields=['mice_project', 'status'], name='mice_quotation_proj_status_idx')),
        migrations.AddIndex(model_name='quotation', index=models.Index(fields=['client_token'], name='mice_quotation_token_idx')),

        # ── QuotationSection ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='QuotationSection',
            fields=[
                ('id',              models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('quotation',       models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='mice.quotation')),
                ('name',            models.CharField(max_length=200)),
                ('sort_order',      models.PositiveIntegerField(default=0)),
                ('subtotal_modal',  models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('subtotal_client', models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_quotation_section', 'ordering': ['sort_order']},
        ),

        # ── QuotationLineItem ─────────────────────────────────────────────────
        migrations.CreateModel(
            name='QuotationLineItem',
            fields=[
                ('id',              models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('section',         models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='mice.quotationsection')),
                ('vendor',          models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='line_items', to='mice.vendor')),
                ('item_name',       models.CharField(max_length=255)),
                ('detail',          models.CharField(blank=True, max_length=500)),
                ('qty',             models.DecimalField(decimal_places=2, default=1, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('vol_unit',        models.CharField(choices=[('pax','Pax'),('pack','Package'),('unit','Unit'),('prsn','Person'),('team','Team'),('set','Set'),('pcs','Pieces'),('file','File'),('space','Space'),('table','Table'),('lot','Lot')], default='pax', max_length=20)),
                ('duration',        models.DecimalField(decimal_places=2, default=1, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('dur_unit',        models.CharField(choices=[('day','Day'),('event','Event'),('venue','Venue'),('hour','Hour'),('pax','Pax'),('team','Team')], default='day', max_length=20)),
                ('modal_price',     models.DecimalField(decimal_places=2, default=0, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
                ('margin_pct',      models.DecimalField(decimal_places=4, default=Decimal('0.15'), max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('total_modal',     models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('margin_amt',      models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('total_margin',    models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('pph_amt',         models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('client_price',    models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ('total_client',    models.DecimalField(decimal_places=2, default=0, max_digits=16)),
                ('sort_order',      models.PositiveIntegerField(default=0)),
                ('notes',           models.TextField(blank=True)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_quotation_line_item', 'ordering': ['sort_order', 'item_name']},
        ),
        migrations.AddIndex(model_name='quotationlineitem', index=models.Index(fields=['section', 'sort_order'], name='mice_lineitem_section_order_idx')),

        # ── ProjectTask ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectTask',
            fields=[
                ('id',              models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('mice_project',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='mice.miceproject')),
                ('assigned_to',     models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL)),
                ('sub_event',       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='mice.subevent')),
                ('title',           models.CharField(max_length=300)),
                ('description',     models.TextField(blank=True)),
                ('status',          models.CharField(choices=[('todo','To Do'),('in_progress','In Progress'),('done','Done'),('blocked','Blocked')], db_index=True, default='todo', max_length=20)),
                ('priority',        models.CharField(choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')], default='medium', max_length=10)),
                ('due_at',          models.DateTimeField(blank=True, null=True)),
                ('completed_at',    models.DateTimeField(blank=True, null=True)),
                ('sort_order',      models.PositiveIntegerField(default=0)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_project_task', 'ordering': ['sort_order', 'due_at']},
        ),
        migrations.AddIndex(model_name='projecttask', index=models.Index(fields=['mice_project', 'status'], name='mice_task_proj_status_idx')),
        migrations.AddIndex(model_name='projecttask', index=models.Index(fields=['assigned_to', 'status'], name='mice_task_assigned_status_idx')),

        # ── ProjectAsset ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectAsset',
            fields=[
                ('id',              models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ('mice_project',    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='mice.miceproject')),
                ('uploaded_by',     models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_assets', to=settings.AUTH_USER_MODEL)),
                ('sub_event',       models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assets', to='mice.subevent')),
                ('asset_type',      models.CharField(choices=[('sow','Scope of Work'),('key_visual','Key Visual 2D'),('stage_3d','Stage Design 3D'),('multimedia','Multimedia / Video'),('contract','Vendor Contract'),('report','Post-Event Report'),('other','Other')], default='other', max_length=30)),
                ('title',           models.CharField(max_length=255)),
                ('description',     models.TextField(blank=True)),
                ('file',            models.FileField(upload_to='mice/assets/%Y/%m/')),
                ('file_size',       models.PositiveIntegerField(default=0)),
                ('mime_type',       models.CharField(blank=True, max_length=100)),
                ('version',         models.CharField(blank=True, max_length=50)),
                ('created_at',      models.DateTimeField(auto_now_add=True)),
                ('updated_at',      models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'mice_project_asset', 'ordering': ['-created_at']},
        ),
    ]
