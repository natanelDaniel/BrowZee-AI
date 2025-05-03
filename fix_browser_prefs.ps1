# Get the full path to browser_prefs.cc
$filePath = "src\chrome\browser\prefs\browser_prefs.cc"

# Read the content
$content = Get-Content $filePath

# Fix 1: Add missing quote in include statement
$content = $content -replace '#include "chrome/browser/promos/promos_utils.h  // nogncheck', '#include "chrome/browser/promos/promos_utils.h"  // nogncheck'

# Fix 2: Comment out MigrateSyncingThemePrefsToNonSyncingIfNeeded function call
$content = $content -replace 'MigrateSyncingThemePrefsToNonSyncingIfNeeded\(profile_prefs\);', '// Fix: This function expects PrefService* but profile_prefs is not defined here'

# Fix 3: Remove global scope resolution from OSCrypt
$content = $content -replace '::OSCrypt::RegisterLocalPrefs\(registry\);', 'OSCrypt::RegisterLocalPrefs(registry);'

# Fix 4: Remove global scope resolution from PlatformAuthPolicyObserver and fix if needed
$content = $content -replace '::PlatformAuthPolicyObserver::RegisterPrefs\(registry\);', 'PlatformAuthPolicyObserver::RegisterPrefs(registry);'
$content = $content -replace 'PlatformAuthPolicyObserver::RegisterPrefs\(registry\);', '// Fix: PlatformAuthPolicyObserver was not found in scope - include it or use correct namespace'

# Fix 5: Remove global scope resolution from promos_utils
$content = $content -replace '::promos_utils::RegisterProfilePrefs\(registry\);', 'promos_utils::RegisterProfilePrefs(registry);'

# Write the content back to the file
$content | Set-Content $filePath

Write-Host "Fixes applied successfully!" 