$(document).ready(function(){
  $('form#pick_ghost_name input[name="first_name"],form#pick_ghost_name input[name="last_name"]').on('keyup',function(){
    var firstName = $('form#pick_ghost_name input[name="first_name"]').val().trim();
    var lastName = $('form#pick_ghost_name input[name="last_name"]').val().trim();

    $('form#pick_ghost_name select[name="ghost_name"] option').each(function(){
      if ($(this).attr('data-ghostname')) {
        var ghostName = $(this).attr('data-ghostname');
        $(this).text(firstName+' “'+ghostName+' ”'+lastName+($(this).attr('data-current')=='1'?' (Current)':''));
      }
    });
  });
});
