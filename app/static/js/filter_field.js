$(document).ready(function() {

    // filter field
    if (document.getElementById('filter')) {
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
        }).focus(function(){
            if(this.value == 'Filter' && ! this.getAttribute('changed')) {
                this.value = '';
            }
        }).blur(function(){
            if(this.value == '') {
                this.value = 'Filter';
            }
        });
        
        if ($('#filter').attr('changed')) do_filter($('#filter').val().toLowerCase());    
    }
    
});