$(document).ready(() => {
  $('#menu-items li').each(function () {
    anchor = $(this).find('a')[0];
    if (location.href === anchor.href) {
      $(this).addClass('active-menu-item');
      $(this).removeClass('menu-item');
    } else {
      $(this).addClass('menu-item');
      $(this).removeClass('active-menu-item');
    }
  });
});
