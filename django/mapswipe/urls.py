# from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from mapswipe.graphql import CustomAsyncGraphQLView, schema as graphql_schema


urlpatterns = [
    path(
        "graphql/",
        CustomAsyncGraphQLView.as_view(
            schema=graphql_schema,
            graphiql=False,
        ),
    ),
]

# admin.site.site_header = "Mapswipe backend administration"

# Enable graphiql in development server only
if settings.DEBUG:
    urlpatterns.append(
        path("graphiql/", CustomAsyncGraphQLView.as_view(schema=graphql_schema))
    )

    # Static and media file urls
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
