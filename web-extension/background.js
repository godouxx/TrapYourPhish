browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveEmails') {
    const emails = request.data;
    console.log('Received emails in background script:', emails);

    const blob = new Blob([JSON.stringify(emails, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    browser.downloads.download({
      url: url,
      filename: 'emails.json',
      saveAs: true
    }).then((downloadId) => {
      console.log('Download started with ID:', downloadId);
      sendResponse({ status: 'success', downloadId: downloadId });
    }).catch((error) => {
      console.error('Download failed:', error);
      sendResponse({ status: 'error', error: error.message });
    });

    return true;  // Indicate that the response will be sent asynchronously
  }
});