$(document).ready(() => {
  $('#customer-list > a > div').each(function () {
    const rank = $(this).find('#rank')[0].innerText;
    if (rank === 'Silver') {
      $(this).addClass('silver');
    } else if (rank === 'Gold') {
      $(this).addClass('gold');
    }
  });
});
