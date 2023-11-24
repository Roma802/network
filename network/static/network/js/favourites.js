document.addEventListener('DOMContentLoaded', (event) => {
    const url = '/bookmarks';

    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    };

    document.querySelectorAll('.favourite-class').forEach(function(favouriteButton){
    favouriteButton.addEventListener('click', function(e) {
        e.preventDefault();
        console.log(favouriteButton);
        // Добавление данных в тело запроса
        var formData = new FormData();
        formData.append('id', favouriteButton.dataset.id);
        formData.append('action', favouriteButton.dataset.action);
        options['body'] = formData;

        // Отправка HTTP-запроса

        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 'ok') {
                    var previousAction = favouriteButton.dataset.action;
                    // Изменение текста кнопки и значения data-action
                    var action = previousAction === 'add' ? 'delete' : 'add';
                    console.log('previousAction', previousAction)
                    console.log('Action', action)
                    favouriteButton.dataset.action = action;
                    var inputElement = favouriteButton.querySelector('.add-to-bookmarks-btn');
                    console.log('inputElement', inputElement)
//                    if (previousAction == 'delete') {
//                        var postWrapper = document.querySelector('.post-wrapper');
//                        postWrapper.style.display = 'none';
//                    }
                    inputElement.innerText = action === 'add' ? 'add to bookmarks' : 'remove from bookmarks';
                }
            });
        });
    });
});