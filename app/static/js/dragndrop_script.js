$(document).ready(function(){

    $('.dragndrop-element').draggable({
        'revert':'invalid'
    });

    
    $('body div:not(.used_stuff)').droppable({
        accept: '.hardware-used, .software-used',
        drop: function(event, ui) {
            if (ui.draggable[0].className.split(' ').indexOf('hardware-used') != -1) {
                $('#menu-hardware-block #free-all').append(ui.draggable.css('left',0).css('top',0))    
                ui.draggable.removeClass('hardware-used').addClass('hardware-base')
            } else if (ui.draggable[0].className.split(' ').indexOf('software-used') != -1) {
                $('#menu-software-block #free-all').append(ui.draggable.css('left',0).css('top',0))    
                ui.draggable.removeClass('software-used').addClass('software-base')
            }
            ui.draggable.addClass('dragged')
            ui.draggable.draggable({ 'revert': 'invalid'});
        }
    });

    $('.used_stuff').droppable({
        accept: '.hardware-base, .software-base',
        drop: function(event, ui) {
            if (ui.draggable[0].className.split(' ').indexOf('hardware-base') != -1) {
                $('.used_stuff .hardware').append(ui.draggable.css('left',0).css('top',0))    
                ui.draggable.removeClass('hardware-base').addClass('hardware-used')
            } else if (ui.draggable[0].className.split(' ').indexOf('software-base') != -1) {
                $('.used_stuff .software').append(ui.draggable.css('left',0).css('top',0))             
                ui.draggable.removeClass('software-base').addClass('software-used')
            }
            ui.draggable.addClass('dragged')
            ui.draggable.draggable({ 'revert': 'invalid'});
        }
    });


    function create_input_fields (fields, status_item) {
        var text = ''
        for (var i = 0; i < fields.length; i ++ ) {
            text += '<input type="hidden" name="electronic_item" value="' 
                + fields[i].id + '"/>'
                + '<input type="hidden" name="status" value="' 
                + status_item + '"/>';
        }
        return text;
    }

    $('.base_form_edit').submit(function() {
        var menu = document.getElementById('menu-hardware-block');
        var hard_free = menu.getElementsByClassName('dragndrop-element dragged');
        var text = create_input_fields(hard_free, 'free'); 

        var menu = document.getElementById('menu-software-block');
        var soft_free = menu.getElementsByClassName('dragndrop-element dragged');
        text += create_input_fields(soft_free, 'free'); 
        
        var used = document.getElementsByClassName('sub_used_stuff software')[0]
        var soft_used = used.getElementsByClassName('dragndrop-element dragged');
        text += create_input_fields(soft_used, 'used'); 

        var used = document.getElementsByClassName('sub_used_stuff hardware')[0]
        var hard_used = used.getElementsByClassName('dragndrop-element dragged');
        text += create_input_fields(hard_used, 'used'); 

        var form = document.forms[0]
        var div = document.createElement('div')
        div.innerHTML = text;
        form.appendChild(div);
        return true;
    });

});
