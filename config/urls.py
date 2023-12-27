from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls.static import static
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Book list Api",
        default_version='v1',
        description="Library demo project",
        terms_of_service="demo.com",
        contact=openapi.Contact(email="farhodjonhikmatullayev@gmail.com"),
        license=openapi.License(name="Demo License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('users/', include('apps.users.urls', namespace='users')),
    path('todo/', include('apps.todo.urls', namespace='todo')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
