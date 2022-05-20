$(document).ready(() => {
  checkbox = $('#external');
  checkbox.change(function () {
    $('#bank').toggleClass('flex hidden');
  });
});
