$(document).ready(() => {
  setActiveTransactionTab();
  setActiveLinechartTab();
});

function setActiveTransactionTab() {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const q = urlSearchParams.get('q');
  if (q === 'credit') {
    $('#credit-transactions').addClass('active');
  } else if (q === 'debit') {
    $('#debit-transactions').addClass('active');
  } else {
    $('#all-transactions').addClass('active');
  }
}

function setActiveLinechartTab() {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const q = urlSearchParams.get('q');
  if (q === 'monthly') {
    $('#chart-monthly').addClass('active');
  } else if (q === 'yearly') {
    $('#chart-yearly').addClass('active');
  } else {
    $('#chart-weekly').addClass('active');
  }
}
