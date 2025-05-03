#include "chrome/browser/ui/webui/ai_chat/ai_chat_ui.h"

#include "chrome/browser/resources/ai_chat/grit/ai_chat_resources.h"
#include "chrome/common/webui_url_constants.h"
#include "content/public/browser/browser_context.h"
#include "content/public/browser/web_contents.h"
#include "content/public/browser/web_ui.h"
#include "content/public/browser/web_ui_data_source.h"
#include "services/network/public/mojom/content_security_policy.mojom.h"

AIChatUI::AIChatUI(content::WebUI* web_ui) : WebUIController(web_ui) {
  content::WebUIDataSource* source = content::WebUIDataSource::CreateAndAdd(
      web_ui->GetWebContents()->GetBrowserContext(),
      chrome::kChromeUIAIChatHost);

  source->SetDefaultResource(IDR_AI_CHAT_HTML);

  source->OverrideContentSecurityPolicy(
      network::mojom::CSPDirectiveName::ConnectSrc,
      "connect-src 'self' http://localhost:8000 ws://localhost:8000;");
  source->OverrideContentSecurityPolicy(
      network::mojom::CSPDirectiveName::FrameSrc, "frame-src * data: blob:;");
}
