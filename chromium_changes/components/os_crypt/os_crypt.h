#ifndef COMPONENTS_OS_CRYPT_OS_CRYPT_H_
#define COMPONENTS_OS_CRYPT_OS_CRYPT_H_

#include "components/prefs/pref_registry_simple.h"

namespace os_crypt {

class OSCrypt {
 public:
  static void RegisterLocalPrefs(PrefRegistrySimple* registry) {
    registry->RegisterStringPref("os_crypt.encrypted_key", std::string());
    registry->RegisterBooleanPref("os_crypt.audit.enabled", false);
  }
};

}  // namespace os_crypt

namespace OSCrypt {

inline void RegisterLocalPrefs(PrefRegistrySimple* registry) {
  os_crypt::OSCrypt::RegisterLocalPrefs(registry);
}

}  // namespace OSCrypt

#endif  // COMPONENTS_OS_CRYPT_OS_CRYPT_H_
