#ifndef CHROME_BROWSER_UI_WEBUI_AI_CHAT_AI_CHAT_UI_H_
#define CHROME_BROWSER_UI_WEBUI_AI_CHAT_AI_CHAT_UI_H_

#include "content/public/browser/web_ui_controller.h"

class AIChatUI : public content::WebUIController {
 public:
  explicit AIChatUI(content::WebUI* web_ui);
  ~AIChatUI() override = default;

  AIChatUI(const AIChatUI&) = delete;
  AIChatUI& operator=(const AIChatUI&) = delete;
};

#endif  // CHROME_BROWSER_UI_WEBUI_AI_CHAT_AI_CHAT_UI_H_
