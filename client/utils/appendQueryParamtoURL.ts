export const appendQueryParamtoURL = (newQueryParam: string) => {
    let currentUrl = window.location.href;

    if (currentUrl.indexOf('?') !== -1) {
        // If there are, remove the old parameter (if it exists) and append the new one
        const urlWithoutParams = currentUrl.split('?')[0];
        currentUrl = urlWithoutParams + '?' + newQueryParam;
    } else {
        // If not, simply append the new parameter with a "?"
        currentUrl += '?' + newQueryParam;
    }

    // Update the URL without refreshing the page
    window.history.pushState({ path: currentUrl }, '', currentUrl);
}