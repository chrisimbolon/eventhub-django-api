# =============================================================================
# apps/mice/models.py
# =============================================================================
# Complete MICE production management models.
#
# New app — attaches to existing Event via OneToOneField.
# Zero changes required to apps/events/models.py.
#
# Model hierarchy:
#   MICEProject (1) ──► SubEvent (many)
#                  ──► Quotation (many revisions)
#                        ──► QuotationSection (many)
#                              ──► QuotationLineItem (many)
#                  ──► ProjectTask (many)
#                  ──► ProjectAsset (many)
#   Vendor (standalone, referenced by line items)
# =============================================================================

import uuid
from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from apps.events.models import Event

User = get_user_model()

TWO_PLACES = Decimal('0.01')


# ── Helpers ───────────────────────────────────────────────────────────────────

def _round(value):
    """Round to 2 decimal places using ROUND_HALF_UP — matches Indonesian accounting."""
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _generate_quotation_token():
    return get_random_string(length=48)


# ── Choices ───────────────────────────────────────────────────────────────────

class ProjectStatus(models.TextChoices):
    DRAFT       = 'draft',       'Draft'
    QUOTED      = 'quoted',      'Quotation Sent'
    APPROVED    = 'approved',    'Client Approved'
    ACTIVE      = 'active',      'Active / In Execution'
    COMPLETED   = 'completed',   'Completed'
    CANCELLED   = 'cancelled',   'Cancelled'


class QuotationStatus(models.TextChoices):
    DRAFT       = 'draft',       'Draft'
    SENT        = 'sent',        'Sent to Client'
    APPROVED    = 'approved',    'Approved by Client'
    REJECTED    = 'rejected',    'Rejected'
    SUPERSEDED  = 'superseded',  'Superseded by Revision'


class TaskStatus(models.TextChoices):
    TODO        = 'todo',        'To Do'
    IN_PROGRESS = 'in_progress', 'In Progress'
    DONE        = 'done',        'Done'
    BLOCKED     = 'blocked',     'Blocked'


class VendorCategory(models.TextChoices):
    VENUE           = 'venue',          'Venue'
    CATERING        = 'catering',       'Catering'
    AV_TECHNICAL    = 'av_technical',   'AV & Technical'
    DECORATION      = 'decoration',     'Decoration & Staging'
    ENTERTAINMENT   = 'entertainment',  'Entertainment & Talent'
    PHOTOGRAPHY     = 'photography',    'Photography & Video'
    TRANSPORTATION  = 'transportation', 'Transportation'
    ACCOMMODATION   = 'accommodation',  'Accommodation'
    CREW            = 'crew',           'Crew & HR'
    DESIGN          = 'design',         'Design & Multimedia'
    OTHER           = 'other',          'Other'


class DurationUnit(models.TextChoices):
    DAY     = 'day',    'Day'
    EVENT   = 'event',  'Event'
    VENUE   = 'venue',  'Venue'
    HOUR    = 'hour',   'Hour'
    PAX     = 'pax',    'Pax'
    TEAM    = 'team',   'Team'


class VolUnit(models.TextChoices):
    PAX     = 'pax',    'Pax'
    PACK    = 'pack',   'Package'
    UNIT    = 'unit',   'Unit'
    PRSN    = 'prsn',   'Person'
    TEAM    = 'team',   'Team'
    SET     = 'set',    'Set'
    PCS     = 'pcs',    'Pieces'
    FILE    = 'file',   'File'
    SPACE   = 'space',  'Space'
    TABLE   = 'table',  'Table'
    LOT     = 'lot',    'Lot'


# ── Vendor ────────────────────────────────────────────────────────────────────

