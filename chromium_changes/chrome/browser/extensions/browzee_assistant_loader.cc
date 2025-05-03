#include "chrome/browser/extensions/browzee_assistant_loader.h"

#include "chrome/browser/extensions/component_loader.h"
#include "chrome/common/extensions/extension_constants.h"
#include "chrome/grit/component_extension_resources.h"
#include "extensions/common/constants.h"

namespace extensions {

ExtensionId AddBrowzeeAssistantExtension(ComponentLoader* component_loader) {
  return component_loader->Add(IDR_BROWZEE_ASSISTANT_MANIFEST,
                               base::FilePath(FILE_PATH_LITERAL("browzee_assistant")));
}

}  // namespace extensions 