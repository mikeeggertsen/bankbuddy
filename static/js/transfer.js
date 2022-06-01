$(document).ready(() => {
  checkbox = $('#external');
  checkbox.change(function () {
    $('#bank').toggleClass('flex hidden');
  });
  checkbox = $('#scheduled');
  checkbox.change(function () {
    $('#scheduled-date').toggleClass('flex hidden');
  });
});
