#ifndef COMPONENTS_OS_CRYPT_OS_CRYPT_H_
#define COMPONENTS_OS_CRYPT_OS_CRYPT_H_

#include "components/prefs/pref_registry_simple.h"

namespace os_crypt {

class OSCrypt {
 public:
  static void RegisterLocalPrefs(PrefRegistrySimple* registry) {
    // תרשום Pref דמה בשם os_crypt.encrypted_key
    registry->RegisterStringPref("os_crypt.encrypted_key", std::string());
  }
};

}  // namespace os_crypt

namespace OSCrypt {

inline void RegisterLocalPrefs(PrefRegistrySimple* registry) {
  // תרשום Pref דמה בשם os_crypt.encrypted_key
  registry->RegisterStringPref("os_crypt.encrypted_key", std::string());
}

}  // namespace OSCrypt

#endif  // COMPONENTS_OS_CRYPT_OS_CRYPT_H_
