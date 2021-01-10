let notificationList;

function getNotifications() {
    fetch('/notification').then(res => {
        if (res.status === 200) {
            res.json().then(obj => addNewNotifications(obj.notifications));
        }
    });
    setTimeout(getNotifications, 500);
}

function addNewNotifications(notifications) {
    notifications.forEach(it => {
        let notification = document.createElement('li');
        let text;
        switch (it.new_status) {
            case 'ODEBRANA':
                text = `Odebrano paczkę ${it.label}!`;
                break;
            case 'W DRODZE':
                text = `Paczka ${it.label} wyruszyła w drogę!`;
                break;
            case 'DOSTARCZONA':
                text = `Dostarczono paczkę ${it.label}!`;
                break;
            default:
                break;
        }
        notification.innerText = text;
        notificationList.insertBefore(notification, notificationList.firstChild);
    });
}

function clearNotifications() {
    if (notificationList) {
        while (notificationList.firstChild) {
            notificationList.removeChild(notificationList.firstChild);
        }
    }
}

window.onload = function () {
    notificationList = document.getElementById("notification-list");
    const clearButton = document.getElementById("clear");
    clearButton.onclick = () => clearNotifications();
    getNotifications()
}