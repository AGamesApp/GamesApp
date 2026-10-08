Google & Firebase: Add games.agames.cv as an authorized domain

This document explains exactly what to add in Google Cloud Console (OAuth client) and in Firebase so social sign-in and OAuth redirects work correctly for https://games.agames.cv.

Quick checklist

- [ ] Add https://games.agames.cv to "Authorized JavaScript origins" (if using frontend JS OAuth flows).
- [ ] Add the redirect URI(s) used by your app to "Authorized redirect URIs" in the OAuth 2.0 client.
- [ ] In Firebase Console → Authentication → Sign-in method → Authorized domains, add games.agames.cv.

Recommended Redirect URIs

Depending on how your Django app handles Google sign-in (Django Allauth, custom endpoint, or a mobile backend), add one or more of the following redirect URIs in the Google Cloud OAuth client configuration:

- https://games.agames.cv/accounts/google/login/callback/
  - This is the common callback used by django-allauth and many Django social auth setups.
- https://games.agames.cv/api/auth/google/callback/
  - Add this if you have an API endpoint that handles the OAuth callback.
- If your frontend uses an OAuth popup flow, add the origin:
  - Authorized JavaScript origin: https://games.agames.cv

Google Cloud Console: step-by-step

1. Open Google Cloud Console: https://console.cloud.google.com
2. Select the project that holds your OAuth client / credentials.
3. Go to APIs & Services → Credentials.
4. Find your OAuth 2.0 Client IDs entry (type "Web application"). Click the name to edit.
5. Under "Authorized JavaScript origins" add:
   - https://games.agames.cv
6. Under "Authorized redirect URIs" add at least the callback URI your app uses, for example:
   - https://games.agames.cv/accounts/google/login/callback/
   - https://games.agames.cv/api/auth/google/callback/
7. Save.

Notes on OAuth redirect URIs

- Redirect URIs must exactly match what the app sends in the authorization request (scheme, host, path, trailing slash). If you registered a URI with a trailing slash but the request uses no trailing slash (or vice versa), Google will reject the callback.
- If you use multiple environments (staging, production), create separate OAuth clients per environment and register the exact URLs.

Firebase Console: step-by-step

1. Open Firebase Console: https://console.firebase.google.com
2. Choose your project.
3. Go to Authentication → Sign-in method.
4. Scroll to the "Authorized domains" section (bottom of the page) and click "Add domain".
5. Add: games.agames.cv and click "Add".

Additional Firebase notes

- If you use Firebase Hosting or Firebase Auth widget, having games.agames.cv in this list is required for hosted sign-in or redirect flows to work.
- If you use OAuth providers via Firebase (instead of direct Google OAuth), ensure the OAuth project (in the Google Cloud Console) is the same project that Firebase uses, or configure provider credentials in Firebase accordingly.

Testing after you update

1. From a browser, visit: https://games.agames.cv/accounts/google/login/ (or whichever URL starts the Google login flow in your app).
2. Confirm the Google consent screen appears and after consenting you are redirected back to your site without error.
3. For API-based flows, perform the full OAuth flow and confirm the backend receives the authorization code and exchanges it successfully for tokens.

Troubleshooting

- "redirect_uri_mismatch": confirm the exact redirect URI registered in Google Console matches the one used by the app.
- CORS / blocked origin errors: ensure https://games.agames.cv is in "Authorized JavaScript origins" if the frontend uses direct browser-based flows.
- If you get sign-in errors in Firebase, check both Firebase's "Authorized domains" and the OAuth client configuration in Google Cloud Console.

If you'd like, I can:
- Inspect your Django Allauth / OAuth configuration and list the exact redirect URIs your app currently uses.
- Prepare the exact list of URIs to paste into Google Cloud and Firebase (I just need to know which social login endpoints you use).

