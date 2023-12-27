const csrftoken = Cookies.get('csrftoken');
document.addEventListener('DOMContentLoaded', (event) => {
    const url = '/likes';
    var options = {
     method: 'POST',
     headers: {'X-CSRFToken': csrftoken},
     mode: 'same-origin'
    }
    document.querySelectorAll('a.like').forEach(function(likeButton) {
    likeButton.addEventListener('click', function(e){
    e.preventDefault();

    var formData = new FormData();
    formData.append('id', likeButton.dataset.id);
    formData.append('action', likeButton.dataset.action);
    options['body'] = formData;
    fetch(url, options)
    .then(response => response.json())
    .then(data => {
    if (data['status'] === 'ok')
    {
        var previousAction = likeButton.dataset.action;
         var action = previousAction === 'like' ? 'unlike' : 'like';
         likeButton.dataset.action = action;
         if (action == 'unlike'){
            likeButton.innerHTML = '<img src="/static/network/img/unlike.png" alt="image" class="icon">';
         }
         else{
            likeButton.innerHTML = '<img src="/static/network/img/like.png" alt="image" class="icon">';
         }
         var likeCount = likeButton.closest('.post-wrapper').querySelector('span.total');
         console.log(likeCount)
         var totalLikes = parseInt(likeCount.innerHTML);
         likeCount.innerHTML = previousAction === 'like' ? totalLikes + 1 : totalLikes - 1;
    }
    })
});
});
})
