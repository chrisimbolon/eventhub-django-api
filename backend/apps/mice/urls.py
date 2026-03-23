# =============================================================================
# apps/mice/urls.py
# =============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from .views import (
    MICEProjectViewSet,
    SubEventViewSet,
    QuotationViewSet,
    QuotationSectionViewSet,
    QuotationLineItemViewSet,
    ProjectTaskViewSet,
    ProjectAssetViewSet,
    VendorViewSet,
    quotation_client_portal,
    quotation_client_approve,
)

# ── Root router ───────────────────────────────────────────────────────────────
router = DefaultRouter()
router.register(r'projects',    MICEProjectViewSet, basename='mice-project')
router.register(r'quotations',  QuotationViewSet,   basename='mice-quotation')
router.register(r'vendors',     VendorViewSet,      basename='mice-vendor')
router.register(r'tasks',       ProjectTaskViewSet, basename='mice-task')
router.register(r'assets',      ProjectAssetViewSet,basename='mice-asset')

# ── Nested: projects → sub-events ────────────────────────────────────────────
projects_router = nested_routers.NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'sub-events', SubEventViewSet, basename='project-sub-events')
projects_router.register(r'tasks',      ProjectTaskViewSet, basename='project-tasks')
projects_router.register(r'assets',     ProjectAssetViewSet, basename='project-assets')

# ── Nested: quotations → sections ────────────────────────────────────────────
quotations_router = nested_routers.NestedDefaultRouter(router, r'quotations', lookup='quotation')
quotations_router.register(r'sections', QuotationSectionViewSet, basename='quotation-sections')

# ── Nested: sections → line items ────────────────────────────────────────────
sections_router = nested_routers.NestedDefaultRouter(
    quotations_router, r'sections', lookup='section'
)
sections_router.register(r'items', QuotationLineItemViewSet, basename='section-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(quotations_router.urls)),
    path('', include(sections_router.urls)),

    # Public client portal — no auth required
    path(
        'quotation/portal/<str:token>/',
        quotation_client_portal,
        name='quotation-portal',
    ),
    path(
        'quotation/portal/<str:token>/approve/',
        quotation_client_approve,
        name='quotation-portal-approve',
    ),
]
