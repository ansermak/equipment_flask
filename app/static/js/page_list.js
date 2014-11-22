$(document).ready(function() {
    $('#filter').keyup(function() {

        var filter_value = this.value.toLowerCase();
        $('.mytable_row').each(function(){
            if ($(this).text().toLowerCase().indexOf(filter_value) == -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
        return;
/*
        $.ajax ({
            url: '/ajax/filter',
            data: {
		filter_value: this.value, 
                page_name: window.location.href
	    },
            type: 'POST',
            success: function (data) {
                if (!data || !data.rzlt) return;
                $('.mytable_row').each(function() {
                    var id = parseInt(this.id.split('_')[1]);
                    if (data.rzlt.indexOf(id) == -1) {
                        $(this).hide()
                    } else {
                        $(this).show()
                    }
                })
            }
        })
*/
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

})


