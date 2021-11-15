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
$('.file_choose .file_input').on('change', function () {
    var file = $(this).prop('files')[0];
    $(this).closest('.file_choose').find('.filename').text(file.name);
   });