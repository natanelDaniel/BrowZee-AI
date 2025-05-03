#ifndef CHROME_BROWSER_EXTENSIONS_BROWZEE_ASSISTANT_LOADER_H_
#define CHROME_BROWSER_EXTENSIONS_BROWZEE_ASSISTANT_LOADER_H_

#include "base/functional/callback.h"
#include "chrome/browser/extensions/component_loader.h"

namespace extensions {

// Adds the BrowZee Assistant component extension to the given component loader.
// Returns the extension ID of the added extension.
ExtensionId AddBrowzeeAssistantExtension(ComponentLoader* component_loader);

}  // namespace extensions

#endif  // CHROME_BROWSER_EXTENSIONS_BROWZEE_ASSISTANT_LOADER_H_ 