#include "extensions/common/file_util.h"

void ComponentExtensionResourceManager::RegisterBrowzee(Profile* profile) {
  base::FilePath path = base::FilePath(FILE_PATH_LITERAL("extensions"))
                            .Append(FILE_PATH_LITERAL("browzee_assistant"));
  extensions::ComponentLoader* loader =
      g_browser_process->component_loader();
  loader->Add(path, "BrowZee Assistant");
}

void ComponentExtensionResourceManager::AddDefaultComponentExtensions(
    Profile* profile) {
  RegisterBrowzee(profile);
} 