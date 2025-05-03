// Copyright 2024 The BrowZee Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/ui/webui/new_tab_page/browzee_page_handler.h"

#include <string>
#include "base/functional/bind.h"
#include "base/logging.h" // For LOGGING
#include "chrome/browser/profiles/profile.h"
// Include necessary headers for network requests later, e.g.:
// #include "services/network/public/cpp/resource_request.h"
// #include "services/network/public/cpp/simple_url_loader.h"
// #include "services/network/public/mojom/url_response_head.mojom.h"
// #include "net/traffic_annotation/network_traffic_annotation.h"

BrowzeePageHandler::BrowzeePageHandler(
    mojo::PendingReceiver<browzee::mojom::BrowzeePageHandler> receiver,
    Profile* profile)
    : receiver_(this, std::move(receiver)), profile_(profile) {
  DVLOG(1) << "BrowzeePageHandler created";
}

BrowzeePageHandler::~BrowzeePageHandler() {
   DVLOG(1) << "BrowzeePageHandler destroyed";
}

void BrowzeePageHandler::SetPage(
    mojo::PendingRemote<browzee::mojom::BrowzeePage> page) {
  page_.Bind(std::move(page));
   DVLOG(1) << "BrowzeePageHandler::SetPage called";
}

void BrowzeePageHandler::SendMessage(const std::string& task_text) {
  DVLOG(1) << "BrowzeePageHandler::SendMessage received task: " << task_text;

  // TODO: Implement the actual network request logic here.
  // 1. Create a net::NetworkTrafficAnnotationTag.
  // 2. Create a network::ResourceRequest.
  //    - Set URL to "http://localhost:8000/run-task"
  //    - Set Method to "POST"
  //    - Set headers (Content-Type: application/json)
  //    - Set request body (JSON string with task_text and mode)
  // 3. Create a network::SimpleURLLoader.
  // 4. Start the loader using profile_->GetURLLoaderFactory().
  // 5. Set a callback for when the request completes (e.g., OnServerResponse).

  // Placeholder: Send a simple response back immediately for testing.
  if (page_) {
    page_->OnAgentResponse("C++ received: " + task_text + ". Network request not implemented yet.");
  } else {
     LOG(ERROR) << "Cannot send response, page_ remote is not bound.";
  }
}

// TODO: Add callback function for SimpleURLLoader, e.g.:
// void BrowzeePageHandler::OnServerResponse(std::unique_ptr<std::string> response_body) {
//   int response_code = -1;
//   if (url_loader_->ResponseInfo() && url_loader_->ResponseInfo()->headers) {
//     response_code = url_loader_->ResponseInfo()->headers->response_code();
//   }
//   if (response_code == 200 && response_body) {
//     // Process response if needed, maybe expect JSON?
//     // For now, just forward the raw body or a success message.
//     if (page_) {
//       page_->OnAgentResponse(*response_body); // Or a parsed/formatted message
//     }
//   } else {
//     LOG(ERROR) << "Server request failed with code: " << response_code;
//     if (page_) {
//        page_->OnAgentResponse("Error communicating with server.");
//     }
//   }
//   url_loader_.reset(); // Reset loader after completion/error
// }
