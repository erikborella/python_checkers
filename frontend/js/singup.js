$("#btn-signup").click(() => {

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
        signup(inputUsername, inputPassword);
    } else {
        M.toast({ html: errors });
    }

})


/**
 * Realize the signup
 * @param {string} username 
 * @param {string} password 
 */
function signup(username, password) {
    $.ajax({
        url: `${apiUrl}/session/signup`,
        type: "POST",
        data: {
            username: username,
            password: password,
            icon: 0
        },
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            handleSignupErros(result);
        }

    })
}

function handleSignupErros(apiResult) {
    if (apiResult.status) {

    } else {
        M.toast({ html: apiResult.message })
    }
}