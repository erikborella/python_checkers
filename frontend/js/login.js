$("#btn-login").click(() => {

    const checkValidValue = (value) => !!value;

    const inputUsername = $("#input-username").val();
    const inputPassword = $("#input-password").val();

    let errors = "";

    let asErrors = false;

    if (!checkValidValue(inputUsername)) {
        errors += "Voce precisa digitar o nome de usuario<br>";
        asErrors = true;
    }

    if (!checkValidValue(inputPassword)) {
        errors += "Voce precisa digitar a sua senha";
        asErrors = true;
    }

    if (!asErrors) {
        login(inputUsername, inputPassword);
    } else {
        M.toast({ html: errors });
    }

})


/**
 * Realize the login
 * @param {string} username 
 * @param {string} password 
 */
function login(username, password) {
    $.ajax({
        url: `${apiUrl}/session/login`,
        type: "POST",
        data: {
            username: username,
            password: password
        },
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            handleLoginErros(result);
        }

    })
}

function handleLoginErros(apiResult) {
    if (apiResult.status) {
        window.location.replace("lobby.html");
    } else {
        M.toast({ html: apiResult.message })
    }
}