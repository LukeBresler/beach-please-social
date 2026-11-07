# Setup: one-time Meta + GitHub wiring (current Meta flow)

Meta replaced "add the Instagram Graph API product" with **use cases**. This is
the route that actually worked (Nov 2026). Costs R0.

## 1. Meta side
1. Instagram account must be **Business or Creator**.
2. developers.facebook.com -> Create app -> use case **Manage messaging & content on Instagram**.
3. Use cases -> Customize -> **API setup with Unified login** -> **Create new configuration**
   (template: System-user access token, never expires). The template's permission list
   can't be edited.
4. Step 2 on that page ("Generate access tokens"): add the Instagram account, then
   **Generate token**. The page also shows the account's numeric ID (= `IG_USER_ID`).
5. Skip step 3 (webhooks) and step 4 (App Review). Your own account works in Development mode.

The token works on `graph.facebook.com` (not `graph.instagram.com`).

## 2. Test the token before it goes anywhere
Never paste a token into chat, a command line, or a file. Load it silently:

    read -rs TOKEN          # press Enter, paste at the blank prompt, press Enter
    echo ${#TOKEN}          # prints a length, not the token
    curl -s "https://graph.facebook.com/v21.0/<IG_USER_ID>?fields=id,username&access_token=$TOKEN"

Expect your username back. Then copy it to the clipboard without showing it, paste
it into the GitHub secret, and clear everything:

    printf %s "$TOKEN" | pbcopy
    pbcopy < /dev/null; unset TOKEN

## 3. GitHub side
Repo (must be **public**, Meta fetches images from raw.githubusercontent.com):
Settings -> Secrets and variables -> Actions -> New repository secret:

| Secret | Value |
|---|---|
| `IG_USER_ID` | the numeric account ID |
| `IG_ACCESS_TOKEN` | the system-user token |

## 4. Safe first run
Actions -> "Beach, Please! social posts" -> Run workflow. **Dry run is ticked by
default** and posts nothing. Check the log shows real conditions and a sensible
caption. Untick **Dry run** for the first live post, while you're watching.

## Controls
- **Kill switch:** Settings -> Secrets and variables -> Actions -> **Variables** ->
  add `PAUSED` = `true`. Every scheduled run stops. Delete it to resume.
- **Stand-downs:** a slot is skipped (warning on the run, nothing posted) when live
  conditions are missing or older than `MAX_CONDITIONS_AGE_HOURS` (default 3), a
  thunderstorm is forecast, or the caption trips the safety filter in `copy_gen.py`.
- **Missing secrets on Actions is an error**, never a silent dry run.
- **If a token is ever exposed:** revoke it in Business Settings, generate a new one
  (step 4 above), and replace the `IG_ACCESS_TOKEN` secret.
