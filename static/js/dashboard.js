$(document).ready(() => {
  $('#transaction-options a').click(function () {
    $('#transaction-options a').removeClass('transaction-option-active');
    $(this).addClass('transaction-option-active');
  });
});
