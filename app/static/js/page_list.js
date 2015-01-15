$(document).ready(function() {
   var do_filter = function(filter_value){
     $('.mytable_row').each(function(){
            if ($(this).text().toLowerCase().indexOf(filter_value) == -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });

   }
    
    
    $('#filter').keyup(function() {
        $(this).attr('changed', true);
        do_filter(this.value.toLowerCase());
        return;
    });
    
    // filtering list of user by department for hardwere_edit_page
    
    var prepare_user_list = function(dep_id) {
        $('#user_id option').each(function() {
            if (dep_id == this.getAttribute('data-department-id')){
                $(this).show()
            } else {
                $(this).hide()
            }
        });
        // при зміні департаменту - якщо поточний користувач не 
        // належить до новообраного відділу - змінюємо користувача
        // на першого видимого 
        if ($('#user_id option:selected').attr('data-department-id') != $('#department_id').val()) {
            $('#user_id').val($('#user_id option:visible')[0].value);
        }
    }

    $('#department_id').change(function(){
        prepare_user_list(this.value);
    });

    // обмежуємо користувачів по відділу відразу після завантаження сторінки
    prepare_user_list($('#department_id').val());
    
    $('#filter').focus(function(){
        if(this.value == 'Filter' && ! this.getAttribute('changed')) {
            this.value = '';
        }
    });
    $('#filter').blur(function(){
        if(this.value == '') {
            this.value = 'Filter';
        }
    });
    if ($('#filter').attr('changed')) do_filter($('#filter').val().toLowerCase());
})


