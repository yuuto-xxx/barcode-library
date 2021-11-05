$(function() {
    $('.hamburger').click(function() {
        $(this).toggleClass('active');
 
        if ($(this).hasClass('active')) {
            $('.globalMenuSp').addClass('active');
            $('.main_board').addClass('active');
        } else {
            $('.globalMenuSp').removeClass('active');
            $('.main_board').removeClass('active');
        }
        
        
    });
});