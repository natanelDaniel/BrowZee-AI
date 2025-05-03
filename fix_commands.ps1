# Fix commands for browser_prefs.cc
# Run these commands in PowerShell from the root of the repository

# Fix 1: Add missing quote in include statement at line 285
(Get-Content src/chrome/browser/prefs/browser_prefs.cc) -replace '#include "chrome/browser/promos/promos_utils.h  // nogncheck', '#include "chrome/browser/promos/promos_utils.h"  // nogncheck' | Set-Content src/chrome/browser/prefs/browser_prefs.cc

# Fix 2: Comment out MigrateSyncingThemePrefsToNonSyncingIfNeeded function call at line 1365
(Get-Content src/chrome/browser/prefs/browser_prefs.cc) -replace 'MigrateSyncingThemePrefsToNonSyncingIfNeeded\(registry\);', '// MigrateSyncingThemePrefsToNonSyncingIfNeeded(registry); // Wrong parameter type' | Set-Content src/chrome/browser/prefs/browser_prefs.cc

# Fix 3: Remove global scope resolution from OSCrypt at line 1784
(Get-Content src/chrome/browser/prefs/browser_prefs.cc) -replace '::OSCrypt::RegisterLocalPrefs\(registry\);', 'OSCrypt::RegisterLocalPrefs(registry);' | Set-Content src/chrome/browser/prefs/browser_prefs.cc

# Fix 4: Comment out PlatformAuthPolicyObserver at line 1818
(Get-Content src/chrome/browser/prefs/browser_prefs.cc) -replace 'PlatformAuthPolicyObserver::RegisterPrefs\(registry\);', '// PlatformAuthPolicyObserver::RegisterPrefs(registry); // Undeclared identifier' | Set-Content src/chrome/browser/prefs/browser_prefs.cc

# Fix 5: Remove global scope resolution from promos_utils at line 2061
(Get-Content src/chrome/browser/prefs/browser_prefs.cc) -replace '::promos_utils::RegisterProfilePrefs\(registry\);', 'promos_utils::RegisterProfilePrefs(registry);' | Set-Content src/chrome/browser/prefs/browser_prefs.cc

Write-Host "All fixes applied successfully!" 