class Vendor(models.Model):
    """
    Saved vendor/supplier in organizer's address book.
    Referenced by QuotationLineItem for rate auto-fill.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors')

    name            = models.CharField(max_length=255, db_index=True)
    category        = models.CharField(max_length=50, choices=VendorCategory.choices)
    contact_name    = models.CharField(max_length=200, blank=True)
    contact_phone   = models.CharField(max_length=30, blank=True)
    contact_email   = models.EmailField(blank=True)
    address         = models.TextField(blank=True)
    notes           = models.TextField(blank=True)

    # Default rate for quick-fill in quotation line items
    default_rate    = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    default_rate_unit = models.CharField(
        max_length=20, choices=VolUnit.choices, blank=True,
    )

    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_vendor'
        ordering    = ['name']
        indexes     = [
            models.Index(fields=['created_by', 'category']),
            models.Index(fields=['created_by', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_category_display()})'


# ── MICEProject ───────────────────────────────────────────────────────────────

class MICEProject(models.Model):
    """
    MICE production project — wraps an existing Event with
    corporate client info, quotation management, and team tools.

    Relationship: OneToOne with Event.
    The Event is still the source of truth for dates/venue/capacity.
    MICEProject adds the B2B production layer on top.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event           = models.OneToOneField(
        Event, on_delete=models.CASCADE, related_name='mice_project',
    )
    organizer       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='mice_projects',
    )

    # Client information
    client_company      = models.CharField(max_length=255)
    client_pic          = models.CharField(max_length=200, help_text='Person in charge at client side')
    client_address      = models.TextField(blank=True)
    client_email        = models.EmailField(blank=True)
    client_phone        = models.CharField(max_length=30, blank=True)

    # Project metadata
    quotation_number    = models.CharField(
        max_length=100, blank=True,
        help_text='e.g. 020/QUO-MEO/IV/2025 — auto-generated if blank',
    )
    status              = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT,
        db_index=True,
    )

    # Dates
    project_start       = models.DateField(null=True, blank=True)
    project_end         = models.DateField(null=True, blank=True)
    approved_at         = models.DateTimeField(null=True, blank=True)

    # Internal notes
    internal_notes      = models.TextField(blank=True)

    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_project'
        ordering    = ['-created_at']
        indexes     = [
            models.Index(fields=['organizer', 'status']),
            models.Index(fields=['organizer', 'created_at']),
        ]

    def __str__(self):
        return f'{self.event.title} — {self.client_company}'

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            self.quotation_number = self._generate_quotation_number()
        super().save(*args, **kwargs)

    def _generate_quotation_number(self):
        from django.utils import timezone
        month   = timezone.now().strftime('%m')
        year    = timezone.now().strftime('%Y')
        count   = MICEProject.objects.filter(organizer=self.organizer).count() + 1
        return f'{count:03d}/QUO-EH/{month}/{year}'

    @property
    def active_quotation(self):
        """Returns the latest non-superseded quotation."""
        return self.quotations.exclude(
            status=QuotationStatus.SUPERSEDED
        ).order_by('-revision').first()

    def approve(self):
        """Mark project as approved and activate it."""
        self.status     = ProjectStatus.APPROVED
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_at', 'updated_at'])

    def activate(self):
        """
        Activate project after client approval.
        Creates TicketTier entries for each SubEvent automatically.
        """
        if self.status != ProjectStatus.APPROVED:
            raise ValueError('Project must be approved before activation')

        with transaction.atomic():
            from apps.events.models import TicketTier

            for sub_event in self.sub_events.filter(is_active=True):
                if not sub_event.ticket_tier_id:
                    tier = TicketTier.objects.create(
                        event           = self.event,
                        name            = sub_event.title,
                        description     = f'Ticket for {sub_event.title}',
                        price           = Decimal('0'),
                        total_slots     = sub_event.capacity,
                        slots_remaining = sub_event.capacity,
                        is_active       = True,
                        sort_order      = sub_event.sort_order,
                    )
                    sub_event.ticket_tier_id = tier.id
                    sub_event.save(update_fields=['ticket_tier_id'])

            self.status = ProjectStatus.ACTIVE
            self.event.status = 'published'
            self.event.save(update_fields=['status'])
            self.save(update_fields=['status', 'updated_at'])


# ── SubEvent ──────────────────────────────────────────────────────────────────

