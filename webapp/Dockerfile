FROM nginx:alpine

# Copy the frontend files to the nginx html directory
COPY frontend /usr/share/nginx/html

# Copy a custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]