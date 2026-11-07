# Privacy Policy — Beach, Please App

**Last updated:** 20 September 2026

This policy covers the **Beach, Please App** Meta Developer App (used for
Instagram integration) and the **"Beach, please!"** iOS app (Cape Town
Beach & Tidal Pool Finder) it belongs to, both operated by the same
developer, Luke Bresler ("we," "us"). It explains what data the app
collects, what it doesn't, and how the Meta/Instagram integration works.

If anything below conflicts with a statement on realpixel.co.za, this
document is the current, accurate one — see the note at the end about
updating that page.

---

## 1. Summary

- We do not require or offer account creation or sign-in.
- We do not use analytics, advertising, or crash-reporting SDKs of any
  kind.
- The only location data used is a coarse, on-device estimate, used only
  to find nearby beaches — it is **never sent to our servers or anyone
  else's**.
- The Meta Developer App is used **only** so that we, the developer, can
  automatically publish scheduled posts to our own Instagram Business
  account. It does not collect data from Instagram or Facebook users, and
  there is no "Log in with Facebook/Instagram" feature in the app.

## 2. Information We Collect

### Location
With your permission, the app uses CoreLocation to request a single,
coarse (city-block-level, not precise-GPS-level) location fix, only while
the app is in use (not in the background). This is used to sort beaches
and tidal pools by distance from you.

That location is cached **only on your device**, in a shared App Group
container used to pass it to the home-screen widget (so the widget
doesn't have to request its own GPS fix). It is never transmitted to our
servers, to Supabase, or to any third party. You can revoke location
access at any time in iOS Settings → Privacy & Security → Location
Services; the app falls back to a score-only ranking (no distance sorting)
if you do.

### App usage signals (for the App Store review prompt)
The app records, locally on your device only (`UserDefaults`, never
transmitted), the date you first opened it and the date of your first
"positive interaction" (such as opening a beach in Maps). This is used
solely to decide, on-device, when it's reasonable to show Apple's native
App Store review prompt (`SKStoreReviewController`). No data leaves your
device for this feature, and we never see whether or how you rated the
app.

### What we do **not** collect
We do not collect your name, email, contacts, photos, precise/background
location, advertising identifiers, or any other personal data. There is
no user account system, so we have no database of users at all.

## 3. Live Conditions Data (Supabase)

The app displays live wind, tide, and water-temperature conditions for
Cape Town's beaches. These are fetched **read-only** from a shared
Supabase database using a public, read-only API key. This request:

- sends no personal or device-identifying data — it is a generic "give me
  the latest conditions" request, identical for every user;
- returns publicly shared weather/tide data, not anything about you.

The underlying weather, tide, and sea-temperature figures are themselves
sourced from third-party providers (Open-Meteo, TideCheck, StormGlass),
fetched on a fixed schedule by our own backend — never triggered by, or
containing data about, an individual user or device.

## 4. The Meta Developer App ("Beach, Please App") and Instagram

Separately from the consumer-facing iOS app, we operate a Meta Developer
App named **Beach, Please App**. Its only purpose is to let our own
automated backend publish scheduled Instagram posts (beach/tidal-pool
highlights and Cape Town facts) to our own Instagram **Business** account,
using the Instagram Graph API's content-publishing endpoints.

Specifically:

- This is a **first-party, server-to-server integration** — it posts on
  our own behalf, to our own account.
- It does **not** implement Facebook Login or Instagram Login for other
  people, and no member of the public authenticates through it.
- It does not collect, access, read, or store data belonging to any other
  Instagram or Facebook user, page, or account.
- It does not use Instagram/Facebook data to build profiles, run ads, or
  for any purpose beyond publishing our own scheduled content.
- The only credentials involved are a long-lived access token authorizing
  posts to our own Instagram Business account, held securely as an
  encrypted secret in our automation pipeline (GitHub Actions), not
  accessible to end users of the app.

## 5. Third Parties and SDKs

The iOS app has exactly one third-party dependency: the official Supabase
Swift SDK, used only as described in Section 3. We do not include any
advertising network, analytics SDK, or crash-reporting SDK in the app.

## 6. Data Retention

Because we don't collect personal data or operate user accounts, there is
nothing to retain, export, or delete on our end. The only stored values —
your cached coarse location and your local review-prompt timestamps — live
solely on your device and are removed automatically if you delete the
app.

## 7. Children's Privacy

The app is a general-audience recreational tool (beach/tide conditions)
and is not directed at children. It does not knowingly collect any
personal information from anyone, of any age, since it does not collect
personal information at all.

## 8. Changes to This Policy

If our data practices change — for example, if we add a feature that
collects new data — we will update this page and the "Last updated" date
above. Material changes will also be reflected in the app's release notes.

## 9. Contact

Questions about this policy, the app, or the Meta/Instagram integration
can be sent to:

**Luke Bresler**
📧 luke@realpixel.co.za
🌐 realpixel.co.za

---

*Note: the "Beach, please!" iOS app already links to a Privacy Policy at
`realpixel.co.za/Privacy Policy for Beach, please!.html`. A matching
standalone HTML version of this document (`privacy-policy.html`) is
included alongside this file — upload it to that same URL so the in-app
link and the Meta App Dashboard's Privacy Policy URL point to the same,
current text.*
