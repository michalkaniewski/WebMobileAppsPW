/*const PL = 'ĄĆĘŁŃÓŚŹŻ';
const pl = 'ąćęłńóśźż';

function setUpEvents() {
    const form = document.getElementById("register-form");
    const firstName = document.getElementById("firstname");
    const lastName = document.getElementById("lastname");
    const login = document.getElementById("login");
    const password = document.getElementById("password");
    const rePassword = document.getElementById("repassword");
    const photo = document.getElementById("photo");
    const submit = document.getElementById("submit");
    rePassword.disabled = true;
    submit.disabled = true;
    firstName.addEventListener('change', (e) => validateName(e));
    lastName.addEventListener('change', (e) => validateName(e));
    login.addEventListener('change', (e) => validateLogin(e, submit));
    password.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    rePassword.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    photo.addEventListener('change', (e) => validateField(e));
    login.addEventListener('focus', () => {submit.disabled = true});
}

function validateName(e) {
    const regex = new RegExp(`^[A-Z${PL}][a-z${pl}]+$`);
    if (e.target.value.match(regex)) {
        e.target.classList.remove('incorrect');
    } else {
        e.target.value = "";
        e.target.classList.add('incorrect');
    }
}

function validateLogin(e, submit) {
    let status;
    const login = e.target.value;
    const regex = /^[a-z]{3,12}$/;

    if (login.match(regex)) {
        fetch(`https://infinite-hamlet-29399.herokuapp.com/check/${login}`).then(async response => {
            status = response.status;
            var data = await response.json();
            if(status === 200 && data[login] === 'available') {
                e.target.classList.remove('incorrect');
                submit.disabled = false;
            } else {
                e.target.value = "";
                submit.disabled = true;
                e.target.classList.add('incorrect');
            }
        });
    } else {
        e.target.value = "";
        e.target.classList.add('incorrect');
        return;
    }
}

function validatePassword(e, password, rePassword) {
    if (e.target.id === "password") {
        if (password.value.trim().length >= 8) {
            e.target.classList.remove('incorrect');
            rePassword.disabled = false;
        } else {
            e.target.classList.add('incorrect');
            rePassword.value = "";
            rePassword.disabled = true;
        }
    } else if (e.target.id === "repassword") {
        if (password.value === rePassword.value) {
            e.target.classList.remove('incorrect');
        } else {
            rePassword.value = "";
            e.target.classList.add('incorrect');
        }
    }
}

window.onload = function() {
    setUpEvents();
}*/