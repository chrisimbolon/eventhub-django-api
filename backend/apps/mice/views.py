# =============================================================================
# apps/mice/views.py
# =============================================================================

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import (
    MICEProject, SubEvent, Quotation, QuotationSection,
    QuotationLineItem, ProjectTask, ProjectAsset, Vendor,
    ProjectStatus, QuotationStatus,
)
from .serializers import (
    MICEProjectListSerializer, MICEProjectDetailSerializer,
    MICEProjectCreateSerializer,
    QuotationOrganizerSerializer, QuotationClientSerializer,
    QuotationCreateSerializer, QuotationSummarySerializer,
    SectionCreateSerializer, SectionOrganizerSerializer,
    LineItemCreateSerializer, LineItemOrganizerSerializer,
    SubEventSerializer, ProjectTaskSerializer,
    ProjectAssetSerializer, VendorSerializer,
)
from .permissions import IsMICEProjectOrganizer


# ── MICEProject ───────────────────────────────────────────────────────────────

class MICEProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for MICE projects.
    GET  /api/v1/mice/projects/           — list organizer's projects
    POST /api/v1/mice/projects/           — create project
    GET  /api/v1/mice/projects/{id}/      — full detail
    PATCH/PUT /api/v1/mice/projects/{id}/ — update
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MICEProject.objects.filter(
            organizer=self.request.user
        ).select_related('event').prefetch_related(
            'sub_events', 'quotations', 'tasks', 'assets'
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return MICEProjectListSerializer
        elif self.action in ('create', 'update', 'partial_update'):
            return MICEProjectCreateSerializer
        return MICEProjectDetailSerializer

    # ── Custom actions ───────────────────────────────────────────────────────

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        POST /api/v1/mice/projects/{id}/activate/
        Converts approved project into live event with TicketTiers.
        """
        project = self.get_object()
        try:
            project.activate()
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            MICEProjectDetailSerializer(project, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """POST /api/v1/mice/projects/{id}/approve/ — internal approval."""
        project = self.get_object()
        project.approve()
        return Response({'status': 'approved', 'approved_at': project.approved_at})

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """
        GET /api/v1/mice/projects/{id}/dashboard/
        Returns a project summary optimised for the organizer dashboard widget.
        """
        project = self.get_object()
        quotation = project.active_quotation
        tasks = project.tasks.all()
        now = timezone.now()

        return Response({
            'project': MICEProjectListSerializer(project, context={'request': request}).data,
            'financials': QuotationSummarySerializer(quotation).data if quotation else None,
            'task_summary': {
                'total':        tasks.count(),
                'done':         tasks.filter(status='done').count(),
                'in_progress':  tasks.filter(status='in_progress').count(),
                'overdue':      tasks.filter(
                    status__in=['todo', 'in_progress'], due_at__lt=now
                ).count(),
            },
            'sub_events': SubEventSerializer(
                project.sub_events.filter(is_active=True), many=True
            ).data,
        })


# ── SubEvent ──────────────────────────────────────────────────────────────────

class SubEventViewSet(viewsets.ModelViewSet):
    """
    Nested under MICEProject.
    /api/v1/mice/projects/{project_id}/sub-events/
    """
    serializer_class    = SubEventSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        return SubEvent.objects.filter(
            mice_project__organizer=self.request.user,
            mice_project=self.kwargs['project_pk'],
        ).order_by('sort_order')

    def perform_create(self, serializer):
        project = get_object_or_404(
            MICEProject,
            pk=self.kwargs['project_pk'],
            organizer=self.request.user,
        )
        serializer.save(mice_project=project)


# ── Quotation ─────────────────────────────────────────────────────────────────

class QuotationViewSet(viewsets.ModelViewSet):
    """
    Quotation management for a MICE project.
    /api/v1/mice/quotations/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Quotation.objects.filter(
            mice_project__organizer=self.request.user
        ).select_related('mice_project__event').prefetch_related(
            'sections__line_items__vendor'
        )
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(mice_project_id=project_id)
        return qs.order_by('-revision')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return QuotationCreateSerializer
        return QuotationOrganizerSerializer

    def perform_create(self, serializer):
        serializer.save()

    # ── Quotation lifecycle actions ──────────────────────────────────────────

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """
        POST /api/v1/mice/quotations/{id}/recalculate/
        Force a full recalculation of all totals.
        Normally triggered automatically on line item save.
        """
        quotation = self.get_object()
        quotation.recalculate()
        return Response(
            QuotationOrganizerSerializer(quotation, context={'request': request}).data
        )

    @action(detail=True, methods=['post'])
    def send_to_client(self, request, pk=None):
        """
        POST /api/v1/mice/quotations/{id}/send-to-client/
        Marks quotation as sent and returns the client portal URL.
        """
        quotation = self.get_object()
        if quotation.status not in (QuotationStatus.DRAFT, QuotationStatus.SENT):
            return Response(
                {'detail': f'Cannot send a quotation with status "{quotation.status}"'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        quotation.send_to_client()
        return Response({
            'status':           quotation.status,
            'sent_at':          quotation.sent_at,
            'client_portal_url': quotation.client_portal_url,
        })

    @action(detail=True, methods=['post'])
    def create_revision(self, request, pk=None):
        """
        POST /api/v1/mice/quotations/{id}/create-revision/
        Clones quotation into a new revision. Old one is superseded.
        """
        quotation = self.get_object()
        new_quotation = quotation.create_revision()
        return Response(
            QuotationOrganizerSerializer(new_quotation, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def mark_payment_received(self, request, pk=None):
        """
        POST /api/v1/mice/quotations/{id}/mark-payment-received/
        Body: { "term": 1 } or { "term": 2 }
        """
        quotation = self.get_object()
        term = request.data.get('term')
        if term == 1:
            Quotation.objects.filter(pk=quotation.pk).update(payment_term_1_paid=True)
            return Response({'term': 1, 'paid': True})
        elif term == 2:
            Quotation.objects.filter(pk=quotation.pk).update(payment_term_2_paid=True)
            return Response({'term': 2, 'paid': True})
        return Response(
            {'detail': 'term must be 1 or 2'},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ── QuotationSection ──────────────────────────────────────────────────────────

class QuotationSectionViewSet(viewsets.ModelViewSet):
    """
    /api/v1/mice/quotations/{quotation_id}/sections/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuotationSection.objects.filter(
            quotation__mice_project__organizer=self.request.user,
            quotation=self.kwargs.get('quotation_pk'),
        ).prefetch_related('line_items__vendor').order_by('sort_order')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return SectionCreateSerializer
        return SectionOrganizerSerializer

    def perform_create(self, serializer):
        quotation = get_object_or_404(
            Quotation,
            pk=self.kwargs['quotation_pk'],
            mice_project__organizer=self.request.user,
        )
        serializer.save(quotation=quotation)

    @action(detail=False, methods=['post'])
    def bulk_create_from_template(self, request, quotation_pk=None):
        """
        POST /api/v1/mice/quotations/{quotation_pk}/sections/bulk-create-from-template/
        Body: { "template": "mufest_standard" }
        Creates all standard sections in one shot.
        """
        quotation = get_object_or_404(
            Quotation,
            pk=quotation_pk,
            mice_project__organizer=request.user,
        )
        STANDARD_SECTIONS = [
            'Concept Development',
            'Venue & Arrangement',
            'Entertainment',
            'Technical Production',
            'Human Resources',
            'Supporting',
            'Accommodation & Transportation',
        ]
        sections = []
        for i, name in enumerate(STANDARD_SECTIONS):
            if not QuotationSection.objects.filter(quotation=quotation, name=name).exists():
                sections.append(
                    QuotationSection(quotation=quotation, name=name, sort_order=i)
                )
        QuotationSection.objects.bulk_create(sections)
        return Response(
            SectionOrganizerSerializer(
                quotation.sections.all(), many=True
            ).data,
            status=status.HTTP_201_CREATED,
        )


# ── QuotationLineItem ─────────────────────────────────────────────────────────

class QuotationLineItemViewSet(viewsets.ModelViewSet):
    """
    /api/v1/mice/sections/{section_id}/items/
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuotationLineItem.objects.filter(
            section__quotation__mice_project__organizer=self.request.user,
            section=self.kwargs.get('section_pk'),
        ).select_related('vendor').order_by('sort_order')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return LineItemCreateSerializer
        return LineItemOrganizerSerializer

    def perform_create(self, serializer):
        section = get_object_or_404(
            QuotationSection,
            pk=self.kwargs['section_pk'],
            quotation__mice_project__organizer=self.request.user,
        )
        serializer.save(section=section)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, section_pk=None):
        """
        POST /api/v1/mice/sections/{section_pk}/items/bulk-create/
        Body: { "items": [ {...}, {...} ] }
        Create multiple line items at once — useful for pasting from Excel.
        Triggers single recalculate at the end instead of N recalculates.
        """
        section = get_object_or_404(
            QuotationSection,
            pk=section_pk,
            quotation__mice_project__organizer=request.user,
        )
        items_data = request.data.get('items', [])
        if not items_data:
            return Response(
                {'detail': 'No items provided'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = []
        errors  = []

        with transaction.atomic():
            for i, item_data in enumerate(items_data):
                item_data['section'] = str(section.pk)
                serializer = LineItemCreateSerializer(
                    data=item_data, context={'request': request}
                )
                if serializer.is_valid():
                    # Override section to prevent injection
                    obj = QuotationLineItem(
                        section     = section,
                        **{k: v for k, v in serializer.validated_data.items()
                           if k != 'section'}
                    )
                    obj.calculate()
                    created.append(obj)
                else:
                    errors.append({'index': i, 'errors': serializer.errors})

            if errors:
                raise Exception('Validation failed')

            QuotationLineItem.objects.bulk_create(created)

        # Single recalculate after all items inserted
        section.recalculate()

        return Response(
            LineItemOrganizerSerializer(
                section.line_items.all(), many=True
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'])
    def reorder(self, request, section_pk=None):
        """
        POST /api/v1/mice/sections/{section_pk}/items/reorder/
        Body: { "order": ["uuid1", "uuid2", "uuid3"] }
        Updates sort_order for all items in one call.
        """
        section = get_object_or_404(
            QuotationSection,
            pk=section_pk,
            quotation__mice_project__organizer=request.user,
        )
        order = request.data.get('order', [])
        for i, item_id in enumerate(order):
            QuotationLineItem.objects.filter(
                pk=item_id, section=section
            ).update(sort_order=i)
        return Response({'reordered': len(order)})


# ── Client portal (PUBLIC — no auth) ─────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def quotation_client_portal(request, token):
    """
    GET /api/v1/mice/quotation/portal/{token}/
    Public endpoint — no login required.
    Returns client-view of quotation (margins stripped).
    """
    quotation = get_object_or_404(
        Quotation.objects.select_related(
            'mice_project__event'
        ).prefetch_related('sections__line_items'),
        client_token=token,
    )
    if quotation.status == QuotationStatus.DRAFT:
        return Response(
            {'detail': 'This quotation is not yet available for review'},
            status=status.HTTP_403_FORBIDDEN,
        )
    return Response(
        QuotationClientSerializer(quotation, context={'request': request}).data
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def quotation_client_approve(request, token):
    """
    POST /api/v1/mice/quotation/portal/{token}/approve/
    Client approves the quotation — no login required.
    Records approval timestamp and notifies organizer.
    """
    quotation = get_object_or_404(Quotation, client_token=token)

    if quotation.status != QuotationStatus.SENT:
        return Response(
            {'detail': f'Quotation cannot be approved — current status: {quotation.status}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    quotation.approve_by_client()

    return Response({
        'approved':     True,
        'approved_at':  quotation.approved_at,
        'message':      'Terima kasih! Quotation telah disetujui. Tim kami akan segera menghubungi Anda.',
    })


# ── ProjectTask ───────────────────────────────────────────────────────────────

class ProjectTaskViewSet(viewsets.ModelViewSet):
    serializer_class    = ProjectTaskSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        qs = ProjectTask.objects.filter(
            mice_project__organizer=self.request.user
        ).select_related('assigned_to', 'sub_event')
        project_id = self.kwargs.get('project_pk') or self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(mice_project_id=project_id)
        return qs.order_by('sort_order', 'due_at')

    def perform_create(self, serializer):
        project = get_object_or_404(
            MICEProject,
            pk=self.kwargs.get('project_pk') or self.request.data.get('mice_project'),
            organizer=self.request.user,
        )
        serializer.save(mice_project=project)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.complete()
        return Response(self.get_serializer(task).data)


# ── ProjectAsset ──────────────────────────────────────────────────────────────

class ProjectAssetViewSet(viewsets.ModelViewSet):
    serializer_class    = ProjectAssetSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        qs = ProjectAsset.objects.filter(
            mice_project__organizer=self.request.user
        ).select_related('uploaded_by', 'sub_event')
        project_id = self.kwargs.get('project_pk') or self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(mice_project_id=project_id)
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        project = get_object_or_404(
            MICEProject,
            pk=self.kwargs.get('project_pk') or self.request.data.get('mice_project'),
            organizer=self.request.user,
        )
        serializer.save(mice_project=project, uploaded_by=self.request.user)


# ── Vendor ────────────────────────────────────────────────────────────────────

class VendorViewSet(viewsets.ModelViewSet):
    """
    Organizer's vendor address book.
    /api/v1/mice/vendors/
    """
    serializer_class    = VendorSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        qs = Vendor.objects.filter(created_by=self.request.user)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        search = self.request.query_params.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs.order_by('name')
