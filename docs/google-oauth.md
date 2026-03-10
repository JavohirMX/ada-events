# Google OAuth Authentication

This document provides detailed instructions on how to set up, configure, and maintain Google OAuth authentication for the ADA Bali Events platform.

## Overview

The application uses `django-allauth` to handle social authentication. We specifically use the Settings-based provider configuration rather than the database-backed `SocialApp` models. This allows configuration to be purely driven by environment variables, making it easier to deploy consistently across environments.

### Workflow

1. A user clicks "Continue with Google" on the Login or Sign Up page.
2. They are redirected to Google to grant permission.
3. Upon returning, `django-allauth` captures their email and profile information.
4. **Auto-linking:** If an existing account has the same email address, the Google social account is automatically linked to that existing user.
5. If the user does not exist, a new `User` is created seamlessly without a password.
6. The user is redirected to the platform's home page.

---

## 1. Setting Up Google Cloud Console

To allow users to log in with Google, you must register the application in the Google Cloud Console and generate OAuth credentials.

### Step 1: Create a Project
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown in the top navigation bar and select **"New Project"**.
3. Name your project (e.g., `ADA Bali Events Auth`) and click **"Create"**.
4. Once created, make sure your new project is selected in the top navigation bar.

### Step 2: Configure the OAuth Consent Screen
The consent screen is what users will see when they click "Continue with Google".

1. In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
2. Select **User Type**:
   - **Internal:** ONLY users within your Google Workspace organization can access it.
   - **External:** Any user with a Google account can access it (Choose this for public access).
3. Click **Create**.
4. Fill out the **App information**:
   - **App name:** ADA Bali Events
   - **User support email:** Your email
   - **App logo:** (Optional) Upload the app logo
5. Fill out the **Developer contact information**:
   - **Email addresses:** Your email
6. Click **Save and Continue**.
7. Under **Scopes**, you do not need to add any sensitive scopes. The default `email`, `profile`, and `openid` scopes are sufficient. Click **Save and Continue**.
8. (If External) Under **Test users**, optionally add email addresses of users who can test the app while in "Testing" mode. Or you can publish the app immediately at the end.
9. Click **Save and Continue**, then review your summary.

### Step 3: Create OAuth Credentials
Now you will generate the Client ID and Secret needed by `django-allauth`.

1. In the left sidebar, navigate to **APIs & Services** > **Credentials**.
2. Click the **"+ CREATE CREDENTIALS"** button at the top and select **OAuth client ID**.
3. From the **Application type** dropdown, select **Web application**.
4. **Name:** Give it a recognizable name (e.g., `Django Allauth Web Client`).
5. **Authorized JavaScript origins**:
   - For local development: `http://localhost:8000` and/or `http://127.0.0.1:8000`
   - For production: `https://your-production-domain.com`
6. **Authorized redirect URIs** (Crucial!):
   - For local development: `http://localhost:8000/accounts/google/login/callback/`
   - For production: `https://your-production-domain.com/accounts/google/login/callback/`
   *(Ensure there is a trailing slash `/` on the callback URL)*
7. Click **Create**.
8. A modal will pop up displaying your **Client ID** and **Client Secret**. Keep these secure.

---

## 2. Setting Environment Variables

Take the Client ID and Secret obtained from Google and add them to your environment variables.

### Local Development
In your `.env` file at the root of the project, add the following lines:

```dotenv
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=your-client-secret-here
```

### Production Deployment
If you are deploying using Docker Compose, Railway, Heroku, or another provider, ensure that these two variables (`GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_SECRET`) are securely defined in your environment settings.

---

## 3. Application Configuration Details

For developers modifying the code, here is an explanation of how the implementation is set up within the application.

### Settings (`ada_events/settings.py`)

- **`INSTALLED_APPS`**: Includes `allauth.socialaccount.providers.google` which tells `django-allauth` to load the Google provider.
- **`SOCIALACCOUNT_PROVIDERS`**: Configured to read directly from the `.env` variables mapped above. This approach bypasses the need for the `SocialApp` database table.
- **`SOCIALACCOUNT_EMAIL_AUTHENTICATION = True`**: Allows allauth to authenticate users by verified social email so existing users are signed in directly instead of being sent to the intermediate third-party signup page.
- **`SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True`**: Automatically maps a Google sign-in to an existing account if the emails match.
- **Redirects**: `LOGIN_REDIRECT_URL = "home"` ensures users land on the events dashboard once authed.

### Templates (`templates/account/login.html` & `signup.html`)

The standard authentication templates have been modified using the `{% provider_login_url 'google' %}` tag to initiate the OAuth flow.

```html
{% load socialaccount %}

<a href="{% provider_login_url 'google' %}">
  Continue with Google
</a>
```

### Dependencies
The `django-allauth[socialaccount]` extra is required, bringing in essential external networking packages like `requests` and `PyJWT` to handle token swapping safely via python.

---

## Troubleshooting

### "Redirect URI mismatch" Error from Google
Google is stringent about redirect URIs. 
- Ensure the URI listed in the Google Console matches **exactly** what the Django app generated. 
- If you are running on `127.0.0.1:8000` but registered `localhost:8000`, Google will reject the request. Make sure both are covered or access the browser through `localhost`.
- Check for trailing slashes. Allauth callbacks require them (`/accounts/google/login/callback/`).

### Appears as insecure or "Unverified"
If your app is in "Testing" mode in the Google Console, users not in the **Test users** list will get a security warning. To remove this, you must switch the app to **In production** from the OAuth Consent screen.

### Connection Refused / Provider Errors Local
Ensure that you restarted your local docker environment/uv environment after adding the `.env` variables. Changes to `.env` require a full restart of the Django server to load the new settings.