const dataUrls = Array.from(document.querySelectorAll('[data-url]'))
  .map(element => element.getAttribute('data-url'));

console.log(dataUrls);

// To copy the array to your clipboard:
copy(dataUrls.join('\n'));
console.log('Data URLs copied to clipboard!');