class SubEvent(models.Model):
    """
    Individual activity within a MICE project.
    e.g. Welcome Dinner, Special Dinner GWK, Yoga & Golf.
    Each maps to a TicketTier once the project is activated.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mice_project    = models.ForeignKey(
        MICEProject, on_delete=models.CASCADE, related_name='sub_events',
    )
    # ticket_tier linked after activation via a separate migration
    # keeping as nullable CharField to store the UUID reference safely
    ticket_tier_id  = models.UUIDField(null=True, blank=True, help_text='TicketTier UUID after activation')

    title           = models.CharField(max_length=200)
    description     = models.TextField(blank=True)
    venue_name      = models.CharField(max_length=255, blank=True)
    venue_address   = models.TextField(blank=True)
    start_datetime  = models.DateTimeField(null=True, blank=True)
    end_datetime    = models.DateTimeField(null=True, blank=True)
    capacity        = models.PositiveIntegerField(default=0)
    sort_order      = models.PositiveIntegerField(default=0)
    is_active       = models.BooleanField(default=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_sub_event'
        ordering    = ['sort_order', 'start_datetime']

    def __str__(self):
        return f'{self.mice_project.event.title} — {self.title}'


# ── Quotation ─────────────────────────────────────────────────────────────────

class Quotation(models.Model):
    """
    A versioned quotation document for a MICE project.
    Supports multiple revisions — only one is active at a time.

    Financial structure (mirrors Awis's Excel exactly):
      subtotal_modal    = sum of all line item modal totals
      subtotal_client   = sum of all line item client totals
      fee_management    = subtotal_modal × fee_management_pct
      total_before_tax  = subtotal_modal + fee_management
      ppn               = total_before_tax × ppn_pct
      total_after_tax   = total_before_tax + ppn

    Internal margin:
      margin_produksi   = sum of all line item margins
      margin_fee        = fee_management
      total_margin      = margin_produksi + margin_fee
      sodaqoh           = total_margin × sodaqoh_pct
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mice_project    = models.ForeignKey(
        MICEProject, on_delete=models.CASCADE, related_name='quotations',
    )

    revision        = models.PositiveIntegerField(default=1)
    status          = models.CharField(
        max_length=20, choices=QuotationStatus.choices,
        default=QuotationStatus.DRAFT, db_index=True,
    )

    # Financial parameters (all stored as percentages 0.00–1.00)
    fee_management_pct  = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.10'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Management fee as decimal e.g. 0.10 = 10%',
    )
    ppn_pct             = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.11'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='PPN VAT as decimal e.g. 0.11 = 11%',
    )
    pph_vendor_pct      = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.02'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Pph withheld from vendors e.g. 0.02 = 2%',
    )
    sodaqoh_pct         = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.025'),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Charitable giving from margin e.g. 0.025 = 2.5%',
    )

    # Computed totals — recalculated on every save via recalculate()
    # Stored for fast reads without re-aggregating all line items
    subtotal_modal      = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    subtotal_client     = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    fee_management_amt  = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_before_tax    = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    ppn_amt             = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_after_tax     = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    # Internal margin summary (never shown to client)
    margin_produksi     = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    margin_fee_amt      = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_margin        = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    sodaqoh_amt         = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    net_margin          = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    margin_pct_of_total = models.DecimalField(max_digits=6, decimal_places=4, default=0)

    # Payment installment tracking
    payment_term_1      = models.DecimalField(
        max_digits=16, decimal_places=2, default=0,
        help_text='First installment amount (Pertama)',
    )
    payment_term_2      = models.DecimalField(
        max_digits=16, decimal_places=2, default=0,
        help_text='Second installment amount (Turun 2)',
    )
    payment_term_1_due  = models.DateField(null=True, blank=True)
    payment_term_2_due  = models.DateField(null=True, blank=True)
    payment_term_1_paid = models.BooleanField(default=False)
    payment_term_2_paid = models.BooleanField(default=False)

    # Client portal access
    client_token        = models.CharField(
        max_length=48, unique=True, default=_generate_quotation_token,
        help_text='Token for client portal URL — no login required',
    )
    sent_at             = models.DateTimeField(null=True, blank=True)
    approved_at         = models.DateTimeField(null=True, blank=True)
    notes               = models.TextField(blank=True)

    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_quotation'
        ordering    = ['-revision']
        unique_together = ['mice_project', 'revision']
        indexes     = [
            models.Index(fields=['mice_project', 'status']),
            models.Index(fields=['client_token']),
        ]

    def __str__(self):
        return (
            f'{self.mice_project.quotation_number} '
            f'Rev.{self.revision} [{self.get_status_display()}]'
        )

    # ── The calculation engine ────────────────────────────────────────────────

    def recalculate(self):
        """
        THE HEART OF THE QUOTATION BUILDER.

        Aggregates all line items and recomputes every financial total.
        Called automatically after any line item is saved or deleted.
        All arithmetic uses Decimal — never float. Indonesian tax law compliant.

        Financial flow:
          1. Sum line items → subtotal_modal, subtotal_client, margin_produksi
          2. fee_management = subtotal_modal × fee_management_pct
          3. total_before_tax = subtotal_modal + fee_management
          4. ppn = total_before_tax × ppn_pct
          5. total_after_tax = total_before_tax + ppn
          6. total_margin = margin_produksi + fee_management
          7. sodaqoh = total_margin × sodaqoh_pct
          8. net_margin = total_margin − sodaqoh
          9. margin_pct = net_margin / total_after_tax
        """
        from django.db.models import Sum

        # Aggregate from all line items across all sections
        agg = QuotationLineItem.objects.filter(
            section__quotation=self
        ).aggregate(
            sum_modal=Sum('total_modal'),
            sum_client=Sum('total_client'),
            sum_margin=Sum('total_margin'),
        )

        subtotal_modal      = _round(agg['sum_modal']  or 0)
        subtotal_client     = _round(agg['sum_client'] or 0)
        margin_produksi     = _round(agg['sum_margin'] or 0)

        fee_management_amt  = _round(subtotal_modal * self.fee_management_pct)
        total_before_tax    = _round(subtotal_modal + fee_management_amt)
        ppn_amt             = _round(total_before_tax * self.ppn_pct)
        total_after_tax     = _round(total_before_tax + ppn_amt)

        margin_fee_amt      = fee_management_amt
        total_margin        = _round(margin_produksi + margin_fee_amt)
        sodaqoh_amt         = _round(total_margin * self.sodaqoh_pct)
        net_margin          = _round(total_margin - sodaqoh_amt)
        margin_pct          = (
            _round(net_margin / total_after_tax)
            if total_after_tax > 0 else Decimal('0')
        )

        # Bulk update — single SQL UPDATE, no signals triggered
        Quotation.objects.filter(pk=self.pk).update(
            subtotal_modal      = subtotal_modal,
            subtotal_client     = subtotal_client,
            fee_management_amt  = fee_management_amt,
            total_before_tax    = total_before_tax,
            ppn_amt             = ppn_amt,
            total_after_tax     = total_after_tax,
            margin_produksi     = margin_produksi,
            margin_fee_amt      = margin_fee_amt,
            total_margin        = total_margin,
            sodaqoh_amt         = sodaqoh_amt,
            net_margin          = net_margin,
            margin_pct_of_total = margin_pct,
            updated_at          = timezone.now(),
        )

        # Refresh instance fields
        self.subtotal_modal      = subtotal_modal
        self.subtotal_client     = subtotal_client
        self.fee_management_amt  = fee_management_amt
        self.total_before_tax    = total_before_tax
        self.ppn_amt             = ppn_amt
        self.total_after_tax     = total_after_tax
        self.margin_produksi     = margin_produksi
        self.margin_fee_amt      = margin_fee_amt
        self.total_margin        = total_margin
        self.sodaqoh_amt         = sodaqoh_amt
        self.net_margin          = net_margin
        self.margin_pct_of_total = margin_pct

    def create_revision(self):
        """
        Create a new revision of this quotation.
        Marks current as SUPERSEDED, clones all sections and line items.
        Returns the new Quotation instance.
        """
        with transaction.atomic():
            # Supersede current
            Quotation.objects.filter(pk=self.pk).update(
                status=QuotationStatus.SUPERSEDED
            )

            # Clone quotation
            new_q = Quotation.objects.create(
                mice_project        = self.mice_project,
                revision            = self.revision + 1,
                fee_management_pct  = self.fee_management_pct,
                ppn_pct             = self.ppn_pct,
                pph_vendor_pct      = self.pph_vendor_pct,
                sodaqoh_pct         = self.sodaqoh_pct,
                notes               = self.notes,
            )

            # Clone all sections and line items
            for section in self.sections.all().order_by('sort_order'):
                new_section = QuotationSection.objects.create(
                    quotation   = new_q,
                    name        = section.name,
                    sort_order  = section.sort_order,
                )
                for item in section.line_items.all().order_by('sort_order'):
                    QuotationLineItem.objects.create(
                        section         = new_section,
                        vendor          = item.vendor,
                        item_name       = item.item_name,
                        detail          = item.detail,
                        qty             = item.qty,
                        vol_unit        = item.vol_unit,
                        duration        = item.duration,
                        dur_unit        = item.dur_unit,
                        modal_price     = item.modal_price,
                        margin_pct      = item.margin_pct,
                        sort_order      = item.sort_order,
                        notes           = item.notes,
                    )

            new_q.recalculate()
            return new_q

    def send_to_client(self):
        """Mark quotation as sent and record timestamp."""
        self.status  = QuotationStatus.SENT
        self.sent_at = timezone.now()
        Quotation.objects.filter(pk=self.pk).update(
            status=self.status, sent_at=self.sent_at
        )

    def approve_by_client(self):
        """Called when client approves via portal."""
        self.status      = QuotationStatus.APPROVED
        self.approved_at = timezone.now()
        Quotation.objects.filter(pk=self.pk).update(
            status=self.status, approved_at=self.approved_at
        )
        # Also approve the parent project
        self.mice_project.approve()

    @property
    def client_portal_url(self):
        from django.conf import settings
        base = getattr(settings, 'FRONTEND_URL', 'https://eventhub.chrisimbolon.dev')
        return f'{base}/quotation/{self.client_token}'


