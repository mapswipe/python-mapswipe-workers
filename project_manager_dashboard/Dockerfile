FROM nginx:stable
COPY nginx.conf /etc/nginx/conf.d/
COPY api-index.html /usr/share/nginx/html/api/
COPY . /usr/share/nginx/html/project_manager_dashboard/
RUN rm /usr/share/nginx/html/project_manager_dashboard/api-index.html
