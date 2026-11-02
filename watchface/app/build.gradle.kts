plugins { id("com.android.application") }

android {
    namespace = "com.krishgam3hacker.neonring"
    compileSdk = 35
    defaultConfig {
        applicationId = "com.krishgam3hacker.neonring"
        minSdk = 33          // Wear OS 4+ (Watch Face Format)
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    buildTypes {
        release {
            // debug-signed so you can sideload it straight away; swap for a real keystore for Play
            signingConfig = signingConfigs.getByName("debug")
        }
    }
}
// No code, no dependencies: a Watch Face Format face is pure XML + resources.
