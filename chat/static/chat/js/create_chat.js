let chatRoomUuid = Math.random().toString(36).slice(2, 12)
console.log('uuid', chatRoomUuid)

document.addEventListener('DOMContentLoaded', (event) => {
//    let chatRoomUuid = uuidv4();
    button_message = document.querySelector(".message-button")
    button_message.addEventListener('click', function(e){

        const url = `/chat/create_room/${chatRoomUuid}`;
        var options = {
         method: 'POST',
         headers: {'X-CSRFToken': csrftoken},
         mode: 'same-origin'
        }
        const firstUserPk = document.getElementById('user-pk').dataset.firstUserPk;
        const secondUserPk = document.getElementById('user-pk').dataset.secondUserPk;
        var formData = new FormData();
        console.log('firstUserPkg', firstUserPk);
        console.log('secondUserPkg', secondUserPk);
        formData.append('user1', firstUserPk);
        formData.append('user2', secondUserPk);
        options['body'] = formData;

        fetch(url, options)
        .then(response => response.json())
        .then(data => {
        console.log(data)
    })
});
});
