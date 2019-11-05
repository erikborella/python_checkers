let user = null;

$(document).ready(() => {
    checkIfIsLogged();
    $('.modal').modal();
});

$("#btn-sair").click(() => {
    $.ajax({
        url: `${apiUrl}/session/logout`,
        type: "GET",
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            redictToLogin();
        }
    });
});

$("#btn-create-room").click(() => {
    $("#modal-create-room").modal("open");
});

$("#modal-btn-create-room").click(() => {
    const checkValidValue = (value) => !!value;
    const checkIfIsPairNumber = (value) => value % 2 == 0;

    const roomName = $("#input-create-room-name").val();
    const password = $("#input-create-password").val();
    const boardSize = $("#input-create-board-size").val();

    let errors = "";
    let asErrors = false;

    if (!checkValidValue(roomName)) {
        errors += "Voce deve digitar o nome da sala<br>";
        asErrors = true;
    }

    if (!checkValidValue(password)) {
        errors += "Voce deve digitar a senha<br>";
        asErrors = true;
    }

    if (!checkValidValue(boardSize)) {
        errors += "Voce deve digitar o tamanho do tabuleiro<br>";
        asErrors = true;
    } else if (!checkIfIsPairNumber(boardSize)) {
        errors += "O tamanho do tabuleiro deve ser par<br>";
        asErrors = true;
    }

    if (asErrors) {
        M.toast({ html: errors })
    } else {
        createRoom(roomName, password, boardSize);
    }

});

$("body").on("click", ".btn-room", function () {
    const enterType = $(this).attr("attr-type");
    const roomId = $(this).attr("attr-id");

    if (enterType === "enter") {
        openModalEnterInARoom(roomId);
    } else {
        redictToGame(roomId);
    }
});

$("#modal-btn-enter-room").click(() => {
    const checkValidValue = (value) => !!value;
    const roomId = $("#input-enter-room-id").val();
    const password = $("#input-enter-room-password").val();

    let errors = "";
    let asErrors = false;

    if (!checkValidValue(password)) {
        errors += "Voce precisa digitar sua senha";
        asErrors = true;
    }

    if (asErrors) {
        M.toast({ html: errors });
    } else {
        enterInARoom(roomId, password);
    }
})

function checkIfIsLogged() {
    $.ajax({
        url: `${apiUrl}/session`,
        type: "GET",
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            if (!result.status) {
                alert("Voce precisa estar logado para isso");
                redictToLogin();
            } else {
                user = result.user;
                loadRooms();
            }
        }
    });
}

function loadRooms() {
    $.ajax({
        url: `${apiUrl}/room/get`,
        type: "GET",
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            renderRooms(result.rooms);
        }
    });
}

function renderRooms(rooms) {
    const checkIfIPlayTheRoom = (room) => {
        if (room.user1_id == user.id) {
            return true;
        }

        if (!!room.user2_id) {
            if (room.user2_id == user.id) {
                return true;
            }
        }

        return false;
    }

    let html = ""; const getBoardSize = (room) => room.board;


    for (const room of rooms) {
        console.log(room);

        html += `<div class="card black">`;
        html += `<div class="card-content white-text">`;
        html += `<span class="card-title">${room.name}</span>`;
        html += `<p>Tamanho do tabuleiro = ${room.board.length}X${room.board.length}</p>`
        html += `</div>`;
        html += `<div class="card-action">`;
        if (checkIfIPlayTheRoom(room)) {
            html += `<a class="btn-room" attr-id="${room.id}" attr-type="open">Jogar</a>`
        } else if (!!room.user2_id) {
            html += `<a class="btn-room" attr-id="${room.id}" attr-type="open">Assistir</a>`
        }
        else {
            html += `<a class="btn-room" attr-id="${room.id}" attr-type="enter">Entrar</a>`;
        }
        html += `</div>`;
        html += `</div>`;

    }

    document.getElementById("rooms-list").innerHTML = html;
}

/**
 * Create the room
 * @param {string} roomName 
 * @param {string} password 
 * @param {number} boardSize 
 */
function createRoom(roomName, password, boardSize) {
    $.ajax({
        url: `${apiUrl}/room`,
        type: "POST",
        data: {
            name: roomName,
            password: password,
            board_size: boardSize
        },
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            if (!result.status) {
                M.toast({ html: result.message })
            } else {
                const html = "Sala criada com sucesso";
                M.toast({ html: html });
                loadRooms();
            }
        }

    })
}

/**
 * Open the modal for enter in a room and configure the id
 * @param {number} roomId 
 */
function openModalEnterInARoom(roomId) {
    $("#input-enter-room-id").val(roomId);
    $("#modal-enter-room").modal("open");
}


/**
 * Enter in the room
 * @param {number} roomId 
 * @param {string} password 
 */
function enterInARoom(roomId, password) {
    $.ajax({
        url: `${apiUrl}/room/enter`,
        type: "POST",
        data: {
            room_id: roomId,
            password: password
        },
        xhrFields: {
            withCredentials: true
        },
        crossDomain: true,
        success: (result) => {
            if (!result.status) {
                M.toast({ html: result.message })
            } else {
                const html = "Voce entrou na sala com sucesso";
                M.toast({ html: html });
                redictToGame(roomId);
            }
        }

    })
}

function redictToLogin() {
    window.location.replace("login.html");
}

/**
 * Go to the game scream
 * @param {number} id 
 */
function redictToGame(id) {
    window.location.replace(`game.html?id=${id}`);
}