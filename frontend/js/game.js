let roomId;
let room;
let user;

$(document).ready(() => {
    checkIfIsLogged();
});

$("#btn-back").click(() => {
    redictToLobby();
});

function init() {
    const url_string = window.location.href;
    const url = new URL(url_string);

    roomId = url.searchParams.get("id");

    $.ajax({
        url: `${apiUrl}/room/get`,
        type: "POST",
        xhrFields: {
            withCredentials: true
        },
        data: {
            room_id: roomId
        },
        crossDomain: true,
        success: (result) => {
            console.log(result);
            if (result.status) {
                room = result.room;
                setTitle(room);
                renderBoard(room.board);
            } else {
                M.toast({ html: result.message })
            }
        }
    });

}

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
                init();
            }
        }
    });
}

function setTitle(room) {
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

    const setHtmlTitle = (str) => {
        $("#title").html(str);
        $("#title-logo").html(str);
    }

    if (checkIfIPlayTheRoom(room)) {
        setHtmlTitle("Jogar");
    } else if (!!room.user2_id) {
        setHtmlTitle("Assistir");
    } else {
        setHtmlTitle("Voce não deveria estar aqui!");
    }

}

function renderBoard(board) {
    let html = "";
    for (let i in board) {
        for (let j in board[i]) {
            if (board[i][j] == -1) {
                html += `<span class="piece" attr-i="${i}" attr-j="${j}">X</span>`;
            } else if (board[i][j] == 1) {
                html += `<span class="piece" attr-i="${i}" attr-j="${j}">O</span>`;
            } else {
                html += `<span class="piece" attr-i="${i}" attr-j="${j}">-</span>`;
            }
        }
        html += "<br>";
    }

    document.getElementById("board").innerHTML = html;
}

function redictToLobby() {
    window.location.replace("lobby.html");
}