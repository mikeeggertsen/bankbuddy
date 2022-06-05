$(document).ready(() => {
  checkbox = $('#external');
  checkbox.change(function () {
    $('#bank').toggleClass('flex hidden');
    $('#scheduled-toggle-holder').toggleClass('hidden');
  });
  checkbox = $('#scheduled');
  checkbox.change(function () {
    $('#scheduled-date').toggleClass('flex hidden');
  });
});
