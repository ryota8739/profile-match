// ================================================
// Profile Match
// chat.js
// ================================================


// ================================================
// API URL
// ================================================

const CHAT_API_URL =
    typeof API_BASE_URL !== "undefined"
        ? API_BASE_URL
        : "http://13.115.204.216:8000";


// ================================================
// URLパラメータ
// ================================================

const params =
    new URLSearchParams(
        window.location.search
    );


const matchId =
    params.get("match_id");


const partnerUserId =
    params.get("user_id");


const partnerName =
    params.get("name") ||
    "相手";


// ================================================
// JWT
// ================================================

const chatToken =
    localStorage.getItem("access_token");


// ================================================
// 現在のユーザーID
// ================================================

const chatCurrentUserId =
    getUserIdFromToken(
        chatToken
    );


// ================================================
// デバッグ
// ================================================

console.log(
    "=== CHAT DEBUG ==="
);

console.log(
    "token exists:",
    !!chatToken
);

console.log(
    "currentUserId:",
    chatCurrentUserId
);

console.log(
    "matchId:",
    matchId
);

console.log(
    "partnerUserId:",
    partnerUserId
);

console.log(
    "partnerName:",
    partnerName
);


// ================================================
// 初期処理
// ================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        // ----------------------------------------
        // ログイン確認
        // ----------------------------------------

        if (!chatToken) {

            alert(
                "ログインしてください"
            );

            window.location.href =
                "login.html";

            return;
        }


        // ----------------------------------------
        // Match ID確認
        // ----------------------------------------

        if (!matchId) {

            alert(
                "Match IDがありません"
            );

            window.location.href =
                "messages.html";

            return;
        }


        // ----------------------------------------
        // 相手の名前
        // ----------------------------------------

        document.getElementById(
            "partnerName"
        ).textContent =
            partnerName;


        // ----------------------------------------
        // メッセージ取得
        // ----------------------------------------

        loadMessages();


        // ----------------------------------------
        // 3秒ごとに更新
        // ----------------------------------------

        setInterval(
            loadMessages,
            3000
        );


        // ----------------------------------------
        // 送信ボタン
        // ----------------------------------------

        document.getElementById(
            "sendButton"
        ).addEventListener(
            "click",
            sendMessage
        );


        // ----------------------------------------
        // Enterで送信
        // ----------------------------------------

        document.getElementById(
            "messageInput"
        ).addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    sendMessage();
                }

            }
        );

    }
);


// ================================================
// メッセージ取得
// ================================================

async function loadMessages() {

    try {

        console.log(
            "Loading messages:",
            matchId
        );


        const response =
            await fetch(
                `${CHAT_API_URL}/api/messages/${encodeURIComponent(matchId)}`,
                {
                    method: "GET",

                    headers: {

                        "Authorization":
                            `Bearer ${chatToken}`
                    }
                }
            );


        console.log(
            "Message API status:",
            response.status
        );


        if (!response.ok) {

            const errorText =
                await response.text();


            console.error(
                "Message API error:",
                errorText
            );


            if (
                response.status === 401
            ) {

                alert(
                    "ログイン情報が無効です。もう一度ログインしてください。"
                );

                localStorage.removeItem(
                    "access_token"
                );

                window.location.href =
                    "login.html";

                return;
            }


            if (
                response.status === 403
            ) {

                alert(
                    "このチャットを見る権限がありません。"
                );

                window.location.href =
                    "messages.html";

                return;
            }


            throw new Error(
                "メッセージ取得失敗"
            );
        }


        const data =
            await response.json();


        console.log(
            "Messages:",
            data
        );


        displayMessages(
            data.messages
        );


    } catch (error) {

        console.error(
            "loadMessages error:",
            error
        );

    }

}


// ================================================
// メッセージ表示
// ================================================

function displayMessages(
    messages
) {

    const container =
        document.getElementById(
            "messages"
        );


    container.innerHTML = "";


    if (
        !messages ||
        messages.length === 0
    ) {

        container.innerHTML = `
            <div class="empty">
                まだメッセージはありません。
            </div>
        `;

        return;
    }


    messages.forEach(
        function (message) {

            const row =
                document.createElement(
                    "div"
                );


            // ------------------------------------
            // 自分 / 相手
            // ------------------------------------

            const isMine =
                message.sender_id ===
                chatCurrentUserId;


            row.className =
                isMine
                    ? "message-row mine"
                    : "message-row other";


            // ------------------------------------
            // メッセージ
            // ------------------------------------

            const messageBox =
                document.createElement(
                    "div"
                );


            const content =
                document.createElement(
                    "div"
                );


            content.className =
                "message";


            content.textContent =
                message.content;


            // ------------------------------------
            // 時刻
            // ------------------------------------

            const time =
                document.createElement(
                    "div"
                );


            time.className =
                "time";


            time.textContent =
                formatDate(
                    message.created_at
                );


            messageBox.appendChild(
                content
            );


            messageBox.appendChild(
                time
            );


            row.appendChild(
                messageBox
            );


            container.appendChild(
                row
            );

        }
    );


    // --------------------------------------------
    // 一番下までスクロール
    // --------------------------------------------

    container.scrollTop =
        container.scrollHeight;
}


// ================================================
// メッセージ送信
// ================================================

async function sendMessage() {

    const input =
        document.getElementById(
            "messageInput"
        );


    const button =
        document.getElementById(
            "sendButton"
        );


    const content =
        input.value.trim();


    if (!content) {

        return;
    }


    button.disabled =
        true;


    try {

        const response =
            await fetch(
                `${CHAT_API_URL}/api/messages`,
                {
                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${chatToken}`
                    },

                    body: JSON.stringify({

                        match_id:
                            matchId,

                        content:
                            content
                    })
                }
            );


        console.log(
            "Send API status:",
            response.status
        );


        if (!response.ok) {

            const errorText =
                await response.text();


            console.error(
                "Send error:",
                errorText
            );


            if (
                response.status === 401
            ) {

                alert(
                    "ログイン情報が無効です。"
                );

                return;
            }


            throw new Error(
                "メッセージ送信失敗"
            );
        }


        const data =
            await response.json();


        console.log(
            "Sent:",
            data
        );


        // ----------------------------------------
        // 入力欄をクリア
        // ----------------------------------------

        input.value = "";


        // ----------------------------------------
        // 即時更新
        // ----------------------------------------

        await loadMessages();


        input.focus();


    } catch (error) {

        console.error(
            "sendMessage error:",
            error
        );

        alert(
            "メッセージの送信に失敗しました"
        );

    } finally {

        button.disabled =
            false;

    }

}


// ================================================
// 日付表示
// ================================================

function formatDate(
    dateString
) {

    if (!dateString) {

        return "";
    }


    const date =
        new Date(
            dateString
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "";
    }


    return date.toLocaleString(
        "ja-JP",
        {
            month: "numeric",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


// ================================================
// JWTからuser_id取得
// ================================================

function getUserIdFromToken(
    token
) {

    if (!token) {

        return null;
    }


    try {

        const parts =
            token.split(".");


        if (parts.length !== 3) {

            return null;
        }


        // Base64URL → Base64
        let payload =
            parts[1]
                .replace(/-/g, "+")
                .replace(/_/g, "/");


        // padding
        while (
            payload.length % 4
        ) {

            payload += "=";
        }


        const decoded =
            JSON.parse(
                atob(payload)
            );


        console.log(
            "JWT payload:",
            decoded
        );


        return (
            decoded.user_id ||
            decoded.sub ||
            null
        );


    } catch (error) {

        console.error(
            "JWT decode error:",
            error
        );

        return null;
    }
}
