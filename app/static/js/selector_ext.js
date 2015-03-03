$(document).ready(function() {

    function ext_select(select) {
    
        // getting list of options
            
        var opt = [].slice.call(select.getElementsByTagName('option'));
        
        // sorting options by value of attrName attribute. Options with equal
        // value in attribute we order by innerHTML

        +function (arr, attrName) {
            arr.sort(function (user1, user2) {
                var rzlt = user1.getAttribute(attrName) > user2.getAttribute(attrName) ?
                    1 : user1.getAttribute(attrName) < user2.getAttribute(attrName) ?
                        -1 : user1.innerHTML > user2.innerHTML ? 1: -1;
                return rzlt;
            });
        }(opt, 'data-department-id');
        
        // creating storage (hidden div) for keeping unused options

        var storage = function() {
            var storage = document.createElement('div');
            storage.style.display = 'none';
            document.body.appendChild(storage);
            for(var i = 0; i < opt.length; i++) {
                storage.appendChild(opt[i]);
            }
            return storage;
        }();

        // add options with specified value of specified attribute to select-element

        select.showByAttr = function (attrName, attrVal) {
            this.clear();
            var i = 0;
            while (i < storage.children.length) {
                if (storage.children[i].getAttribute(attrName) == attrVal) {
                    select.appendChild(storage.children[i]);
                } else {
                    i++;
                }
            }
        };

        // teaking of all options from select-element to our storage

        select.clear = function () {
            while (select.children.length > 0) {
                storage.appendChild(select.children[0])
            }
        };      
    }


   
        // при зміні департаменту - якщо поточний користувач не 
        // належить до новообраного відділу - змінюємо користувача
        // на першого видимого 
        //if ($('#user_id option:selected').attr('data-department-id') != $('#department_id').val()) {
        //    $('#user_id').val($('#user_id option:visible')[0].value);
       // }
    

    $('#department_id').change(function(){
        user_select.showByAttr('data-department-id', this.value);
    });

    // обмежуємо користувачів по відділу відразу після завантаження сторінки
    
    var user_select = document.getElementById('user_id');
    ext_select(user_select);
    user_select.showByAttr('data-department-id', $('#department_id').val());   
})


