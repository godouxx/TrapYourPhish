//Simple script to debug the extension

function debugExtension() {
  console.log("Debugging the extension...");
  //We grap all requests made
    chrome.webRequest.onBeforeRequest.addListener(
        function (details) {
        console.log("Request made:", details);
        },
        { urls: ["<all_urls>"] },
        ["blocking"]
    );
}