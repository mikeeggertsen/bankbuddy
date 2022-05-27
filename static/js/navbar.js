$(document).ready(() => {
  $('#menu-items li').each(function () {
    anchor = $(this).find('a')[0];
    const { 1: path } = location.pathname.split('/');
    const { 1: href } = anchor.pathname.split('/');
    if (path === href) {
      $(this).addClass('active');
    } else {
      $(this).removeClass('active');
    }
  });
});
