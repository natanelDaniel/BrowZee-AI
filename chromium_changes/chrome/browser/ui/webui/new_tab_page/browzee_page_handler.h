// Copyright 2024 The BrowZee Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_BROWZEE_PAGE_HANDLER_H_
#define CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_BROWZEE_PAGE_HANDLER_H_

#include "base/memory/raw_ptr.h"
#include "base/memory/weak_ptr.h"
#include "chrome/browser/ui/webui/new_tab_page/browzee.mojom.h"
#include "mojo/public/cpp/bindings/pending_receiver.h"
#include "mojo/public/cpp/bindings/pending_remote.h"
#include "mojo/public/cpp/bindings/receiver.h"
#include "mojo/public/cpp/bindings/remote.h"

class Profile;

// Handles communication between the Browzee NTP UI (JS) and the browser process (C++).
// It receives messages from JS via Mojo, performs actions (like contacting the
// FastAPI server), and sends results back to the JS page via the Page remote.
class BrowzeePageHandler : public browzee::mojom::BrowzeePageHandler {
 public:
  BrowzeePageHandler(
      mojo::PendingReceiver<browzee::mojom::BrowzeePageHandler> receiver,
      Profile* profile);

  BrowzeePageHandler(const BrowzeePageHandler&) = delete;
  BrowzeePageHandler& operator=(const BrowzeePageHandler&) = delete;

  ~BrowzeePageHandler() override;

  // browzee::mojom::BrowzeePageHandler:
  void SetPage(mojo::PendingRemote<browzee::mojom::BrowzeePage> page) override;
  void SendMessage(const std::string& task_text) override;

 private:
  mojo::Receiver<browzee::mojom::BrowzeePageHandler> receiver_;
  mojo::Remote<browzee::mojom::BrowzeePage> page_;
  raw_ptr<Profile> profile_; // Used for network requests, etc.

  // Used for network requests to the FastAPI server
  // std::unique_ptr<network::SimpleURLLoader> url_loader_;

  base::WeakPtrFactory<BrowzeePageHandler> weak_ptr_factory_{this};
};

#endif // CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_BROWZEE_PAGE_HANDLER_H_
