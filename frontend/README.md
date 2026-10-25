# Frontend — Django Templates (Server-Side Rendered)

This project's frontend is built with **Django Templates**, **Bootstrap 5.3.3**, and custom **CSS/JS** files. It is **not** a standalone single-page application (SPA).

## Architecture

The frontend consists of:

- **Django HTML Templates** (`backend/templates/`) — Server-side rendered using Django's template engine
- **Static Assets** (`backend/static/`) — CSS, JavaScript, and images served by Django + Whitenoise

These files are tightly coupled to Django and are served directly by the backend. They use Django template tags such as:

- `{% load static %}` — Static file URLs
- `{% url 'view_name' %}` — URL resolution
- `{% csrf_token %}` — CSRF protection
- `{% block content %}` / `{% extends 'base.html' %}` — Template inheritance
- `{{ form.as_p }}` — Form rendering
- `{% if request.user.is_authenticated %}` — Auth context

## Why No Vercel Deployment?

Vercel is designed for static sites and JavaScript frameworks (React, Next.js, Vue, etc.).  
Django templates require Django's server-side rendering engine and cannot run on Vercel.

The entire application (backend + templates + static files) is deployed as a single unit on **Render**.

## To Convert to a Vercel-Deployable Frontend

If you want to deploy a frontend separately on Vercel in the future, you would need to:

1. Create a REST API (Django REST Framework) in the backend
2. Rewrite all ~160 Django templates as a React/Vue/Next.js frontend
3. Replace `{% url %}` tags with API calls
4. Replace `{% csrf_token %}` with token-based authentication (JWT)
5. Replace `{% static %}` with local imports or a CDN

This is a significant rewrite and should be planned carefully.
