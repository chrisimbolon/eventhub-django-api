# apps/mice/admin.py
from django.contrib import admin
from .models import (
    MICEProject, SubEvent, Quotation, QuotationSection,
    QuotationLineItem, ProjectTask, ProjectAsset, Vendor,
)


class SubEventInline(admin.TabularInline):
    model = SubEvent
    extra = 1
    fields = ['title', 'venue_name', 'start_datetime', 'capacity', 'sort_order']


class QuotationInline(admin.TabularInline):
    model = Quotation
    extra = 0
    fields = ['revision', 'status', 'total_after_tax', 'net_margin', 'approved_at']
    readonly_fields = ['revision', 'total_after_tax', 'net_margin', 'approved_at']
    show_change_link = True


@admin.register(MICEProject)
class MICEProjectAdmin(admin.ModelAdmin):
    list_display    = ['event', 'client_company', 'status', 'quotation_number', 'created_at']
    list_filter     = ['status', 'created_at']
    search_fields   = ['event__title', 'client_company', 'quotation_number']
    readonly_fields = ['quotation_number', 'approved_at', 'created_at', 'updated_at']
    inlines         = [SubEventInline, QuotationInline]
    raw_id_fields   = ['event', 'organizer']


class QuotationSectionInline(admin.TabularInline):
    model           = QuotationSection
    extra           = 0
    fields          = ['name', 'sort_order', 'subtotal_modal', 'subtotal_client']
    readonly_fields = ['subtotal_modal', 'subtotal_client']
    show_change_link = True


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display    = [
        '__str__', 'total_after_tax', 'net_margin',
        'margin_pct_of_total', 'status', 'approved_at',
    ]
    list_filter     = ['status']
    readonly_fields = [
        'subtotal_modal', 'subtotal_client',
        'fee_management_amt', 'total_before_tax', 'ppn_amt', 'total_after_tax',
        'margin_produksi', 'margin_fee_amt', 'total_margin',
        'sodaqoh_amt', 'net_margin', 'margin_pct_of_total',
        'client_token', 'sent_at', 'approved_at', 'created_at', 'updated_at',
    ]
    inlines = [QuotationSectionInline]


class LineItemInline(admin.TabularInline):
    model           = QuotationLineItem
    extra           = 1
    fields          = [
        'item_name', 'detail', 'qty', 'vol_unit', 'duration', 'dur_unit',
        'modal_price', 'margin_pct', 'total_modal', 'client_price', 'total_client',
    ]
    readonly_fields = ['total_modal', 'margin_amt', 'pph_amt', 'client_price', 'total_client']


@admin.register(QuotationSection)
class QuotationSectionAdmin(admin.ModelAdmin):
    list_display    = ['name', 'quotation', 'subtotal_modal', 'subtotal_client', 'sort_order']
    readonly_fields = ['subtotal_modal', 'subtotal_client']
    inlines         = [LineItemInline]


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display    = ['name', 'category', 'contact_name', 'contact_phone', 'is_active']
    list_filter     = ['category', 'is_active']
    search_fields   = ['name', 'contact_name', 'contact_email']


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display    = ['title', 'mice_project', 'assigned_to', 'status', 'priority', 'due_at']
    list_filter     = ['status', 'priority']
    raw_id_fields   = ['mice_project', 'assigned_to', 'sub_event']


@admin.register(ProjectAsset)
class ProjectAssetAdmin(admin.ModelAdmin):
    list_display    = ['title', 'mice_project', 'asset_type', 'uploaded_by', 'created_at']
    list_filter     = ['asset_type']
    raw_id_fields   = ['mice_project', 'uploaded_by']
