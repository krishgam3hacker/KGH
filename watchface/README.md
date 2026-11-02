# KGH Neon Ring: Galaxy Watch 8 watch face

Watch Face Format (WFF v2) face: pure XML, no code. Works on Wear OS 4+ (Galaxy Watch 8 = Wear OS 6).

Layout: seconds tick ring with a live marker, battery arc + charging shimmer, heart-rate arc,
steps ring, big time, date, and three customizable complication slots (long-press the face to pick).

## Get the APK (no Android Studio needed)
1. Push this branch, go to GitHub -> Actions -> "Build watch face APK" -> download `kgh-neon-ring-apk`.
2. Install on the watch over Wi-Fi ADB:
   - Watch: Settings -> About watch -> Software -> tap Software version 5x (Developer mode),
     then Developer options -> ADB debugging + Wireless debugging -> Pair new device.
   - PC: `adb pair <ip:port>` (enter the code), `adb connect <ip:port>`, then
     `adb install app-debug.apk`
3. Long-press the watch face -> pick "KGH Neon Ring". Grant Body sensors / Physical activity when asked.

## Tweaking
Edit `generate.py` (colours, radii, fonts, positions), run `python3 generate.py`, push.
Validate against Google's spec: https://github.com/google/watchface (XSD v2).
Fonts: Space Mono Bold + Space Grotesk Bold (SIL OFL, see FONT-LICENSE-OFL.txt).
