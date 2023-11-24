document.addEventListener('DOMContentLoaded', (event) => {
    const url = '/follow';

    var options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    };

    document.querySelector('a.follow').addEventListener('click', function(e) {
        e.preventDefault();
        var followButton = this;
        console.log(followButton);
        // Добавление данных в тело запроса
        var formData = new FormData();
        formData.append('id', followButton.dataset.id);
        formData.append('action', followButton.dataset.action);
        options['body'] = formData;

        // Отправка HTTP-запроса

        fetch(url, options)
            .then(response => response.json())
            .then(data => {
                if (data['status'] === 'ok') {
                    var previousAction = followButton.dataset.action;
                    // Изменение текста кнопки и значения data-action
                    var action = previousAction === 'follow' ? 'unfollow' : 'follow';
                    console.log('Action1', action)
                    followButton.dataset.action = action;
                    var inputElement = followButton.querySelector('.user-follow');
                    inputElement.value = action;

                    // Обновление количества подписчиков
                    var followerCount = document.querySelector('span.total1');
                    var totalFollowers = parseInt(followerCount.innerHTML);
                    followerCount.innerHTML = previousAction === 'follow' ? totalFollowers + 1 : totalFollowers - 1;
                }
            });
        });

});
