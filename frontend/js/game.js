let roomId;
let room;
let user;

let isSelected = false;
let isMyTurn = true;
let movements = []

$(document).ready(() => {
    checkIfIsLogged();
});

$("#btn-back").click(() => {
    redictToLobby();
});

$("body").on("click", ".piece", function () {

    const type = $(this).attr("attr-type");
    const row = $(this).attr("attr-i");
    const col = $(this).attr("attr-j");

    let findPossibleMove = false;

    if (isSelected) {
        for (const move of movements) {
            if (move.row == row && move.col == col) {
                movePiece(row, col);
                findPossibleMove = true;
                break;
            }
        }
    }
    if (!findPossibleMove) {
        if (checkPieceType(type)) {
            $.ajax({
                url: `${apiUrl}/game/movements`,
                type: "POST",
                xhrFields: {
                    withCredentials: true
                },
                data: {
                    room_id: roomId,
                    row: row,
                    col: col
                },
                crossDomain: true,
                success: (result) => {
                    renderBoard(room.board);
                    movements = result.movements;
                    if (result.movements.length > 0) {
                        isSelected = true;
                        for (const piece of result.movements) {
                            setPieceColor(piece.row, piece.col);
                        }
                    } else {
                        M.toast({ html: "Nenhum movimento possivel" })
                        isSelected = false;
                    }
                }
            })
        }
    }

})

function setPieceColor(i, j) {
    $(`.piece[attr-i=${i}][attr-j=${j}]`).css("color", "green");
}

function movePiece(row, col) {
    $.ajax({
        url: `${apiUrl}/game/play`,
        type: "POST",
        xhrFields: {
            withCredentials: true
        },
        data: {
            room_id: roomId,
            row: row,
            col: col
        },
        crossDomain: true,
        success: (result) => {
            console.log(result);
        }
    })
}

function checkPieceType(type) {
    const showToast = (message) => M.toast({ html: message });
    if (type === "enemy") {
        showToast("Você não pode selecionar uma pessoa enemiga")
        return false;
    } else if (type == "nothing") {
        showToast("Voce não pode selecionar o nada");
        return false;
    } else {
        return true;
    }
}


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
                updateTurnIndicator();
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
                html += `<span class="piece" attr-i="${i}" attr-j="${j}" attr-type="your">X</span>`;
            } else if (board[i][j] == 1) {
                html += `<span class="piece" attr-i="${i}" attr-j="${j}" attr-type="enemy">O</span>`;
            } else {
                html += `<span class="piece" attr-i="${i}" attr-j="${j}" attr-type="nothing">-</span>`;
            }
        }
        html += "<br>";
    }

    document.getElementById("board").innerHTML = html;
}

function updateTurnIndicator() {
    const update = (turn) => {
        $("#turn-indicator").html(turn ? "Sua vez" : "Vez do adversario");
    }
    if (room.turn == 1) {
        if (user.id == room.user1_id) {
            update(true);
        } else {
            update(false)
        }
    } else if (room.turn == 2) {
        if (user.id == room.user2_id) {
            update(true);
        } else {
            update(false)
        }
    }
}

function redictToLobby() {
    window.location.replace("lobby.html");
}