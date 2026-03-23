# =============================================================================
# apps/mice/serializers.py
# =============================================================================
# Dual-view serializers:
#   - Organizer serializers: full data including modal_price, margins
#   - Client serializers: client-facing price only, margins stripped
# =============================================================================

from decimal import Decimal
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    MICEProject, SubEvent, Quotation, QuotationSection,
    QuotationLineItem, ProjectTask, ProjectAsset, Vendor,
    ProjectStatus, QuotationStatus,
)

User = get_user_model()


# ── Vendor ────────────────────────────────────────────────────────────────────

class VendorSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model   = Vendor
        fields  = [
            'id', 'name', 'category', 'category_display',
            'contact_name', 'contact_phone', 'contact_email',
            'address', 'notes', 'default_rate', 'default_rate_unit',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


# ── QuotationLineItem — ORGANIZER view (full pricing) ─────────────────────────

class LineItemOrganizerSerializer(serializers.ModelSerializer):
    """
    Full serializer — includes modal_price, margin, pph.
    ONLY for the organizer. Never sent to client.
    """
    vendor_name     = serializers.CharField(source='vendor.name', read_only=True, default=None)
    vol_unit_display= serializers.CharField(source='get_vol_unit_display', read_only=True)
    dur_unit_display= serializers.CharField(source='get_dur_unit_display', read_only=True)

    class Meta:
        model   = QuotationLineItem
        fields  = [
            'id', 'sort_order',
            'vendor', 'vendor_name',
            'item_name', 'detail',
            'qty', 'vol_unit', 'vol_unit_display',
            'duration', 'dur_unit', 'dur_unit_display',
            # Internal pricing (organizer only)
            'modal_price', 'margin_pct',
            'margin_amt', 'total_margin', 'pph_amt',
            'total_modal',
            # Client pricing
            'client_price', 'total_client',
            'notes',
        ]
        read_only_fields = [
            'id', 'margin_amt', 'total_margin', 'pph_amt',
            'total_modal', 'client_price', 'total_client',
        ]


class LineItemCreateSerializer(serializers.ModelSerializer):
    """Used to create/update line items. Triggers recalculate() on save."""

    class Meta:
        model   = QuotationLineItem
        fields  = [
            'id', 'section', 'vendor', 'item_name', 'detail',
            'qty', 'vol_unit', 'duration', 'dur_unit',
            'modal_price', 'margin_pct', 'sort_order', 'notes',
        ]
        read_only_fields = ['id']

    def validate_modal_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Modal price cannot be negative')
        return value

    def validate_margin_pct(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError('Margin must be between 0 and 1000%')
        return value


# ── QuotationLineItem — CLIENT view (prices only, no margins) ─────────────────

class LineItemClientSerializer(serializers.ModelSerializer):
    """
    Client-facing serializer.
    STRIPS: modal_price, margin_pct, margin_amt, total_margin, pph_amt.
    Client only sees what they pay.
    """
    vol_unit_display = serializers.CharField(source='get_vol_unit_display', read_only=True)
    dur_unit_display = serializers.CharField(source='get_dur_unit_display', read_only=True)

    class Meta:
        model   = QuotationLineItem
        fields  = [
            'id', 'sort_order',
            'item_name', 'detail',
            'qty', 'vol_unit', 'vol_unit_display',
            'duration', 'dur_unit', 'dur_unit_display',
            'client_price', 'total_client',
        ]


# ── QuotationSection ──────────────────────────────────────────────────────────

class SectionOrganizerSerializer(serializers.ModelSerializer):
    line_items = LineItemOrganizerSerializer(many=True, read_only=True)

    class Meta:
        model   = QuotationSection
        fields  = [
            'id', 'name', 'sort_order',
            'subtotal_modal', 'subtotal_client',
            'line_items',
        ]
        read_only_fields = ['id', 'subtotal_modal', 'subtotal_client']


class SectionClientSerializer(serializers.ModelSerializer):
    line_items = LineItemClientSerializer(many=True, read_only=True)

    class Meta:
        model   = QuotationSection
        fields  = [
            'id', 'name', 'sort_order',
            'subtotal_client',
            'line_items',
        ]


class SectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = QuotationSection
        fields  = ['id', 'quotation', 'name', 'sort_order']
        read_only_fields = ['id']


# ── Quotation ─────────────────────────────────────────────────────────────────

class QuotationSummarySerializer(serializers.ModelSerializer):
    """Lightweight — for list views and project summaries."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model   = Quotation
        fields  = [
            'id', 'revision', 'status', 'status_display',
            'total_after_tax', 'total_margin', 'net_margin',
            'margin_pct_of_total', 'sent_at', 'approved_at',
            'client_portal_url', 'created_at',
        ]


class QuotationOrganizerSerializer(serializers.ModelSerializer):
    """
    Full organizer view — ALL financial data including internal margins.
    This is what Awis sees on his dashboard.
    """
    sections        = SectionOrganizerSerializer(many=True, read_only=True)
    status_display  = serializers.CharField(source='get_status_display', read_only=True)
    mice_project_name = serializers.CharField(
        source='mice_project.event.title', read_only=True
    )
    client_company  = serializers.CharField(
        source='mice_project.client_company', read_only=True
    )

    class Meta:
        model   = Quotation
        fields  = [
            'id', 'revision', 'status', 'status_display',
            'mice_project', 'mice_project_name', 'client_company',

            # Financial parameters
            'fee_management_pct', 'ppn_pct',
            'pph_vendor_pct', 'sodaqoh_pct',

            # Computed totals — full internal view
            'subtotal_modal', 'subtotal_client',
            'fee_management_amt', 'total_before_tax',
            'ppn_amt', 'total_after_tax',

            # Internal margin summary
            'margin_produksi', 'margin_fee_amt',
            'total_margin', 'sodaqoh_amt',
            'net_margin', 'margin_pct_of_total',

            # Payment tracking
            'payment_term_1', 'payment_term_2',
            'payment_term_1_due', 'payment_term_2_due',
            'payment_term_1_paid', 'payment_term_2_paid',

            # Access
            'client_portal_url', 'sent_at', 'approved_at',
            'notes', 'created_at', 'updated_at',

            # Nested
            'sections',
        ]
        read_only_fields = [
            'id', 'revision',
            'subtotal_modal', 'subtotal_client',
            'fee_management_amt', 'total_before_tax',
            'ppn_amt', 'total_after_tax',
            'margin_produksi', 'margin_fee_amt',
            'total_margin', 'sodaqoh_amt',
            'net_margin', 'margin_pct_of_total',
            'client_portal_url', 'sent_at', 'approved_at',
            'created_at', 'updated_at',
        ]


class QuotationClientSerializer(serializers.ModelSerializer):
    """
    CLIENT PORTAL VIEW — margins completely stripped.
    What Mandiri Utama Finance sees at the approval URL.
    No modal_price, no margins, no internal data.
    """
    sections        = SectionClientSerializer(many=True, read_only=True)
    event_title     = serializers.CharField(
        source='mice_project.event.title', read_only=True
    )
    client_company  = serializers.CharField(
        source='mice_project.client_company', read_only=True
    )
    client_pic      = serializers.CharField(
        source='mice_project.client_pic', read_only=True
    )
    quotation_number = serializers.CharField(
        source='mice_project.quotation_number', read_only=True
    )
    event_dates     = serializers.SerializerMethodField()

    class Meta:
        model   = Quotation
        fields  = [
            'id', 'revision',
            'event_title', 'client_company', 'client_pic',
            'quotation_number', 'event_dates',

            # Client-visible financials ONLY
            'subtotal_client',
            'fee_management_amt',
            'total_before_tax', 'ppn_amt', 'total_after_tax',

            # Payment terms
            'payment_term_1', 'payment_term_2',
            'payment_term_1_due', 'payment_term_2_due',

            'status', 'created_at',
            'sections',
        ]

    def get_event_dates(self, obj):
        event = obj.mice_project.event
        return {
            'start': event.start_date,
            'end':   event.end_date,
            'venue': event.venue_name,
            'city':  event.city,
        }


class QuotationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Quotation
        fields  = [
            'mice_project',
            'fee_management_pct', 'ppn_pct',
            'pph_vendor_pct', 'sodaqoh_pct',
            'payment_term_1', 'payment_term_2',
            'payment_term_1_due', 'payment_term_2_due',
            'notes',
        ]

    def validate(self, data):
        request = self.context['request']
        project = data.get('mice_project')
        if project and project.organizer != request.user:
            raise serializers.ValidationError(
                'You are not the organizer of this project'
            )
        return data

    def create(self, validated_data):
        # Auto-set revision number
        project     = validated_data['mice_project']
        last_rev    = project.quotations.aggregate(
            max_rev=__import__('django.db.models', fromlist=['Max']).Max('revision')
        )['max_rev'] or 0
        validated_data['revision'] = last_rev + 1
        return super().create(validated_data)


# ── SubEvent ──────────────────────────────────────────────────────────────────

class SubEventSerializer(serializers.ModelSerializer):

    class Meta:
        model   = SubEvent
        fields  = [
            'id', 'title', 'description',
            'venue_name', 'venue_address',
            'start_datetime', 'end_datetime',
            'capacity', 'sort_order', 'is_active',
            'ticket_tier_id',
            'created_at',
        ]
        read_only_fields = ['id', 'ticket_tier_id', 'created_at']


# ── ProjectTask ───────────────────────────────────────────────────────────────

class ProjectTaskSerializer(serializers.ModelSerializer):
    assigned_to_name    = serializers.CharField(
        source='assigned_to.get_full_name', read_only=True, default=None
    )
    status_display      = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue          = serializers.SerializerMethodField()

    class Meta:
        model   = ProjectTask
        fields  = [
            'id', 'title', 'description',
            'status', 'status_display', 'priority',
            'assigned_to', 'assigned_to_name',
            'sub_event', 'due_at', 'completed_at',
            'sort_order', 'is_overdue', 'created_at',
        ]
        read_only_fields = ['id', 'completed_at', 'created_at']

    def get_is_overdue(self, obj):
        from django.utils import timezone
        return (
            obj.due_at is not None
            and obj.due_at < timezone.now()
            and obj.status not in ('done',)
        )


# ── ProjectAsset ──────────────────────────────────────────────────────────────

class ProjectAssetSerializer(serializers.ModelSerializer):
    uploaded_by_name    = serializers.CharField(
        source='uploaded_by.get_full_name', read_only=True, default=None
    )
    asset_type_display  = serializers.CharField(source='get_asset_type_display', read_only=True)
    file_size_display   = serializers.SerializerMethodField()

    class Meta:
        model   = ProjectAsset
        fields  = [
            'id', 'asset_type', 'asset_type_display',
            'title', 'description', 'file', 'version',
            'file_size', 'file_size_display', 'mime_type',
            'sub_event', 'uploaded_by', 'uploaded_by_name',
            'created_at',
        ]
        read_only_fields = ['id', 'file_size', 'mime_type', 'uploaded_by', 'created_at']

    def get_file_size_display(self, obj):
        size = obj.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        else:
            return f'{size / (1024 * 1024):.1f} MB'

    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        file = validated_data.get('file')
        if file:
            validated_data['file_size'] = file.size
            validated_data['mime_type'] = getattr(file, 'content_type', '')
        return super().create(validated_data)


# ── MICEProject ───────────────────────────────────────────────────────────────

class MICEProjectListSerializer(serializers.ModelSerializer):
    """Lightweight — for dashboard list views."""
    event_title         = serializers.CharField(source='event.title', read_only=True)
    event_start         = serializers.DateTimeField(source='event.start_date', read_only=True)
    status_display      = serializers.CharField(source='get_status_display', read_only=True)
    active_quotation    = QuotationSummarySerializer(read_only=True)
    sub_event_count     = serializers.SerializerMethodField()
    task_counts         = serializers.SerializerMethodField()

    class Meta:
        model   = MICEProject
        fields  = [
            'id', 'event', 'event_title', 'event_start',
            'client_company', 'client_pic',
            'quotation_number', 'status', 'status_display',
            'active_quotation', 'sub_event_count', 'task_counts',
            'created_at',
        ]

    def get_sub_event_count(self, obj):
        return obj.sub_events.filter(is_active=True).count()

    def get_task_counts(self, obj):
        tasks = obj.tasks.all()
        return {
            'total':        tasks.count(),
            'done':         tasks.filter(status='done').count(),
            'overdue':      tasks.filter(
                status__in=['todo', 'in_progress'],
                due_at__lt=__import__('django.utils.timezone', fromlist=['now']).now()
            ).count(),
        }


class MICEProjectDetailSerializer(serializers.ModelSerializer):
    """Full detail — includes all sub-events, quotations, tasks, assets."""
    event_title     = serializers.CharField(source='event.title', read_only=True)
    event_start     = serializers.DateTimeField(source='event.start_date', read_only=True)
    event_end       = serializers.DateTimeField(source='event.end_date', read_only=True)
    event_venue     = serializers.CharField(source='event.venue_name', read_only=True)
    event_city      = serializers.CharField(source='event.city', read_only=True)
    status_display  = serializers.CharField(source='get_status_display', read_only=True)

    sub_events      = SubEventSerializer(many=True, read_only=True)
    quotations      = QuotationSummarySerializer(many=True, read_only=True)
    tasks           = ProjectTaskSerializer(many=True, read_only=True)
    assets          = ProjectAssetSerializer(many=True, read_only=True)

    class Meta:
        model   = MICEProject
        fields  = [
            'id', 'event', 'event_title', 'event_start', 'event_end',
            'event_venue', 'event_city',
            'client_company', 'client_pic', 'client_address',
            'client_email', 'client_phone',
            'quotation_number', 'status', 'status_display',
            'project_start', 'project_end',
            'approved_at', 'internal_notes',
            'sub_events', 'quotations', 'tasks', 'assets',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'quotation_number', 'approved_at', 'created_at', 'updated_at'
        ]


class MICEProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = MICEProject
        fields  = [
            'event',
            'client_company', 'client_pic', 'client_address',
            'client_email', 'client_phone',
            'quotation_number',
            'project_start', 'project_end',
            'internal_notes',
        ]

    def validate_event(self, event):
        request = self.context['request']
        if event.organizer != request.user:
            raise serializers.ValidationError(
                'You can only create a MICE project for events you organize'
            )
        if hasattr(event, 'mice_project'):
            raise serializers.ValidationError(
                'This event already has a MICE project'
            )
        return event

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)
