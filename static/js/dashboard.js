$(document).ready(() => {
  $('.transaction-option-active').removeClass('transaction-option-active');
  const urlSearchParams = new URLSearchParams(window.location.search);
  const q = urlSearchParams.get('q');
  if (q === 'credit') {
    $('#credit-transactions').addClass('transaction-option-active');
  } else if (q === 'debit') {
    $('#debit-transactions').addClass('transaction-option-active');
  } else {
    $('#all-transactions').addClass('transaction-option-active');
  }
});
