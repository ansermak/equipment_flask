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
})
