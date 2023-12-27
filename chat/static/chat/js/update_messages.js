const csrftoken = Cookies.get('csrftoken');
document.addEventListener("DOMContentLoaded", function(event) {
    console.log('2')
    fetch(window.location.href, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({}),
    });
});