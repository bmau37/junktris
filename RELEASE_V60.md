# Junktris V60 — Locked Release

Locked for release: 2026-08-24

## Public release

- Public web root: https://bmau37.github.io/junktris/
- Release build: V60
- Public-facing version/date labels remain hidden from players.
- V60 is generated from the preserved V58 source through guarded V59/V60 builders.
- If a future V60 build fails, GitHub Pages automatically falls back to V59, then preserved V58.
- Service-worker cache was bumped for the V60 public release.

## Preserved rollback baseline

- `v58-junktris-final.html` remains untouched as the permanent known-good source.
- V59 is retained as the immediate rollback release.
- The deployed build also preserves `v60-locked.html` when the V60 audit passes.

## Locked gameplay/release state

- Easy / Medium / Hard difficulty selection is active.
- Hard preserves the original V59 difficulty rules.
- Music begins on the first landing-page interaction when audio permission is available.
- Exactly three curb choices remain visible.
- Line Haul and Tight Pack modes remain available.
- 16 active junk items are retained.
- Dining Table is removed; Coffee Table remains.
- Twin Mattress and Queen Mattress remain.
- Recliner and Dryer have dedicated art.
- Shed remains the rare oversized bonus item.
- Junk Hauler's Guide remains in Settings.
- Current Shed balance and difficulty tuning are accepted for this release and may be adjusted later from player feedback.

## Android / Google Play package

- Application ID: `com.fcjrd.junktris`
- App name: Junktris
- Target SDK: Android 16 / API 36
- Minimum SDK: API 26
- Android build embeds the locked V60 game inside the app for offline play.
- Android app no longer depends on the GitHub Pages game URL at runtime.
- Internet permission is not required for gameplay.
- Debug APK build: PASS
- Release Android App Bundle (`.aab`) build: PASS (unsigned packaging artifact)
- Native Android launcher vector is used to avoid the prior PNG/AAPT2 release-build failure.

## Remaining release gates

1. Create/open the Google Play Console app entry.
2. Create and securely preserve the upload key; enable Play App Signing.
3. Sign the release AAB and upload it to the appropriate Play testing track.
4. Complete the Play Store listing, content rating, Data safety, and required declarations.
5. Add Junktris to the FCJRD WordPress website.
6. Treat future gameplay changes as post-release feedback revisions rather than reopening the V60 launch build.
