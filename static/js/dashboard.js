$(document).ready(() => {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const q = urlSearchParams.get('q');
  if (q === 'credit') {
    $('#credit-transactions').addClass('active');
  } else if (q === 'debit') {
    $('#debit-transactions').addClass('active');
  } else {
    $('#all-transactions').addClass('active');
  }
});
