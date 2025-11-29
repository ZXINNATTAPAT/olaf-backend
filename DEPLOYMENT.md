# Railway Deployment Guide

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. Railway CLI (optional, for local deployment)
3. Git repository

## Deployment Steps

### 1. Connect Repository to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect Django project

### 2. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

#### Required Variables:
```
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
```

#### Database (if using Railway PostgreSQL):
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```
Railway automatically provides `DATABASE_URL` if you add PostgreSQL service.

#### CORS Configuration:
```
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,https://another-domain.com
```

#### Cloudinary (if using):
```
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

#### JWT Settings (optional, defaults are fine):
```
SIMPLE_JWT_ACCESS_TOKEN_LIFETIME=3600
SIMPLE_JWT_REFRESH_TOKEN_LIFETIME=604800
```

### 3. Add PostgreSQL Service (if needed)

1. In Railway project, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable

### 4. Build Configuration

Railway will automatically:
- Detect Python project from `requirements.txt`
- Use Python version from `runtime.txt`
- Run migrations from `Procfile`

### 5. Run Migrations

After first deployment, run migrations:

**Option 1: Railway Dashboard**
1. Go to your service
2. Click "Deployments" tab
3. Click on latest deployment
4. Open "Shell" tab
5. Run: `python manage.py migrate`

**Option 2: Railway CLI**
```bash
railway run python manage.py migrate
```

**Option 3: Add to Procfile (automatic)**
```procfile
release: python manage.py migrate
web: gunicorn mysite.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 6. Create Superuser (optional)

```bash
railway run python manage.py createsuperuser
```

Or use Railway dashboard shell.

### 7. Static Files

Static files are handled by WhiteNoise (already configured in `settings.py`).

For production, ensure:
- `STATIC_ROOT` is set correctly
- `STATICFILES_STORAGE` uses WhiteNoise
- Run `python manage.py collectstatic` during build

Add to `Procfile`:
```procfile
release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn mysite.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 8. Custom Domain (optional)

1. In Railway project, go to "Settings"
2. Click "Generate Domain" or "Add Custom Domain"
3. Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` with new domain

## Railway-Specific Settings

### Port Configuration
Railway automatically sets `$PORT` environment variable. The `Procfile` uses this:
```
web: gunicorn mysite.wsgi --bind 0.0.0.0:$PORT
```

### Build Process
Railway uses Nixpacks (or Dockerfile if present) to build:
1. Installs Python from `runtime.txt`
2. Installs dependencies from `requirements.txt`
3. Runs `release` command from `Procfile` (if exists)
4. Starts `web` command from `Procfile`

### Rust Toolchain (for Django-Bolt)
Railway should automatically detect and install Rust for Django-Bolt.
If not, you may need to add a `nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python310", "rustc", "cargo"]

[phases.install]
cmds = ["pip install -r requirements.txt"]
```

## Monitoring

### Logs
View logs in Railway dashboard:
1. Go to your service
2. Click "Deployments" tab
3. Click on deployment
4. View "Logs" tab

### Metrics
Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request count

## Troubleshooting

### Build Fails
- Check `requirements.txt` for correct versions
- Ensure Rust toolchain is available (for Django-Bolt)
- Check Railway logs for specific error

### Application Crashes
- Check environment variables are set correctly
- Verify `DATABASE_URL` is correct
- Check `ALLOWED_HOSTS` includes Railway domain
- Review application logs

### Database Connection Issues
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- Ensure migrations have run

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Verify `STATIC_ROOT` and `STATICFILES_STORAGE` settings
- Check WhiteNoise is in `INSTALLED_APPS` middleware

## Environment Variables Checklist

Before deploying, ensure these are set in Railway:

- [ ] `SECRET_KEY` - Django secret key
- [ ] `DEBUG=False` - Production mode
- [ ] `ALLOWED_HOSTS` - Your Railway domain
- [ ] `DATABASE_URL` - PostgreSQL connection (auto-set if using Railway DB)
- [ ] `CORS_ALLOWED_ORIGINS` - Frontend domains
- [ ] `CLOUDINARY_URL` - If using Cloudinary
- [ ] `CSRF_TRUSTED_ORIGINS` - Your Railway domain

## Quick Deploy Checklist

1. [ ] Code pushed to GitHub
2. [ ] Railway project created
3. [ ] Repository connected
4. [ ] Environment variables set
5. [ ] PostgreSQL service added (if needed)
6. [ ] Migrations run
7. [ ] Static files collected
8. [ ] Domain configured
9. [ ] CORS origins updated
10. [ ] Test API endpoints

## Post-Deployment

After successful deployment:

1. **Test API endpoints:**
   - `GET /api/docs/` - Swagger UI
   - `GET /api/posts` - List posts
   - `POST /api/auth/login` - Login

2. **Update frontend:**
   - Update API base URL to Railway domain
   - Update CORS settings if needed

3. **Monitor:**
   - Check Railway metrics
   - Review logs for errors
   - Test all endpoints

## Support

For Railway-specific issues:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