# ── QuotationSection ──────────────────────────────────────────────────────────

class QuotationSection(models.Model):
    """
    A grouping of line items within a quotation.
    Matches the section headers in Awis's Excel:
      CONCEPT DEVELOPMENT · VENUE & ARRANGEMENT · ENTERTAINMENT ·
      TECHNICAL PRODUCTION · HUMAN RESOURCES · SUPPORTING · ACCOMMODATION
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quotation   = models.ForeignKey(
        Quotation, on_delete=models.CASCADE, related_name='sections',
    )
    name        = models.CharField(max_length=200)
    sort_order  = models.PositiveIntegerField(default=0)

    # Section-level subtotals (computed, cached)
    subtotal_modal  = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    subtotal_client = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_quotation_section'
        ordering    = ['sort_order']

    def __str__(self):
        return f'{self.quotation} — {self.name}'

    def recalculate(self):
        """Recompute section subtotals and trigger parent quotation recalc."""
        from django.db.models import Sum
        agg = self.line_items.aggregate(
            sm=Sum('total_modal'),
            sc=Sum('total_client'),
        )
        QuotationSection.objects.filter(pk=self.pk).update(
            subtotal_modal  = _round(agg['sm'] or 0),
            subtotal_client = _round(agg['sc'] or 0),
        )
        self.quotation.recalculate()


# ── QuotationLineItem ─────────────────────────────────────────────────────────

class QuotationLineItem(models.Model):
    """
    A single line item in a quotation section.

    Mirrors every column from Awis's Excel:
      NO · ITEM · DETAIL · QTY · VOL · DUR · VOL(unit) ·
      MODAL PRICE · TOTAL · MARGIN · TOTAL MARGIN · Pph · PRICE · TOTAL

    Calculation (all Decimal, ROUND_HALF_UP):
      total_modal   = modal_price × qty × duration
      margin_amt    = modal_price × margin_pct
      pph_amt       = modal_price × pph_vendor_pct
      client_price  = (modal_price + margin_amt − pph_amt)
      total_margin  = margin_amt × qty × duration
      total_client  = client_price × qty × duration

    The pph_vendor_pct is inherited from the parent Quotation.
    """
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section     = models.ForeignKey(
        QuotationSection, on_delete=models.CASCADE, related_name='line_items',
    )
    vendor      = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='line_items',
    )

    # Core item info
    item_name   = models.CharField(max_length=255)
    detail      = models.CharField(max_length=500, blank=True)

    # Quantity dimensions
    qty         = models.DecimalField(
        max_digits=10, decimal_places=2, default=1,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    vol_unit    = models.CharField(
        max_length=20, choices=VolUnit.choices, default=VolUnit.PAX,
    )
    duration    = models.DecimalField(
        max_digits=10, decimal_places=2, default=1,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    dur_unit    = models.CharField(
        max_length=20, choices=DurationUnit.choices, default=DurationUnit.DAY,
    )

    # Pricing (Decimal only — never float)
    modal_price     = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        help_text='Internal cost — never shown to client',
    )
    margin_pct      = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.15'),
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text='Margin as decimal e.g. 0.15 = 15%',
    )

    # Computed fields (auto-calculated on save, stored for fast reads)
    total_modal     = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    margin_amt      = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_margin    = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    pph_amt         = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    client_price    = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_client    = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    sort_order  = models.PositiveIntegerField(default=0)
    notes       = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_quotation_line_item'
        ordering    = ['sort_order', 'item_name']
        indexes     = [
            models.Index(fields=['section', 'sort_order']),
        ]

    def __str__(self):
        return f'{self.section.name} — {self.item_name}'

    def calculate(self):
        """
        Compute all derived price fields for this line item.
        Uses pph_vendor_pct from parent Quotation.
        Pure math — no DB calls. Call save() to persist.
        """
        pph_pct = self.section.quotation.pph_vendor_pct

        total_modal     = _round(self.modal_price * self.qty * self.duration)
        margin_amt      = _round(self.modal_price * self.margin_pct)
        total_margin    = _round(margin_amt * self.qty * self.duration)
        pph_amt         = _round(self.modal_price * pph_pct)
        client_price    = _round(self.modal_price + margin_amt - pph_amt)
        total_client    = _round(client_price * self.qty * self.duration)

        self.total_modal    = total_modal
        self.margin_amt     = margin_amt
        self.total_margin   = total_margin
        self.pph_amt        = pph_amt
        self.client_price   = client_price
        self.total_client   = total_client

    def save(self, *args, **kwargs):
        # Always recalculate before saving
        self.calculate()
        super().save(*args, **kwargs)
        # Cascade up: section → quotation
        self.section.recalculate()

    def delete(self, *args, **kwargs):
        section = self.section
        super().delete(*args, **kwargs)
        # Cascade recalc after deletion too
        section.recalculate()


# ── ProjectTask ───────────────────────────────────────────────────────────────

class ProjectTask(models.Model):
    """
    A task within a MICE project — assigned to a team member.
    Covers the "To do list" and SOW items from Awis's sketch.
    """
    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mice_project    = models.ForeignKey(
        MICEProject, on_delete=models.CASCADE, related_name='tasks',
    )
    assigned_to     = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tasks',
    )
    sub_event       = models.ForeignKey(
        SubEvent, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tasks',
        help_text='Optional — link task to a specific sub-event',
    )

    title           = models.CharField(max_length=300)
    description     = models.TextField(blank=True)
    status          = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO,
        db_index=True,
    )
    priority        = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')],
        default='medium',
    )
    due_at          = models.DateTimeField(null=True, blank=True)
    completed_at    = models.DateTimeField(null=True, blank=True)
    sort_order      = models.PositiveIntegerField(default=0)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_project_task'
        ordering    = ['sort_order', 'due_at']
        indexes     = [
            models.Index(fields=['mice_project', 'status']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f'{self.mice_project} — {self.title}'

    def complete(self):
        self.status       = TaskStatus.DONE
        self.completed_at = timezone.now()
        ProjectTask.objects.filter(pk=self.pk).update(
            status=self.status, completed_at=self.completed_at
        )


# ── ProjectAsset ──────────────────────────────────────────────────────────────

class ProjectAsset(models.Model):
    """
    File attached to a MICE project.
    Covers "How team share & distribute assets" from Awis's sketch.
    Types: SOW document, Key Visual, Stage 3D, Multimedia, etc.
    """
    ASSET_TYPES = [
        ('sow',         'Scope of Work'),
        ('key_visual',  'Key Visual 2D'),
        ('stage_3d',    'Stage Design 3D'),
        ('multimedia',  'Multimedia / Video'),
        ('contract',    'Vendor Contract'),
        ('report',      'Post-Event Report'),
        ('other',       'Other'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mice_project    = models.ForeignKey(
        MICEProject, on_delete=models.CASCADE, related_name='assets',
    )
    uploaded_by     = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploaded_assets',
    )
    sub_event       = models.ForeignKey(
        SubEvent, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assets',
    )

    asset_type      = models.CharField(max_length=30, choices=ASSET_TYPES, default='other')
    title           = models.CharField(max_length=255)
    description     = models.TextField(blank=True)
    file            = models.FileField(upload_to='mice/assets/%Y/%m/')
    file_size       = models.PositiveIntegerField(default=0, help_text='Bytes')
    mime_type       = models.CharField(max_length=100, blank=True)
    version         = models.CharField(max_length=50, blank=True, help_text='e.g. v1, v2-final')
    client_visible  = models.BooleanField(default=False, db_index=True,help_text='If True, visible to client via their portal',)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table    = 'mice_project_asset'
        ordering    = ['-created_at']

    def __str__(self):
        return f'{self.mice_project} — {self.title}'

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)
