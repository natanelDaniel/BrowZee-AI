// קביעת התנהגות הפאנל - פתיחת הפאנל בלחיצה על האייקון
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

// בעת לחיצה על האייקון, הקוד הישן להפעלת חלון יימחק
chrome.action.onClicked.addListener(async (tab) => {
  // ניסיון להשתמש ב-API של גרסה 116+ אם זמיןl
  if (chrome.sidePanel.open) {
    try {
      await chrome.sidePanel.open({ tabId: tab.id });
    } catch (error) {
      console.error('Error opening side panel:', error);
      // פתיחת חלון פופאפ כגיבוי אם ה-API לא זמין
      chrome.windows.create({
        url: 'index.html',
        type: 'popup',
        width: 400,
        height: 600
      });
    }
  } else {
    // אם ה-API לא זמין בגרסה זו, נגדיר את האפשרויות ונסמוך על כך שהמשתמש ילחץ על הפאנל
    await chrome.sidePanel.setOptions({
      tabId: tab.id,
      path: 'index.html',
      enabled: true
    });
  }
}); 