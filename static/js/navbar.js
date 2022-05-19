$(document).ready(() => {
  $('#menu-items li').each(function () {
    anchor = $(this).find('a')[0];
    const { 1: path } = location.pathname.split('/');
    const { 1: href } = anchor.pathname.split('/');
    if (path === href) {
      $(this).addClass('active-menu-item');
      $(this).removeClass('menu-item');
    } else {
      $(this).addClass('menu-item');
      $(this).removeClass('active-menu-item');
    }
  });
});
