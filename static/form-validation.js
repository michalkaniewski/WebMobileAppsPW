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
    login.addEventListener('change', (e) => {
        validateLogin(e, submit);
    });
    password.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    rePassword.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    photo.addEventListener('change', (e) => validateField(e));
    login.addEventListener('focus', () => {submit.disabled = true});
}

function validateName(e) {
    const regex = /^[A-Z][a-z][a-z]*/; // FIXME: do poprawy regex
    if (e.target.value.match(regex)) {
        console.log(e.target.name, "valid");
    } else {
        e.target.value = "";
        console.log(e.target.name, "invalid");
    }
}

function validateLogin(e, submit) {
    const login = e.target.value;
    const regex = /^[a-z][a-z][a-z]*/; // FIXME: do poprawy regex
    if (!login.match(regex)) {
        e.target.value = "";
        console.log("Login invalid");
        return;
    }
    let status;
    
    fetch(`https://infinite-hamlet-29399.herokuapp.com/check/${login}`).then(async response => {
        status = response.status;
        var data = await response.json();
        if(status === 200 && data[login] === 'available') {
            console.log("Login OK");
            submit.disabled = false;
        } else {
            e.target.value = "";
            submit.disabled = true;
            console.log("login taken");
        }
    });
}

function validatePassword(e, password, rePassword) {
    if (e.target.id === "password") {
        if (password.value.length >= 8) {
            rePassword.disabled = false;
        } else {
            console.log("PASSWORD TOO SHORT")
            rePassword.value = "";
            rePassword.disabled = true;
        }
    } else if (e.target.id === "repassword") {
        if (password.value === rePassword.value) {
            console.log("PASSWORD OK")
        } else {
            rePassword.value = "";
            console.log("PASSWORD MUST BE THE SAME");
        }
    }
}

window.onload = function() {
    setUpEvents();
}