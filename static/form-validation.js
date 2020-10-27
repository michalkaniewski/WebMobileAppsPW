function setUpEvents() {
    const firstName = document.getElementById("firstname");
    const lastName = document.getElementById("lastname");
    const login = document.getElementById("login");
    const password = document.getElementById("password");
    const rePassword = document.getElementById("repassword");
    const photo = document.getElementById("photo");
    const submit = document.getElementById("submit");
    firstName.addEventListener('change', (e) => validateField(e));
    lastName.addEventListener('change', (e) => validateField(e));
    login.addEventListener('change', (e) => validateField(e));
    password.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    rePassword.addEventListener('change', (e) => validatePassword(e, password, rePassword));
    photo.addEventListener('change', (e) => validateField(e));
}

function validateField(e) {
    switch (e.target.id) {
        case "firstname":
        case "lastname":
            validateName(e.target.value);
            break;
        case "login":
            validateLogin(e.target.value);
            break;
        default:
            break;
    }
}

function validateName(name) {
    const regex = /^[A-Z][a-z][a-z]*/; // FIXME: do poprawy regex
    if (name.match(regex)) {
        console.log("valid");
    } else {
        console.log("invalid");
    }
}

function validateLogin(login) {
    const regex = /^[a-z][a-z][a-z]*/; // FIXME: do poprawy regex
    if (!login.match(regex)) {
        console.log("invalid");
        return;
    }
    let status;
    
    fetch(`https://infinite-hamlet-29399.herokuapp.com/check/${login}`).then(async response => {
        status = response.status;
        var data = await response.json();
        if(status === 200 && data[login] === 'available') {
            console.log("valid")
        } else {
            console.log("invalid");
        }
    });
}

function validatePassword(e, password, rePassword) {
    if (e.target.id === "password") {
        // TODO: regex
    } else if (e.target.id === "repassword") {
        if (password.value === rePassword.value) {
            console.log("re password valid");
        } else {
            console.log("re password invalid");
        }
    }
}

window.onload = function() {
    setUpEvents();
}